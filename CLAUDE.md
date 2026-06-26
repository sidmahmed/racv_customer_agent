# agent-scaffold

A RACV customer-support chatbot: a FastAPI backend running a LangChain
tool-calling agent (OpenAI) that answers questions grounded in RACV's Help &
Support content via hybrid search (Supabase pgvector + full-text + RRF
fusion), chat history persisted in SQLite, and a Next.js/TypeScript frontend
with streaming responses.

## Stack

- Backend: FastAPI, Pydantic, LangChain (`langchain.agents.create_agent`,
  langgraph under the hood), OpenAI via `langchain-openai` (chat +
  embeddings), Supabase Postgres (pgvector + full-text search) for the
  retrieval index, SQLite (via `langgraph-checkpoint-sqlite`) for agent/thread
  state.
- Frontend: Next.js 16 (App Router), TypeScript, Tailwind CSS.
- Package management: `uv` (backend), `npm` (frontend).

## Layout

```
backend/
  app/
    main.py            # FastAPI app, CORS, route registration
    config.py           # pydantic-settings, reads .env
    agent.py             # builds the LangChain agent, RACV system prompt, sqlite-backed thread memory
    tools.py             # search_help_center (hybrid RAG) tool
    supabase_client.py   # supabase-py client singleton
    db.py                 # sqlite connection + langgraph SqliteSaver checkpointer (/tmp on Vercel)
    models.py             # pydantic request/response models
    routes/
      chat.py              # POST /api/chat, POST /api/chat/stream, GET /api/chat/{session_id}/history
  scripts/
    ingest.py             # one-time/developer-run: fetch RACV pages, chunk, embed, upsert to Supabase
  supabase/
    schema.sql            # documents table + hybrid_search RPC -- run once via SQL editor
  chat_history.db        # sqlite db (gitignored, created on first run)
frontend/
  app/
    page.tsx              # chat UI (client component)
    stream.ts              # SSE client for the streaming chat endpoint
    types.ts                # shared request/response types
```

## Commands

Backend (run from `backend/`):
- `uv sync` — install runtime + dev dependencies
- `uv run uvicorn app.main:app --reload` — run dev server (http://localhost:8000)
- `uv run pytest` — run tests
- `uv run ruff check .` — lint (add `--fix` to autofix)
- `uv add <package>` — add a runtime dependency
- `uv sync --group ingest` — install ingestion-only deps (BeautifulSoup, `langchain-text-splitters`)
- `uv run python -m scripts.ingest` — (re-)populate Supabase from the 11 RACV pages

Frontend (run from `frontend/`):
- `npm install`
- `npm run dev` — run dev server (http://localhost:3000)
- `npm run build`

## One-time setup (before first run)

1. Create a Supabase project, then run `backend/supabase/schema.sql` in its
   SQL editor (creates the `documents` table and the `hybrid_search` RPC).
2. Copy `backend/.env.example` to `backend/.env`, fill in `OPENAI_API_KEY`,
   `SUPABASE_URL`, `SUPABASE_KEY` (service role key).
3. `cd backend && uv sync --group ingest && uv run python -m scripts.ingest`
   to populate the `documents` table from the 11 RACV Help & Support pages.

## Environment variables

- `backend/.env` (copy from `backend/.env.example`): `OPENAI_API_KEY`,
  `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`, `DATABASE_URL`, `CORS_ORIGINS`,
  `SUPABASE_URL`, `SUPABASE_KEY` (use the service role key -- the backend
  calls Supabase server-side, there's no per-end-user Supabase auth here).
- `frontend/.env.local` (copy from `frontend/.env.example`):
  `NEXT_PUBLIC_API_URL`.

## Deployment (two Vercel Projects from this one repo)

- **Backend** (Root Directory `backend/`): no build command needed --
  Vercel's Python runtime auto-detects `app/main.py`'s `app = FastAPI()` and
  installs deps natively from `pyproject.toml`/`uv.lock` (only
  `[project.dependencies]`; the `dev`/`ingest` groups are excluded
  automatically). Env vars: `OPENAI_API_KEY`, `OPENAI_MODEL`,
  `OPENAI_EMBEDDING_MODEL`, `SUPABASE_URL`, `SUPABASE_KEY`, `CORS_ORIGINS`
  (set to the deployed frontend's exact origin as a JSON-array string --
  FastAPI's `CORSMiddleware` rejects `"*"` when `allow_credentials=True`,
  which `main.py` sets). `VERCEL` is set automatically by the platform and
  triggers the `/tmp` checkpointer path in `db.py`.
- **Frontend** (Root Directory `frontend/`): just `NEXT_PUBLIC_API_URL` set
  to the deployed backend's URL.
- Known PoC limitation: chat history only persists within a warm Vercel
  instance's lifetime in production (filesystem is ephemeral outside
  `/tmp`); a future iteration would swap `SqliteSaver` for
  `langgraph-checkpoint-postgres` pointed at the same Supabase instance.

## Notes

- Agent thread/session memory is keyed by `session_id` (sent from the
  frontend, persisted in `localStorage`) and stored via langgraph's
  `SqliteSaver` checkpointer in `backend/chat_history.db` (or `/tmp` when
  deployed to Vercel).
- The agent's tool (`backend/app/tools.py`) replaces the scaffold's original
  demo tool: `search_help_center` (hybrid semantic+keyword search over the
  ingested RACV pages, with an optional `category` filter and citations). A
  pricing lookup tool was scoped out for now -- the agent is told it has no
  pricing access and to direct members to contact RACV for a quote. To add
  another tool, follow the same `@tool`-decorated pattern and include it in
  `TOOLS`.
- `frontend/AGENTS.md` flags that this Next.js version may differ from
  training data on routing/caching APIs — check `node_modules/next/dist/docs/`
  before relying on prior knowledge of Next.js conventions.
