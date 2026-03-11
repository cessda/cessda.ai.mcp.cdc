#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Simple test script for HTTP/SSE deployment

echo "Testing MCP CESSDA Datasets HTTP Server..."
echo ""

# Test 1: Health check
echo "1. Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "   ✓ Health check passed (HTTP 200)"
else
    echo "   ✗ Health check failed (HTTP $HEALTH_RESPONSE)"
fi
echo ""

# Test 2: Check if server is responding
echo "2. Testing server response..."
SERVER_RESPONSE=$(curl -s http://localhost:8000/ 2>/dev/null)
if [ -n "$SERVER_RESPONSE" ]; then
    echo "   ✓ Server is responding"
else
    echo "   ✗ Server is not responding"
fi
echo ""

# Test 3: Docker container status
echo "3. Checking Docker container status..."
if docker ps | grep -q mcp-cessda; then
    echo "   ✓ Container is running"
    docker ps | grep mcp-cessda
else
    echo "   ✗ Container is not running"
    echo "   Checking all containers:"
    docker ps -a | grep mcp-cessda
fi
echo ""

# Test 4: Check logs for errors
echo "4. Checking recent logs for errors..."
if docker logs mcp-cessda-datasets-http 2>&1 | tail -20 | grep -i "error"; then
    echo "   ⚠ Errors found in logs"
else
    echo "   ✓ No recent errors in logs"
fi
echo ""

echo "Testing complete!"
echo ""
echo "To view full logs: docker logs -f mcp-cessda-datasets-http"
echo "To stop server: docker compose down"
