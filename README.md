# agent-scaffold

A RACV customer-support chatbot proof-of-concept: a FastAPI backend running a
LangChain tool-calling agent (OpenAI) that answers questions grounded in
RACV's official Help & Support content via hybrid (semantic + keyword)
search, plus a deterministic pricing lookup tool, with a Next.js/TypeScript
frontend with streaming responses.

## Stack

- **Backend**: FastAPI, Pydantic, LangChain (`langchain.agents.create_agent`,
  LangGraph under the hood), OpenAI via `langchain-openai` (chat +
  embeddings), Supabase Postgres (pgvector + full-text search, fused via a
  documented RRF SQL function) for the retrieval index and pricing table,
  SQLite for agent/thread memory (`langgraph-checkpoint-sqlite`).
- **Frontend**: Next.js 16 (App Router), TypeScript, Tailwind CSS,
  `react-markdown` for rendering assistant responses (including citation
  links).
- **Package management**: `uv` (backend), `npm` (frontend).

## Getting started

### 1. Supabase setup (one-time)

Create a [Supabase](https://supabase.com) project, then run
`backend/supabase/schema.sql` in its SQL editor. This creates the
`documents`/`pricing` tables, the `hybrid_search` RPC function, and seeds the
mock pricing dataset.

### 2. Backend

```bash
cd backend
cp .env.example .env   # fill in OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY
uv sync
uv sync --group ingest
uv run python -m scripts.ingest   # populate Supabase from the 11 RACV pages
uv run uvicorn app.main:app --reload
```

Runs on http://localhost:8000.

### 3. Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Runs on http://localhost:3000.

## Project layout

```
backend/
  app/
    main.py              # FastAPI app, CORS, route registration
    config.py             # pydantic-settings, reads .env
    agent.py               # builds the LangChain agent, RACV system prompt, sqlite-backed thread memory
    tools.py               # search_help_center (hybrid RAG) + get_pricing (deterministic) tools
    supabase_client.py     # supabase-py client singleton
    db.py                   # sqlite connection + langgraph SqliteSaver checkpointer (/tmp on Vercel)
    models.py               # pydantic request/response models
    routes/
      chat.py                # POST /api/chat, POST /api/chat/stream, GET /api/chat/{session_id}/history
  scripts/
    ingest.py               # one-time/developer-run: fetch RACV pages, chunk, embed, upsert to Supabase
  supabase/
    schema.sql               # documents/pricing tables + hybrid_search RPC -- run once via SQL editor
  tests/                     # pytest
frontend/
  app/
    page.tsx                 # chat UI (client component)
    stream.ts                 # SSE client for the streaming chat endpoint
    types.ts                   # shared request/response types
```

## Testing & linting

```bash
cd backend
uv run pytest
uv run ruff check .   # add --fix to autofix
```

## Deployment

Deploys as two Vercel Projects from this one repo (Root Directory `backend/`
and `frontend/` respectively) -- see the "Deployment" section in
[CLAUDE.md](./CLAUDE.md) for exact settings and env vars.

## More detail

See [CLAUDE.md](./CLAUDE.md) for a fuller reference (environment variables,
one-time setup, deployment, how to add a new agent tool, etc).
