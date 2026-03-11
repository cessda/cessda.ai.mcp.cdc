# CESSDA MCP Server - HTTP/SSE Deployment Guide

This guide covers deploying the CESSDA MCP server with HTTP/SSE transport for web-based access.

## Overview

The MCP server supports two transport modes:

- **STDIO**: For local Claude Desktop integration (original `Dockerfile`)
- **HTTP/SSE**: For web deployment and remote access (`Dockerfile.http`)

This guide focuses on HTTP/SSE deployment to a web server.

## Quick Start with Docker Compose

The easiest way to deploy the HTTP server is using Docker Compose:

```bash
# Clone the repository (if not already done)
git clone https://github.com/cessda/mcp-cessda-datasets.git
cd mcp-cessda-datasets

# Start the server
docker compose up -d

# Check logs
docker compose logs -f

# Stop the server
docker compose down
```

The server will be available at `http://localhost:8000`

## Manual Docker Deployment

### Build the Image

```bash
# Build the HTTP/SSE version
docker build -f Dockerfile.http -t cessda/mcp-datasets-http:0.1.0 .
```

### Run the Container

```bash
# Basic run
docker run -d \
  --name mcp-cessda-http \
  -p 8000:8000 \
  cessda/mcp-datasets-http:0.1.0

# With custom configuration
docker run -d \
  --name mcp-cessda-http \
  -p 8000:8000 \
  -e CESSDA_LOG_LEVEL=INFO \
  -e CESSDA_API_TIMEOUT=60 \
  -e MCP_PORT=8000 \
  cessda/mcp-datasets-http:0.1.0

# Check logs
docker logs -f mcp-cessda-http

# Stop container
docker stop mcp-cessda-http
docker rm mcp-cessda-http
```

## Configuration

### Environment Variables

The HTTP server supports all standard configuration variables plus HTTP-specific ones:

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | HTTP server bind address |
| `MCP_PORT` | `8000` | HTTP server port |
| `CESSDA_API_BASE_URL` | `https://datacatalogue.cessda.eu/api` | CESSDA API URL |
| `CESSDA_API_TIMEOUT` | `30` | API timeout (seconds) |
| `CESSDA_API_MAX_RETRIES` | `3` | Max retry attempts |
| `CESSDA_LOG_LEVEL` | `WARN` | Log level (INFO/WARN/ERROR) |
| `CESSDA_DEFAULT_LANGUAGE` | `en` | Default metadata language |
| `CESSDA_DEFAULT_LIMIT` | `10` | Default result limit |
| `CESSDA_MAX_LIMIT` | `200` | Maximum result limit |

### Using .env File

Create a `.env` file in the project root:

```bash
# HTTP Server
MCP_HOST=0.0.0.0
MCP_PORT=8000

# API Configuration
CESSDA_API_TIMEOUT=60
CESSDA_LOG_LEVEL=INFO
CESSDA_DEFAULT_LIMIT=20
```

Docker Compose will automatically load this file.

## Deployment Scenarios

### 1. Deploy to Generic VPS/Cloud Server

```bash
# SSH into your server
ssh user@your-server.com

# Install Docker and Docker Compose (if not already installed)
# See: https://docs.docker.com/engine/install/

# Clone repository
git clone https://github.com/cessda/mcp-cessda-datasets.git
cd mcp-cessda-datasets

# Configure environment (optional)
cp .env.example .env
nano .env

# Start with Docker Compose
docker compose up -d

# Set up reverse proxy (see below)
```

### 2. Behind Nginx Reverse Proxy

Create `/etc/nginx/sites-available/mcp-cessda`:

```nginx
server {
    listen 80;
    server_name mcp.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE-specific settings
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }
}
```

Enable and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/mcp-cessda /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. With SSL/TLS (Let's Encrypt)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d mcp.yourdomain.com

# Certbot will automatically configure HTTPS
# Your server will be available at https://mcp.yourdomain.com
```

### 4. Deploy to AWS EC2

```bash
# Launch EC2 instance (Ubuntu/Amazon Linux)
# Open port 8000 in security group (or 80/443 if using reverse proxy)

# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy application
git clone https://github.com/cessda/mcp-cessda-datasets.git
cd mcp-cessda-datasets
docker compose up -d
```

### 5. Deploy to Google Cloud Run

Create `cloudrun.yaml`:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: mcp-cessda-datasets
spec:
  template:
    spec:
      containers:
      - image: gcr.io/YOUR_PROJECT/mcp-cessda-datasets-http:0.1.0
        ports:
        - containerPort: 8000
        env:
        - name: CESSDA_LOG_LEVEL
          value: INFO
        - name: MCP_PORT
          value: "8000"
```

Deploy:

```bash
# Build and push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT/mcp-cessda-datasets-http:0.1.0 -f Dockerfile.http

# Deploy to Cloud Run
gcloud run deploy mcp-cessda-datasets \
  --image gcr.io/YOUR_PROJECT/mcp-cessda-datasets-http:0.1.0 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

## Testing the Deployment

### Health Check

```bash
curl http://localhost:8000/health
# or
curl https://mcp.yourdomain.com/health
```

### Test MCP Endpoint

The server exposes MCP protocol endpoints. You can test with an MCP client or tools.

Example using `curl` to check server info:

```bash
# List available tools
curl -X POST http://localhost:8000/mcp/v1/tools \
  -H "Content-Type: application/json"
```

### Test with MCP Client

Update your MCP client configuration to use the HTTP endpoint:

```json
{
  "mcpServers": {
    "cessda-datasets": {
      "url": "http://your-server.com:8000/mcp/v1",
      "transport": "http"
    }
  }
}
```

## Monitoring and Logs

### View Logs

```bash
# Docker Compose
docker compose logs -f

# Direct Docker
docker logs -f mcp-cessda-http

# Last 100 lines
docker logs --tail 100 mcp-cessda-http
```

### Log Format

Logs are in structured JSON format:

```json
{
  "timestamp": "2025-01-15T10:30:45.123456Z",
  "level": "INFO",
  "message": "Starting CESSDA MCP server via HTTP/SSE",
  "host": "0.0.0.0",
  "port": 8000
}
```

### Monitoring Endpoints

- **Health**: `GET /health` - Returns 200 if server is healthy
- **Metrics**: Check Docker stats: `docker stats mcp-cessda-http`

## Security Considerations

### 1. Authentication

The basic deployment doesn't include authentication. For production:

- Deploy behind an API gateway with authentication
- Use Nginx with basic auth or OAuth2 proxy
- Restrict access via firewall rules

Example Nginx with basic auth:

```bash
# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd username

# Update Nginx config
auth_basic "MCP Server";
auth_basic_user_file /etc/nginx/.htpasswd;
```

### 2. HTTPS/TLS

Always use HTTPS in production (see Let's Encrypt section above).

### 3. Rate Limiting

Add rate limiting in Nginx:

```nginx
limit_req_zone $binary_remote_addr zone=mcp_limit:10m rate=10r/s;

server {
    location / {
        limit_req zone=mcp_limit burst=20;
        # ... rest of config
    }
}
```

### 4. CORS Configuration

If needed for browser-based clients, configure CORS in Nginx:

```nginx
location / {
    add_header 'Access-Control-Allow-Origin' 'https://allowed-domain.com';
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
    # ... rest of config
}
```

## Updating the Server

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Troubleshooting

### Server won't start

```bash
# Check logs
docker compose logs

# Check if port is already in use
sudo netstat -tulpn | grep 8000

# Try different port
MCP_PORT=8001 docker compose up -d
```

### Can't connect from outside

- Check firewall rules: `sudo ufw status`
- Verify security group settings (AWS/GCP)
- Check if server is binding to 0.0.0.0: `docker logs mcp-cessda-http | grep "Starting"`

### High memory usage

Adjust Docker resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 256M
```

## Production Checklist

- [ ] Configure HTTPS/TLS
- [ ] Set up authentication
- [ ] Configure rate limiting
- [ ] Set up monitoring/alerting
- [ ] Configure log aggregation
- [ ] Set up automated backups (if storing state)
- [ ] Configure auto-restart on failure
- [ ] Document API endpoints for users
- [ ] Set up CI/CD for updates
- [ ] Configure firewall rules

## Support

- Documentation: https://docs.tech.cessda.eu
- Issues: https://github.com/cessda/mcp-cessda-datasets/issues
- MCP Protocol: https://modelcontextprotocol.io/

## License

Apache 2.0 - See LICENSE.txt
