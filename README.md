# Fullstack AI SaaS

[![CI](https://github.com/GavrilovEgorOf/fullstack-ai-saas/actions/workflows/ci.yml/badge.svg)](https://github.com/GavrilovEgorOf/fullstack-ai-saas/actions/workflows/ci.yml)

Fullstack **AI SaaS starter**: landing page, signup/login, workspace dashboard, knowledge entries, mock RAG Q&A, and usage limits (free vs pro).

## Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Static HTML/CSS/JS (TypeScript/React-ready API contract)
- **AI:** Mock RAG responses with citations (no API key required)

## Features

- Landing page with value proposition
- Sign up / login (in-memory demo store)
- Workspace dashboard with usage meters
- Knowledge entry list + create
- Ask AI with citation mock
- Billing mock: free (100 queries) / pro (10,000 queries)

## Quick Start

```bash
pip install -e .
uvicorn backend.main:app --reload --port 8020
```

Open http://localhost:8020 — dashboard login: `demo@team.com` / `demo1234`

## Docker

```bash
docker compose up --build
```

## What This Proves

Product engineering for startups: **backend + frontend + AI feature + usage limits** in one repo.

## Related Projects

- [enterprise-rag-assistant](https://github.com/GavrilovEgorOf/enterprise-rag-assistant) — production RAG backend
- [llm-gateway](https://github.com/GavrilovEgorOf/llm-gateway) — LLM infrastructure layer

## License

MIT
