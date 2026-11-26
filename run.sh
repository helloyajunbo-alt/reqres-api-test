#!/usr/bin/env bash
# 一键：装依赖 -> 跑冒烟 -> 打开报告
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
pytest "$@"
echo "report: $(pwd)/reports/report.html"
