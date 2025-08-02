# Wikipedia Path Finder - Deployment Guide

This document provides comprehensive instructions for deploying the Wikipedia Path Finder application in various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Monitoring and Logging](#monitoring-and-logging)

## Local Development

### Prerequisites

- Python 3.9+ with pip
- Node.js 16+ with npm
- Git

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd WikipediaGame

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up backend
cd bot
npm install
npm start &  # Start API server on port 3001

# Set up frontend (in new terminal)
cd ../client
npm install
npm run dev  # Start development server on port 5173
```

### Development Workflow

1. **Backend Development**: Edit files in `bot/` directory
2. **Frontend Development**: Edit files in `client/src/` directory
3. **Testing**: Run `python test_simple.py` for backend tests
4. **Building**: Run `npm run build` in client directory for production build

## Docker Deployment

### Using Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./bot
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - PYTHON_PATH=/app
    volumes:
      - ./bot:/app
      - glove_cache:/app/glove_cache
    restart: unless-stopped

  frontend:
    build:
      context: ./client
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  python-worker:
    build:
      context: .
      dockerfile: Dockerfile.python
    volumes:
      - ./bot:/app
      - glove_cache:/app/glove_cache
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

volumes:
  glove_cache:
```

### Backend Dockerfile

Create `bot/Dockerfile`:

```dockerfile
FROM node:18-alpine

# Install Python and dependencies
RUN apk add --no-cache python3 py3-pip python3-dev build-base

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p glove_cache

EXPOSE 3001

CMD ["npm", "start"]
```

### Frontend Dockerfile

Create `client/Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Python Worker Dockerfile

Create `Dockerfile.python`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot/ ./

# Create cache directory
RUN mkdir -p glove_cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py", "--help"]
```

### Deployment Commands

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update and restart
docker-compose pull
docker-compose up --build -d
```

## Cloud Deployment

### Heroku Deployment

1. **Prepare for Heroku**:

Create `Procfile`:
```
web: cd bot && npm start
```

Create `runtime.txt`:
```
python-3.11.0
```

2. **Deploy**:
```bash
# Install Heroku CLI and login
heroku create wikipedia-pathfinder

# Set buildpacks
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python

# Configure environment
heroku config:set NODE_ENV=production
heroku config:set PYTHON_ENV=production

# Deploy
git push heroku main
```

### AWS Deployment (EC2)

1. **Launch EC2 Instance** (Ubuntu 20.04 LTS)

2. **Setup Script** (`deploy/setup-aws.sh`):
```bash
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Install Nginx
sudo apt install -y nginx

# Install PM2 for process management
sudo npm install -g pm2

# Clone and setup application
git clone <repository-url> /var/www/wikipedia-pathfinder
cd /var/www/wikipedia-pathfinder

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup backend
cd bot
npm install --production
pm2 start ecosystem.config.js

# Setup frontend
cd ../client
npm install
npm run build

# Configure Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/wikipedia-pathfinder
sudo ln -s /etc/nginx/sites-available/wikipedia-pathfinder /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Setup SSL (optional)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

3. **PM2 Ecosystem** (`bot/ecosystem.config.js`):
```javascript
module.exports = {
  apps: [{
    name: 'wikipedia-pathfinder-api',
    script: 'server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'development',
      PORT: 3001
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 3001
    }
  }]
}
```

### Digital Ocean App Platform

Create `.do/app.yaml`:
```yaml
name: wikipedia-pathfinder
services:
- name: api
  source_dir: /bot
  github:
    repo: your-username/WikipediaGame
    branch: main
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /api
  envs:
  - key: NODE_ENV
    value: production

- name: web
  source_dir: /client
  github:
    repo: your-username/WikipediaGame
    branch: main
  build_command: npm run build
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
```

## Environment Configuration

### Environment Variables

Create `.env` files for each environment:

**Backend** (`bot/.env`):
```
NODE_ENV=production
PORT=3001
CORS_ORIGIN=https://your-domain.com
API_TIMEOUT=30000
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX=100
LOG_LEVEL=info
```

**Python** (`.env`):
```
PYTHON_ENV=production
GLOVE_CACHE_DIR=./glove_cache
TORCH_HOME=./torch_cache
MAX_SEARCH_TIME=180
MAX_ARTICLES_CHECKED=1000
```

### Configuration Management

Create `config/production.js`:
```javascript
module.exports = {
  server: {
    port: process.env.PORT || 3001,
    cors: {
      origin: process.env.CORS_ORIGIN || '*'
    }
  },
  python: {
    maxSearchTime: parseInt(process.env.MAX_SEARCH_TIME) || 180,
    maxArticlesChecked: parseInt(process.env.MAX_ARTICLES_CHECKED) || 1000
  },
  cache: {
    gloveDir: process.env.GLOVE_CACHE_DIR || './glove_cache'
  }
}
```

## Monitoring and Logging

### Health Checks

The API includes health check endpoints:
- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed system status

### Logging Configuration

**Backend Logging** (`bot/logger.js`):
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

module.exports = logger;
```

### Monitoring with PM2

```bash
# Monitor processes
pm2 monit

# View logs
pm2 logs

# Restart application
pm2 restart all

# Save configuration
pm2 save
pm2 startup
```

### Performance Monitoring

Add performance monitoring to `bot/server.js`:
```javascript
const prometheus = require('prom-client');

// Create metrics
const httpDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status']
});

const searchDuration = new prometheus.Histogram({
  name: 'wikipedia_search_duration_seconds',
  help: 'Duration of Wikipedia searches in seconds',
  labelNames: ['algorithm', 'success']
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', prometheus.register.contentType);
  res.end(prometheus.register.metrics());
});
```

## Backup and Recovery

### Database Backup (if using database)

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application data
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
  /var/www/wikipedia-pathfinder \
  --exclude=node_modules \
  --exclude=.git \
  --exclude=logs

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/app_backup_$DATE.tar.gz \
  s3://your-backup-bucket/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "app_backup_*.tar.gz" -mtime +7 -delete
```

### Disaster Recovery

1. **Automated Deployments**: Use CI/CD pipelines for quick redeployment
2. **Infrastructure as Code**: Use Terraform or CloudFormation
3. **Data Persistence**: Store GloVe embeddings in persistent storage
4. **Health Monitoring**: Set up alerts for downtime

## Security Considerations

1. **HTTPS**: Always use SSL/TLS in production
2. **Rate Limiting**: Implemented in the API server
3. **Input Validation**: Sanitize all user inputs
4. **CORS**: Configure appropriate CORS policies
5. **Updates**: Regularly update dependencies
6. **Secrets**: Use environment variables for sensitive data

## Troubleshooting

### Common Issues

1. **Memory Issues**: Increase server memory for GloVe embeddings
2. **Network Timeouts**: Adjust timeout configurations
3. **Rate Limiting**: Wikipedia API has rate limits
4. **CORS Errors**: Check frontend/backend URL configuration

### Debug Commands

```bash
# Check service status
systemctl status nginx
pm2 status

# View logs
tail -f /var/log/nginx/error.log
pm2 logs --lines 100

# Test API endpoints
curl -I http://localhost:3001/api/health
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"start":"Python","goal":"Machine Learning","algorithm":"best-first"}'
```

For additional support, check the project documentation or create an issue in the repository.
