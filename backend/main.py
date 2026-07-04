import csv
import io
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app import (
    AskRequest,
    KnowledgeCreate,
    LoginRequest,
    USERS,
    create_token,
    decode_token,
    mock_rag_answer,
    pwd_context,
    save_qa,
    seed_demo_knowledge,
    verify_login,
)
from backend.db import KnowledgeEntry, ProcessingJob, QaHistory, SessionLocal, init_db
from backend.jobs import process_entry


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_demo_knowledge(db, "acme-corp")
        seed_demo_knowledge(db, "starter-team")
    finally:
        db.close()
    yield


app = FastAPI(title="Team Knowledge API", version="1.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def current_user(
    authorization: str | None = Header(default=None),
) -> tuple[str, dict]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Login required")
    try:
        payload = decode_token(authorization.removeprefix("Bearer ").strip())
    except Exception as exc:
        raise HTTPException(401, "Invalid token") from exc
    email = payload["sub"]
    user = USERS.get(email)
    if not user:
        raise HTTPException(401, "User not found")
    return email, user


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "team-knowledge-api"}


@app.post("/api/auth/signup")
def signup(body: LoginRequest, db: Session = Depends(get_db)):
    if body.email in USERS:
        raise HTTPException(400, "User exists")
    workspace = body.email.split("@")[0].replace(".", "-")
    USERS[body.email] = {
        "password_hash": pwd_context.hash(body.password),
        "workspace": workspace,
        "plan": "free",
        "queries_limit": 100,
        "queries_used": 0,
    }
    seed_demo_knowledge(db, workspace)
    token = create_token(body.email, workspace)
    return {"access_token": token, "plan": "free", "workspace": workspace}


@app.post("/api/auth/login")
def login(body: LoginRequest):
    user = verify_login(body.email, body.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    return {
        "access_token": create_token(body.email, user["workspace"]),
        "workspace": user["workspace"],
        "plan": user["plan"],
    }


@app.get("/api/dashboard")
def dashboard(auth: tuple[str, dict] = Depends(current_user), db: Session = Depends(get_db)):
    email, user = auth
    docs = (
        db.query(KnowledgeEntry)
        .filter(KnowledgeEntry.workspace == user["workspace"])
        .count()
    )
    return {
        "email": email,
        "workspace": user["workspace"],
        "plan": user["plan"],
        "queries_used": user["queries_used"],
        "queries_limit": user["queries_limit"],
        "knowledge_entries": docs,
    }


@app.get("/api/knowledge")
def list_knowledge(auth: tuple[str, dict] = Depends(current_user), db: Session = Depends(get_db)):
    _, user = auth
    rows = (
        db.query(KnowledgeEntry)
        .filter(KnowledgeEntry.workspace == user["workspace"])
        .order_by(KnowledgeEntry.id.desc())
        .all()
    )
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "content": r.content[:200],
            "status": r.status,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@app.post("/api/knowledge")
def add_knowledge(
    body: KnowledgeCreate,
    background: BackgroundTasks,
    auth: tuple[str, dict] = Depends(current_user),
    db: Session = Depends(get_db),
):
    _, user = auth
    entry = KnowledgeEntry(
        workspace=user["workspace"],
        title=body.title,
        content=body.content,
        status="processing",
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    job = ProcessingJob(entry_id=entry.id, status="queued")
    db.add(job)
    db.commit()
    background.add_task(process_entry, entry.id)
    return {"id": str(entry.id), "status": "processing", "job_id": job.id}


@app.get("/api/jobs/{job_id}")
def job_status(job_id: int, auth: tuple[str, dict] = Depends(current_user), db: Session = Depends(get_db)):
    _, user = auth
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    entry = db.get(KnowledgeEntry, job.entry_id)
    if not entry or entry.workspace != user["workspace"]:
        raise HTTPException(404, "Job not found")
    return {"job_id": job.id, "status": job.status, "entry_status": entry.status, "error": job.error}


@app.post("/api/ask")
def ask(body: AskRequest, auth: tuple[str, dict] = Depends(current_user), db: Session = Depends(get_db)):
    email, user = auth
    if user["queries_used"] >= user["queries_limit"]:
        raise HTTPException(402, "Monthly query limit reached — upgrade to Pro")
    user["queries_used"] += 1
    result = mock_rag_answer(db, user["workspace"], body.question)
    row = save_qa(db, user["workspace"], email, body.question, result)
    return {
        "answer": result["answer"],
        "citations": result["citations"],
        "history_id": row.id,
    }


@app.get("/api/history")
def history(auth: tuple[str, dict] = Depends(current_user), db: Session = Depends(get_db)):
    _, user = auth
    rows = (
        db.query(QaHistory)
        .filter(QaHistory.workspace == user["workspace"])
        .order_by(QaHistory.id.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": r.id,
            "question": r.question,
            "answer": r.answer,
            "citations": json.loads(r.citations_json),
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@app.get("/api/history/export")
def export_history(
    format: str = "json",
    auth: tuple[str, dict] = Depends(current_user),
    db: Session = Depends(get_db),
):
    _, user = auth
    rows = (
        db.query(QaHistory)
        .filter(QaHistory.workspace == user["workspace"])
        .order_by(QaHistory.id.desc())
        .all()
    )
    if format == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "question", "answer", "created_at"])
        for r in rows:
            writer.writerow([r.id, r.question, r.answer, r.created_at.isoformat()])
        from fastapi.responses import PlainTextResponse

        return PlainTextResponse(buf.getvalue(), media_type="text/csv")
    return [
        {
            "id": r.id,
            "question": r.question,
            "answer": r.answer,
            "citations": json.loads(r.citations_json),
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


if Path(__file__).resolve().parents[1].joinpath("frontend").is_dir():
    pass  # legacy static frontend removed in favor of Next.js
