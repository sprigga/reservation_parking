# reservation_parking — 社區公共車位預約系統

本文件彙整系統需求與啟動手冊，供開發與部署參考。

## 1. 系統目標與功能

### 1.1 預約功能
- **表單欄位**：姓名、戶別、手機號碼、預約車位號碼、預約起迄時間
- **車位選擇**：下拉式選單顯示可用車位，由資料庫動態管理
- **時間衝突防護**：自動檢測並阻止重疊時間的預約申請
- **智能時間選擇**：
  - 30分鐘時間粒度（00:00、00:30、01:00...）
  - 預設開始時間為下一個30分鐘整點
  - 結束日期自動同步開始日期，防止跨天預約
  - 即時顯示已被預約的時間段（灰色禁用）
- **預約狀況展示**：實時顯示所有當前預約，按時間排序

### 1.2 管理者功能
- **安全登入**：JWT token 驗證的管理員系統
- **車位管理**：新增車位、編輯車位號碼、啟用/停用車位
- **預約管理**：查看所有預約、取消特定預約
- **系統維護**：自動清理過期預約（結束時間超過8小時）

## 2. 技術棧
- 前端：Vue 3 + Vite + Axios
- 後端：FastAPI + SQLAlchemy + SQLite
- 部署：Docker Compose

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
├── docker-compose.yml        # SQLite + FastAPI + Vite 一鍵啟動
├── .env.example              # compose 用的環境變數範例
├── DEPLOYMENT.md             # 完整部署指南（含生產環境 Nginx + SSL）
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

### 重疊判斷與智能檢測
**後端驗證**：
- 條件：`(new_start < existing_end) AND (new_end > existing_start)`
- 若時間衝突則回應 409 狀態碼並阻止建立

**前端智能防護**：
- 即時檢測時間段是否已被預約
- 自動禁用（灰色顯示）已預約的時間選項
- 合併重疊時間段，計算完整被預約的日期
- 當選擇車位或日期變動時，自動清除無效的時間選擇

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

產生安全的 SECRET_KEY：
```bash
# 產生 32 位元組的隨機密鑰
openssl rand -hex 32

# 或者直接寫入 .env 檔案
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

.env 重要變數：
- BACKEND_PORT、FRONTEND_PORT：後端/前端對外埠（預設 8000 / 5173）
- CORS_ORIGINS：前端來源（預設 http://localhost:5173）
- VITE_API_BASE：前端 API 基礎路徑（預設 http://localhost:8000）
- TZ：時區設定（預設 Asia/Taipei）
- SECRET_KEY：JWT 簽章密鑰（請務必更換為安全密鑰）
- ADMIN_USERNAME / ADMIN_PASSWORD：預設管理者帳密（啟動時建立）

2) 啟動服務
```bash
docker compose up -d --build
# 查看狀態
docker compose ps
# 查看日誌
docker compose logs -f
# 查看後端健康檢查
curl http://localhost:${BACKEND_PORT:-8000}/health
```
預設網址：
- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/health
- SQLite 資料庫：儲存在容器內 `/app/reservation_parking.db`

3) 首次資料庫初始化
- 後端啟動時會自動建立 SQLite 資料庫與資料表。
- 自動建立預設車位（A-01 ~ A-05）及管理者帳號。
- 過期預約會在啟動時自動清理。

## 5. 智能時間選擇系統

### 5.1 時間格式與粒度
- **24小時制**：採用 24 小時格式，避免 AM/PM 混淆
- **30分鐘粒度**：時間選項為 00:00、00:30、01:00、01:30 ... 23:30
- **自動預設**：開始時間自動設為下一個 30 分鐘整點
- **預設時長**：結束時間預設為開始時間 +30 分鐘

### 5.2 智能同步機制
- **日期同步**：變更開始日期時，結束日期自動同步為相同日期
- **衝突檢測**：即時檢查並禁用已被預約的時間段
- **視覺回饋**：已預約時間段以灰色禁用顯示
- **動態更新**：車位或日期變動時自動重新檢查時間可用性

### 5.3 前端驗證
- 確保結束時間晚於開始時間
- 防止選擇已被預約的時間段
- 當選擇的時間因其他預約而變為不可用時，自動清空選擇

## 6. 管理者系統

### 6.1 身份驗證
- **JWT Token 驗證**：採用業界標準的 JWT token 進行身份驗證
- **預設管理員**：系統啟動時自動建立（可透過環境變數設定）
  - 預設帳號：admin
  - 預設密碼：admin123（生產環境請務必修改）
- **自動登出**：Token 過期時自動清除並重導至登入頁面

### 6.2 管理功能
**車位管理**：
- 新增車位：輸入車位號碼並設定啟用狀態
- 編輯車位：修改車位號碼
- 狀態切換：啟用/停用車位（停用車位不顯示在預約選單）
- 批量操作：支援多個車位的狀態管理

**預約管理**：
- 查看所有預約：完整的預約列表與詳細資訊
- 取消預約：刪除特定預約記錄
- 過期清理：系統自動清理結束時間超過8小時的預約

### 6.3 權限保護
- 所有管理功能需要管理員權限 (`is_admin=True`)
- API 層級的權限檢查 (`Depends(require_admin)`)
- 前端自動在請求中附加 Authorization header

## 7. 常見問題與除錯指南（本專案實測）

### 7.1 後端問題
1) **後端啟動失敗**
- 現象：`NameError: name 'cleanup_expired_reservations' is not defined`
- 解法：確認 `backend/app/main.py` 中已正確匯入相關函數
- 檢查：`from .api import router, cleanup_expired_reservations`

2) **資料庫權限問題**
- 現象：SQLite 資料庫無法寫入
- 解法：確保容器內 `/app` 目錄有適當的寫入權限
- 檢查：`docker exec -it rp_backend ls -la /app/`

### 7.2 前端問題
1) **依賴版本衝突**
- 現象：npm 建置時 Vite 版本不相容錯誤
- 解法：檢查 `frontend/package.json` 確保版本匹配
- 建議：Vite ^6.0.0 配合 @vitejs/plugin-vue@^5.0.0

2) **時間選擇異常**
- 現象：時間選項無法正常顯示或選擇
- 解法：檢查瀏覽器時區設定，確認 API 返回的時間格式

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

5) 前端依賴安裝問題 (npm ci/npm install 錯誤)
- 現象：執行 `npm ci` 或 `npm install` 時報錯，例如 `EUSAGE` 或找不到 `package-lock.json`。
- 解法：
  - 確保在 `frontend/` 目錄下執行 `npm install` 以生成 `package-lock.json`。
  - 若仍有問題，嘗試先刪除 `frontend/node_modules` 和 `frontend/package-lock.json`，然後重新執行 `npm install`。
  - 確保 `npm` 版本與專案相容。

6) 前端畫面空白 / Vite 顯示 Syntax error "n"
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
- 連入 SQLite 資料庫檢查：
  ```bash
  # 進入後端容器
  docker exec -it rp_backend sqlite3 /app/reservation_parking.db
  
  # SQLite 指令
  .tables                    # 列出所有表
  .schema                    # 顯示表結構  
  SELECT * FROM parking_spots;    # 查看車位
  SELECT * FROM reservations;     # 查看預約記錄
  .quit                      # 退出
  ```

## 8. 開發指令速查
- **啟動**：`docker compose up -d --build`
- **查看日誌**：`docker compose logs -f backend frontend`
- **重啟單一服務**：`docker compose restart backend`（或 frontend）
- **停止**：`docker compose down`
- **清除資料重啟**：`docker compose down -v && docker compose up -d --build`
- **健康檢查**：`curl http://localhost:8000/health`
- **檢查資料庫**：`docker exec -it rp_backend sqlite3 /app/reservation_parking.db`

## 9. 非 Docker 啟動（可選）
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

## 10. 生產環境部署
詳細的生產環境部署指南（包含 Nginx 反向代理、SSL 憑證、安全設定等）請參考 [DEPLOYMENT.md](./DEPLOYMENT.md)。

---
若需新增使用者管理（建立/停用/重設密碼/設為管理者）等功能，請告知以便擴充程式。
