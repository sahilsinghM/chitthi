# Cost-Optimized Mobile Architecture

## Requirements
- ✅ Minimize cost
- ✅ Do it right (proper architecture)
- ✅ Run in browser on phone (mobile-responsive)
- ✅ Complete workflow accessible from mobile

## Architecture Decision: Next.js Full-Stack on Vercel

**Why this approach:**
- Single codebase (TypeScript everywhere)
- Serverless functions = pay only for usage
- Vercel free tier (generous)
- Supabase free tier (generous)
- Mobile-responsive React components
- Zero infrastructure management

---

## Tech Stack (Cost-Optimized)

### Frontend + Backend
- **Next.js 14** (App Router) - Full-stack framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling (lightweight)
- **shadcn/ui** - Components (can use mobile-optimized versions)
- **React Hook Form** - Form handling
- **Zustand** - State management (lightweight)

### Backend Services
- **Vercel Serverless Functions** - API routes (free tier)
- **Supabase** - Database + pgvector + storage (free tier)
- **LiteLLM** - Unified model switching (Python via API or JS port)

### AI/ML
- **OpenAI API** - GPT-4 Turbo (cheaper than GPT-4)
- **Anthropic API** - Claude 3 Haiku (cheapest Claude)
- **Ollama** - Open-source models (free, if self-hosted or cloud)
- **OpenAI Embeddings** - text-embedding-3-small (cheapest)

### Content Processing
- **@mozilla/readability** (JS) - Article extraction
- **pdf.js** (browser) - PDF parsing
- **youtube-transcript** (npm) - Video transcripts

---

## Cost Breakdown (Monthly)

### Tier 1: Free Tier Usage (Optimistic)
**Scenario:** 1 newsletter/week, minimal content processing

| Service | Free Tier | Usage | Cost |
|---------|-----------|-------|------|
| Vercel | 100GB bandwidth | ~10GB | $0 |
| Supabase | 500MB DB, 1GB storage | ~100MB | $0 |
| OpenAI API | Embeddings + drafts | ~50k tokens/week | $2-5 |
| Anthropic API | Model switching | ~10k tokens/week | $0.10-0.50 |
| **Total** | | | **$2-6/month** |

### Tier 2: Moderate Usage (Realistic)
**Scenario:** 1 newsletter/week, 10-20 content items/week, some experimentation

| Service | Usage | Cost |
|---------|-------|------|
| Vercel | 50GB bandwidth (within free) | $0 |
| Supabase | 200MB DB, 500MB storage (within free) | $0 |
| OpenAI API | ~200k tokens/week (embeddings + drafts) | $8-15 |
| Anthropic API | ~50k tokens/week | $0.50-2 |
| Optional: Supabase Pro | If exceed free tier | $25 |
| **Total** | | **$8-17/month** |

### Tier 3: Heavy Usage (With Supabase Pro)
**Scenario:** Multiple newsletters, lots of content, model comparisons

| Service | Usage | Cost |
|---------|-------|------|
| Vercel Pro | Unlimited bandwidth | $20 |
| Supabase Pro | 8GB DB, 100GB storage | $25 |
| OpenAI API | ~500k tokens/week | $20-40 |
| Anthropic API | ~100k tokens/week | $1-4 |
| **Total** | | **$66-89/month** |

---

## Cost Optimization Strategies

### 1. **Smart Embedding Caching**
```typescript
// Only generate embeddings once per URL
// Store in database, reuse forever
- Check if URL exists before generating embedding
- Cache embeddings in Supabase
- Estimated savings: 60-80% of embedding costs
```

### 2. **Model Selection Strategy**
```typescript
// Use cheaper models for different tasks:
- Embeddings: text-embedding-3-small ($0.02/1M tokens)
- Draft generation: GPT-4 Turbo ($10/1M tokens) or Claude Haiku ($0.25/1M)
- QA/Review: Claude Haiku (cheaper than GPT-4)
- Model switching UI: Let user choose (don't run parallel)
```

### 3. **Token Optimization**
```typescript
// Reduce prompt sizes:
- Summarize content before embedding
- Use concise prompts
- Cache context in database
- Estimated savings: 30-50% token usage
```

### 4. **Batch Processing**
```typescript
// Process multiple items in one API call when possible
- Batch embeddings (OpenAI supports up to 2048 items)
- Combine similar operations
- Estimated savings: 20-30% API overhead
```

### 5. **Smart Vector Search**
```typescript
// Use Supabase pgvector efficiently:
- Index properly
- Limit search results
- Cache frequent queries
```

### 6. **Serverless = Pay Only for Usage**
```typescript
// No always-on server costs:
- Vercel free tier: 100GB bandwidth/month
- Supabase free tier: 500MB DB, 1GB file storage
- Only pay for API calls you make
```

---

## Architecture Details

### Project Structure
```
chitthi/
├── app/                          # Next.js App Router
│   ├── (mobile)/                 # Mobile-optimized routes
│   │   ├── ingest/              # Content input page
│   │   ├── topics/              # Topic selection
│   │   ├── drafts/              # Draft generation
│   │   ├── edit/[id]/          # Draft editing
│   │   └── qa/[id]/            # Quality check
│   ├── api/                      # API routes (serverless)
│   │   ├── content/             # Content ingestion
│   │   ├── embeddings/          # Vector operations
│   │   ├── topics/              # Topic clustering
│   │   ├── drafts/              # Draft generation
│   │   └── models/              # Model switching
│   └── layout.tsx               # Root layout
├── components/                   # React components
│   ├── ui/                      # shadcn components
│   ├── mobile/                  # Mobile-specific components
│   └── shared/                  # Shared components
├── lib/                          # Utilities
│   ├── ai/                      # AI client (LiteLLM-like)
│   ├── db/                      # Supabase client
│   ├── embeddings/              # Embedding utilities
│   └── content/                 # Content extraction
├── supabase/                     # Supabase config
│   └── migrations/              # DB migrations
├── public/                       # Static assets
└── package.json
```

### Database Schema (Supabase)
```sql
-- Content storage
CREATE TABLE content_items (
  id UUID PRIMARY KEY,
  url TEXT UNIQUE,
  file_path TEXT,
  extracted_text TEXT,
  summary TEXT,  -- Cache summary to reduce tokens
  tags TEXT[],
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

-- Embeddings (pgvector)
CREATE TABLE content_embeddings (
  id UUID PRIMARY KEY,
  content_id UUID REFERENCES content_items(id),
  embedding vector(1536),  -- OpenAI small model
  model_used TEXT,
  created_at TIMESTAMPTZ
);

CREATE INDEX ON content_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Topics
CREATE TABLE topics (
  id UUID PRIMARY KEY,
  title TEXT,
  description TEXT,
  priority_score FLOAT,
  tags TEXT[],
  created_at TIMESTAMPTZ
);

-- Drafts
CREATE TABLE drafts (
  id UUID PRIMARY KEY,
  topic_id UUID REFERENCES topics(id),
  title TEXT,
  content TEXT,
  version INTEGER DEFAULT 1,
  status TEXT,  -- 'draft', 'reviewing', 'final'
  model_used TEXT,
  prompt_used TEXT,  -- Store for regeneration
  created_at TIMESTAMPTZ
);

-- Draft versions (for history)
CREATE TABLE draft_versions (
  id UUID PRIMARY KEY,
  draft_id UUID REFERENCES drafts(id),
  version_number INTEGER,
  content TEXT,
  changes_summary TEXT,
  created_at TIMESTAMPTZ
);

-- Model configs
CREATE TABLE model_configs (
  id UUID PRIMARY KEY,
  provider TEXT,  -- 'openai', 'anthropic', 'ollama'
  model_name TEXT,
  api_key_encrypted TEXT,  -- Encrypt in Supabase Vault
  is_active BOOLEAN,
  cost_per_1k_tokens FLOAT,
  created_at TIMESTAMPTZ
);
```

### Mobile-First Features

1. **Touch-Optimized UI**
   - Large tap targets
   - Swipe gestures for draft navigation
   - Pull-to-refresh
   - Bottom sheet modals

2. **Offline Support (Progressive Web App)**
   - Cache drafts locally
   - Queue content ingestion
   - Sync when online

3. **Responsive Design**
   - Mobile-first breakpoints
   - Collapsible sidebar
   - Stack layout on mobile
   - Optimized images

---

## API Cost Estimation (Detailed)

### Content Ingestion (per item)
- URL extraction: $0 (serverless function)
- Embedding generation: ~800 tokens = $0.016 (once, cached)
- Summary generation: ~500 tokens = $0.005 (GPT-4 Turbo)
- **Total per item: $0.021**

### Topic Prioritization (weekly)
- Clustering: ~2000 tokens = $0.02 (GPT-4 Turbo)
- Ranking: ~1500 tokens = $0.015
- **Total: $0.035/week**

### Draft Generation (per draft)
- Context retrieval: $0 (vector search in Supabase)
- Draft generation: ~3000 tokens = $0.03 (GPT-4 Turbo)
- Headline suggestions: ~1000 tokens = $0.01
- **Total: $0.04/draft**

### QA Check (per draft)
- Quality analysis: ~2000 tokens = $0.005 (Claude Haiku, cheaper)
- **Total: $0.005/draft**

### Weekly Cost Estimate
- 20 content items: 20 × $0.021 = $0.42
- Topic prioritization: $0.035
- 1 draft generation: $0.04
- 1 QA check: $0.005
- **Total: ~$0.50/week = $2/month**

---

## Implementation Phases

### Phase 1: Core MVP (Week 1-2)
**Goal:** Get one newsletter generated end-to-end

**Features:**
- Content ingestion form (mobile-optimized)
- Basic embedding & storage
- Simple topic selection
- Draft generation (single model)
- Markdown editor with preview
- Manual publishing (copy button)

**Cost:** ~$2-5/month

### Phase 2: Enhancements (Week 3-4)
**Goal:** Add quality features

**Features:**
- Model switching dropdown
- QA checks
- Version history
- Better mobile UI
- Offline support

**Cost:** ~$5-10/month

### Phase 3: Optimization (Week 5+)
**Goal:** Cost optimization + advanced features

**Features:**
- Embedding caching
- Batch processing
- Advanced analytics
- Model comparison (optional)
- Automated workflows

**Cost:** ~$10-20/month (with optimizations)

---

## Key Decisions for Cost Optimization

1. **Use Next.js instead of separate React + FastAPI**
   - Single codebase = easier deployment
   - Serverless = no server costs
   - Free Vercel tier generous

2. **Supabase for everything**
   - Database + storage + auth in one
   - Free tier covers MVP
   - pgvector included

3. **Smart caching strategy**
   - Cache embeddings (biggest cost saver)
   - Cache summaries
   - Cache prompt results when possible

4. **Model selection**
   - GPT-4 Turbo for drafts (cheaper than GPT-4)
   - Claude Haiku for QA (cheapest Claude)
   - text-embedding-3-small for embeddings (cheapest)

5. **Avoid parallel model calls**
   - Single model selection
   - User chooses, generates once
   - Comparison feature optional (costs more)

---

## Cost Monitoring

### Built-in Cost Tracking
```typescript
// Track API costs in database
CREATE TABLE api_usage (
  id UUID PRIMARY KEY,
  provider TEXT,
  model TEXT,
  tokens_used INTEGER,
  cost FLOAT,
  operation_type TEXT,  -- 'embedding', 'draft', 'qa'
  created_at TIMESTAMPTZ
);

// Show cost dashboard in UI
- Daily/weekly/monthly spend
- Cost per operation
- Projections
```

---

## Final Cost Estimate

### Conservative (Most Likely)
- **$5-15/month** for moderate usage
- Includes: 1-2 newsletters/week, 10-30 content items
- Free tier services for hosting/database

### Optimistic (Light Usage)
- **$2-6/month** if you're careful with caching
- Minimal content processing
- Reuse embeddings aggressively

### Heavy Usage
- **$20-40/month** if you process lots of content
- Multiple model comparisons
- Might need Supabase Pro

---

## Migration Path

If costs get too high:
1. Self-host Ollama for free models
2. Use cheaper embeddings (sentence-transformers)
3. Reduce draft generation frequency
4. Move to Supabase Pro only if needed

---

## Recommendation

**Go with Next.js + Supabase architecture:**
- ✅ Mobile-friendly (React, responsive)
- ✅ Cost-optimized (serverless, caching)
- ✅ Proper architecture (scalable, maintainable)
- ✅ Low initial cost ($2-15/month)
- ✅ Can scale up when needed

**Start with MVP features, add optimizations incrementally.**

