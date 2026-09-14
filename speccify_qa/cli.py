"""`speccify-qa`: Abnahmen anlegen, laufen lassen, Checklisten erfassen, berichten.

Alles ist ohne Terminal-Interaktion bedienbar (Agenten): Antworten kommen als
`--antworten 1=ja,2=nein --pruefer Name`; ohne `--antworten` fragt die CLI
interaktiv.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from speccify_qa import abnahme as ab
from speccify_qa.environments import current_environment
from speccify_qa.speccify import mcp_reachable, mcp_tools, reachable


def _root(args: argparse.Namespace) -> Path:
    return Path(args.root).resolve()


def cmd_env(args: argparse.Namespace) -> int:
    env = current_environment()
    print(f"Umgebung: {env.name} — {env.label}")
    down: list[str] = []
    for key, value in env.speccify.items():
        state = ""
        if key in {"desktop_ui", "board_mcp"}:
            ok = mcp_reachable(value)
        elif key in {"mock", "board"}:
            ok = reachable(value)
        else:
            ok = None
        if ok is not None:
            state = "  (erreichbar)" if ok else "  (nicht erreichbar)"
            if not ok:
                down.append(key)
        print(f"  {key}: {value}{state}")
    missing = env.missing_secrets()
    if missing:
        print(
            "  fehlende Secrets: "
            + ", ".join(missing)
            + "  (als Umgebungsvariable setzen; nie in Dateien)"
        )
    hints = [(key, env.hints[key]) for key in down if key in env.hints]
    if hints:
        print("Nicht erreichbare Ziele starten:")
        for key, hint in hints:
            print(f"  {key}: {hint}")
    if args.tools:
        try:
            print("  Desktop-UI-Tools: " + ", ".join(mcp_tools(env.target("desktop_ui"))))
        except Exception as exc:  # noqa: BLE001
            print(f"  Desktop-UI-Tools: {exc}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    items = ab.list_all(_root(args))
    if not items:
        print("Keine Abnahmen.")
        return 0
    for item in items:
        result = item.ergebnis() or {}
        tests = result.get("tests", {}).get("summary")
        check = result.get("checkliste")
        state = []
        if tests is not None:
            state.append("Tests " + ("grün" if result["tests"].get("exit_code") == 0 else "rot"))
        if check:
            state.append(
                "Checkliste " + ("bestanden" if check.get("bestanden") else "offen/nicht bestanden")
            )
        print(
            f"{item.name}: {item.titel}"
            + (f"  [{' · '.join(state)}]" if state else "  [kein Lauf]")
        )
    return 0


def cmd_anlegen(args: argparse.Namespace) -> int:
    plan = Path(args.plan).read_text(encoding="utf-8") if args.plan else ""
    bezug = dict(item.split("=", 1) for item in args.bezug or [])
    item = ab.anlegen(_root(args), args.name, titel=args.titel or args.name, bezug=bezug, plan=plan)
    print(f"Angelegt: {item.folder}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    item = ab.load(_root(args), args.name)
    tests = ab.run_tests(_root(args), item, pytest_args=args.pytest_args)
    ab.ergebnis_schreiben(item, tests=tests)
    print(tests["output_tail"])
    print(
        json.dumps(
            {"exit_code": tests["exit_code"], "summary": tests["summary"]}, ensure_ascii=False
        )
    )
    return 0 if tests["exit_code"] == 0 else 1


def cmd_checkliste(args: argparse.Namespace) -> int:
    item = ab.load(_root(args), args.name)
    if not item.schritte:
        print("Keine Checkliste (checkliste.yaml ohne Schritte).")
        return 1
    if args.antworten:
        antworten = ab.parse_antworten(args.antworten)
        pruefer = args.pruefer or ""
        notizen = dict(n.split("=", 1) for n in args.notiz or [])
    else:
        if not sys.stdin.isatty():
            print(
                "Keine Antworten und kein Terminal — "
                "`--antworten 1=ja,... --pruefer Name` verwenden."
            )
            return 2
        pruefer = args.pruefer or input("Prüfer: ").strip()
        antworten, notizen = {}, {}
        for schritt in item.schritte:
            print(f"\n[{schritt.id}] {schritt.text}\n    Erwartung: {schritt.erwartung}")
            while True:
                answer = input("    ja / nein / offen: ").strip().lower() or "offen"
                if answer in {"ja", "nein", "offen"}:
                    break
            antworten[schritt.id] = answer
            note = input("    Notiz (leer = keine): ").strip()
            if note:
                notizen[schritt.id] = note
    result = ab.checkliste_erfassen(item, pruefer=pruefer, antworten=antworten, notizen=notizen)
    ab.ergebnis_schreiben(item, checkliste=result)
    print("bestanden" if result["bestanden"] else "nicht bestanden")
    return 0 if result["bestanden"] else 1


def cmd_bericht(args: argparse.Namespace) -> int:
    item = ab.load(_root(args), args.name)
    print(ab.bericht(item), end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="speccify-qa", description="QA für Speccify — von Agenten bedienbar."
    )
    parser.add_argument(
        "--root", default=".", help="Projektwurzel (Standard: aktuelles Verzeichnis)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    env = sub.add_parser("env", help="Umgebung und Erreichbarkeit der Prüfziele zeigen")
    env.add_argument("--tools", action="store_true", help="Tools des Desktop-UI-MCP auflisten")
    env.set_defaults(func=cmd_env)

    abn = sub.add_parser("abnahme", help="Abnahmen verwalten")
    abn_sub = abn.add_subparsers(dest="abnahme_command", required=True)
    abn_sub.add_parser("list", help="alle Abnahmen mit Stand").set_defaults(func=cmd_list)
    anlegen = abn_sub.add_parser("anlegen", help="neue Abnahme anlegen")
    anlegen.add_argument("name")
    anlegen.add_argument("--titel")
    anlegen.add_argument("--plan", help="Markdown-Datei als plan.md übernehmen")
    anlegen.add_argument(
        "--bezug", action="append", help="z. B. spec=011-auftragskontext, repo=speccify"
    )
    anlegen.set_defaults(func=cmd_anlegen)
    run = abn_sub.add_parser("run", help="automatische Prüfungen der Abnahme ausführen")
    run.add_argument("name")
    run.add_argument("pytest_args", nargs="*", help="weitere pytest-Argumente")
    run.set_defaults(func=cmd_run)
    check = abn_sub.add_parser("checkliste", help="menschliche Prüfschritte erfassen")
    check.add_argument("name")
    check.add_argument("--antworten", help="1=ja,2=nein,3=offen (ohne: interaktiv)")
    check.add_argument("--pruefer", help="Name der prüfenden Person")
    check.add_argument("--notiz", action="append", help="<schritt>=<Text>")
    check.set_defaults(func=cmd_checkliste)
    bericht = abn_sub.add_parser("bericht", help="Markdown-Bericht des letzten Standes")
    bericht.add_argument("name")
    bericht.set_defaults(func=cmd_bericht)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (ab.AbnahmeError, KeyError) as exc:
        print(f"x {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
