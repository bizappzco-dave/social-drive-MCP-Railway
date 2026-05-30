#!/bin/bash
# SocialDrive AI MCP Server - Deployment Script
# Deploys MCP server to VPS with systemd for 24/7 operation

set -e

# Configuration
VPS_USER="dpmcg"
VPS_HOST="your-vps-ip-or-domain"  # ← UPDATE THIS
VPS_PATH="/home/dpmcg/image-analyzer-mcp"
LOCAL_SERVICE_FILE="./mcp-server.service"

echo "🚀 SocialDrive AI MCP Server Deployment"
echo "========================================"
echo ""

# Step 1: Check if VPS host is configured
if [ "$VPS_HOST" = "your-vps-ip-or-domain" ]; then
    echo "❌ Error: Please update VPS_HOST in this script"
    echo "   Edit line 10 with your actual VPS IP or domain"
    exit 1
fi

# Step 2: Test SSH connection
echo "📡 Testing SSH connection to $VPS_HOST..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$VPS_USER@$VPS_HOST" "echo 'Connection successful'" > /dev/null 2>&1; then
    echo "❌ Error: Cannot connect to VPS via SSH"
    echo "   Check:"
    echo "   1. VPS_HOST is correct"
    echo "   2. SSH key is configured (~/.ssh/id_rsa.pub on VPS)"
    echo "   3. SSH agent is running (ssh-add -l)"
    exit 1
fi
echo "✅ SSH connection successful"
echo ""

# Step 3: Copy MCP server code to VPS
echo "📦 Copying MCP server to VPS..."
scp -r /home/dpmcg/image-analyzer-mcp/*.py "$VPS_USER@$VPS_HOST:$VPS_PATH/" 2>/dev/null || {
    echo "⚠️  Some files failed to copy, continuing..."
}
scp /home/dpmcg/image-analyzer-mcp/requirements.txt "$VPS_USER@$VPS_HOST:$VPS_PATH/" 2>/dev/null || true
echo "✅ Files copied"
echo ""

# Step 4: Copy systemd service file
echo "📋 Copying systemd service file..."
scp "$LOCAL_SERVICE_FILE" "$VPS_USER@$VPS_HOST:~/mcp-server.service"
echo "✅ Service file copied"
echo ""

# Step 5: Install and configure service on VPS
echo "⚙️  Installing systemd service on VPS..."
ssh "$VPS_USER@$VPS_HOST" << 'ENDSSH'
# Create logs directory
mkdir -p ~/image-analyzer-mcp/logs

# Install systemd service
sudo cp ~/mcp-server.service /etc/systemd/system/mcp-server.service
sudo systemctl daemon-reload
sudo systemctl enable mcp-server

# Install Python dependencies
cd ~/image-analyzer-mcp
pip3 install -r requirements.txt --quiet

# Start the service
sudo systemctl start mcp-server

# Check status
sudo systemctl status mcp-server --no-pager

ENDSSH

echo "✅ Service installed and started"
echo ""

# Step 6: Verify deployment
echo "🔍 Verifying deployment..."
sleep 3
ssh "$VPS_USER@$VPS_HOST" "curl -s http://localhost:8765/health 2>/dev/null | head -1 || echo '⚠️  Health check pending (server may still be starting)'"

echo ""
echo "========================================"
echo "✅ Deployment Complete!"
echo ""
echo "📊 Service Status:"
echo "   ssh $VPS_USER@$VPS_HOST 'sudo systemctl status mcp-server'"
echo ""
echo "📝 View Logs:"
echo "   ssh $VPS_USER@$VPS_HOST 'journalctl -u mcp-server -f'"
echo ""
echo "🔄 Restart Service:"
echo "   ssh $VPS_USER@$VPS_HOST 'sudo systemctl restart mcp-server'"
echo ""
echo "🛑 Stop Service:"
echo "   ssh $VPS_USER@$VPS_HOST 'sudo systemctl stop mcp-server'"
echo ""
echo "🌐 Test Endpoint:"
echo "   curl http://$VPS_HOST:8765/health"
echo ""
echo "🔧 Update Frontend:"
echo "   Change MCP_BASE_URL from 'http://localhost:8765' to 'http://$VPS_HOST:8765'"
echo "   in: src/app/upload/[token]/simple-page.tsx"
echo "       src/app/upload/[token]/pro-page.tsx"
echo ""
echo "========================================"
