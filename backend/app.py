import json
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.db import KnowledgeEntry, QaHistory

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = "dev-saas-secret-change-me"
JWT_ALGO = "HS256"

USERS = {
    "demo@team.com": {
        "password_hash": pwd_context.hash("demo1234"),
        "workspace": "acme-corp",
        "plan": "pro",
        "queries_limit": 10000,
        "queries_used": 42,
    },
    "free@team.com": {
        "password_hash": pwd_context.hash("free1234"),
        "workspace": "starter-team",
        "plan": "free",
        "queries_limit": 100,
        "queries_used": 95,
    },
}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AskRequest(BaseModel):
    question: str


class KnowledgeCreate(BaseModel):
    title: str
    content: str


def verify_login(email: str, password: str) -> dict | None:
    user = USERS.get(email)
    if user and pwd_context.verify(password, user["password_hash"]):
        return user
    return None


def create_token(email: str, workspace: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=8)
    return jwt.encode({"sub": email, "workspace": workspace, "exp": exp}, JWT_SECRET, algorithm=JWT_ALGO)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])


def seed_demo_knowledge(db: Session, workspace: str) -> None:
    if db.query(KnowledgeEntry).filter_by(workspace=workspace).count():
        return
    for title, content in [
        ("Onboarding guide", "Welcome to Team Knowledge. Add docs and ask questions."),
        ("API limits", "Pro plan includes 10,000 AI queries per month."),
    ]:
        db.add(
            KnowledgeEntry(
                workspace=workspace,
                title=title,
                content=content,
                status="ready",
            )
        )
    db.commit()


def mock_rag_answer(db: Session, workspace: str, question: str) -> dict:
    entries = (
        db.query(KnowledgeEntry)
        .filter(KnowledgeEntry.workspace == workspace, KnowledgeEntry.status == "ready")
        .all()
    )
    if not entries:
        return {"answer": "No indexed documents yet.", "citations": []}

    q = question.lower()
    best = entries[0]
    for entry in entries:
        if any(word in entry.content.lower() for word in q.split() if len(word) > 3):
            best = entry
            break

    snippet = best.content[:180]
    return {
        "answer": f"From team docs ({best.title}): {snippet}",
        "citations": [{"document_id": str(best.id), "title": best.title}],
    }


def save_qa(db: Session, workspace: str, email: str, question: str, result: dict) -> QaHistory:
    row = QaHistory(
        workspace=workspace,
        email=email,
        question=question,
        answer=result["answer"],
        citations_json=json.dumps(result.get("citations", [])),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
