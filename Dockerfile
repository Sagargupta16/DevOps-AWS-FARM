FROM node:22-alpine AS frontend
WORKDIR /client
COPY client/package.json client/package-lock.json ./
RUN npm ci --ignore-scripts
COPY client/ ./
RUN npm run build

# slim, not alpine: pymongo publishes no musllinux wheel, so alpine needed gcc to build it from source
FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_FORMAT=json
WORKDIR /app
# Hash-locked and wheels only: nothing is compiled and nothing enters the image without a checksum
COPY requirements.lock.txt ./
RUN pip install --no-cache-dir --require-hashes --only-binary :all: -r requirements.lock.txt
COPY . /app/
COPY --from=frontend /client_build /app/client_build
# Run as an unprivileged user; it owns /app only so the file log handler can create app.log
RUN useradd --system --uid 10001 --no-create-home app && chown app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"]
# The request middleware already writes one JSON access line per request
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
