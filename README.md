# 四軌講義 Skill（Claude Code／Codex）

讓 AI 助理依照 Celine Lee 的學思達四軌設計，產生翰林國中英語 **S1–S4 四軌講義**：Dialogue 或 Reading，每份五個 Task，同時輸出學生版、紅字答案的教用版和教師版（Word 檔）。另外也可以做 LoiLoNote 統整卡（PDF）。

| 軌 | 對象 | 講義特色 |
|---|---|---|
| S1 自主深化 | 月考 90+ | 開放、推理、全英文 |
| S2 結構引導 | 80–90 | 同題，加 organizer；事實自己寫，句框只給說理由 |
| S3 基礎鷹架 | 60–80 | 同題，Word Bank 含干擾字、選擇題後寫理由、回原文找證據 |
| S4 基礎重建 | 60 以下 | 單字重建（拍音節、KK、紅綠燈、救援站）＋3 個核心句 |

每個單元有一個核心問題（Big Question），Dialogue、Reading 和四軌共用。設計理念與規格都在 `four-track-handout/references/`。

## 安裝：把下面這段貼給你的 AI

打開 Claude Code（或 Codex），把這段話整段貼上：

> 請幫我安裝這個 skill：https://github.com/celinelee0401/four-track-handout-skill
> 先讀 repo 的 README.md，再照「給 AI 的安裝步驟」做，做完告訴我結果。

## 需要的環境

| | Mac | Windows |
|---|---|---|
| AI 助理 | Claude Code 或 Codex | Claude Code 或 Codex |
| Python 3 | 內建或自行安裝 | 從 python.org 安裝（勾選 Add to PATH） |
| Python 套件 | `pip3 install python-docx pymupdf` | `python -m pip install python-docx pymupdf` |
| Microsoft Word | 用來轉 PDF 做版面檢查 | 同左 |
| 做 LoiLo 卡片 | Google Chrome | Chrome 或內建的 Edge |
| 中文字型 | 內建即可 | 建議安裝免費的 [Noto Sans TC](https://fonts.google.com/noto/specimen/Noto+Sans+TC) |

另外需要你自己的翰林課本、教用課本、備課用書 PDF（這個 repo 不附）。

## 給 AI 的安裝步驟

（AI 助理請照順序執行；任何一步失敗就停下來，用中文告訴老師原因。）

**重要：如果 `~/.claude/skills/four-track-handout`（或 `~/.codex/skills/four-track-handout`）已經存在，而且不是指向這個 repo 的連結，就停止安裝並告訴老師。絕對不要移動、覆蓋或刪除那個資料夾。** 那可能是老師自己做的版本。安裝程式遇到這種情況也會自動停止。

### Mac
1. 下載 repo：
   ```bash
   mkdir -p ~/Projects && git clone https://github.com/celinelee0401/four-track-handout-skill.git ~/Projects/four-track-handout-skill
   ```
   資料夾已經存在的話，改成在該資料夾執行 `git pull`。
2. 執行安裝程式：`bash ~/Projects/four-track-handout-skill/install.sh`
3. 安裝 Python 套件：`pip3 install python-docx pymupdf`
4. 檢查有沒有 Microsoft Word（`/Applications/Microsoft Word.app`）和 Google Chrome，缺的話告訴老師。

### Windows（PowerShell）
1. 下載 repo：
   ```powershell
   git clone https://github.com/celinelee0401/four-track-handout-skill.git "$HOME\Projects\four-track-handout-skill"
   ```
   沒有 git 的話，從 GitHub 頁面按 Code → Download ZIP，解壓縮到 `%USERPROFILE%\Projects\four-track-handout-skill`。
2. 執行安裝程式：`powershell -ExecutionPolicy Bypass -File "$HOME\Projects\four-track-handout-skill\install.ps1"`
3. 安裝 Python 套件：`python -m pip install python-docx pymupdf`
4. 檢查有沒有 Microsoft Word 和中文字型 Noto Sans TC，缺的話告訴老師。

### 最後（兩種系統都一樣）
告訴老師：安裝完成，要重新開一個對話，skill 才會載入。第一次說「幫我做 U5 Dialogue 的四軌講義」時，AI 會先問姓名、課本 PDF 位置、Task 5 頁碼等設定。

## 更新

在 repo 資料夾執行 `git pull`（用 ZIP 安裝的話，重新下載 ZIP 蓋過去，但保留 `teacher-profile.md` 和 `assets/class_qr.png`）。老師的個人設定和班級 QR 不會被蓋掉，也不會被上傳。

## 資料夾內容

```
four-track-handout/
  SKILL.md                    AI 的工作流程
  teacher-profile.example.md  個人設定範本
  references/                 理念、Dialogue／Reading 規格、答案與教師版規則、檢核表
  scripts/                    排版（Markdown → Word）、Word 轉 PDF（Mac／Windows）、PDF 抽字與轉圖、LoiLo 卡片
  assets/golden_template.docx Word 版型（頁首、頁尾、字型）
  examples/                   B3 U3、U4 的完整範例（Unit Brief＋S1–S4 來源檔＋LoiLo 卡片）
```

## 更新紀錄

- **2026-11-01**：每單元加一個核心問題（Big Question），Dialogue、Reading、S1–S4 共用，從 Task 1 貫穿到 Task 5（I used to think … Now I think …）。S2、S3 減少鷹架：思考層次和 S1 一樣要到連結、比較、判斷；S2 事實題自己寫，S3 不再只圈只勾。U4 範例全部換成新程度。另修正換頁（Step 不再整串被拉到下一頁、Word 避頭尾點）、LoiLo 卡片可用 `compact: true` 縮小字級。
- **2026-10-22**：第一版分享。

## 注意

- 講義以 Mac 開發與測試；Windows 版的指令已經寫好，但還沒有在 Windows 電腦實測過。遇到問題歡迎回報。
- AI 產出的講義一律標 `PILOT`，請老師自己檢查過再印。

## 授權

本 repo 以 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh-hant) 授權（全文見 `LICENSE`）：歡迎使用、修改和分享，但請註明原作者 Celine Lee，且不得用於商業用途。範例中引用的課文，版權屬原出版社所有。

## 作者與感謝

四軌講義設計：Celine Lee
感謝利真老師的四軌講義，詳見 Shareclass 網站：https://www.shareclass.org/profile/dacbeb5aceaa4f889d2faf4510c4a544/
