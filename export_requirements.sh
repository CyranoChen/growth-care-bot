#!/bin/sh

# Export uv.lock to requirements.txt
uv export --no-hashes --no-header --no-group dev > requirements.txt
uv export --no-hashes --no-header --only-dev > requirements-dev.txt
