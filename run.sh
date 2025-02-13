#!/bin/sh
set -e

# uv init
# uv run pre-commit install
# uv venv
# source .venv/bin/activate
# uv sync

uv run python main.py
# uv run python test.py
