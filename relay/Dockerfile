FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/
COPY stackfix /app/stackfix
COPY relay /app/relay

RUN pip install --no-cache-dir -e ".[relay]"

EXPOSE 8000

CMD ["python", "-m", "relay.app"]