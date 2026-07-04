FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY backend ./backend
RUN pip install --no-cache-dir .
RUN mkdir -p data
EXPOSE 8020
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8020"]
