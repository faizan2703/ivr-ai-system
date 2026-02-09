# IVR AI Agent System - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure OpenAI API
```bash
# Edit .env file with your OpenAI API key
# Get key from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Start Backend
```bash
python backend/main.py
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
✓ RAG service initialized
✓ Call manager initialized
✓ Agent AI service initialized
✓ All services initialized successfully
INFO:     Application startup complete [0.00s]
```

### Step 4: Open Frontend
Open `frontend/index.html` in your browser (or serve with a web server)

### Step 5: Test the System

1. **Go to "Make Call"**
   - Name: Test User
   - Phone: +1234567890
   - Topic: Billing Inquiry
   - Click "Initiate Call"

2. **Add Sample Documents**
   - Go to "Knowledge Base"
   - Click "Add Document"
   - Add sample FAQ content
   - Search to verify

3. **Send Test Message**
   - Type in chat box
   - See AI response
   - Check intent detection

## API Testing

### Using curl

```bash
# Check Health
curl http://localhost:8000/api/v1/health

# Initiate Call
curl -X POST http://localhost:8000/api/v1/calls/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "John Doe",
    "user_phone": "+1234567890",
    "call_topic": "billing"
  }'

# Send Message (replace CALL_ID with actual call id)
curl -X POST http://localhost:8000/api/v1/conversations/message \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "CALL_ID",
    "message": "I want to check my bill"
  }'

# Add Document
curl -X POST http://localhost:8000/api/v1/knowledge/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Billing FAQ",
    "content": "Q: How do I check my bill? A: Visit the billing section...",
    "category": "billing",
    "tags": ["faq", "billing"]
  }'

# Search Knowledge Base
curl -X POST http://localhost:8000/api/v1/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to check bill",
    "top_k": 3
  }'
```

### Using Postman
1. Import endpoints from API docs: `http://localhost:8000/docs`
2. Create collection "IVR System"
3. Test each endpoint


## Docker Quick Start

```bash
# Build and run
docker-compose up --build

# Access
# Backend: http://localhost:8000
# Frontend: http://localhost:8080
# API Docs: http://localhost:8000/docs
```

## Troubleshooting

### ImportError: No module named 'openai'
```bash
pip install -r requirements.txt
```

### ConnectionError: Cannot connect to backend
- Ensure backend is running on port 8000
- Update API Endpoint in Settings
- Check firewall settings

### OPENAI_API_KEY not found
- Copy `.env.example` to `.env`
- Add your actual OpenAI API key
- Restart backend

### Frontend shows "Offline"
- Check if backend is running
- Verify CORS is enabled
- Try incognito mode (clear cache)

## Sample Knowledge Base Content

Create these documents in the Knowledge Base:

### Document 1: Billing FAQ
```
Title: How to Check Your Bill
Content: To check your bill, log into your account and navigate to the Billing section. 
You can view your current balance, recent charges, and payment history. 
Bills are typically issued on the first day of each month.
```

### Document 2: Technical Support
```
Title: Common Technical Issues
Content: If you experience connection problems, try these steps:
1. Restart your device
2. Clear browser cache
3. Check your internet connection
4. Disable browser extensions
5. Try a different browser
If issues persist, please contact technical support.
```

### Document 3: Account Management
```
Title: Account Security
Content: Keep your account secure by:
- Using a strong password (minimum 12 characters)
- Enabling two-factor authentication
- Not sharing your credentials
- Logging out when using shared devices
- Regularly updating your security settings
```

## Next Steps

1. **Customize Knowledge Base**
   - Add your actual FAQ documents
   - Organize by categories
   - Test searches

2. **Adjust AI Model**
   - Change OPENAI_MODEL in `.env`
   - Adjust temperature for creativity
   - Test with different prompts

3. **Implement Phone Integration** (Optional)
   - Add Twilio credentials
   - Connect to phone service
   - Test with real phone calls

4. **Deploy to Production**
   - Use Docker for consistency
   - Set up SSL/TLS
   - Configure proper logging
   - Set up monitoring

## Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- OpenAI API: https://platform.openai.com/docs
- LangChain: https://python.langchain.com
- Chroma: https://www.trychroma.com

---

**You're all set! 🚀**
