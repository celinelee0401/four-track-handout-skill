# 講義來源檔格式（render_handout.py）

```markdown
---
title: "Unit 3: Mom Was Doing the Dishes at Half Past Twelve"
locator: U3 D S1                 # 頁首、頁尾右側
course: 115-1 G8                 # 頁首前綴（取自 teacher-profile.md）
teacher: Ms. Wang                # 頁尾左側老師姓名（取自 teacher-profile.md）
filename: 115-1_G8_B3_U3_Dialogue_S1
---

# Part 1: Dialogue - A Broken Cup Mystery        ← Part 標題（14 pt 粗體）
Goal: I can ...                                    ← 一般段落；可用 **粗體**

## Task 1: See-Think-Wonder (觀察・推論・提問)       ← 灰底 Task bar
flow: 👤🧠 自學思考 → 👥 討論 → 📋 統整
step: 👤 Look at the pictures on pp. 49-50.         ← 一步一行，放在該題「正上方」；自動編號 Step 1、2…（每個 Task 重新起算）
step: 🧠 Write your ideas in the table below.        ← 深灰「Step N」小標＋A1 句子；不再用 instruction: 清單
（S4 在 front matter 加 `step_label: 第 {n} 步`，編號顯示為「第 1 步」）
（舊語法 instruction: / 任務說明： / 操作指令： 仍可渲染，但 U4 起不要再用）

### ■ 1. Who was doing what?                         ← 粗體小標
Kim broke her [[favorite]] cup.                     ← [[答案]]：學生版空格，教用版紅字
At 12:30, Mom was [[doing the dishes|20]].          ← |20 指定空格長度
Kim {{was* / were}} sleepwalking.                   ← 圈選題：學生看到 ( was / were )，教用版正確項紅字
[[x]] Mom   □ Jamie                                 ← 勾選題：[[x]] 學生版 □，教用版紅色 ☑

widths: 18 41 41                                    ← 下一個表格的欄寬比例
blue: Speaking Help                                 ← 下一個表格加淡藍標題列
small-table                                          ← 下一個表格用 10.5 pt
| Step | Question | My Notes |
|---|---|---|
| See | ... | 1. ____<br>2. ____ |                    ← <br> 為格內換行

lines: 3                                            ← 3 條寫線
lines: 2 | It was cold. | 有天氣形容詞即可           ← 開放題：教用版顯示紅字範例＋條件
key: 答案：1. A  2. C  3. B                         ← 只出現在教用版的紅字註記
bloom: 1 理解｜2 推論｜3 評鑑                         ← 只出現在教用版的灰色小字「🎯 Bloom：…」，放在 ### 小標下一行
step: Take a photo of your notes. Upload it.        ← 不放圖示的步驟（純操作）
qr: U3 Dialogue recording — full Dialogue + 30-second extension
[box]                                               ← 外框文字框（策略說明、範例）
📖 What is a timeline?
...
[/box]
[teacher]                                           ← 教用版限定區塊：教用版原位顯示（紅字「🍎 教用版補充」標籤），學生版不出現
### ■ 🗣 KK 音標助念員                               ← 例：S4 KK 助念員（Celine 2026-10 決定只放教用版）
| 符號 | 唸法提示 | 本課單字 |
|---|---|---|
[/teacher]
---pagebreak---

=== TEACHER GUIDE ===                               ← 之後只出現在教用版
## Task 1: See-Think-Wonder
...
```

注意：
- `[box]` 框可以跨頁（設成不跨頁會在 Part B 短文等長框前留下大空白，2026-11-01 試過）；框被切在半句時，把框尾的範例句移到框外，不要整框禁止跨頁。
- 表格第一列一定是表頭（灰底、粗體、跨頁重複）。
- 換頁規則（render_handout.py 自動處理，2026-10-31）：Step 只黏住「緊接在它下面的題目或表格」；連續好幾個 Step 時彼此不黏，避免整串連同表格搬到下一頁、留下半頁空白。下一行是 `##`／`#` 標題時也不黏。
- 文件預設東亞語言設為 zh-TW，Word 才會套用避頭尾點（「，」「。」不會出現在行首）。
- 框（`[box]`）、標題裡的中英對照：英文標籤要短（例如 `❓ **Big Question:**`），讓英文句子放得進一行，中文另起一行；不要讓英文只剩一兩個字被擠到第二行。Task 標題控制在一行內（約 60 個半形字元）。
- 需要空白讓學生寫的格子，直接寫 `____________`。
- 不要把 S1–S4 的內容寫在同一個檔案；每軌一檔。
