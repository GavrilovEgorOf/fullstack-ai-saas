from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

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
    }
}

KNOWLEDGE = [
    {"id": "1", "title": "Onboarding guide", "content": "Welcome to AI Knowledge Base for Teams."},
    {"id": "2", "title": "API limits", "content": "Pro plan includes 10,000 AI queries per month."},
]


class LoginRequest(BaseModel):
    email: str
    password: str


class AskRequest(BaseModel):
    question: str


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


def mock_rag_answer(question: str) -> dict:
    snippet = KNOWLEDGE[0]["content"]
    return {
        "answer": f"[Mock RAG] Based on team docs: {snippet} (Question: {question})",
        "citations": [{"document_id": "1", "title": KNOWLEDGE[0]["title"]}],
    }
