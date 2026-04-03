#!/bin/bash
# Cloud VM Deployment Script - Platinum Tier
# Deploys Personal AI Employee to cloud VM (Oracle Cloud Free Tier)
# Usage: ./deploy_cloud.sh

set -e

echo "============================================================"
echo " Personal AI Employee - Cloud VM Deployment"
echo " Platinum Tier"
echo "============================================================"
echo ""

# Configuration
VM_USER=${VM_USER:-"ubuntu"}
VM_HOST=${VM_HOST:-"your-vm-ip"}
VM_KEY=${VM_KEY:-"~/.ssh/id_rsa"}
REMOTE_PATH="/opt/ai-employee"
PROJECT_DIR=$(pwd)

echo "Configuration:"
echo "  VM User: $VM_USER"
echo "  VM Host: $VM_HOST"
echo "  Remote Path: $REMOTE_PATH"
echo ""

# Check SSH key
if [ ! -f "${VM_KEY/#\~/$HOME}" ]; then
    echo "ERROR: SSH key not found: $VM_KEY"
    echo "Generate with: ssh-keygen -t rsa -b 4096"
    exit 1
fi

echo "[1/6] Testing SSH connection..."
ssh -i "$VM_KEY" -o ConnectTimeout=5 "$VM_USER@$VM_HOST" "echo 'Connected!'" || {
    echo "ERROR: Cannot connect to VM"
    echo "Check:"
    echo "  - VM is running"
    echo "  - SSH key is added to VM"
    echo "  - Firewall allows SSH (port 22)"
    exit 1
}

echo "[2/6] Installing dependencies on VM..."
ssh -i "$VM_KEY" "$VM_USER@$VM_HOST" << 'ENDSSH'
sudo apt-get update
sudo apt-get install -y python3 python3-pip nodejs npm git

# Install Python dependencies
pip3 install watchdog python-dotenv requests pydantic psutil

# Install Playwright
pip3 install playwright
python3 -m playwright install chromium --with-deps
ENDSSH

echo "[3/6] Creating remote directories..."
ssh -i "$VM_KEY" "$VM_USER@$VM_HOST" "mkdir -p $REMOTE_PATH $REMOTE_PATH/vault"

echo "[4/6] Syncing project to VM..."
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
    --exclude='.env' --exclude='*.token' --exclude='*credentials*' \
    "$PROJECT_DIR/" "$VM_USER@$VM_HOST:$REMOTE_PATH/"

echo "[5/6] Setting up systemd services..."
ssh -i "$VM_KEY" "$VM_USER@$VM_HOST" << ENDSSH
# Cloud Agent service
sudo tee /etc/systemd/system/ai-employee-cloud.service > /dev/null << 'EOF'
[Unit]
Description=AI Employee Cloud Agent
After=network.target

[Service]
Type=simple
User=$VM_USER
WorkingDirectory=$REMOTE_PATH/vault
ExecStart=/usr/bin/python3 $REMOTE_PATH/vault/src/cloud_agent.py
Restart=always
RestartSec=60
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Health Monitor service
sudo tee /etc/systemd/system/ai-employee-health.service > /dev/null << 'EOF'
[Unit]
Description=AI Employee Health Monitor
After=network.target

[Service]
Type=simple
User=$VM_USER
WorkingDirectory=$REMOTE_PATH/vault
ExecStart=/usr/bin/python3 $REMOTE_PATH/vault/src/health_monitor.py
Restart=always
RestartSec=120
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable ai-employee-cloud
sudo systemctl enable ai-employee-health
sudo systemctl start ai-employee-cloud
sudo systemctl start ai-employee-health
ENDSSH

echo "[6/6] Verifying deployment..."
ssh -i "$VM_KEY" "$VM_USER@$VM_HOST" << 'ENDSSH'
echo "Cloud Agent Status:"
sudo systemctl status ai-employee-cloud --no-pager

echo ""
echo "Health Monitor Status:"
sudo systemctl status ai-employee-health --no-pager

echo ""
echo "Recent Logs:"
sudo journalctl -u ai-employee-cloud --no-pager -n 10
ENDSSH

echo ""
echo "============================================================"
echo " Deployment Complete!"
echo "============================================================"
echo ""
echo "Access your cloud VM:"
echo "  SSH: ssh -i $VM_KEY $VM_USER@$VM_HOST"
echo "  Status: sudo systemctl status ai-employee-cloud"
echo "  Logs: sudo journalctl -u ai-employee-cloud -f"
echo ""
echo "IMPORTANT: Setup vault sync between cloud and local!"
echo "  See: PLATINUM_TIER_README.md"
echo ""
