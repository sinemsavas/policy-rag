# Policy RAG

A portfolio project being developed into a source-citing RAG assistant for public insurance documents. The current milestone provides a containerized FastAPI service, PostgreSQL with pgvector, configuration management, a health smoke test with a GitHub Actions workflow, verified acquisition of a reviewed public corpus, and page-preserving extraction.

**Status: foundation, source acquisition, and page extraction implemented.** Database ingestion, embeddings, question answering, evaluation results, and AWS deployment are planned. This repository does not yet expose a question-answering endpoint.

## Implemented foundation

- FastAPI with Pydantic response schemas and validated environment settings.
- Separate liveness (`/health`) and database readiness (`/ready`) endpoints.
- PostgreSQL 17 with pgvector 0.8.7, initialized through `init.sql`.
- An API image that installs locked dependencies and runs as a non-root user.
- Docker Compose with a persistent database volume and service health checks.
- One automated smoke test that verifies liveness without a database connection.
- A CI workflow for pushes and pull requests; see the repository's Actions tab for actual run results.
- A reviewed three-document FEMA/NFIP corpus with pinned source fingerprints and an offline-tested download command.
- Page-preserving JSONL extraction with verified section boundaries, source metadata, and offline real-PDF tests.

## Architecture

Docker Compose runs two services: `api` and `db`. The API runs Uvicorn on container port 8000 and reaches PostgreSQL through the Compose service name `db` on port 5432. Host ports are bound to loopback for local development. PostgreSQL stores its data in the `postgres_data` named volume, while `init.sql` enables the vector extension on initial database creation. Connection settings are provided through environment variables and validated by Pydantic Settings. `/ready` opens a database connection and checks that the vector extension is enabled; `/health` reports API liveness independently of PostgreSQL.

## Run locally

Requirements: Docker with the Compose plugin. On Windows, use Docker Desktop with WSL2 integration and run commands in Ubuntu. Local Python and uv are needed for development and testing, but not for the Compose startup command.

From the repository root, create a local configuration for a **new** setup:

```bash
cp .env.example .env
```

Fill in all three values in `.env`. Use local database and user names such as `policy_rag`, and a new local password. An existing working `.env` can be kept as-is. The example intentionally contains variable names without values.

Start the complete stack:

```bash
docker compose up -d --build --wait --wait-timeout 60
```

The first build downloads the images and Python dependencies. Check service status:

```bash
docker compose ps
```

Both `api` and `db` should become healthy. Open:

| URL | Purpose | Expected result |
| --- | --- | --- |
| http://localhost:8000/health | API liveness | HTTP 200 and `{"status":"ok"}` |
| http://localhost:8000/ready | PostgreSQL connectivity and vector-extension availability | HTTP 200 and `{"status":"ok"}` when ready |
| http://localhost:8000/docs | Interactive OpenAPI documentation | API documentation |

`/ready` returns HTTP 503 for database connection/query failures or a missing vector extension. The root path `/` has no route and returns HTTP 404.

Useful commands:

```bash
docker compose logs --tail=50 api
docker compose stop
docker compose up -d --wait --wait-timeout 60
```

Rebuild with the startup command after changing application code or dependencies. The named database volume persists when containers are recreated. Database initialization scripts run only when the data directory is empty; changing `.env` does not rotate an existing database password.

## Development and tests

Use Python 3.12 and uv 0.13.5. From the repository root:

```bash
uv sync --locked --group dev
uv run --locked python -m pytest -q
```

The smoke test supplies temporary settings before importing the application. It asserts HTTP 200 and the response contract for `/health`, and fails if that request attempts a PostgreSQL connection. Docker, an LLM API key, and real database credentials are not required for this test. Downloader tests use mocked network calls and extraction tests generate small PDFs locally, so the test suite does not contact the document host. Readiness and RAG behavior need separate integration/evaluation coverage in later milestones.

For API development against the Compose database, stop the containerized API before using the same host port:

```bash
docker compose stop api
uv run fastapi dev main.py
```

## Public source corpus

The first collection contains three FEMA/NFIP Standard Flood Insurance Policy forms from the October 1, 2025 annual CFR edition. See the [corpus catalogue](docs/corpus.md) for sources, reuse review, scope, and extraction constraints; [corpus.json](docs/corpus.json) pins document IDs, versions, sizes, and SHA-256 values.

After installing the development environment, download and verify the source files:

```bash
uv run --locked python -m scripts.download_corpus
```

PDFs are stored in local `data/raw/`, outside Git and the Docker build context. Repeat runs verify cached files and skip downloading them.

Extract the intended policy appendix from each source while preserving original PDF page numbers:

```bash
uv run --locked python -m scripts.extract_corpus
```

Page records are written to local `data/processed/<document_id>.pages.jsonl`. Each record includes the document ID, source URL/hash, edition, original PDF position, printed page label, text/hash, and extraction metadata. [Extraction notes](docs/extraction.md) explain section boundaries, the output contract, validation, and supported PDF layout. Database ingestion and chunking are the next steps.

## Specification and roadmap

[SPEC.md](SPEC.md) defines scope, constraints, acceptance criteria, and the evidence needed to complete each milestone.

1. Foundation documentation and CI smoke test (implemented).
2. Reviewed public corpus and verified source downloads (implemented).
3. Page/section extraction with source metadata (implemented).
4. Chunking, database ingestion, embeddings, and pgvector retrieval.
5. Structured answers with verified citations and explicit abstention.
6. A 40–50-question evaluation set and reproducible experiment reports.
7. Latency, token, and estimated-cost monitoring; CI image builds.
8. AWS deployment, a Bedrock backend, and an MCP interface.

No accuracy, groundedness, latency, cost, or cloud-deployment results are claimed until they are measured and published.
