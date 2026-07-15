# 📚 API Documentation - Oceania RAG Chatbot

Complete REST API documentation for integrating the Oceania chatbot into external systems.

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication required for local deployments. For production, add Bearer token authentication.

---

## Endpoints

### 1. Health Check

**Endpoint**: `GET /health`

**Description**: Check if the chatbot is ready to use.

**Response**:
```json
{
  "status": "healthy",
  "chatbot": "ready"
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

---

### 2. Single Chat Query

**Endpoint**: `POST /chat`

**Description**: Send a query and get an answer with sources.

**Request Body**:
```json
{
  "query": "What are your granite products?",
  "include_sources": true
}
```

**Response**:
```json
{
  "answer": "We offer premium granite slabs with various finishes...",
  "sources": [
    "granite_slab_cut_to_size_catalog.pdf (Page 1)",
    "website - products page"
  ],
  "images": [
    "./extracted_images/granite_slab_p1_img1.png"
  ],
  "retrieved_chunks": 5
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about quartz products",
    "include_sources": true
  }'
```

---

### 3. Batch Chat

**Endpoint**: `POST /batch-chat`

**Description**: Process multiple queries at once.

**Request Body**:
```json
{
  "queries": [
    "What's your pricing?",
    "Do you have certifications?",
    "Custom solutions available?"
  ]
}
```

**Response**:
```json
[
  {
    "answer": "Pricing varies...",
    "sources": ["quote_sheet.pdf"],
    "images": [],
    "retrieved_chunks": 5
  },
  {
    "answer": "Yes, we have QC certifications...",
    "sources": ["qc_report.pdf"],
    "images": [],
    "retrieved_chunks": 3
  },
  {
    "answer": "We offer custom solutions...",
    "sources": ["website - solutions"],
    "images": [],
    "retrieved_chunks": 4
  }
]
```

**Example**:
```bash
curl -X POST http://localhost:8000/batch-chat \
  -H "Content-Type: application/json" \
  -d '{
    "queries": ["pricing?", "certifications?"]
  }'
```

---

### 4. Get Conversation History

**Endpoint**: `GET /history`

**Description**: Retrieve the current conversation history.

**Response**:
```json
{
  "history": [
    {
      "role": "user",
      "content": "What are your products?"
    },
    {
      "role": "assistant",
      "content": "We offer granite and quartz products..."
    },
    {
      "role": "user",
      "content": "What's the pricing?"
    },
    {
      "role": "assistant",
      "content": "Pricing varies by product..."
    }
  ]
}
```

**Example**:
```bash
curl http://localhost:8000/history
```

---

### 5. Clear Conversation History

**Endpoint**: `POST /clear-history`

**Description**: Clear all conversation history.

**Response**:
```json
{
  "status": "success",
  "message": "History cleared"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/clear-history
```

---

### 6. Get Retrieval Details

**Endpoint**: `GET /retrieval-details/{query}`

**Description**: Get detailed information about what documents were retrieved for a query.

**Response**:
```json
{
  "query": "granite products",
  "num_retrieved": 5,
  "documents": [
    {
      "rank": 1,
      "source": "granite_slab_cut_to_size_catalog.pdf (Page 1)",
      "source_type": "pdf_text",
      "preview": "Our granite slabs offer premium quality with various finishes including..."
    },
    {
      "rank": 2,
      "source": "website - products page",
      "source_type": "website",
      "preview": "Premium granite and quartz solutions for residential and commercial..."
    }
  ]
}
```

**Example**:
```bash
curl 'http://localhost:8000/retrieval-details/granite%20products'
```

---

### 7. WebSocket Chat (Streaming)

**Endpoint**: `WS /ws/chat`

**Description**: Real-time streaming chat with token-by-token responses.

**Protocol**: WebSocket

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = function(event) {
  // Send query
  ws.send(JSON.stringify({
    query: "Tell me about your products"
  }));
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  if (data.type === 'token') {
    console.log('Token:', data.content);
  } else if (data.type === 'complete') {
    console.log('Complete response:', data.content);
  }
};

ws.onerror = function(error) {
  console.error('WebSocket error:', error);
};
```

---

## Error Responses

### 503 Chatbot Not Initialized
```json
{
  "detail": "Chatbot not initialized"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message describing what went wrong"
}
```

### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

---

## Python Examples

### Using requests library

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Single query
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "query": "What are your products?",
        "include_sources": True
    }
)
print(json.dumps(response.json(), indent=2))

# Batch queries
batch_response = requests.post(
    f"{BASE_URL}/batch-chat",
    json={
        "queries": ["pricing?", "certifications?"]
    }
)
print(json.dumps(batch_response.json(), indent=2))

# Get history
history = requests.get(f"{BASE_URL}/history")
print(json.dumps(history.json(), indent=2))

# Clear history
requests.post(f"{BASE_URL}/clear-history")

# Retrieval details
details = requests.get(f"{BASE_URL}/retrieval-details/granite")
print(json.dumps(details.json(), indent=2))
```

---

## JavaScript Examples

### Using fetch API

```javascript
const BASE_URL = 'http://localhost:8000';

// Single query
async function chat(query) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      include_sources: true
    })
  });
  return response.json();
}

// Batch queries
async function batchChat(queries) {
  const response = await fetch(`${BASE_URL}/batch-chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ queries })
  });
  return response.json();
}

// Get history
async function getHistory() {
  const response = await fetch(`${BASE_URL}/history`);
  return response.json();
}

// Usage
(async () => {
  const result = await chat('What are your products?');
  console.log(result);
})();
```

---

## cURL Examples

### Basic Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are your products?",
    "include_sources": true
  }'
```

### Batch Processing
```bash
curl -X POST http://localhost:8000/batch-chat \
  -H "Content-Type: application/json" \
  -d '{
    "queries": ["pricing", "quality", "delivery"]
  }'
```

### Get History
```bash
curl http://localhost:8000/history
```

### Retrieval Debug
```bash
curl 'http://localhost:8000/retrieval-details/granite%20slabs'
```

---

## Response Headers

All responses include:

```
Content-Type: application/json
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

## Rate Limiting

Currently no rate limiting. For production, consider implementing:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: ChatRequest):
    # ...
```

---

## Authentication (Optional)

Add Bearer token authentication:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return credentials

@app.post("/chat")
async def chat(request: ChatRequest, token = Depends(verify_token)):
    # ...
```

---

## CORS Configuration

Enable CORS for your domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Optimization

### Caching Responses

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cache_response(query: str):
    # Cache responses for identical queries
    return chatbot.chat(query)
```

### Connection Pooling

```python
import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.post(url, json=data) as resp:
        return await resp.json()
```

---

## Monitoring

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

request_count = Counter(
    'chatbot_requests_total',
    'Total requests',
    ['endpoint']
)

response_time = Histogram(
    'chatbot_response_seconds',
    'Response time'
)
```

---

## Testing

### Using pytest

```python
import pytest
from httpx import AsyncClient
from api import app

@pytest.mark.asyncio
async def test_chat():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat",
            json={"query": "test", "include_sources": True}
        )
        assert response.status_code == 200
        assert "answer" in response.json()

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
```

---

## Deployment

Run API in production:

```bash
# Install uvicorn
pip install uvicorn

# Run with workers
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# With auto-reload for development
uvicorn api:app --reload --port 8000
```

---

## Interactive Documentation

Once running, access Swagger UI:

```
http://localhost:8000/docs
```

Or ReDoc:

```
http://localhost:8000/redoc
```

---

**API Version**: 1.0.0
**Last Updated**: December 2024
