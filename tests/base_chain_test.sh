#!/usr/bin/env bash
# 底层工具串联测试：上一个工具的输出直接作为下一个工具的输入。
# 依赖：ffmpeg、demucs、openai-whisper、ocrmypdf(+tesseract-ocr)、pymupdf、espeak-ng（生成测试语音）
set -euo pipefail
W=$(mktemp -d); cd "$W"; echo "workdir: $W"

# 链 1：ffmpeg 抽音频 → demucs 分离人声 → whisper 出字幕 → ffmpeg 烧录
espeak-ng -s 140 -w speech.wav "Hello world. This is a short test of the subtitle pipeline."
ffmpeg -v error -y -f lavfi -i testsrc=size=640x360:rate=25 -i speech.wav -f lavfi -i sine=f=220:duration=6 \
  -filter_complex "[2]volume=0.3[b];[1][b]amix=inputs=2:duration=first[a]" -map 0:v -map "[a]" -shortest \
  -c:v libx264 -pix_fmt yuv420p -c:a aac src.mp4
ffmpeg -v error -y -i src.mp4 -vn -ac 2 -ar 44100 audio.wav
demucs --two-stems=vocals audio.wav -o sep/ >/dev/null 2>&1
test -s sep/htdemucs/audio/vocals.wav
whisper sep/htdemucs/audio/vocals.wav --model tiny --language en --output_format srt --output_dir subs/ >/dev/null 2>&1
test -s subs/vocals.srt && cat subs/vocals.srt
ffmpeg -v error -y -i src.mp4 -vf subtitles=subs/vocals.srt -c:a copy burned.mp4
ffmpeg -v error -i burned.mp4 -f null -
echo "CHAIN1 PASS: burned.mp4"

# 链 2：无文字层扫描 PDF → ocrmypdf → pymupdf 读文字
python3 - <<'P'
import pymupdf
d=pymupdf.open(); p=d.new_page(); p.insert_text((72,100),"Invoice 2026 total 4821 AUD",fontsize=20)
s=pymupdf.open(); q=s.new_page(); q.insert_image(q.rect,pixmap=p.get_pixmap(dpi=200)); s.save("scan.pdf")
assert pymupdf.open("scan.pdf")[0].get_text().strip()==""
P
ocrmypdf -l eng scan.pdf scan_ocr.pdf >/dev/null 2>&1
python3 -c "import pymupdf;t=pymupdf.open('scan_ocr.pdf')[0].get_text();print(repr(t));assert '4821' in t"
echo "CHAIN2 PASS"
