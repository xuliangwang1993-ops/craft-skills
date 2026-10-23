# 宣传视频试生产流水线（纯 CPU）。用法：make setup && make run SENTENCE="..."
PY ?= python3
SENTENCE ?= 给悉尼小锅米线（Slurp Slurp Noodle）做一支 30 秒宣传短视频，配中英字幕和三个社媒尺寸
.PHONY: setup verify run fault-demo report schemas
setup:
	$(PY) -m pip install -r pipeline/requirements.txt
	$(PY) -c "import argostranslate.package as p; p.update_package_index(); [p.install_from_path(x.download()) for x in p.get_available_packages() if (x.from_code,x.to_code) in (('zh','en'),('en','zh'))]"
schemas:
	$(PY) schemas/gen.py
verify:
	bash pipeline/verify_tools.sh
run:
	$(PY) pipeline/run.py "$(SENTENCE)"
fault-demo:
	-FAULT=price $(PY) pipeline/run.py "$(SENTENCE)"
	-FAULT=nolicense $(PY) pipeline/run.py "$(SENTENCE)"
report:
	$(PY) pipeline/scorecard.py
