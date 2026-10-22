# craft-skills · Airbnb 上架包流水线
#
#   make run SENTENCE="给我家 Airbnb 做全套上架包"
#   make audit            # 只跑检查（不重跑生产站）
#   make verify           # 记录 ⚠️ 工具的真实状态（pass / fail）
#
# 需要：python3 + jq + ffmpeg + weasyprint + sox + libvips/ImageMagick。
# 可选：FFMPEG_HOST=pc（本机 ffmpeg 不可用时，用 SSH 把编码送到另一台 Linux）

SHELL := /bin/sh
PY := python3
SENTENCE ?= 给我家 Airbnb（Home in Rosebery · 独立房间）做全套上架包
RUN_ID ?= R$(shell date +%Y%m%d-%H%M)-airbnb
export RUN_ID
export SENTENCE
export FFMPEG_HOST ?= pc

.PHONY: run stations audit verify clean score list

run:
	$(PY) pipeline/make_schemas.py
	$(PY) pipeline/run_all.py --sentence "$(SENTENCE)" --run-id "$(RUN_ID)"

stations:
	@for s in 0_brief 1_collect 2_pricing 3_photos 4_video 5_copy 6_guide 7_site 9_support 8_qc; do \
	  echo "== $$s"; $(PY) pipeline/$$s.py || exit 1; \
	done

audit:
	$(PY) qa/secret_scan.py runs/$(RUN_ID) --json runs/$(RUN_ID)/reports/secret_scan.json
	$(PY) qa/trace_check.py runs/$(RUN_ID)
	$(PY) pipeline/failtest.py
	$(PY) pipeline/scorecards.py

verify:
	$(PY) pipeline/verify_tools.py

score:
	$(PY) pipeline/scorecards.py

list:
	@ls -1 runs/ | tail -10

clean:
	rm -rf runs/$(RUN_ID)/_build
