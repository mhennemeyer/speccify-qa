from pathlib import Path

from speccify_qa.environments import current_environment, load_environments


def test_default_environment_names_the_speccify_targets() -> None:
    default, environments = load_environments()
    assert default == "local" and "local" in environments
    env = current_environment()
    assert env.target("desktop_ui").startswith("http://127.0.0.1:")
    assert env.target("mock").endswith("mock.html")
    assert env.repo.name == "speccify" or env.repo.is_absolute()


def test_env_expansion(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("QA_X", "/tmp/x")
    (tmp_path / "environments.yaml").write_text(
        "default_environment: a\nenvironments:\n  a:\n    label: A\n    speccify:\n"
        "      repo: ${QA_X}\n      mock: ${QA_MISSING:-http://m}\n",
        encoding="utf-8",
    )
    _, environments = load_environments(tmp_path / "environments.yaml")
    assert environments["a"].speccify == {"repo": "/tmp/x", "mock": "http://m"}
