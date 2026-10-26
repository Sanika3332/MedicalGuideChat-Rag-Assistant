# MedicalGuideChat RAG Assistant

A health-information API that answers questions only from WHO fact sheets, with source citations and safety guardrails. Built with Django REST Framework, PostgreSQL + pgvector and sentence-transformers.

> Informational only. Not medical advice.

## How it works

1. WHO fact sheets (dengue, diabetes, hypertension) are split into 180-word chunks with 40-word overlap and embedded with `all-MiniLM-L6-v2` (384 dimensions).
2. Chunks and vectors are stored in PostgreSQL with pgvector.
3. A question is embedded and the 4 closest chunks are retrieved by cosine distance.
4. Safety checks run before anything else:
   - emergency keywords return a fixed emergency message;
   - diagnosis requests are refused;
   - if the best match is farther than the distance threshold (0.6), the reply is "couldn't find reliable information".
5. Otherwise the retrieved passages go to an LLM with instructions to answer only from them and cite sources. The generation layer is implemented; it needs an API key with credits. Without it, the app runs in retrieval-only mode (`LLM_MODE=retrieval_only`).
6. The answer and its sources are saved with the conversation.

## Features

- JWT authentication (register, login, refresh)
- Per-user conversations and message history; one user cannot read another's (returns 404)
- Source-cited answers and guardrails
- Evaluation command and 12 automated tests (pytest)

## Results

- Retrieval: top-1 accuracy 10/10 and hit rate (top 4) 10/10 on a a 10-question set (see evaluate.py) I wrote from the documents.
- Off-topic rejection: 4/4 at threshold 0.6 (relevant questions scored 0.2-0.4, off-topic 0.88-0.98).
- The sets are small, so treat this as a sanity check, not a benchmark.

## Setup

```bash
git clone https://github.com/Sanika3332/MedicalGuideChat-Rag-Assistant.git
cd MedicalGuideChat-Rag-Assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # fill in the values
docker compose up -d
python manage.py migrate
# put the .txt fact sheets in data/sources/, then:
python manage.py ingest
python manage.py runserver
```

Run tests: `pytest -v`. Run evaluation: `python manage.py evaluate`.

## API

| Method | Endpoint | Auth |
|---|---|---|
| POST | /api/auth/register/ | No |
| POST | /api/auth/login/ | No |
| POST | /api/auth/refresh/ | No |
| GET / POST | /api/conversations/ | Yes |
| GET / POST | /api/conversations/{id}/messages/ | Yes |

## Limitations

- Only three topics; knowledge is limited to the ingested documents.
- Guardrails are keyword-based and can miss rephrased emergencies.
- Text sources have no page numbers, so citations name the document.
- Not deployed; runs locally with Docker Compose for the database.
- Answers can still contain errors. Do not use for medical decisions.

## Sources and credits

WHO fact sheets (see `data/sources/SOURCES.md`). Project idea inspired by shsarv/Machine-Learning-Projects; no code was copied.
