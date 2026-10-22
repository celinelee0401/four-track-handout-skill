# Export DOCX files to PDF with Microsoft Word on Windows (the authoritative renderer).
# Word is quit at the end only if it has no other documents open (never the user's own work).
# usage: powershell -ExecutionPolicy Bypass -File word_pdf.ps1 OUT_DIR file1.docx [file2.docx ...]
param([Parameter(Mandatory = $true)][string]$Out, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Files)
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
foreach ($f in $Files) {
  $src = (Resolve-Path $f).Path
  $pdf = Join-Path (Resolve-Path $Out).Path ([IO.Path]::GetFileNameWithoutExtension($src) + ".pdf")
  try {
    $doc = $word.Documents.Open($src, $false, $true)
    $doc.SaveAs2($pdf, 17)   # 17 = wdFormatPDF
    $doc.Close($false)
    Write-Output $pdf
  } catch {
    Write-Error "FAILED: $f"
  }
}
if ($word.Documents.Count -eq 0) { $word.Quit() }
else { Write-Warning "Word has other documents open; left Word running" }
