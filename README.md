# reservation_parking — 社區公共車位預約系統

本文件彙整系統需求與啟動手冊，供開發與部署參考。

## 1. 系統目標與功能
- 1.1 畫面欄位：姓名、戶別、手機、預約車位號碼、預約時間起迄。
- 1.2 預約車位號碼以下拉式選單呈現，車位號碼由資料庫管理。
- 1.3 若相同車位之預約時間有重疊，需跳出警告並禁止預約。
- 1.4 畫面需顯示目前已被預約之車位號碼的各時間點供參考。
- 1.5 需具備管理者模式，可取消已預約之車位號碼時間點，並進行車位管理（新增/編輯/啟用或停用）。

## 2. 技術棧
- 前端：Vue (Vite)
- 後端：FastAPI (SQLAlchemy)
- 資料庫：MySQL

### 專案目錄結構
```
reservation_parking/
├── backend/
│   ├── app/
│   │   ├── api.py            # API 路由：車位/預約 CRUD、重疊檢查、登入/權限
│   │   ├── auth.py           # JWT/OAuth2、bcrypt 密碼雜湊、管理者權限保護
│   │   ├── database.py       # 連線與 Session 管理
│   │   ├── main.py           # FastAPI 入口、建表、預設管理者建立、CORS
│   │   ├── models.py         # SQLAlchemy 模型 (User, ParkingSpot, Reservation)
│   │   └── schemas.py        # Pydantic Schemas
│   ├── .env.example
│   └── requirements.txt
├── database/
│   └── schema.sql            # MySQL 建表與初始資料（含 A-01 ~ A-05、users 表）
├── docker-compose.yml        # MySQL + FastAPI + Vite 一鍵啟動
├── .env.example              # compose 用的環境變數範例
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── api.js            # Axios + 自動帶上 Authorization
        ├── auth.js           # 簡易 token 儲存/檢查
        ├── App.vue
        ├── main.js
        └── pages/
            ├── Admin.vue     # 管理者登入、車位管理、預約刪除
            └── ReservationForm.vue  # 一般使用者預約表單
```

### 重疊判斷（應用層）
預約時間不可重疊，於建立預約時執行：
- 條件：(new_start < existing_end) AND (new_end > existing_start)
- 若符合則回應 409 並禁止建立。

## 3. Git 初始化（僅供參考）
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

## 4. 使用 Docker Compose 本地啟動
前置需求：已安裝 Docker 與 Docker Compose（v2+）。

步驟：
1) 於專案根目錄建立 .env（可由範例複製並視需要調整）
```bash
cd reservation_parking
cp .env.example .env
```
.env 重要變數：
- DB_ROOT_PASSWORD：MySQL root 密碼（預設 password）
- MYSQL_DATABASE：資料庫名稱（預設 reservation_parking）
- DB_PORT：對外映射的 MySQL 埠（預設 3306；若本機已占用，改成 3307）
- BACKEND_PORT、FRONTEND_PORT：後端/前端對外埠（預設 8000 / 5173）
- CORS_ORIGINS：前端來源（預設 http://localhost:5173）
- SECRET_KEY：JWT 簽章密鑰（請務必在正式環境修改）
- ADMIN_USERNAME / ADMIN_PASSWORD：預設管理者帳密（啟動時建立）

2) 啟動服務
```bash
docker compose up -d --build
# 查看狀態
docker compose ps
# 查看後端健康檢查
curl http://localhost:${BACKEND_PORT:-8000}/health
```
預設網址：
- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/health
- MySQL: 127.0.0.1:${DB_PORT}（root / $DB_ROOT_PASSWORD）

3) 首次資料庫初始化
- docker-compose 會自動匯入 `database/schema.sql` 建立資料表與預設車位（A-01 ~ A-05）。
- 後端啟動時若找不到 `ADMIN_USERNAME` 對應帳號，會自動建立管理者。

## 5. 管理者登入與權限
- 前端管理者區塊（Admin.vue）預設顯示登入表單。
- 預設帳密：
  - 帳號：admin
  - 密碼：admin123
- 登入成功後可進行：
  - 車位管理：新增/編輯/啟用或停用。
  - 預約管理：刪除既有預約。
- 受保護 API（如新增/修改車位、刪除預約）僅管理者可操作。

## 6. 常見問題與除錯指南（本專案實測）
1) MySQL 埠衝突
- 現象：本機已有 MySQL 佔用 3306 導致 compose 無法綁定。
- 解法：修改 `.env` 的 `DB_PORT`（例如改為 3307），重新 `docker compose up -d`。

2) Compose 警告：version 欄位已過時
- 現象：`the attribute version is obsolete`。
- 解法：安全可忽略，或移除 `docker-compose.yml` 的 `version` 欄位。

3) 後端啟動時出現 bcrypt/passlib 警告
- 現象：`module 'bcrypt' has no attribute '__about__'`（非致命）。
- 解法（可選）：在 `backend/requirements.txt` 釘選相容版本，例如：
  - `bcrypt==4.1.2`
  - `passlib==1.7.4`
  調整後 `docker compose up -d --build` 重建。僅為消音，功能不受影響。

4) 後端語法錯誤（SyntaxError: unexpected character after line continuation character）
- 現象：檔案內混入非預期字元（例如 `\n` 字面），導致 Python 載入失敗。
- 解法：重新建立檔案（`auth.py` 等），確保檔案內容未帶入跳脫字元。重啟後端：
  ```bash
  docker compose restart backend
  docker compose logs backend -f
  ```

5) 前端畫面空白 / Vite 顯示 Syntax error "n"
- 現象：Vite 日誌顯示 `Failed to scan... Syntax error "n"`，通常是檔案含有字面 `\n` 或非 UTF-8 字元（本案為 `src/auth.js`）。
- 解法：
  - 重新建立該檔案（例如 `frontend/src/auth.js`），確保無特殊字元。
  - 重啟前端：`docker compose restart frontend`。
  - 重新整理瀏覽器（建議 Shift+Reload）。
  - 進一步調試：
    ```bash
    docker compose logs -f frontend
    curl http://localhost:5173/src/auth.js
    ```

6) 401 自動登出
- 現象：token 過期或無效時，Axios 會在 401 自動清除 token 並重載頁面。
- 建議：若遇到反覆 401，請重新登入。可在瀏覽器 DevTools 的 Application -> Local Storage 檢查/清除 `rp_token`。

7) 驗證 API 與 DB
- 健康檢查：`curl http://localhost:8000/health`
- 公開車位列表：`curl http://localhost:8000/spots`
- 以表單登入（取得 token）：
  ```bash
  curl -X POST http://localhost:8000/auth/login \
       -H 'Content-Type: application/x-www-form-urlencoded' \
       -d 'username=admin&password=admin123'
  ```
- 連入 MySQL 容器檢查：
  ```bash
  docker exec -it rp_mysql mysql -uroot -p${DB_ROOT_PASSWORD} -e "USE ${MYSQL_DATABASE}; SHOW TABLES; SELECT * FROM parking_spots;"
  ```

## 7. 開發指令速查
- 啟動：`docker compose up -d --build`
- 查看日誌：`docker compose logs -f backend frontend db`
- 重啟單一服務：`docker compose restart backend`（或 frontend/db）
- 停止：`docker compose down`
- 連同資料卷清除：`docker compose down -v`（會刪除資料庫資料）

## 8. 非 Docker 啟動（可選）
- 後端：
  ```bash
  cd backend
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env  # 設定 DATABASE_URL, CORS_ORIGINS, SECRET_KEY, ADMIN_*
  uvicorn app.main:app --reload --port 8000
  ```
- 前端：
  ```bash
  cd frontend
  npm install
  echo "VITE_API_BASE=http://localhost:8000" > .env.local
  npm run dev
  ```

---
若需新增使用者管理（建立/停用/重設密碼/設為管理者）、Nginx 反代或正式部署指引，請告知我以便擴充文件與程式。
