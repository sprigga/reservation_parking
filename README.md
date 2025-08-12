# reservation_parking — 社區公共車位預約系統

本文件彙整系統需求，供開發時作為系統架構與實作依據。

## 1. 系統目標與功能
- 1.1 畫面欄位：姓名、戶別、手機、預約車位號碼、預約時間起迄。
- 1.2 預約車位號碼以下拉式選單呈現，車位號碼由資料庫管理。
- 1.3 若相同車位之預約時間有重疊，需跳出警告並禁止預約。
- 1.4 畫面需顯示目前已被預約之車位號碼的各時間點供參考。
- 1.5 需具備管理者模式，可取消已預約之車位號碼時間點。

## 2. 技術棧
- 前端：Vue
- 後端：FastAPI
- 資料庫：MySQL

## 3. Git 初始化
此專案需使用 Git 進行版本控管。可依下列步驟初始化：

```bash
# 於專案資料夾內初始化 Git
git init

# 設定主要分支（可選）
git checkout -b main

# 首次提交
git add .
git commit -m "chore: initialize reservation_parking project"

# 若需綁定遠端（以 GitHub 為例）
# git remote add origin <your-repo-url>
# git push -u origin main
```
