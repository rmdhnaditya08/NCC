# STAGE 1 — Builder
FROM python:3.11 AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/packages -r requirements.txt


# STAGE 2 - Final
FROM python:3.11-slim AS final

WORKDIR /app

COPY --from=builder /app/packages /app/packages

COPY app.py .

ENV PYTHONPATH=/app/packages

RUN mkdir -p /app/logs

EXPOSE 5000

CMD ["python", "app.py"]
