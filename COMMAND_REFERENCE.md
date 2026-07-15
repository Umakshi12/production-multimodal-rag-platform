# 🚀 COMMAND REFERENCE - Oceania RAG Chatbot

## ⚡ Quick Commands

### One-Time Setup
```bash
export OPENAI_API_KEY='sk-your-key-here'
./setup.sh full
```

### Run Web Interface
```bash
streamlit run streamlit_app.py
# Access: http://localhost:8501
```

### Run CLI Chat
```bash
python rag_chatbot.py
```

### Run REST API
```bash
python -m uvicorn api:app --reload
# Access: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Run with Docker
```bash
export OPENAI_API_KEY='sk-your-key-here'
docker-compose up -d
# Access: http://localhost:8501
```

---

## 📋 Setup Script Commands

```bash
./setup.sh install        # Install dependencies only
./setup.sh setup          # Create directories and env files
./setup.sh ingest         # Run data ingestion pipeline
./setup.sh streamlit      # Start Streamlit web interface
./setup.sh cli            # Start CLI chatbot
./setup.sh docker         # Run with Docker Compose
./setup.sh full           # Full setup (install → ingest → streamlit)
./setup.sh clean          # Clean generated files
./setup.sh help           # Show help message
```

---

## 🐍 Python Commands

```bash
# Run data ingestion
python data_ingestion.py

# Run chatbot CLI
python rag_chatbot.py

# Start web interface
streamlit run streamlit_app.py

# Start REST API
python api.py

# Or with uvicorn
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

---

## 🐳 Docker Commands

```bash
# Build image
docker build -t oceania-chatbot .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY='sk-your-key' \
  oceania-chatbot

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 🔍 Debugging Commands

```bash
# View logs
tail -f logs/chatbot.log

# View API key status
echo $OPENAI_API_KEY

# Check vector database
ls -lh chroma_db/

# Count documents
ls -1 company_data/ | wc -l

# View extracted images
ls -1 extracted_images/ | wc -l

# Python interactive mode
python
>>> from rag_chatbot import create_chatbot
>>> chatbot = create_chatbot()
>>> print(chatbot.chat("test"))
```

---

## 📊 Verification Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -i langchain

# Check file structure
tree -L 2

# Check code quality
python -m py_compile *.py

# Count lines of code
wc -l *.py

# Find TODO comments
grep -r "TODO" *.py

# Check imports
python -c "import config; import logger; import rag_chatbot"
```

---

## 🌐 API Testing Commands

```bash
# Health check
curl http://localhost:8000/health

# Chat query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are your products?",
    "include_sources": true
  }'

# Get history
curl http://localhost:8000/history

# Clear history
curl -X POST http://localhost:8000/clear-history

# Retrieval details
curl 'http://localhost:8000/retrieval-details/granite'

# Using Python
python -c "
import requests
response = requests.post(
    'http://localhost:8000/chat',
    json={'query': 'test'}
)
print(response.json())
"
```

---

## 🔄 Maintenance Commands

```bash
# Rebuild vector database
rm -rf chroma_db/
python data_ingestion.py

# Clear everything
./setup.sh clean

# Update dependencies
pip install --upgrade -r requirements.txt

# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Find large files
du -sh * | sort -h
```

---

## 📝 Git Commands

```bash
# Check status
git status

# View changes
git diff

# Commit changes
git add .
git commit -m "message"

# Push to remote
git push origin main

# View logs
git log --oneline
```

---

## 🚀 Deployment Commands

### Heroku
```bash
heroku login
heroku create oceania-chatbot
heroku config:set OPENAI_API_KEY='sk-your-key'
git push heroku main
heroku logs --tail
```

### AWS EC2
```bash
ssh -i key.pem ubuntu@instance-ip
cd oceanic_rag_chatbot
./setup.sh full
```

### Docker Push to Registry
```bash
docker tag oceania-chatbot:latest username/oceania-chatbot:latest
docker push username/oceania-chatbot:latest
```

---

## 📊 Monitoring Commands

```bash
# Watch log file in real-time
tail -f logs/chatbot.log

# Count queries
grep -c "User Query" logs/chatbot.log

# Find errors
grep ERROR logs/chatbot.log

# Monitor API usage
watch -n 5 'curl -s http://localhost:8000/health | jq .'

# Monitor Docker memory
docker stats oceania-chatbot

# Check system resources
top -p $(pgrep -f streamlit)
```

---

## 🧪 Testing Commands

```bash
# Test imports
python -c "from rag_chatbot import create_chatbot; print('OK')"

# Test configuration
python -c "from config import *; print('Config loaded')"

# Test with pytest
pip install pytest
pytest tests/

# Run specific test
pytest tests/test_chatbot.py -v

# Check coverage
pip install pytest-cov
pytest --cov=. tests/
```

---

## 🔐 Security Commands

```bash
# Generate random API key (for testing)
python -c "import secrets; print('sk-' + secrets.token_urlsafe(32))"

# Check for hardcoded secrets
grep -r "sk-" *.py

# Scan dependencies for vulnerabilities
pip install safety
safety check

# Check Python version security
python -m pip list | grep -i python
```

---

## 🎯 Common Workflows

### Development Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY='sk-your-key'
python data_ingestion.py
streamlit run streamlit_app.py
```

### Add New Document
```bash
# 1. Copy file to company_data/
cp mydoc.pdf company_data/

# 2. Rebuild database
rm -rf chroma_db/
python data_ingestion.py

# 3. Test in chatbot
streamlit run streamlit_app.py
```

### Add Website URL
```bash
# 1. Edit config.py
nano config.py
# Add URL to WEBSITE_URLS

# 2. Rebuild database
python data_ingestion.py

# 3. Verify
python -c "from config import WEBSITE_URLS; print(WEBSITE_URLS)"
```

### Deploy to Production
```bash
# 1. Set up environment
export OPENAI_API_KEY='sk-prod-key'

# 2. Build Docker image
docker build -t oceania-chatbot:1.0.0 .

# 3. Push to registry
docker push myregistry/oceania-chatbot:1.0.0

# 4. Deploy
kubectl apply -f deployment.yaml
# (or use your deployment tool)

# 5. Verify
curl https://chatbot.yourdomain.com/health
```

---

## 📚 Resource Links

```bash
# OpenAI API Status
# https://status.openai.com/

# ChromaDB Documentation
# https://docs.trychroma.com/

# LangChain Docs
# https://python.langchain.com/

# Streamlit Docs
# https://docs.streamlit.io/

# FastAPI Docs
# https://fastapi.tiangolo.com/

# Docker Docs
# https://docs.docker.com/

# Check your API usage
# https://platform.openai.com/account/usage/overview
```

---

## 💡 Helpful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
alias oc-start='cd ~/oceanic_rag_chatbot && ./setup.sh full'
alias oc-web='streamlit run streamlit_app.py'
alias oc-cli='python rag_chatbot.py'
alias oc-api='python -m uvicorn api:app --reload'
alias oc-logs='tail -f logs/chatbot.log'
alias oc-clean='./setup.sh clean'
alias oc-test='curl http://localhost:8000/health'
```

Usage:
```bash
oc-start      # Start everything
oc-web        # Open web interface
oc-logs       # View logs
oc-test       # Test API
```

---

## 🆘 Emergency Commands

```bash
# Restart everything
pkill -f streamlit
pkill -f uvicorn
sleep 2
./setup.sh full

# Force stop Docker
docker-compose down -v
docker system prune -f
docker-compose up -d

# Reset to fresh start
git checkout -- .
rm -rf venv chroma_db extracted_images logs
./setup.sh full

# Check what's using port 8501
lsof -i :8501

# Kill process using port
kill -9 $(lsof -t -i:8501)
```

---

## 📖 Quick Reference

| Task | Command |
|------|---------|
| Setup | `./setup.sh full` |
| Web UI | `streamlit run streamlit_app.py` |
| CLI | `python rag_chatbot.py` |
| API | `python -m uvicorn api:app --reload` |
| Docker | `docker-compose up -d` |
| Logs | `tail -f logs/chatbot.log` |
| Test | `curl http://localhost:8000/health` |
| Clean | `./setup.sh clean` |
| Help | `./setup.sh help` |

---

**Save this file for quick reference!**
