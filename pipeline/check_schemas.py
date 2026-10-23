#!/usr/bin/env python3
"""Validates every schemas/*.schema.json against JSON Schema 2020-12."""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

bad = 0
for path in sorted(Path(__file__).resolve().parents[1].joinpath("schemas").glob("*.schema.json")):
    schema = json.loads(path.read_text(encoding="utf-8"))
    try:
        Draft202012Validator.check_schema(schema)   # raises on an invalid schema
        print("OK   " + path.name)
    except Exception as exc:
        print("BAD  " + path.name + " — " + str(exc)[:160])
        bad += 1
print(f"{len(list(Path(__file__).resolve().parents[1].joinpath('schemas').glob('*.json')))} schemas, {bad} error(s)")
sys.exit(0 if bad == 0 else 1)
