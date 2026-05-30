#!/bin/bash
# SocialDrive AI MCP Server - Monitoring Script
# Check if MCP server is running and healthy

set -e

VPS_USER="dpmcg"
VPS_HOST="your-vps-ip-or-domain"  # ← UPDATE THIS (same as deploy script)
MCP_PORT=8765

echo "🔍 SocialDrive AI MCP Server Health Check"
echo "=========================================="
echo ""

# Check if running locally or on VPS
if [ "$1" = "local" ]; then
    echo "📊 Checking LOCAL MCP server..."
    echo ""
    
    # Check process
    if pgrep -f "simple_http_server.py" > /dev/null; then
        echo "✅ Process: RUNNING"
        pgrep -f "simple_http_server.py" | xargs ps aux | awk '{print "   PID: "$2", CPU: "$3"%, MEM: "$4"%"}'
    else
        echo "❌ Process: NOT RUNNING"
    fi
    
    # Check port
    if netstat -tuln 2>/dev/null | grep -q ":$MCP_PORT" || ss -tuln 2>/dev/null | grep -q ":$MCP_PORT"; then
        echo "✅ Port $MCP_PORT: LISTENING"
    else
        echo "❌ Port $MCP_PORT: NOT LISTENING"
    fi
    
    # Health check
    HEALTH=$(curl -s "http://localhost:$MCP_PORT/health" 2>/dev/null || echo '{"status":"error"}')
    if echo "$HEALTH" | grep -q '"status":"ok"'; then
        echo "✅ Health: OK"
        echo "   Response: $HEALTH"
    else
        echo "⚠️  Health: UNKNOWN"
        echo "   Response: $HEALTH"
    fi
    
    echo ""
    echo "📝 Recent Logs:"
    journalctl -u mcp-server --no-pager -n 5 2>/dev/null || echo "   (No systemd logs - running manually)"
    
else
    echo "📊 Checking VPS MCP server ($VPS_HOST)..."
    echo ""
    
    # Check via SSH
    ssh "$VPS_USER@$VPS_HOST" << ENDSSH
echo "✅ Process Status:"
sudo systemctl is-active mcp-server

echo ""
echo "✅ Service Status:"
sudo systemctl status mcp-server --no-pager | head -5

echo ""
echo "📊 Resource Usage:"
ps aux | grep "simple_http_server" | grep -v grep | awk '{print "   CPU: "\$3"%, MEM: "\$4"%"}'

echo ""
echo "🌐 Health Check:"
curl -s "http://localhost:$MCP_PORT/health" | head -1

echo ""
echo "📝 Last 5 Log Entries:"
sudo journalctl -u mcp-server --no-pager -n 5

ENDSSH
fi

echo ""
echo "=========================================="
echo ""
echo "💡 Quick Commands:"
echo "   Local:  ./monitor-mcp.sh local"
echo "   VPS:    ./monitor-mcp.sh"
echo ""
echo "📊 Full Logs:"
echo "   Local:  journalctl -u mcp-server -f"
echo "   VPS:    ssh $VPS_USER@$VPS_HOST 'sudo journalctl -u mcp-server -f'"
