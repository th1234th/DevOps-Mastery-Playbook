FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=1.0.0

WORKDIR /app
COPY --chown=65534:65534 server.py /app/server.py
USER 65534:65534
EXPOSE 8080
CMD ["python", "/app/server.py"]