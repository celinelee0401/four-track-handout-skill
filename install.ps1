# Link the four-track-handout skill in this repo into Claude Code (and Codex, if installed). Windows.
# Usage: powershell -ExecutionPolicy Bypass -File install.ps1
# Uses a directory junction (no admin rights needed).
# Never moves, replaces or deletes an existing four-track-handout folder: if one is there, it stops.
$ErrorActionPreference = "Stop"
$skill = Join-Path $PSScriptRoot "four-track-handout"
$homes = @(Join-Path $HOME ".claude\skills")
if (Test-Path (Join-Path $HOME ".codex")) { $homes += Join-Path $HOME ".codex\skills" }
foreach ($h in $homes) {
  $target = Join-Path $h "four-track-handout"
  if (Test-Path $target) {
    $item = Get-Item $target -Force
    if ($item.LinkType -eq "Junction" -and $item.Target -contains $skill) { Write-Output "已連結：$target"; continue }
    Write-Error "停止：$target 已經存在（可能是你自己的版本），安裝程式不會動它。要改用這個 repo 的版本，請先自己把那個資料夾移走，再重新執行。"
    exit 1
  }
}
foreach ($h in $homes) {
  $target = Join-Path $h "four-track-handout"
  if (Test-Path $target) { continue }
  New-Item -ItemType Directory -Force -Path $h | Out-Null
  New-Item -ItemType Junction -Path $target -Target $skill | Out-Null
  Write-Output "建立連結：$target → $skill"
}
$profilePath = Join-Path $skill "teacher-profile.md"
if (-not (Test-Path $profilePath)) {
  Copy-Item (Join-Path $skill "teacher-profile.example.md") $profilePath
  Write-Output "已建立個人設定：$profilePath（第一次做講義時 AI 會問你要填的欄位）"
}
python -c "import docx, fitz" 2>$null
if ($LASTEXITCODE -ne 0) { Write-Output "提醒：請執行 python -m pip install python-docx pymupdf" }
