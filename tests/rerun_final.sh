#!/bin/sh
# Final re-render after the end-card + subtitle fixes (only s07's clip and the
# subtitle plates changed, so stations 0/1/2/3 mostly hit their caches).
set -e
cd /var/minis/workspace/craft-skills
export RUN_ID=dev
python3 -u pipeline/stations/s03_edit.py > /tmp/final_s03.log 2>&1
python3 -u pipeline/stations/s04_subs.py > /tmp/final_s04.log 2>&1
python3 -u pipeline/stations/s05_compose.py > /tmp/final_s05.log 2>&1
python3 -u pipeline/stations/s06_qa.py > /tmp/final_s06.log 2>&1
python3 -u pipeline/stations/s07_customer.py > /tmp/final_s07.log 2>&1
python3 pipeline/report.py dev > /tmp/final_report.log 2>&1
echo ALL_DONE > /tmp/final_done
