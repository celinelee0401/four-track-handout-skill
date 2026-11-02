---
name: four-track-handout
description: Generate 學思達 S1–S4 四軌講義 (Grade 8 翰林 English, Dialogue or Reading, five Tasks) with a red-answer 教用版 and Teacher Guide as Word files, following Celine Lee's four-track design. Use when the user asks for 四軌講義, S1–S4 handouts, 分軌講義, a unit's Dialogue/Reading handout, or to revise/compare/QA an existing four-track handout.
---

# 四軌講義生成（Claude 版）

Design by Celine Lee（學思達四軌：S1 自主深化／S2 結構引導／S3 基礎鷹架／S4 基礎重建）。

Claude writes every word of the handouts; the script only lays them out. Quality comes from a source-grounded **Unit Brief**, track-by-track writing against the specs, and an honest QA pass. Never batch-fill units from a template.

## Read first (every time)

1. `teacher-profile.md` — 這位老師的姓名、頁首課程代號、QR、Task 5 頁碼、課本檔案位置。不存在就先從 `teacher-profile.example.md` 複製一份。**仍有 `<請填>` 的欄位，先在 Preflight 問老師、填好再開始。**
2. `references/philosophy.md` — 核心理念、四軌輪廓、禁止事項。
3. `references/dialogue-spec.md` **or** `references/reading-spec.md`（+ `reading-strategy-map.yaml`）。
4. `references/answer-key-teacher-guide.md`、`references/source-format.md`、`references/quality-checklist.md`。
5. The closest finished example in `examples/` (same part type). Match its depth and tone; do not copy its content.

## Workflow

### 0. Preflight（問清楚再開始，只問缺的）
- 單元、Dialogue／Reading、要哪幾軌（預設 S1–S4 全做）。
- QR：Task 4、Task 5 用 `teacher-profile.md` 指定的做法。若 `assets/class_qr.png` 存在，`qr:` 區塊會自動嵌入；不存在就留「QR code（請貼上）」框，交付時提醒老師貼。
- Task 5 手寫筆記頁碼：查 `teacher-profile.md` 的頁碼表；表上沒有就問老師。
- 輸出位置與檔名：依 `teacher-profile.md`；若檔案已存在，不可覆蓋老師已編修的版本：先把舊版（docx、教用、PDF預覽、src）整組移到同資料夾的 `_v1/` 子資料夾、檔名加後綴，新版沿用原檔名。檔名、`locator`、頁首頁尾一律不寫 v2 等版本號（學生看得到，資料夾也會亂）。

### 1. Gather sources
- 學用課本、教用課本、備課用書 PDF：位置見 `teacher-profile.md`；找不到就請老師給路徑。
- 抽文字：`python3 scripts/pdf_text.py FILE.pdf FIRST LAST`（先複製到暫存資料夾；雲端檔可能要先下載）。macOS 也可用 `swift scripts/pdf_text.swift`。
- KK 字型常抽不出文字：把課本後附 Word Bank 該單元那幾頁轉成 PNG（`python3 scripts/pdf_to_png.py FILE.pdf OUT 1.6`）直接看圖讀。
- Windows：指令裡的 `python3` 改成 `python`。

### 2. Write the Unit Brief（`<輸出資料夾>/unit-brief_U#_<D|R>.md`）
Must contain, all verified against the textbook:
- 課文全文（逐字）、頁碼、人物、時間地點、事件順序。
- 本課文法焦點（課本 Grammar Focus）：只給老師參考，講義不出文法題（philosophy.md §4b）。
- **Answer Bank**：T1–T3 每一個固定答案的正確事實（四軌都從這裡取答案）。
- 3 個原文核心句（能代表本課內容與核心問題）。
- **核心問題（Big Question）**：一題，Dialogue／Reading、四軌共用（philosophy.md §4a）；同單元另一個 Part 已有就沿用。寫出它怎麼貫穿 T1–T5。
- T3 主題問題與框架（SEL／SDGs／TBLT／思考常規）及理由；4/3/2 說話題目。
- S4 18 字表（Core 10、Support 8）：Claps、Sound chunks、KK、中文；KK 以課本／備課用書 Word Bank 為準，查不到的標 ⚠ 讓老師確認。
- Reading：策略名稱與說明比喻、策略圖正確答案、Part A 問題梯、Part B CAP 短文（S1/S2 版、S3 簡化版、S4 迷你版）與出處說明。

Show the teacher a short summary of the Brief (key facts, Big Question, T3 question, Part B text) before writing the tracks when the unit is new to this conversation; proceed directly if they asked for no check-ins.

### 3. Write the tracks, in order S1 → S2 → S3 → S4
One source file per track (`<輸出資料夾>/src/<filename>.md`, syntax in `source-format.md`). Put `teacher:` and `course:` from `teacher-profile.md` in every front matter.
- **S1** first: the full-challenge version of each Task's core question.
- **S2 / S3**: keep the same Task function, core question and facts; change only the scaffold per the spec table. The thinking level is the same as S1 (connect, compare, judge). Follow the scaffold-reduction rules in philosophy.md §4a: S2 writes facts without frames; S3 uses Word Banks with extra words, evidence copying and MC + reason, never tick-only or copy-match items.
- **S4**: the word-rebuilding package plus the shared 3 core sentences (and for Reading, the mini Part B).
- Each file includes its own `=== TEACHER GUIDE ===` section, specific to that track and this unit.
- **Instructions are the most important text.** Write them as numbered five-ring steps (👤 自學 → 🧠 思考 → 👥 討論 → 📢 表達 → 📋 統整) in CEFR A1 English (philosophy.md §5). Use the icons in their 學思達 meaning (philosophy.md §3a): partner/table talk = 👥; 📢 only for whole-class sharing; 📋 only for the teacher's 統整 and it is a stop point (§3b: at most one per Task end, mid-Task only where a new reading strategy needs aligning, always say what is summarized); photo/upload steps get no icon. **Place each step (`step:` line) directly above the item it refers to — never one list at the top of the Task** (philosophy.md §5.1a); name the item ("Fill in the timeline in A"); put 👥/📢/📋 wrap-up steps after the last item. Listening always uses the audio track or QR, never the teacher reading the text.
- Every fixed answer is marked inline (`[[ ]]`, `{{ * }}`, `[[x]]`) so the 教用版 shows red answers on the blanks.
- Under every item heading add a `bloom:` line (教用版-only grey tag); the Teacher Guide gives each Task (T1–T5, S4 too) a `Bloom：…｜會考能力：…` line and a 統整腳本 for each 📋 (answer-key-teacher-guide.md). S3's Teacher Guide ends with the S3 觀察紀錄 table.
- **No grammar tasks** in any track unless Celine names that unit's grammar (philosophy.md §4b). No "done early" box.

### 4. Align and QA
- Build a side-by-side table (T1–T3 core question + key answers × S1–S4) and fix any drift.
- Go through `quality-checklist.md` A–E for every track. Fix, don't just report.

### 5. Render and inspect
macOS:
```bash
K=~/.claude/skills/four-track-handout/scripts
python3 $K/render_handout.py SRC.md --out-dir OUT
zsh $K/word_pdf.sh SCRATCH/pdf OUT/FILE.docx OUT/教用/FILE_教用.docx   # Microsoft Word export
python3 $K/pdf_to_png.py SCRATCH/pdf/FILE.pdf SCRATCH/png 1.0
```
Windows (PowerShell):
```powershell
$K = "$HOME\.claude\skills\four-track-handout\scripts"
python $K\render_handout.py SRC.md --out-dir OUT
powershell -ExecutionPolicy Bypass -File $K\word_pdf.ps1 SCRATCH\pdf OUT\FILE.docx OUT\教用\FILE_教用.docx
python $K\pdf_to_png.py SCRATCH\pdf\FILE.pdf SCRATCH\png 1.0
```
Read the PNGs: check checklist F (header/footer, tables, emoji, Chinese glyphs, no red in the student file, writing space). Use Word for QA: LibreOffice (`--pdf`) drops the emoji and is only a fallback. Word may ask to update fields when opening (choose Yes).

### 6. (Optional) LoiLoNote 統整卡
After the handouts, ask whether to make LoiLo cards (or do it when asked on its own). Follow `references/loilo-cards.md`: one shared S1–S4 set per Part, 16:9 PDF, paired blank → answer pages, rendered by `scripts/render_cards.py`.

### 6b. (On request) 文法 LoiLo 卡
Only when the teacher asks ("做 U# 文法卡"). One set per unit, ordered by the 文法解析 pages in `teacher-profile.md` (ask if missing), examples from the unit's own Dialogue/Reading — see `references/loilo-cards.md` §文法卡.

### 7. Deliver
Report: the files written (student + 教用 per track), the Unit Brief, the alignment table, QA results, anything left for the teacher (⚠ KK, QR to paste, Part B source note). Label the set `PILOT` until the teacher approves it; never call it final on their behalf.

## Design defaults（Celine Lee 的設計決定，2026-10）
`teacher-profile.md`「我的偏好」寫的優先於以下預設。
- Task 4 = 掃 QR 錄音；Task 5 = 掃 QR 看解說影片、手寫筆記、拍照上傳。兩者分開，不改成紙本卡。Task 5 的 📋 放在看影片那一步（影片＝老師統整），上傳那一步不放圖示（2026-11-02）。
- 教用版 = 同一份講義＋紅字答案寫在空格上＋教師版。
- Reading 不用 first topic／final topic／keep-change。
- Reading T2 = Part A 課文問題梯 ＋ Part B CAP 改寫短文（S1/S2 完整、S3 簡化、S4 迷你）。
- T3 依課文主題自然連到 SEL／SDGs／生活議題。
- Instruction = 五環編號步驟＋CEFR A1；聽力只用音檔／QR，絕不請老師朗讀課文。
- 步驟緊接題目：`step:` 一步一行放在該題正上方，不顯示「Instruction:」標籤。
- S4 KK 音標助念員只放教用版：用 `[teacher] … [/teacher]` 包住（學生版不出現）。
- 文法不進講義、圖示照五環原意、📋 是停點、教用版逐題標 Bloom、S3 觀察紀錄、不放提早完成框（2026-11-02，U4 起；來自利真老師回饋）。範例：`examples/B3-U4-*`。
- 核心問題＋鷹架減量（2026-11-01，U4 起）：每單元一題 Big Question 貫穿四軌與 D/R；S2、S3 拿掉只填單字、只圈只勾的鷹架，思考層次和 S1 一樣到連結／判斷（philosophy.md §4a）。範例：`examples/B3-U4-dialogue`、`examples/B3-U4-reading`。
