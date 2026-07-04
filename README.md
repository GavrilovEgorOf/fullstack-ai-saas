# team-knowledge-app

[![CI](https://github.com/GavrilovEgorOf/fullstack-ai-saas/actions/workflows/ci.yml/badge.svg)](https://github.com/GavrilovEgorOf/fullstack-ai-saas/actions/workflows/ci.yml)

**Small SaaS-shaped demo** — landing page, login, workspace dashboard, doc list, “ask AI” with citations, monthly query cap.

FastAPI backend + static frontend — auth, usage limits, and an AI Q&A feature in a small product-shaped UI.

## Demo login

- Email: `demo@team.com`
- Password: `demo1234`

## Run

```bash
pip install -e .
uvicorn backend.main:app --reload --port 8020
```

Open http://localhost:8020 — landing at `/`, dashboard at `/dashboard.html`

Docker: `docker compose up --build`

## Related

Heavier RAG backend: [enterprise-rag-assistant](https://github.com/GavrilovEgorOf/enterprise-rag-assistant)

## Roadmap

See [ROADMAP.md](ROADMAP.md)

## License

MIT
