#!/bin/bash
set -e

cd /home/ec2-user/CoffeeMate

# 1. 拉取代码
git pull origin main


# 2.mcp服务器1
cd /home/ec2-user/CoffeeMate/HowToCook-mcp-master/HowToCook-mcp-master
npm ci
npm run build
node build/index.js --transport http --port 8080

# 3. mcp服务器2
cd /home/ec2-user/CoffeeMate/coffee_mcp
[ -d .venv ] || uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
source ./.venv/bin/activate
deactivate


# 4. 构建前端
cd /home/ec2-user/CoffeeMate/coffee-vue
npm ci
npm run build



# 5. 后端环境
cd /home/ec2-user/CoffeeMate/coffee-fastapi
[ -d .venv ] || uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
source .venv/bin/activate
deactivate


# 6.写入mcp服务器1的服务
sudo tee /etc/systemd/system/howtocook-mcp.service <<EOF
[Unit]
Description=HowToCook MCP Server
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/CoffeeMate/HowToCook-mcp-master/HowToCook-mcp-master
ExecStart=/usr/bin/node build/index.js --transport http --port 8080
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable howtocook-mcp.service
sudo systemctl start howtocook-mcp.service

# 7.写入mcp服务器2的服务
sudo tee /etc/systemd/system/coffee-mcp.service <<EOF
[Unit]
Description=Coffee MCP Server
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/CoffeeMate/coffee_mcp
ExecStart=/home/ec2-user/CoffeeMate/coffee_mcp/.venv/bin/python /home/ec2-user/CoffeeMate/coffee_mcp/mcp_server.py

Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable coffee-mcp.service
sudo systemctl start coffee-mcp.service

# 8.写入vue前端的nginx服务
if ! rpm -q nginx &> /dev/null; then
    echo "Installing Nginx..."
    sudo dnf install -y nginx
    sudo systemctl enable nginx --now
fi

sudo rm -rf /usr/share/nginx/html/*
sudo cp -r /home/ec2-user/CoffeeMate/coffee-vue/dist/* /usr/share/nginx/html/

sudo tee /etc/nginx/conf.d/coffee-vue.conf <<EOF
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

sudo nginx -t && sudo systemctl reload nginx

# 9.写入后端服务
sudo tee /etc/systemd/system/coffee-fastapi.service <<EOF
[Unit]
Description=Coffee Backend
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/CoffeeMate/coffee-fastapi
ExecStart=/home/ec2-user/CoffeeMate/coffee-fastapi/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable coffee-fastapi.service --now
echo "✅ Deployment completed on Amazon Linux 2023!"