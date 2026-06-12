# Deployment

## Local

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.scripts.ingest_documents --source ./knowledge-base
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`.

## Docker

```bash
copy .env.example .env
docker compose -f docker/docker-compose.yml up --build
```

Then ingest the knowledge base inside the running container if needed:

```bash
docker compose -f docker/docker-compose.yml exec broking-ai python -m app.scripts.ingest_documents --source ./knowledge-base
```

## Environment

The app runs without an OpenAI key in offline demo mode. Add a real `OPENAI_API_KEY` to enable OpenAI embeddings and generated responses.
