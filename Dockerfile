# Demonstrates deployability: this image can be built and run anywhere
# (Cloud Run, any container host) without further changes.

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# GOOGLE_API_KEY and AGENT_MODEL are injected at runtime via
# `docker run --env-file .env ...` or the host platform's secret manager —
# never baked into the image.

EXPOSE 8000

CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000"]
