# Setup Guide

## Quick Start

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENAI_API_KEY=sk-your-key-here  # Optional
ANTHROPIC_API_KEY=sk-ant-your-key-here  # Optional
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

Visit `http://localhost:3000`

## Getting API Keys

### OpenRouter (Required)
1. Go to https://openrouter.ai
2. Sign up for free account
3. Get API key from dashboard
4. Add to `.env` as `OPENROUTER_API_KEY`

### OpenAI (Optional - for fallback)
1. Go to https://platform.openai.com
2. Create API key
3. Add to `.env` as `OPENAI_API_KEY`

### Anthropic (Optional - for fallback)
1. Go to https://console.anthropic.com
2. Create API key
3. Add to `.env` as `ANTHROPIC_API_KEY`

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Troubleshooting

### Backend won't start
- Check Python version (3.11+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check `.env` file exists and has API keys

### Frontend won't connect to backend
- Verify backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Verify `next.config.js` rewrites are correct

### Models not loading
- Verify OpenRouter API key is correct
- Check backend logs for errors
- Test API directly: `curl http://localhost:8000/api/models/`

## Next Steps

After setup works:
1. Test model generation
2. Configure Supabase (see plan)
3. Add content ingestion
4. Set up Phoenix for evaluations

