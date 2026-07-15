# 📦 Deployment Guide - Oceania RAG Chatbot

This guide covers multiple deployment options for the production chatbot.

## Table of Contents
- [Docker (Recommended)](#docker)
- [Heroku](#heroku)
- [AWS](#aws)
- [GCP](#gcp)
- [Azure](#azure)
- [Local Server](#local-server)

---

## Docker (Recommended) ⭐

### Prerequisites
- Docker installed
- OpenAI API key

### Deployment

```bash
# 1. Set environment variable
export OPENAI_API_KEY='sk-your-key'

# 2. Build and run
docker-compose up -d

# 3. Access at http://localhost:8501
```

### Production Docker Command

```bash
docker run -d \
  --name oceania-chatbot \
  -p 8501:8501 \
  -e OPENAI_API_KEY='sk-your-key' \
  -v $(pwd)/chroma_db:/app/chroma_db \
  -v $(pwd)/extracted_images:/app/extracted_images \
  oceania-chatbot:latest
```

### Scale with Docker Swarm

```bash
docker swarm init
docker stack deploy -c docker-compose.yml oceania
```

---

## Heroku

### Prerequisites
- Heroku CLI installed
- Heroku account

### Deployment Steps

```bash
# 1. Login to Heroku
heroku login

# 2. Create Heroku app
heroku create oceania-chatbot

# 3. Set environment variable
heroku config:set OPENAI_API_KEY='sk-your-key'

# 4. Create Procfile
cat > Procfile << EOF
web: streamlit run streamlit_app.py --server.port $PORT
EOF

# 5. Deploy
git push heroku main

# 6. View logs
heroku logs --tail
```

### Heroku Buildpack

```bash
heroku buildpacks:add heroku/python
git push heroku main
```

---

## AWS

### Option 1: EC2

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. SSH into instance
ssh -i key.pem ubuntu@instance-ip

# 3. Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv

# 4. Clone repo and setup
git clone <repo>
cd oceanic_rag_chatbot
./setup.sh install

# 5. Set API key
export OPENAI_API_KEY='sk-your-key'

# 6. Run with systemd service
sudo nano /etc/systemd/system/oceania.service
```

### systemd Service File

```ini
[Unit]
Description=Oceania RAG Chatbot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/oceanic_rag_chatbot
Environment="OPENAI_API_KEY=sk-your-key"
Environment="PATH=/home/ubuntu/oceanic_rag_chatbot/venv/bin"
ExecStart=/home/ubuntu/oceanic_rag_chatbot/venv/bin/streamlit run streamlit_app.py --server.port 8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable oceania
sudo systemctl start oceania
```

### Option 2: ECS (Elastic Container Service)

```bash
# 1. Push image to ECR
aws ecr create-repository --repository-name oceania-chatbot
docker tag oceania-chatbot:latest <account>.dkr.ecr.region.amazonaws.com/oceania-chatbot:latest
docker push <account>.dkr.ecr.region.amazonaws.com/oceania-chatbot:latest

# 2. Create ECS task definition
# 3. Create ECS service
# 4. Configure load balancer
```

### Option 3: Elastic Beanstalk

```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize
eb init -p python-3.11 oceania-chatbot

# 3. Create environment
eb create oceania-prod

# 4. Deploy
eb deploy
```

---

## GCP

### Cloud Run

```bash
# 1. Authenticate
gcloud auth login

# 2. Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/oceania-chatbot

# 3. Deploy
gcloud run deploy oceania-chatbot \
  --image gcr.io/PROJECT_ID/oceania-chatbot \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY='sk-your-key' \
  --memory 2Gi \
  --port 8501
```

### Compute Engine

```bash
# 1. Create instance
gcloud compute instances create oceania-chatbot \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=e2-medium

# 2. SSH into instance
gcloud compute ssh oceania-chatbot

# 3. Follow local server setup
```

---

## Azure

### Azure Container Instances

```bash
# 1. Push to ACR
az acr build --registry <registry-name> --image oceania-chatbot .

# 2. Deploy
az container create \
  --resource-group <group> \
  --name oceania-chatbot \
  --image <registry>.azurecr.io/oceania-chatbot \
  --ports 8501 \
  --environment-variables \
    OPENAI_API_KEY='sk-your-key' \
  --cpu 2 \
  --memory 4
```

### App Service

```bash
# 1. Create app service plan
az appservice plan create --name oceania-plan --sku B2

# 2. Create webapp
az webapp create --resource-group <group> \
  --plan oceania-plan \
  --name oceania-chatbot

# 3. Deploy from Git
az webapp deployment source config-zip --resource-group <group> \
  --name oceania-chatbot --src deployment.zip
```

---

## Local Server

### Production Setup with Nginx

```bash
# 1. Install Nginx
sudo apt install nginx

# 2. Create Nginx config
sudo nano /etc/nginx/sites-available/oceania

# 3. Add config:
```

```nginx
upstream oceania {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name oceania.yourdomain.com;

    location / {
        proxy_pass http://oceania;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# 4. Enable site
sudo ln -s /etc/nginx/sites-available/oceania /etc/nginx/sites-enabled/

# 5. Test and restart
sudo nginx -t
sudo systemctl restart nginx

# 6. Get SSL certificate
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d oceania.yourdomain.com
```

### Gunicorn Setup

```bash
# 1. Create ASGI wrapper
cat > asgi.py << EOF
from streamlit.web import cli as stcli
import sys

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "streamlit_app.py"]
    stcli.main()
EOF

# 2. Run with Gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8501 asgi:app
```

---

## Monitoring & Health Checks

### Health Check Endpoint

```bash
curl http://localhost:8501/_stcore/health
```

### Monitoring with Prometheus

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'oceania-chatbot'
    static_configs:
      - targets: ['localhost:8501']
```

### Logging

```bash
# View logs
tail -f logs/chatbot.log

# Send to CloudWatch (AWS)
aws logs create-log-group --log-group-name /oceania/chatbot
aws logs create-log-stream --log-group-name /oceania/chatbot --log-stream-name app
```

---

## Performance Optimization

### Caching
- Implement Redis for response caching
- Cache embeddings for frequently asked questions

### Load Balancing
- Use AWS ALB or NGINX for load distribution
- Deploy multiple instances behind load balancer

### Database
- Consider managed ChromaDB service
- Use cloud storage for extracted images

### CDN
- Serve static files through CloudFront/CloudFlare
- Cache images globally

---

## Security Checklist

- [ ] Set `OPENAI_API_KEY` as environment variable
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Implement rate limiting
- [ ] Add authentication if needed
- [ ] Enable logging and monitoring
- [ ] Use secrets manager
- [ ] Regular security updates

---

## Troubleshooting

### Port already in use
```bash
lsof -i :8501
kill -9 <PID>
```

### Out of memory
- Reduce `CHUNK_SIZE` in config
- Reduce number of workers
- Increase instance memory

### Slow responses
- Check API rate limits
- Optimize retriever settings
- Cache frequent queries

---

## Cost Estimates

| Platform | Monthly Cost |
|----------|-------------|
| Docker (Self-hosted) | $0-20 |
| Heroku (Hobby) | $7-50 |
| AWS EC2 (t3.medium) | $30-50 |
| GCP Cloud Run | $0.02 per 100k requests |
| Azure App Service | $50-100 |

---

**Need more help?** See README.md or check logs for errors.
