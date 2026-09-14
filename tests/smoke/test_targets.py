"""Erreichbarkeit der Prüfziele — hier ist Erreichbarkeit die Aussage."""

import pytest

from speccify_qa.speccify import mcp_tools


@pytest.mark.smoke
def test_desktop_ui_mcp_offers_the_question_tools(desktop_ui: str) -> None:
    tools = mcp_tools(desktop_ui)
    assert {"ask_bo", "show_ui", "ui_result"} <= set(tools), tools
