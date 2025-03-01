#!/bin/sh

# Export uv.lock to requirements.txt
uv export --no-hashes --no-header --no-group dev --no-emit-project > requirements.txt
uv export --no-hashes --no-header --all-groups --no-emit-project > requirements-dev.txt
