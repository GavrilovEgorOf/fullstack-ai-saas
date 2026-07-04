import re
import time

from sqlalchemy.orm import Session

from backend.db import KnowledgeEntry, ProcessingJob, SessionLocal


def chunk_text(text: str, size: int = 400) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    for word in words:
        current.append(word)
        if len(" ".join(current)) >= size:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks or [text]


def process_entry(entry_id: int) -> None:
    """Simulate background doc processing (chunk + index)."""
    time.sleep(0.05)
    db: Session = SessionLocal()
    try:
        entry = db.get(KnowledgeEntry, entry_id)
        job = (
            db.query(ProcessingJob)
            .filter(ProcessingJob.entry_id == entry_id, ProcessingJob.status == "queued")
            .order_by(ProcessingJob.id.desc())
            .first()
        )
        if not entry or not job:
            return
        job.status = "running"
        db.commit()

        cleaned = re.sub(r"\s+", " ", entry.content.strip())
        chunks = chunk_text(cleaned)
        entry.content = cleaned
        entry.status = "ready" if chunks else "failed"
        job.status = "done" if chunks else "failed"
        if not chunks:
            job.error = "empty document"
        db.commit()
    finally:
        db.close()
