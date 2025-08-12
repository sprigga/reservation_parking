# 正式部署指南（Nginx 反向代理 + HTTPS）

本指南說明如何在生產環境使用 Docker Compose、Nginx 反向代理與 Let's Encrypt（certbot）提供 HTTPS，並以 Nginx 提供前端靜態檔案與反向代理後端 API。

## 0. 前置準備
- 一個可公開訪問的主機（Linux）
- 一個網域名稱（假設為 `example.com`），DNS A 記錄已指向該主機
- 防火牆開放 80 與 443（以及若需 SSH：22）

## 1. 目標拓樸
- Nginx（:80, :443）
  - 靜態檔案（Vue build 後的 `dist`）直接由 Nginx 提供
  - 反向代理 `/api/` 至 FastAPI （內網連線，不對外開放）
- FastAPI（:8000 容器內）
  - 僅在 Docker network 內被 Nginx 訪問
  - 移除 --reload，改為生產模式（可考慮增加 workers）
- MySQL（內網，不對外開放）

## 2. 生產用環境變數
請根據實際情況設定 `reservation_parking/.env`（可由 `.env.example` 複製）：

```
# 只給容器內互連，不外露 DB 埠（不指定 DB_PORT 對外綁定）
DB_ROOT_PASSWORD=your-strong-password
MYSQL_DATABASE=reservation_parking

# 後端 API 內部埠（Nginx 透過內網連至 backend:8000）
BACKEND_PORT=8000

# 允許的前端來源請改為你的正式域名
CORS_ORIGINS=https://example.com

# JWT 與預設管理者
SECRET_KEY=please-change-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=please-change

# 時區
TZ=Asia/Taipei
```

## 3. 以 /api 作為前端的 API Base（同源）
生產時建議讓前端呼叫同一網域下的 `/api`，避免 CORS 問題。
- 在 `frontend/.env.production` 設定：
  ```
  VITE_API_BASE=/api
  ```
- 之後執行打包（下一節）。

## 4. 建置前端靜態檔
在主機上（或 CI/CD）執行：
```bash
cd reservation_parking/frontend
npm ci
npm run build
# 產物在 frontend/dist
```

## 5. Nginx 設定
範例檔位於 `reservation_parking/deploy/nginx/conf.d/reservation_parking.conf`（需將 `example.com` 改為你的域名）。
- HTTP（80）先提供 ACME 驗證與 HTTP -> HTTPS 轉址
- HTTPS（443）提供靜態網站與反向代理 /api

```
# /etc/nginx/conf.d/reservation_parking.conf

# 1) HTTP - 轉址到 HTTPS，並保留 ACME 驗證
server {
    listen 80;
    server_name example.com;

    location /.well-known/acme-challenge/ {
        root /usr/share/nginx/html; # Nginx 靜態根目錄
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# 2) HTTPS - 提供靜態與反向代理 API
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;

    # 靜態檔
    root /usr/share/nginx/html;
    index index.html;

    # 前端 SPA：路由交由前端處理
    location / {
        try_files $uri /index.html;
        add_header Cache-Control "public, max-age=3600";
    }

    # 反向代理 FastAPI
    location /api/ {
        proxy_pass http://rp_backend:8000/; # 注意尾端斜線
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 6. 生產版 docker-compose（範例）
檔案：`reservation_parking/deploy/docker-compose.prod.yml`

- 不對外暴露 MySQL 與 Backend 的埠（只讓 Nginx 連）
- Nginx 綁 80/443，掛載 `frontend/dist` 與證書路徑

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - TZ=${TZ:-Asia/Taipei}
    volumes:
      - db_data:/var/lib/mysql
      - ../database/schema.sql:/docker-entrypoint-initdb.d/01_schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h 127.0.0.1 -p$${MYSQL_ROOT_PASSWORD} || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=mysql+pymysql://root:${DB_ROOT_PASSWORD}@db:3306/${MYSQL_DATABASE}
      - CORS_ORIGINS=${CORS_ORIGINS}
      - SECRET_KEY=${SECRET_KEY}
      - ADMIN_USERNAME=${ADMIN_USERNAME}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - TZ=${TZ:-Asia/Taipei}
    depends_on:
      db:
        condition: service_healthy
    # 不對外開放，僅供 Nginx 內網連線

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      # 前端打包後的靜態檔案（請先完成第 4 節 build）
      - ../frontend/dist:/usr/share/nginx/html:ro
      # Nginx 站台設定
      - ./nginx/conf.d/reservation_parking.conf:/etc/nginx/conf.d/default.conf:ro
      # Let's Encrypt 證書與憑證
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend

volumes:
  db_data:
```

啟動：
```bash
cd reservation_parking/deploy
# 先打包前端（若尚未）
( cd ../frontend && npm ci && npm run build )
# 啟動
docker compose -f docker-compose.prod.yml up -d --build
```

## 7. 申請與安裝 Let's Encrypt 憑證
方式 A：使用 certbot standalone（暫時停用 Nginx 80 埠）
```bash
# 暫時停用 Nginx
docker compose -f reservation_parking/deploy/docker-compose.prod.yml stop nginx

# 以 standalone 在 80 取得憑證（請替換網域與 email）
sudo docker run --rm -it \
  -p 80:80 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  certbot/certbot certonly --standalone \
  -d example.com --email admin@example.com --agree-tos --no-eff-email

# 啟動 Nginx 並使用憑證
docker compose -f reservation_parking/deploy/docker-compose.prod.yml up -d nginx
```

方式 B：使用 webroot（不需停 Nginx，需先設定 80 站點的 `/.well-known/acme-challenge/` 路由）
```bash
sudo docker run --rm -it \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  certbot/certbot certonly --webroot \
  -w /usr/share/nginx/html -d example.com \
  --email admin@example.com --agree-tos --no-eff-email

# 重新載入 Nginx
docker exec $(docker ps -q -f name=nginx) nginx -s reload || true
```

憑證續期（建議以 cron 執行）：
```bash
sudo docker run --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  certbot/certbot renew --quiet --no-self-upgrade

# 續期後重載 Nginx
docker exec $(docker ps -q -f name=nginx) nginx -s reload || true
```

## 8. 其他建議
- 安全性：
  - 請務必更改 `SECRET_KEY`、`ADMIN_PASSWORD`。
  - 若無需對外提供 MySQL，請勿在生產 compose 暴露其埠。
- FastAPI：可視硬體資源調整 uvicorn workers，或改用 `gunicorn -k uvicorn.workers.UvicornWorker`。
- 監控/日誌：可搭配 nginx/access.log、error.log，與後端應用層日誌。
- 前端快取：若需更長快取策略，可針對 assets 設置更高 max-age 並使用指紋檔名（Vite 預設已指紋化）。

---
若你希望我將本指南對應的 `docker-compose.prod.yml` 與 nginx.conf 範例一起提交並套用你的域名，請提供 domain 與 email，我可以直接替你產出可用的設定檔並驗證部署。
