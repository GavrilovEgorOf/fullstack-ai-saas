from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app import (
    AskRequest,
    KNOWLEDGE,
    LoginRequest,
    USERS,
    create_token,
    decode_token,
    mock_rag_answer,
    pwd_context,
    verify_login,
)

app = FastAPI(title="Fullstack AI SaaS", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"


def current_user(authorization: str | None = Header(default=None)) -> tuple[str, dict]:
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
    return {"status": "ok"}


@app.post("/api/auth/signup")
def signup(body: LoginRequest):
    if body.email in USERS:
        raise HTTPException(400, "User exists")
    USERS[body.email] = {
        "password_hash": pwd_context.hash(body.password),
        "workspace": "new-workspace",
        "plan": "free",
        "queries_limit": 100,
        "queries_used": 0,
    }
    token = create_token(body.email, "new-workspace")
    return {"access_token": token, "plan": "free"}


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
def dashboard(auth: tuple[str, dict] = Depends(current_user)):
    email, user = auth
    return {
        "email": email,
        "workspace": user["workspace"],
        "plan": user["plan"],
        "queries_used": user["queries_used"],
        "queries_limit": user["queries_limit"],
        "knowledge_entries": len(KNOWLEDGE),
    }


@app.get("/api/knowledge")
def list_knowledge(auth: tuple[str, dict] = Depends(current_user)):
    return KNOWLEDGE


@app.post("/api/knowledge")
def add_knowledge(entry: dict, auth: tuple[str, dict] = Depends(current_user)):
    kid = str(len(KNOWLEDGE) + 1)
    KNOWLEDGE.append({"id": kid, "title": entry.get("title", "Untitled"), "content": entry.get("content", "")})
    return {"id": kid}


@app.post("/api/ask")
def ask(body: AskRequest, auth: tuple[str, dict] = Depends(current_user)):
    email, user = auth
    if user["queries_used"] >= user["queries_limit"]:
        raise HTTPException(402, "Monthly query limit reached — upgrade to Pro")
    user["queries_used"] += 1
    return mock_rag_answer(body.question)


if FRONTEND.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")
