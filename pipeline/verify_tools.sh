#!/usr/bin/env bash
# ⚠️ 未验证工具：本次运行中按 SKILL.md 安装并跑通示例，结果写 reports/tool_verification.json
set -u; cd "$(dirname "$0")/.."; W=$(mktemp -d); OUT=reports/tool_verification.json; mkdir -p reports
rows=()
rec(){ # name version install example code secs status note
  rows+=("$(jq -n --arg n "$1" --arg v "$2" --arg i "$3" --arg e "$4" --argjson c "$5" --argjson s "$6" --arg st "$7" --arg no "$8" '{tool:$n,version:$v,install:$i,example:$e,exit_code:$c,seconds:$s,status:$st,note:$no}')")
}
t(){ local s=$(date +%s%N); bash -c "$1" >"$W/log" 2>&1; local c=$?; echo "$c $(awk -v a=$s -v b=$(date +%s%N) "BEGIN{printf \"%.2f\", (b-a)/1e9}")"; }
# jq
read c s < <(t 'echo "{\"a\":[1,2,3]}" | jq -e ".a|length==3"')
rec jq "$(jq --version)" "apt install jq（系统已装）" 'echo {"a":[1,2,3]} | jq -e ".a|length==3"' $c $s $([ $c = 0 ] && echo pass || echo fail) "第 0/2 站用于断言 brief.json"
# pyscenedetect
ffmpeg -v error -y -f lavfi -i testsrc=size=320x240:rate=25:d=2 -f lavfi -i color=c=red:s=320x240:r=25:d=2 -filter_complex "[0][1]concat=n=2:v=1[v]" -map "[v]" "$W/cut.mp4"
read c s < <(t "scenedetect -i $W/cut.mp4 -o $W detect-content list-scenes -q && test \$(tail -n +3 $W/cut-Scenes.csv | wc -l) -eq 2")
rec pyscenedetect "$(scenedetect version 2>/dev/null | head -1)" 'pip install scenedetect==0.7.2（SKILL.md 写的 [opencv] extra 在 0.7.2 已不存在，opencv 需另装）' "scenedetect -i cut.mp4 detect-content list-scenes（2 段合成片应检出 2 镜）" $c $s $([ $c = 0 ] && echo pass || echo fail) "SKILL.md 安装行需修正"
# argos-translate
read c s < <(t "python -c \"import argostranslate.translate as t; r=t.translate('云南米线很好吃','zh','en'); print(r); assert r\"")
rec argos-translate "$(python -c 'import importlib.metadata as m;print(m.version("argostranslate"))')" "pip install argostranslate==1.11.0 + 安装 zh↔en 模型包" "translate('云南米线很好吃','zh','en') → $(head -1 $W/log)" $c $s $([ $c = 0 ] && echo pass || echo fail) "可用但中英质量弱，必须人工校对"
# crawl4ai（独立 venv，避免依赖冲突）
C4=${C4A_PY:-/workspace/c4a/bin/python}
read c s < <(t "$C4 -c \"import asyncio,crawl4ai as c
async def m():
  async with c.AsyncWebCrawler() as w:
    r=await w.arun('https://revu.website/142620/'); print(r.markdown[:200]); assert 'Slurp' in (r.html or '')
asyncio.run(m())\"")
rec crawl4ai "$($C4 -c 'import importlib.metadata as m;print(m.version("crawl4ai"))' 2>/dev/null || echo not-installed)" "pip install -U crawl4ai && crawl4ai-setup（独立 venv）" "AsyncWebCrawler().arun(官网)" $c $s $([ $c = 0 ] && echo pass || echo "fail→降级 curl") "$(tail -c 300 $W/log | tr '\n' ' ')"
for n in librosa playwright yt-dlp; do rec $n "-" "-" "-" 0 0 "not-used" "本次链路未用到，未验证"; done
printf '%s\n' "${rows[@]}" | jq -s '{generated: (now|todate), tools: .}' > $OUT; cat $OUT | jq -c '.tools[]|{tool,version,status,seconds}'
