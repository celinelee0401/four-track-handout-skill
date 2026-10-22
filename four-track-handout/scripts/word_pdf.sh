#!/bin/zsh
# Export DOCX files to PDF with Microsoft Word (the authoritative renderer).
# Word is sandboxed, so files are copied into its container first.
# Word's AppleScript cannot close documents, so at the end Word is quit
# only if every open document is one this script opened (never the user's own work).
# usage: word_pdf.sh OUT_DIR file1.docx [file2.docx ...]
out="$1"; shift
mkdir -p "$out"
box=~/Library/Containers/com.microsoft.Word/Data/Documents/four-track-qa
mkdir -p "$box"
ours=()
for f in "$@"; do
  name=$(basename "$f" .docx)
  cp "$f" "$box/$name.docx"
  ours+=("$name.docx")
  osascript >/dev/null <<EOF
with timeout of 180 seconds
  tell application "Microsoft Word"
    set d to open file name "$box/$name.docx"
    save as d file name "$box/$name.pdf" file format format PDF
  end tell
end timeout
EOF
  if [[ -f "$box/$name.pdf" ]]; then
    mv "$box/$name.pdf" "$out/$name.pdf"
    echo "$out/$name.pdf"
  else
    echo "FAILED: $f" >&2
  fi
done

open_docs=$(osascript -e 'tell application "Microsoft Word" to get name of every document' 2>/dev/null)
foreign=0
for d in ${(s:, :)open_docs}; do
  if (( ! ${ours[(Ie)$d]} )); then foreign=1; fi
done
if (( foreign == 0 )); then
  osascript -e 'tell application "Microsoft Word" to quit saving no' >/dev/null 2>&1
else
  echo "note: Word has other documents open; QA copies left open in Word" >&2
fi
rm -f "$box"/*.docx
