FROM python:3.12-slim

ENV APP_VERSION=1.0.0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY --chown=10001:10001 app/server.py /app/server.py
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=2s --start-period=2s --retries=3 \
  CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8080/healthz', timeout=1)"
CMD ["python", "/app/server.py"]