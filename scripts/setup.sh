#!/usr/bin/env bash
# Einrichten: uv-Umgebung, Playwright-Browser, versteckte .pth-Dateien (macOS).
set -euo pipefail
cd "$(dirname "$0")/.."
uv sync --all-groups
# macOS: uv setzt UF_HIDDEN auf .pth-Dateien; Python ≥ 3.13 überspringt sie dann.
if [ "$(uname)" = "Darwin" ]; then
  find .venv/lib -name "*.pth" -exec chflags nohidden {} + 2>/dev/null || true
fi
uv run playwright install chromium >/dev/null 2>&1 || echo "Playwright-Browser nicht installiert (offline?) — später: uv run playwright install chromium"
uv run python -m speccify_qa.cli env
