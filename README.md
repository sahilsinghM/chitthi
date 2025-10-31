# Newsletter Engine

AI-powered Hinglish Newsletter Engine with multi-model support via OpenRouter, OpenAI, and Anthropic. Built with Agno (Phidata) Agent Development Kit.

## Quick Start

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file in `backend/`:
```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-your-key-here
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-key

# Optional (for fallback)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Run backend:
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:3000

## API Keys

**Required:** OpenRouter API key from https://openrouter.ai  
**Optional:** OpenAI and Anthropic keys for direct fallback access

## Features

✅ Multi-model support (OpenRouter, OpenAI, Anthropic)  
✅ Agno agents for orchestration (Draft, Content, Topic agents)  
✅ Automatic fallback between providers  
✅ Cost tracking and estimation  
✅ Draft generation with Hinglish support  
✅ Content ingestion with website reading tools  
✅ Topic prioritization with AI clustering  
✅ Supabase database integration with pgvector  
✅ Testing infrastructure

## Project Structure

```
chitthi/
├── backend/          # FastAPI server
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── agents/   # Agno agents (Draft, Content, Topic)
│   │   ├── models/   # Model providers
│   │   └── config/   # Config files
│   └── tests/        # Test suite
├── frontend/         # Next.js app
│   └── src/
│       ├── app/      # Pages
│       ├── components/  # React components
│       └── lib/      # Utilities
└── README.md
```

## Development

**Tests:**
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

**GitHub:**
```bash
git remote add origin https://github.com/YOUR_USERNAME/chitthi.git
git push -u origin main
```

## Supabase Setup

### Step 1: Get Credentials
1. Go to Supabase Dashboard: https://supabase.com/dashboard/project/chitthi
2. Settings → API
3. Copy **Project URL** and **anon/public key**

### Step 2: Add to .env
```bash
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-key-here
```

### Step 3: Run Database Migration
1. Supabase Dashboard → **SQL Editor** → **New Query**
2. Copy entire file: `supabase/migrations/001_init_schema.sql`
3. Paste and **Run**

This creates:
- ✅ 8 tables (content_items, embeddings, topics, drafts, versions, api_usage, analytics, model_configs)
- ✅ pgvector extension for embeddings
- ✅ Indexes and triggers

### Step 4: (Optional) Vector Search Function
Copy `supabase/functions/match_content_embeddings.sql` to SQL Editor and run for optimized vector search.

### Step 5: Test Connection
```bash
# Via API (backend must be running)
curl http://localhost:8000/api/db/test

# Or Python
cd backend && source venv/bin/activate
python -c "from app.db.client import get_supabase; print('✅ Connected')"
```

### Database Schema

**Tables:**
- `content_items` - URLs, files, extracted text
- `content_embeddings` - Vector embeddings (1536 dims, pgvector)
- `topics` - Newsletter topics with priority scores
- `drafts` - Newsletter drafts
- `draft_versions` - Version history
- `api_usage` - Cost tracking
- `model_configs` - Model configurations
- `analytics` - Newsletter performance metrics

**Troubleshooting:**
- "relation does not exist" → Run migration SQL
- Connection failed → Check `.env` has correct URL/key
- Vector search not working → Enable pgvector extension

## Pending Implementation

- Embedding generation and storage (vector search)
- Enhanced topic prioritization with database
- Phoenix evaluation integration
- Model comparison UI
- Cost tracking dashboard

## License

MIT License
