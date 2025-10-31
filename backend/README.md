# AI Supervisor System - Phase 1

Human-in-the-loop AI agent system for salon customer service. When the AI doesn't know an answer, it escalates to a human supervisor, follows up with the customer, and updates its knowledge base automatically.

## 🏗️ Architecture Overview

### System Flow
```
Customer Call → AI Agent (LiveKit) → Knowledge Base Check
                    ↓
            Knows Answer? 
         Yes ↓         ↓ No
    Respond Directly   Create Help Request
                            ↓
                    Notify Supervisor
                            ↓
                    Supervisor Responds
                            ↓
                    1. Notify Customer
                    2. Update Knowledge Base
```

### Tech Stack
- **AI**: Lightning AI (GPT-4)
- **Voice Agent**: LiveKit
- **Database**: Firebase Realtime Database
- **API**: FastAPI
- **Language**: Python 3.9+

## 📁 Project Structure

```
ai-supervisor-backend/
├── src/
│   ├── config/          # Settings & Firebase initialization
│   ├── models/          # Data models (HelpRequest, KnowledgeEntry)
│   ├── services/        # Business logic layer
│   ├── agents/          # LiveKit agent & prompts
│   ├── api/            # FastAPI routes
│   ├── database/       # Firebase client wrapper
│   └── utils/          # Logging, validators
├── scripts/            # Seeding & cleanup scripts
├── tests/              # Unit tests
├── .env               # Environment variables (NOT in git)
└── run.py             # Entry point
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher
- Firebase account
- Lightning AI API key
- LiveKit account

### 2. Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project: "ai-supervisor-db"
3. Enable **Realtime Database**
4. Download service account credentials:
   - Project Settings → Service Accounts → Generate New Private Key
   - Save as `firebase-credentials.json` in project root

### 3. Environment Configuration
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Update these values:
```bash
LIGHTNING_AI_API_KEY=your_lightning_api_key
LIVEKIT_URL=wss://ai-supervisor-demo-lpazizzu.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_secret
FIREBASE_DATABASE_URL=https://ai-supervisor-db-default-rtdb.asia-southeast1.firebasedatabase.app
```

### 4. Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Seed Initial Data
```bash
# Populate knowledge base with salon information
python scripts/seed_knowledge.py
```

### 6. Run the API Server
```bash
# Start FastAPI backend
python run.py
```

API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 7. Run the LiveKit Agent (Separate Terminal)
```bash
# Start the AI agent
python -m src.agents.salon_agent
```

## 🔑 Key Design Decisions

### 1. Help Request Lifecycle
```
PENDING → RESOLVED (supervisor answered)
       → TIMEOUT (no response in 1 hour)
```

**Database Schema:**
```json
{
  "request_id": "uuid",
  "customer_phone": "+1234567890",
  "question": "Do you have parking?",
  "status": "pending|resolved|timeout",
  "supervisor_answer": "Yes, free parking available",
  "created_at": "ISO datetime",
  "timeout_at": "ISO datetime",
  "customer_notified": true
}
```

### 2. Knowledge Base Structure
```json
{
  "entry_id": "uuid",
  "question": "What are your hours?",
  "answer": "Mon-Fri 9AM-8PM...",
  "category": "hours",
  "keywords": ["hours", "open", "timing"],
  "times_used": 15,
  "source_request_id": "linked_help_request"
}
```

**Retrieval Strategy:**
- Keyword-based search (Phase 1)
- Can upgrade to semantic search with embeddings (Phase 2)

### 3. Supervisor Notification
Currently simulated via **console logs** with structured format:
```
📞 SUPERVISOR NOTIFICATION
Customer: +1234567890
Question: Do you have vegan hair products?
Request ID: abc-123
```

**Production-ready hooks** for:
- SMS via Twilio
- Webhook to Slack/Teams
- Email notifications

### 4. Customer Follow-up
When supervisor responds:
1. Update help request → RESOLVED
2. Notify customer (simulated text)
3. Add Q&A to knowledge base
4. Link knowledge entry to source request

### 5. Scaling Considerations

**10 requests/day → 1,000 requests/day:**

| Component | Current | At Scale |
|-----------|---------|----------|
| Database | Firebase (NoSQL) | ✅ Can handle, add indexes |
| Knowledge Search | Linear scan | → Vector embeddings + Pinecone |
| Notifications | Synchronous | → Message queue (Redis/SQS) |
| Timeout Checks | Manual endpoint | → Cron job (AWS Lambda) |
| Agent Instances | Single | → Horizontal scaling (K8s) |

**Code is modular** - swap implementations without changing business logic.

## 📡 API Endpoints

### Help Requests
```
POST   /api/help-requests              Create new help request
GET    /api/help-requests              Get all requests (filterable)
GET    /api/help-requests/{id}         Get specific request
POST   /api/help-requests/check-timeouts  Trigger timeout check
```

### Supervisor Actions
```
POST   /api/supervisor/{id}/resolve    Resolve help request
GET    /api/supervisor/dashboard/stats Get dashboard statistics
```

### Knowledge Base
```
GET    /api/knowledge                  Get all knowledge
GET    /api/knowledge/search?query=    Search knowledge
POST   /api/knowledge                  Add manual entry
GET    /api/knowledge/{id}             Get specific entry
```

## 🧪 Testing

### Manual Testing
```bash
# 1. Start API server
python run.py

# 2. Create a help request
curl -X POST http://localhost:8000/api/help-requests \
  -H "Content-Type: application/json" \
  -d '{
    "customer_phone": "+1234567890",
    "question": "Do you offer bridal packages?",
    "context": "Planning wedding in June"
  }'

# 3. Get pending requests
curl http://localhost:8000/api/help-requests?status=pending

# 4. Resolve as supervisor
curl -X POST http://localhost:8000/api/supervisor/{request_id}/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "supervisor_answer": "Yes! We offer bridal packages starting at $500.",
    "supervisor_id": "supervisor_1"
  }'

# 5. Verify knowledge base updated
curl http://localhost:8000/api/knowledge
```

### Unit Tests
```bash
pytest tests/
```

## 📊 Monitoring & Logs

Structured JSON logging:
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Help request created: abc-123",
  "request_id": "abc-123"
}
```

View logs:
```bash
# Follow logs in real-time
tail -f logs/app.log

# Search for specific request
grep "abc-123" logs/app.log
```

## 🔄 Scheduled Tasks

### Timeout Checker (Run via Cron)
```bash
# Add to crontab: Check every 15 minutes
*/15 * * * * cd /path/to/project && python scripts/cleanup_old_requests.py
```

## 🚧 What's Next (Phase 2)

1. **Live Call Transfer**
   - If supervisor available during call → transfer directly
   - If not → fallback to text-based flow

2. **Improved Search**
   - Semantic search with embeddings
   - Learn from conversation patterns

3. **Real Integrations**
   - Twilio for SMS
   - Slack/Teams webhooks
   - Calendar integration

4. **Analytics Dashboard**
   - Response time metrics
   - Most escalated questions
   - Supervisor performance

## 🐛 Troubleshooting

### Firebase Connection Issues
```bash
# Verify credentials file exists
ls firebase-credentials.json

# Check database URL in .env
echo $FIREBASE_DATABASE_URL
```

### LiveKit Agent Not Starting
```bash
# Verify LiveKit credentials
echo $LIVEKIT_API_KEY
echo $LIVEKIT_API_SECRET

# Test connection
curl -X GET $LIVEKIT_URL
```

### API Errors
```bash
# Check logs
tail -f logs/app.log

# Verify all services running
ps aux | grep python
```

## 📝 License
MIT

## 👥 Authors
Your Name - AI Supervisor System

---

**Note**: This is Phase 1 - focused on core functionality and clean architecture. All notification mechanisms are currently simulated for demonstration. Production deployment would require real SMS/webhook integrations.