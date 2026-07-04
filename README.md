# team-knowledge-app

[![CI](https://github.com/GavrilovEgorOf/fullstack-ai-saas/actions/workflows/ci.yml/badge.svg)](https://github.com/GavrilovEgorOf/fullstack-ai-saas/actions/workflows/ci.yml)

**Team doc library with AI Q&A** — landing, login, workspace dashboard, doc upload, questions with citations, usage limits, history export.

GitHub repo slug: `fullstack-ai-saas`. Stack: **FastAPI + Next.js**.

## Demo login

- Email: `demo@team.com`
- Password: `demo1234`

Free-tier demo: `free@team.com` / `free1234` (near query limit)

## Run locally

Terminal 1 — API:

```bash
pip install -e ".[dev]"
uvicorn backend.main:app --reload --port 8020
```

Terminal 2 — Next.js:

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000

Docker: `docker compose up --build` (API on :8020, web on :3000)

## Features

- JWT login and workspace isolation
- Doc upload with background indexing job
- Q&A with citations (mock RAG over indexed docs)
- Free vs pro query limits
- Q&A history + CSV export

## Tests

```bash
pytest -q
cd web && npm run build
```

## Related

RAG backend with eval CI: [enterprise-rag-assistant](https://github.com/GavrilovEgorOf/enterprise-rag-assistant)

## Roadmap

See [ROADMAP.md](ROADMAP.md)

## License

MIT
