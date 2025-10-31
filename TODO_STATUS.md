# Todo Status - Newsletter Engine

## ✅ Completed

- [x] Initialize project structure (FastAPI + Next.js)
- [x] Create unified model abstraction layer (OpenRouter, OpenAI, Anthropic)
- [x] Create models.yaml configuration file
- [x] Implement OpenRouter API client
- [x] Implement direct OpenAI and Anthropic SDK clients as fallbacks
- [x] Build model registry system
- [x] Create API endpoints (/api/models, /api/drafts/generate, /api/models/costs)
- [x] Set up Supabase database schema with pgvector
- [x] Build React model selector component
- [x] Add automatic fallback from OpenRouter to direct APIs
- [x] Build content ingestion layer with Agno agents
- [x] Integrate Agno (Phidata) Agent Development Kit
- [x] Set up testing infrastructure (pytest + Vitest)
- [x] Set up LLM evaluation framework (Phoenix installed)

## 🔄 In Progress

- [ ] Test Supabase connection (add keys to .env and run migration)

## ⏳ Pending

- [ ] Implement embedding generation and storage (vector search)
- [ ] Implement API usage tracking and cost estimation dashboard
- [ ] Enhanced topic prioritization with database integration
- [ ] Phoenix evaluation integration and test suite
- [ ] Model comparison UI (side-by-side comparison)
- [ ] Draft versioning UI (view/edit versions)
- [ ] Cost tracking dashboard
- [ ] Draft saving to database
- [ ] Vector search implementation for content discovery

## 📝 Notes

- Supabase keys need to be in `backend/.env`
- Run migration SQL in Supabase SQL Editor
- Backend must be running to test via API: `GET /api/db/test`



