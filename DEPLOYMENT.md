# 部署指南

本指南說明如何部署社區停車位預約系統到生產環境。

## 系統架構

- **後端**: FastAPI + SQLAlchemy + SQLite
- **前端**: Vue 3 + Vite  
- **部署**: Docker Compose
- **反向代理**: Nginx (生產環境)
- **SSL**: Let's Encrypt

## 開發環境部署

### 1. 環境準備

確保系統已安裝：
- Docker & Docker Compose
- Git

### 2. 克隆專案

```bash
git clone <repository-url>
cd reservation_parking
```

### 3. 環境變數設定

複製環境變數範本：
```bash
cp .env.example .env
```

產生安全的 SECRET_KEY：
```bash
# 產生 32 位元組的隨機密鑰
openssl rand -hex 32

# 或者直接寫入 .env 檔案
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

編輯 `.env` 檔案：
```bash
# 後端與前端埠號
BACKEND_PORT=8000
FRONTEND_PORT=5173

# CORS 設定 (開發環境)
CORS_ORIGINS=http://localhost:5173

# 前端 API 基礎路徑
VITE_API_BASE=http://localhost:8000

# 時區
TZ=Asia/Taipei

# 後端認證設定 (建議產生安全的 SECRET_KEY)
SECRET_KEY=change-this-in-production  # 或使用: $(openssl rand -hex 32)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### 4. 啟動服務

```bash
# 建置並啟動所有服務
docker compose up -d --build

# 查看服務狀態
docker compose ps

# 查看日誌
docker compose logs -f
```

### 5. 驗證部署

```bash
# 後端健康檢查
curl http://localhost:8000/health

# 管理員登入測試
curl -X POST http://localhost:8000/auth/login \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=admin&password=admin123'
```

前端訪問：http://localhost:5173

## 生產環境部署

### 1. 生產環境變數

建立生產環境 `.env`：
```bash
# 生產埠號 (內部使用，透過 Nginx 反向代理)
BACKEND_PORT=8000
FRONTEND_PORT=5173

# CORS 設定 (改為你的域名)
CORS_ORIGINS=https://your-domain.com

# 前端 API 基礎路徑 (同域名下)
VITE_API_BASE=/api

# 時區
TZ=Asia/Taipei

# 重要：生產環境請更換這些密鑰

# 產生安全的 SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-strong-password
```

### 2. 前端建置

```bash
cd frontend

# 建立生產環境變數
echo "VITE_API_BASE=/api" > .env.production

# 安裝依賴並建置
npm ci
npm run build

# 建置產物位於 frontend/dist
```

### 3. 生產版 Docker Compose

建立 `docker-compose.prod.yml`：

```yaml
services:
  # 後端 API (內網連線，不對外開放)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: rp_backend_prod
    environment:
      - DATABASE_URL=sqlite:///./reservation_parking.db
      - CORS_ORIGINS=${CORS_ORIGINS}
      - SECRET_KEY=${SECRET_KEY}
      - ADMIN_USERNAME=${ADMIN_USERNAME}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - TZ=${TZ:-Asia/Taipei}
    volumes:
      - sqlite_data:/app/data
      - ./backend/reservation_parking.db:/app/reservation_parking.db
    restart: unless-stopped
    # 不對外開放埠號，僅供 Nginx 內網連線

  # Nginx 反向代理 + 靜態檔案伺服
  nginx:
    image: nginx:alpine
    container_name: rp_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      # 前端靜態檔案
      - ./frontend/dist:/usr/share/nginx/html:ro
      # Nginx 設定
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      # Let's Encrypt 憑證 (如需 HTTPS)
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  sqlite_data:
```

### 4. Nginx 設定

建立 `nginx.conf`：

```nginx
# HTTP 伺服器 (重新導向到 HTTPS 或僅用於開發)
server {
    listen 80;
    server_name your-domain.com;

    # Let's Encrypt ACME 挑戰
    location /.well-known/acme-challenge/ {
        root /usr/share/nginx/html;
    }

    # 重新導向到 HTTPS (生產環境)
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS 伺服器 (生產環境)
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 憑證 (使用 Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/your-domain.com/chain.pem;

    # SSL 設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 前端靜態檔案
    root /usr/share/nginx/html;
    index index.html;

    # Vue.js SPA 路由支援
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=3600";
    }

    # 反向代理到後端 API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (如果需要)
        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # 安全標頭
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

### 5. SSL 憑證申請 (Let's Encrypt)

```bash
# 方法 1: Standalone (需暫停 Nginx)
docker compose -f docker-compose.prod.yml stop nginx

sudo docker run --rm -it \
  -p 80:80 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  certbot/certbot certonly --standalone \
  -d your-domain.com \
  --email your-email@domain.com \
  --agree-tos --no-eff-email

docker compose -f docker-compose.prod.yml up -d nginx

# 方法 2: Webroot (不需停止服務)
sudo docker run --rm -it \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  -v $(pwd)/frontend/dist:/usr/share/nginx/html \
  certbot/certbot certonly --webroot \
  -w /usr/share/nginx/html \
  -d your-domain.com \
  --email your-email@domain.com \
  --agree-tos --no-eff-email
```

### 6. 憑證自動更新

建立 crontab 任務：
```bash
# 編輯 crontab
sudo crontab -e

# 新增以下行 (每日 2:30 檢查更新)
30 2 * * * docker run --rm -v /etc/letsencrypt:/etc/letsencrypt -v /var/lib/letsencrypt:/var/lib/letsencrypt certbot/certbot renew --quiet && docker exec rp_nginx nginx -s reload
```

### 7. 啟動生產環境

```bash
# 確保前端已建置
cd frontend && npm run build && cd ..

# 啟動生產服務
docker compose -f docker-compose.prod.yml up -d --build

# 查看狀態
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

## 資料庫管理

### 備份 SQLite 資料庫

```bash
# 備份資料庫
docker exec rp_backend_prod sqlite3 /app/reservation_parking.db ".backup /app/backup.db"

# 複製備份到主機
docker cp rp_backend_prod:/app/backup.db ./backup-$(date +%Y%m%d).db
```

### 查看資料庫內容

```bash
# 進入容器
docker exec -it rp_backend_prod sqlite3 /app/reservation_parking.db

# SQLite 指令
.tables                    # 列出所有表
.schema                    # 顯示表結構
SELECT * FROM parking_spots;    # 查看車位
SELECT * FROM reservations;     # 查看預約記錄
.quit                      # 退出
```

## 監控與維護

### 日誌查看

```bash
# 查看所有服務日誌
docker compose -f docker-compose.prod.yml logs -f

# 查看特定服務日誌
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f nginx
```

### 健康檢查

```bash
# 後端 API 健康檢查
curl https://your-domain.com/api/health

# 前端訪問檢查
curl -I https://your-domain.com
```

### 服務重啟

```bash
# 重啟特定服務
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml restart nginx

# 重啟所有服務
docker compose -f docker-compose.prod.yml restart
```

## 安全建議

1. **更換預設密碼**: 務必更改 `SECRET_KEY`、`ADMIN_PASSWORD`
2. **防火牆設定**: 僅開放必要埠號 (80, 443, SSH)
3. **定期更新**: 定期更新 Docker images 和依賴套件
4. **備份策略**: 定期備份 SQLite 資料庫和設定檔案
5. **監控日誌**: 定期檢查 access.log 和 error.log

## 故障排除

### 後端無法啟動
```bash
# 檢查後端日誌
docker compose logs backend

# 檢查資料庫檔案權限
docker exec -it rp_backend ls -la /app/

# 重建容器
docker compose down && docker compose up -d --build
```

### 前端無法訪問 API
```bash
# 檢查 Nginx 設定
docker exec rp_nginx nginx -t

# 重新載入 Nginx 設定
docker exec rp_nginx nginx -s reload

# 檢查網路連線
docker exec rp_nginx ping backend
```

### SSL 憑證問題
```bash
# 檢查憑證到期時間
sudo docker run --rm -v /etc/letsencrypt:/etc/letsencrypt certbot/certbot certificates

# 手動更新憑證
sudo docker run --rm -v /etc/letsencrypt:/etc/letsencrypt certbot/certbot renew --force-renewal
```