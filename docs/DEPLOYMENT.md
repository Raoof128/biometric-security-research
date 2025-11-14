# Deployment Guide

Complete deployment guide for the Biometric Security Research System v2.0.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Deployment](#local-development-deployment)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Configuration](#configuration)
- [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Hardware Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB
- Webcam (optional, for real-time features)

**Recommended:**
- CPU: 4+ cores
- RAM: 8GB
- Storage: 20GB+ SSD
- GPU (optional, for faster processing)
- Webcam (for liveness detection)

### Software Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS 11+, Windows 10+
- **Python**: 3.8, 3.9, 3.10, or 3.11
- **Git**: 2.x+
- **Docker** (optional): 20.10+
- **Docker Compose** (optional): 2.x+

---

## Local Development Deployment

###Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/biometric-security-research.git
cd biometric-security-research
```

### Step 2: Automated Setup

```bash
# Make install script executable
chmod +x install.sh

# Run automated installation
./install.sh
```

The script will:
- Check Python version
- Create virtual environment
- Install dependencies
- Create directories
- Offer to download dlib model
- Run tests

### Step 3: Manual Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/{enrolled_users,test_samples,attack_samples,results}
mkdir -p biometric/models logs

# Run tests
pytest
```

### Step 4: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Key settings to configure:**
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
BIOMETRIC_MODEL=Facenet
BIOMETRIC_THRESHOLD=0.6
```

### Step 5: Verify Installation

```bash
# Check system status
python cli_enhanced.py status

# Run tests
make test

# Verify all systems
make all
```

---

## Docker Deployment

### Quick Start with Docker

```bash
# Build Docker image
docker build -t biometric-security:2.0.0 .

# Run container
docker run -it \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  biometric-security:2.0.0
```

### Using Docker Compose

**Step 1: Configure Environment**

```bash
# Create .env file
cp .env.example .env

# Edit as needed
nano .env
```

**Step 2: Start Services**

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

**Step 3: Execute Commands**

```bash
# Check system status
docker-compose exec biometric-security python cli_enhanced.py status

# Enroll user
docker-compose exec biometric-security \
  python cli_enhanced.py enroll \
  --user-id alice \
  --modality face \
  --image-dir /app/data/alice

# Run tests
docker-compose exec biometric-security pytest
```

**Step 4: Stop Services**

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker Production Configuration

**Dockerfile.prod** (optimized for production):

```dockerfile
FROM python:3.10-slim

# Production-specific settings
ENV PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO

# Install production dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
WORKDIR /app
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

CMD ["python", "cli_enhanced.py", "status"]
```

Build and run:

```bash
docker build -f Dockerfile.prod -t biometric-security:prod .
docker run -d --name biometric-prod biometric-security:prod
```

---

## Production Deployment

### System Preparation

**1. Update System**

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
  build-essential \
  cmake \
  git \
  python3.10 \
  python3.10-venv \
  python3-pip \
  libgomp1 \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender-dev \
  libgl1-mesa-glx
```

**2. Create Service User**

```bash
# Create dedicated user
sudo useradd -r -s /bin/bash -m -d /opt/biometric biouser

# Create application directory
sudo mkdir -p /opt/biometric
sudo chown biouser:biouser /opt/biometric
```

**3. Deploy Application**

```bash
# Switch to service user
sudo su - biouser

# Clone repository
cd /opt/biometric
git clone https://github.com/yourusername/biometric-security-research.git
cd biometric-security-research

# Setup virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/{enrolled_users,test_samples,attack_samples,results}
mkdir -p logs
```

**4. Configure Service**

Create systemd service file `/etc/systemd/system/biometric-security.service`:

```ini
[Unit]
Description=Biometric Security Research System
After=network.target

[Service]
Type=simple
User=biouser
Group=biouser
WorkingDirectory=/opt/biometric/biometric-security-research
Environment="PATH=/opt/biometric/biometric-security-research/venv/bin"
Environment="ENVIRONMENT=production"
Environment="LOG_LEVEL=INFO"
ExecStart=/opt/biometric/biometric-security-research/venv/bin/python cli_enhanced.py status
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/biometric/biometric-security-research/data
ReadWritePaths=/opt/biometric/biometric-security-research/logs

# Resource limits
MemoryLimit=4G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

**5. Enable and Start Service**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable biometric-security

# Start service
sudo systemctl start biometric-security

# Check status
sudo systemctl status biometric-security

# View logs
sudo journalctl -u biometric-security -f
```

### Nginx Reverse Proxy (Future Web Interface)

`/etc/nginx/sites-available/biometric-security`:

```nginx
server {
    listen 80;
    server_name biometric.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name biometric.example.com;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/biometric.crt;
    ssl_certificate_key /etc/ssl/private/biometric.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=biometric:10m rate=10r/s;
    limit_req zone=biometric burst=20 nodelay;

    # Logging
    access_log /var/log/nginx/biometric-access.log;
    error_log /var/log/nginx/biometric-error.log;

    # Proxy to application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static {
        alias /opt/biometric/biometric-security-research/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## Cloud Deployment

### AWS EC2 Deployment

**1. Launch EC2 Instance**

```bash
# Instance type: t3.medium (2 vCPU, 4GB RAM)
# AMI: Ubuntu Server 22.04 LTS
# Storage: 20GB gp3
# Security Group: Allow SSH (22), HTTPS (443)
```

**2. Connect and Setup**

```bash
# Connect via SSH
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3.10 python3.10-venv git

# Clone and setup (follow production deployment steps)
```

**3. Configure Elastic IP**

```bash
# Allocate Elastic IP in AWS Console
# Associate with EC2 instance
```

**4. Setup Auto Scaling (Optional)**

Create launch template and auto-scaling group in AWS Console.

### Google Cloud Platform (GCP)

**1. Create Compute Instance**

```bash
gcloud compute instances create biometric-security \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB \
  --tags=http-server,https-server
```

**2. SSH and Setup**

```bash
gcloud compute ssh biometric-security

# Follow production deployment steps
```

### Azure VM Deployment

```bash
# Create resource group
az group create --name biometric-rg --location eastus

# Create VM
az vm create \
  --resource-group biometric-rg \
  --name biometric-vm \
  --image UbuntuLTS \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys

# SSH and setup
ssh azureuser@your-vm-ip
```

### Kubernetes Deployment

**deployment.yaml**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: biometric-security
spec:
  replicas: 2
  selector:
    matchLabels:
      app: biometric-security
  template:
    metadata:
      labels:
        app: biometric-security
    spec:
      containers:
      - name: biometric-security
        image: biometric-security:2.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: biometric-data-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: biometric-logs-pvc
```

---

## Configuration

### Environment-Specific Configs

**Development (.env.development)**:
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ENABLE_GPU=false
CACHE_EMBEDDINGS=true
```

**Production (.env.production)**:
```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
ENABLE_GPU=true
CACHE_EMBEDDINGS=true
SECURE_DELETE=true
```

### Configuration Management

```bash
# Use specific config
export ENV_FILE=.env.production
python cli_enhanced.py status

# Override specific settings
export LOG_LEVEL=DEBUG
python cli_enhanced.py status
```

---

## Monitoring & Maintenance

### Log Management

**View Logs:**
```bash
# Application logs
tail -f logs/biometric_security.log

# Audit logs
tail -f logs/audit.log

# Error logs only
grep ERROR logs/biometric_security.log
```

**Log Rotation:**
```bash
# Configured in utils/logger.py
# Max size: 10MB
# Backup count: 5
```

### Performance Monitoring

```bash
# Check system status
python cli_enhanced.py status

# Monitor resources
make status

# Performance snapshot
python -c "
from utils.performance import get_performance_monitor
monitor = get_performance_monitor()
print(monitor.get_memory_usage())
print(f'CPU: {monitor.get_cpu_usage():.1f}%')
"
```

### Backup & Recovery

**Backup:**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=/backup/biometric/$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

# Backup enrolled users
cp -r data/enrolled_users $BACKUP_DIR/

# Backup configuration
cp .env $BACKUP_DIR/
cp config.json $BACKUP_DIR/ 2>/dev/null || true

# Backup logs
cp -r logs $BACKUP_DIR/

# Create archive
tar -czf $BACKUP_DIR.tar.gz -C /backup/biometric $(date +%Y%m%d)
rm -rf $BACKUP_DIR

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

**Recovery:**
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

# Extract backup
tar -xzf $BACKUP_FILE -C /tmp/

# Restore enrolled users
cp -r /tmp/$(basename $BACKUP_FILE .tar.gz)/enrolled_users data/

# Restore configuration
cp /tmp/$(basename $BACKUP_FILE .tar.gz)/.env .

echo "Restoration completed"
```

### Health Checks

```bash
# System health check script
#!/bin/bash
# health_check.sh

# Check if process is running
if pgrep -f "cli_enhanced.py" > /dev/null; then
    echo "✓ Application is running"
else
    echo "✗ Application is not running"
    exit 1
fi

# Check disk space
DISK_USAGE=$(df -h /opt/biometric | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠ Disk usage high: ${DISK_USAGE}%"
fi

# Check memory
FREE_MEM=$(free -m | grep Mem | awk '{print $7}')
if [ $FREE_MEM -lt 1000 ]; then
    echo "⚠ Low memory: ${FREE_MEM}MB free"
fi

echo "Health check completed"
```

### Updates & Upgrades

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Run tests
pytest

# Restart service
sudo systemctl restart biometric-security
```

---

## Troubleshooting

See [FAQ.md](FAQ.md) for common issues and solutions.

---

For security considerations, see [SECURITY.md](../SECURITY.md).
