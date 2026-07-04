FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY backend ./backend
COPY frontend ./frontend
RUN pip install --no-cache-dir .
EXPOSE 8020
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8020"]
