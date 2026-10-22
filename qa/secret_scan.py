#!/usr/bin/env python3
"""Secret scan — 交付物里不许出现真实密码 / 门锁码 / 电话 / API key。

用法: python3 qa/secret_scan.py runs/<run_id> [--json out.json]
退出码: 0 = 干净, 2 = 命中
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEXT_EXT = {".md", ".json", ".html", ".css", ".js", ".txt", ".srt", ".svg", ".xml", ".ics", ".example", ".sh", ".py", ".yml", ".yaml"}
SKIP_DIRS = {"_build", "assets", "node_modules", ".git", "raw"}
SKIP_FILES = {"reports/secret_scan.json"}          # 扫描器自己的输出，避免自指

PATTERNS = [
    ("api_key", re.compile(r"\b(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_\-]{30,}|xox[baprs]-[A-Za-z0-9\-]{10,})")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("au_mobile", re.compile(r"(?<![\d+])(?:\+?61[\s-]?4\d{2}[\s-]?\d{3}[\s-]?\d{3}|04\d{2}[\s-]?\d{3}[\s-]?\d{3})(?![\d])")),
    ("assigned_secret", re.compile(
        r"(?i)\b(?:wifi|wi-fi|password|passwd|passcode|door\s*code|keybox|key\s*box|lock\s*code|"
        r"密码|门锁码|门禁码|钥匙盒)\b\s*[:：=]\s*([^\s<>{}\"',;]{3,})")),
    ("code6", re.compile(r"(?i)\b(?:code|pin|密码)\D{0,12}(\d{4,8})\b")),
]


def scan_text(text: str, rel: str) -> list[dict]:
    hits = []
    for name, rx in PATTERNS:
        for m in rx.finditer(text):
            frag = m.group(0)
            if "{{" in frag or "}}" in frag:
                continue
            if name == "code6" and "{{" in text[max(0, m.start() - 40):m.start()]:
                continue
            if re.search(r"(?i)placeholder|example|dummy|xxxx|占位", frag):
                continue
            masked = frag[:4] + "*" * max(0, min(12, len(frag) - 4))
            hits.append({"file": rel, "rule": name, "match": masked,
                         "line": text[:m.start()].count("\n") + 1})
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--json", default="")
    args = ap.parse_args()
    root = Path(args.root)
    hits, scanned = [], 0
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXT:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if str(p.relative_to(root)).replace("\\", "/") in SKIP_FILES:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        scanned += 1
        rel = str(p.relative_to(root))
        found = scan_text(text, rel)
        if p.suffix.lower() in (".html", ".htm", ".md"):
            stripped = re.sub(r"<[^>]+>", " ", text)
            found += scan_text(stripped, rel)
        seen = set()
        for h in found:
            k = (h["file"], h["rule"], h["match"])
            if k not in seen:
                seen.add(k)
                hits.append(h)

    # 允许：任务书/报告里对规则的引用，用带引号的「示例」标注
    hits = [h for h in hits if not (h["rule"] == "assigned_secret" and h["match"].startswith(("密码：{{", "密码:{{")))]
    out = {"root": str(root), "files_scanned": scanned, "hits": hits, "clean": not hits}
    if args.json:
        Path(args.json).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2)[:3000])
    return 0 if not hits else 2


if __name__ == "__main__":
    sys.exit(main())
