# 老師個人設定（每位老師各自填寫）

這是範本。`install.sh` 會把它複製成 `teacher-profile.md`（你自己的設定，不會上傳到 GitHub，`git pull` 也不會蓋掉）。
Claude 每次做講義前會先讀 `teacher-profile.md`；看到 `<請填>` 時，會先問你，再幫你填好。

## 基本資料
- 姓名（印在每頁頁尾左側）：<請填，例：Ms. Wang>
- 頁首課程代號（front matter 的 `course:`）：<請填，例：115-1 G8>
- 冊別：<請填，例：翰林 B3>

## QR（Task 4 錄音、Task 5 解說影片）
- 做法：<請填：A. 全部 Task 4/5 用同一個班級 QR／B. 每份講義各自貼 QR>
- 若選 A：把班級 QR 圖片存成 `assets/class_qr.png`（PNG，正方形），渲染時會自動嵌入。
- 若選 B：不要放 `class_qr.png`，講義會留「QR code（請貼上）」框。

## Task 5 手寫筆記頁碼（依你們學生講義合訂本的目錄）
| Unit | Dialogue Wrap-up | Reading Wrap-up |
|---|---|---|
| U1 | <請填> | <請填> |
| U2 | <請填> | <請填> |
| U3 | <請填> | <請填> |
| U4 | <請填> | <請填> |
| U5 | <請填> | <請填> |
| U6 | <請填> | <請填> |

沒有合訂本的話寫「不用頁碼」，Task 5 會改寫成「寫在本講義背面」。

## 檔案位置（填資料夾完整路徑）
- 學用課本 PDF：<請填>
- 教用課本 PDF：<請填>
- 備課用書 PDF：<請填>
- 課本後附 Word Bank（KK 音標用）：<請填，可留空>
- 講義輸出資料夾：<請填，例：~/Documents/四軌講義/U#/Dialogue/>
- 檔名格式：<請填，例：115-1_G8_B3_U#_Dialogue_S#>

## 我的偏好（選填，會優先於 SKILL.md 的預設）
- （例：S4 也要英文指令；Task 3 秒數改 40/30/20）
