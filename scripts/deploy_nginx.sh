#!/bin/bash
# Setup nginx + Let's Encrypt for olymp.oshsu.kg.
# NOTE: SSL only if DNS publicly resolves. Internal-only — skip certbot.
set -e

PROJ=/var/www/olymp.oshsu.kg

sudo tee /etc/nginx/sites-available/olymp.oshsu.kg > /dev/null << 'NGINX'
limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name olymp.oshsu.kg www.olymp.oshsu.kg _;

    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;

    client_max_body_size 5M;
    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;

    location /static/ {
        alias /var/www/olymp.oshsu.kg/static/;
        expires 30d;
        access_log off;
    }

    location /media/ {
        alias /var/www/olymp.oshsu.kg/media/;
        expires 7d;
        access_log off;
    }

    location /event/ {
        proxy_pass http://127.0.0.1:9996/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 24h;
    }

    location /channels/ {
        proxy_pass http://127.0.0.1:15100/;
        proxy_set_header Host $host;
    }

    location ~ ^/(accounts/login|accounts/register)/ {
        limit_req zone=auth burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
NGINX

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/olymp.oshsu.kg /etc/nginx/sites-enabled/

sudo nginx -t 2>&1 | tail -3
sudo systemctl reload nginx

echo "==> nginx ready"
