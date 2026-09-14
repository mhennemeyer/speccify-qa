"""Page-Objects für die Speccify-App über die QA-Brücke.

Jedes Objekt kapselt DOM-Wissen (Rollen, Labels, data-Attribute) an genau
einer Stelle; Tests sprechen von „Board“, „Auftrag“, „Terminal“. Klicks und
Eingaben laufen im DOM der echten App, Prüfungen lesen den DOM oder den
QA-Haken `window.__speccifyQa`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from speccify_qa.bridge import Bridge, BridgeError

# Gemeinsame DOM-Helfer, in jedes Skript eingebettet.
_HELPERS = r"""
function $$(sel, root) { return Array.from((root || document).querySelectorAll(sel)); }
function byRole(role, name, root) {
  const all = $$('[role="' + role + '"], ' + (role === 'button' ? 'button' : 'x-none'), root);
  return all.find(el => name === undefined || (el.getAttribute('aria-label') || el.textContent || '').trim() === name) || null;
}
function byLabel(label, root) {
  return $$('[aria-label="' + label + '"]', root)[0] || null;
}
function dialog(name) { return $$('[role="dialog"]').find(el => (el.getAttribute('aria-label') || '') === name) || null; }
function statusText(root) { return $$('[role="status"]', root || document).map(el => el.textContent.trim()); }
function setValue(el, value) {
  const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, value);
  el.dispatchEvent(new Event('input', { bubbles: true }));
}
"""


def _js(body: str) -> str:
    return _HELPERS + "\n" + body


@dataclass
class App:
    bridge: Bridge

    def windows(self) -> list[dict[str, Any]]:
        return self.bridge.windows()

    def project_windows(self) -> list[ProjectWindow]:
        found = []
        for info in self.windows():
            label = info["label"]
            if not label.startswith("project-"):
                continue
            root = self.bridge.invoke(label, "project_current")
            found.append(ProjectWindow(self.bridge, label, Path(root) if root else None))
        return found

    def project_window(self, root: Path) -> ProjectWindow | None:
        wanted = root.resolve()
        for window in self.project_windows():
            if window.root and window.root.resolve() == wanted:
                return window
        return None

    def open_project(self, root: Path, *, timeout: float = 15.0) -> ProjectWindow:
        """Projektfenster öffnen (oder das vorhandene fokussieren) und zurückgeben."""
        existing = self.project_window(root)
        if existing:
            self.bridge.focus(existing.label)
            return existing
        self.bridge.invoke("main", "project_open", {"path": str(root)})
        import time

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            window = self.project_window(root)
            if window and window.ready():
                return window
            time.sleep(0.3)
        raise BridgeError(f"Projektfenster für {root} nicht erschienen")


@dataclass
class ProjectWindow:
    bridge: Bridge
    label: str
    root: Path | None

    def eval(self, body: str, **kwargs: Any) -> Any:
        return self.bridge.eval(self.label, _js(body), **kwargs)

    def wait(self, body: str, *, timeout: float = 10.0) -> Any:
        return self.bridge.wait_for(self.label, _js(body), timeout=timeout)

    def ready(self) -> bool:
        try:
            return bool(
                self.eval(
                    "return !!document.querySelector('[data-spec-card], [aria-label=\"Spec-Liste\"]') || document.body.textContent.includes('Backlog');"
                )
            )
        except BridgeError:
            return False

    def screenshot(self, target: Path) -> Path:
        return self.bridge.screenshot(self.label, target)

    # --- Board -------------------------------------------------------------

    @property
    def board(self) -> Board:
        return Board(self)

    @property
    def terminal(self) -> Terminal:
        return Terminal(self)

    def handover_dialog(self) -> HandoverDialog:
        return HandoverDialog(self)

    def clipboard(self) -> str:
        return str(self.bridge.invoke(self.label, "plugin:clipboard-manager|read_text") or "")

    def read_file(self, relative: str) -> str:
        return str(
            self.bridge.invoke(
                self.label, "project_read_file", {"project": str(self.root), "file": relative}
            )
        )

    def write_file(self, relative: str, content: str) -> None:
        self.bridge.invoke(
            self.label,
            "project_write_file",
            {"project": str(self.root), "file": relative, "content": content},
        )


@dataclass
class Board:
    window: ProjectWindow

    def cards(self, station: str | None = None) -> list[dict[str, str]]:
        scope = f'[data-station="{station}"] ' if station else ""
        return self.window.eval(
            f"""return $$('{scope}[data-spec-card]').map(el => ({{ file: el.getAttribute('data-spec-card'),
              station: (el.closest('[data-station]') || {{getAttribute(){{return ''}}}}).getAttribute('data-station'),
              text: el.textContent.trim().slice(0, 120) }}));"""
        )

    def select(self, file: str) -> None:
        """Karte anklicken (erste Schaltfläche = Auswahl in den Inspektor)."""
        ok = self.window.eval(
            f"""const card = $$('[data-spec-card]').find(el => el.getAttribute('data-spec-card') === {json.dumps(file)});
            if (!card) return false; (card.querySelector('button') || card).click(); return true;"""
        )
        if not ok:
            raise BridgeError(f"Spec-Karte {file} nicht gefunden")
        self.window.wait("return !!byRole('button', 'Auftrag…');")

    def open_handover(self) -> HandoverDialog:
        self.window.eval("byRole('button', 'Auftrag…').click(); return true;")
        dialog = self.window.handover_dialog()
        dialog.wait_open()
        return dialog


@dataclass
class HandoverDialog:
    window: ProjectWindow

    def wait_open(self) -> None:
        self.window.wait(
            "return !!(dialog('Auftrag') && byLabel('Auftragstext', dialog('Auftrag')));"
        )

    def is_open(self) -> bool:
        return bool(self.window.eval("return !!dialog('Auftrag');"))

    def preview(self) -> str:
        return str(self.window.eval("return byLabel('Auftragstext', dialog('Auftrag')).value;"))

    def path(self) -> str:
        return str(
            self.window.eval(
                "return dialog('Auftrag').querySelector('.font-mono[title]').getAttribute('title');"
            )
        )

    def kinds(self) -> list[str]:
        return list(
            self.window.eval(
                "return $$('.rounded-full', dialog('Auftrag')).map(el => el.textContent.trim());"
            )
        )

    def choose(self, kind_label: str) -> None:
        self.window.eval(
            f"byRole('button', {json.dumps(kind_label)}, dialog('Auftrag')).click(); return true;"
        )

    def terminal_ready(self) -> bool:
        return self.window.eval(
            "return dialog('Auftrag').querySelector('[data-terminal-ready]').getAttribute('data-terminal-ready') === 'true';"
        )

    def insert_into_terminal(self) -> str:
        self.window.eval(
            "byRole('button', 'Ins Terminal einfügen', dialog('Auftrag')).click(); return true;"
        )
        return str(
            self.window.wait(
                "const s = statusText(dialog('Auftrag')); return s.length ? s[s.length - 1] : '';"
            )
        )

    def copy(self) -> str:
        self.window.eval("byRole('button', 'Kopieren', dialog('Auftrag')).click(); return true;")
        return str(
            self.window.wait(
                "const s = statusText(dialog('Auftrag')).filter(t => t.includes('kopiert')); return s[0] || '';"
            )
        )

    def start_terminal(self) -> None:
        self.window.eval(
            "byRole('button', 'Terminal starten', dialog('Auftrag')).click(); return true;"
        )

    def statuses(self) -> list[str]:
        return list(self.window.eval("return statusText(dialog('Auftrag'));"))

    def has_button(self, name: str) -> bool:
        return bool(
            self.window.eval(f"return !!byRole('button', {json.dumps(name)}, dialog('Auftrag'));")
        )

    def close(self) -> None:
        self.window.eval(
            "const b = byRole('button', 'Schließen', dialog('Auftrag')); if (b) b.click(); return true;"
        )


@dataclass
class Terminal:
    window: ProjectWindow

    def ready(self) -> bool:
        return bool(self.window.eval("return window.__speccifyQa.terminalReady();"))

    def wait_ready(self, timeout: float = 20.0) -> None:
        self.window.wait("return window.__speccifyQa.terminalReady();", timeout=timeout)

    def text(self) -> str:
        return str(self.window.eval("return window.__speccifyQa.terminalText() || '';"))

    def wait_text(self, needle: str, timeout: float = 20.0) -> str:
        self.window.wait(
            f"return (window.__speccifyQa.terminalText() || '').includes({json.dumps(needle)});",
            timeout=timeout,
        )
        return self.text()
