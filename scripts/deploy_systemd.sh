#!/bin/bash
# Setup systemd units for OshSU Olymp.
set -e

PROJ=/var/www/olymp.oshsu.kg

echo "==> Creating systemd units"

sudo tee /etc/systemd/system/olymp-web.service > /dev/null << EOF
[Unit]
Description=OshSU Olymp Django (gunicorn)
After=network.target postgresql.service redis-server.service

[Service]
User=admin
Group=admin
WorkingDirectory=$PROJ
Environment=DJANGO_SETTINGS_MODULE=dmoj.settings
ExecStart=$PROJ/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 --access-logfile /var/log/olymp/gunicorn-access.log --error-logfile /var/log/olymp/gunicorn-error.log dmoj.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/olymp-bridge.service > /dev/null << EOF
[Unit]
Description=OshSU Olymp Judge Bridge
After=network.target postgresql.service

[Service]
User=admin
Group=admin
WorkingDirectory=$PROJ
Environment=DJANGO_SETTINGS_MODULE=dmoj.settings
ExecStart=$PROJ/venv/bin/python manage.py runbridged
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Event daemon — Node.js
sudo tee /etc/systemd/system/olymp-event.service > /dev/null << EOF
[Unit]
Description=OshSU Olymp Event Daemon (websocket)
After=network.target

[Service]
User=admin
Group=admin
WorkingDirectory=$PROJ/websocket
ExecStart=/usr/bin/node daemon.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Setup websocket dependencies
cd $PROJ/websocket
if [ ! -d node_modules ]; then
    npm install ws simplesets qu 2>&1 | tail -3
fi

# Create config.js for event daemon if not exists
if [ ! -f $PROJ/websocket/config.js ]; then
    cat > $PROJ/websocket/config.js << 'CONF'
module.exports = {
    get_host: '127.0.0.1',
    get_port: 9996,
    post_host: '127.0.0.1',
    post_port: 9997,
    http_host: '127.0.0.1',
    http_port: 15100,
    long_poll_timeout: 29000,
};
CONF
fi

sudo systemctl daemon-reload
sudo systemctl enable olymp-web olymp-bridge olymp-event 2>&1 | tail -3
sudo systemctl restart olymp-web olymp-bridge olymp-event

sleep 3
echo "==> Status:"
sudo systemctl status olymp-web --no-pager -l | head -5
sudo systemctl status olymp-bridge --no-pager -l | head -5
sudo systemctl status olymp-event --no-pager -l | head -5
