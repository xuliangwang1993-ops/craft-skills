# craft-skills · 宣传视频试生产流水线
#
#   make run SENTENCE="给悉尼小锅米线（Slurp Slurp Noodle）做一支 30 秒宣传短视频，配中英字幕和三个社媒尺寸"
#
# Runs 8 stations, each writing handoff.json / qa.json / scorecard.json.
# Any station that exits non-zero stops the chain (and make exits non-zero).

SHELL := /bin/sh
PY ?= python3
RUN_ID ?= $(shell date -u +%Y%m%dT%H%M%S)
SENTENCE ?=

.PHONY: help run verify-tools schemas report fail-drill clean-check check-schemas

help:
	@echo "make run SENTENCE=\"...\"   # 全链跑一遍"
	@echo "make verify-tools          # 写 reports/tool_verification.json"
	@echo "make schemas               # 重新生成 schemas/*.schema.json"
	@echo "make report RUN_ID=...     # 汇总评分卡"
	@echo "make fail-drill            # 演示：字幕价格被改错 → 下游停链"

run:
	@test -n "$(SENTENCE)" || (echo 'SENTENCE is required'; exit 2)
	@RUN_ID=$(RUN_ID) SENTENCE="$(SENTENCE)" $(PY) pipeline/run_all.py

verify-tools:
	@$(PY) pipeline/verify_tools.py

schemas:
	@$(PY) pipeline/make_schemas.py

report:
	@$(PY) pipeline/report.py $(RUN_ID)

fail-drill:
	@$(PY) tests/fail_drill.py

check-schemas:
	@$(PY) - <<'PY'
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator
ok = True
for p in sorted(Path("schemas").glob("*.schema.json")):
    schema = json.loads(p.read_text())
    errs = list(Draft202012Validator.check_schema(schema))
    print(("OK  " if not errs else "BAD ") + p.name)
    ok = ok and not errs
sys.exit(0 if ok else 1)
PY
