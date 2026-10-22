#!/bin/bash
# Link the four-track-handout skill in this repo into Claude Code (and Codex, if installed). macOS.
# Usage (from anywhere): bash install.sh
# Never moves, replaces or deletes an existing four-track-handout folder: if one is there, it stops.
set -euo pipefail
skill="$(cd "$(dirname "$0")" && pwd)/four-track-handout"
homes=("$HOME/.claude/skills")
[ -d "$HOME/.codex" ] && homes+=("$HOME/.codex/skills")
for home in "${homes[@]}"; do
  target="$home/four-track-handout"
  if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill" ]; then
    echo "已連結：$target"; continue
  fi
  if [ -e "$target" ] || [ -L "$target" ]; then
    echo "停止：$target 已經存在（可能是你自己的版本），安裝程式不會動它。" >&2
    echo "要改用這個 repo 的版本，請先自己把那個資料夾移走，再重新執行。" >&2
    exit 1
  fi
done
for home in "${homes[@]}"; do
  target="$home/four-track-handout"
  [ -L "$target" ] && continue
  mkdir -p "$home"
  ln -s "$skill" "$target"; echo "建立連結：$target → $skill"
done
if [ ! -f "$skill/teacher-profile.md" ]; then
  cp "$skill/teacher-profile.example.md" "$skill/teacher-profile.md"
  echo "已建立個人設定：$skill/teacher-profile.md（第一次做講義時 AI 會問你要填的欄位）"
fi
python3 -c "import docx, fitz" 2>/dev/null || echo "提醒：請執行 pip3 install python-docx pymupdf"
