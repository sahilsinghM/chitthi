# Newsletter Engine

AI-powered Hinglish Newsletter Engine with multi-model support via OpenRouter.

## Architecture

- **Backend**: FastAPI (Python) with OpenRouter, OpenAI, and Anthropic model support
- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, and shadcn/ui
- **Database**: Supabase (PostgreSQL with pgvector) - to be configured
- **Testing**: pytest (backend), Vitest (frontend)
- **Evaluation**: Phoenix (Arize AI) for LLM evaluation

## Setup

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Run backend:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

## API Keys Required

1. **OpenRouter** (Primary): Get from https://openrouter.ai
2. **OpenAI** (Fallback): Optional, for direct OpenAI access
3. **Anthropic** (Fallback): Optional, for direct Claude access
4. **Supabase**: To be configured later

## Features

- ✅ Multi-model support (OpenRouter, OpenAI, Anthropic)
- ✅ Automatic fallback between providers
- ✅ Cost tracking and estimation
- ✅ Model comparison
- ✅ Draft generation with Hinglish support
- ✅ Testing infrastructure
- ⏳ Content ingestion (in progress)
- ⏳ Vector search with embeddings (in progress)
- ⏳ Topic prioritization (in progress)
- ⏳ Phoenix evaluation integration (in progress)

## Project Structure

```
chitthi/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── models/       # Model providers
│   │   └── config/       # Configuration files
│   ├── tests/            # Test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   └── package.json
└── README.md
```

## Development

### Running Tests

Backend:
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm test
```

## Deployment

### GitHub Setup

1. Create a new repository on GitHub
2. Push code:
```bash
git remote add origin https://github.com/yourusername/chitthi.git
git branch -M main
git push -u origin main
```

### Environment Variables

Add these secrets to GitHub (Settings > Secrets):
- `OPENROUTER_API_KEY` (required)
- `OPENAI_API_KEY` (optional)
- `ANTHROPIC_API_KEY` (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Next Steps

See the plan file for detailed implementation roadmap.

