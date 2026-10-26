# Policy RAG — Specification

Status: foundation and source acquisition implemented; extraction and RAG capabilities specified for subsequent milestones.

## Purpose

Build an inspectable assistant that answers questions about a small collection of public insurance documents using retrieved evidence, returns traceable source citations, and explicitly abstains when the documents do not support an answer.

The portfolio should demonstrate backend engineering, retrieval quality, reproducible evaluation, containerization, CI, observability, and eventually AWS delivery. A milestone is complete when its acceptance criteria have corresponding evidence in the repository.

## Initial scope

- A small, versioned corpus of approximately 3–5 public, text-based insurance PDFs, initially in English. The first collection is three FEMA/NFIP policy forms from the October 1, 2025 annual CFR edition, recorded in `docs/corpus.json`.
- A Python/FastAPI backend with Pydantic schemas and PostgreSQL/pgvector.
- A single LLM provider for the first answering baseline; a Bedrock backend later.
- A REST interface first, followed by an MCP tool using the same retrieval/answering logic.

## Constraints

- Use no real customer, patient, claimant, or other personal records.
- Check document reuse conditions and record provenance before ingestion. Redistribute source PDFs only where permitted.
- Preserve document identity, version, original PDF page number, and chunk identity throughout retrieval and answering.
- Keep real `.env` files and API credentials outside version control and container images. Track only an empty `.env.example`.
- Support local development on a 16 GB laptop. The initial design uses a hosted LLM and does not require a local GPU.
- Keep cloud resources and API consumption within a deliberately chosen budget, with monitoring before deployment.
- Treat retrieved document instructions as untrusted content, not application instructions.
- Report implementation status and measured results honestly. Planned features are not completed features.

## Acceptance criteria — foundation

| ID | Requirement | Evidence |
| --- | --- | --- |
| F-01 | With valid local configuration, one Compose command starts `api` and `db` and both become healthy. | README command and local Compose verification. |
| F-02 | `GET /health` returns HTTP 200 with exactly `{"status":"ok"}` without opening a database connection. | `tests/test_health.py`. |
| F-03 | `GET /ready` returns HTTP 200 only after a successful PostgreSQL query confirms the vector extension. Database/query failures or a missing extension return HTTP 503. | `main.py`, positive local verification; failure-path integration coverage remains to be added. |
| F-04 | All required configuration variable names appear in `.env.example` with empty values. The actual `.env` is ignored by Git and Docker builds. | Example and ignore rules. |
| F-05 | The API image installs from `uv.lock` and runs as a non-root user. | Dockerfile and successful local container startup. |
| F-06 | The smoke test runs locally and on pushes and pull requests with no database service or real secrets. | Pytest output and the actual GitHub Actions run. |
| F-07 | README describes setup, architecture, endpoint semantics, current scope, and planned work. | README review. |

## Acceptance criteria — source acquisition

| ID | Requirement | Evidence |
| --- | --- | --- |
| C-01 | A reviewed manifest records stable document IDs, source URLs, edition, SHA-256, byte size, PDF page count, reuse-review basis, and neighboring-section boundary notes for the initial three documents. | `docs/corpus.json`, `docs/corpus.md`, and inspection of the downloaded sources. |
| C-02 | The download command validates the manifest, bounds network reads, and checks the PDF header, exact byte size, and SHA-256 before saving a source file. | `scripts/download_corpus.py`, rejected-content tests, and a real acquisition run. |
| C-03 | A repeat run verifies and reuses existing files. Mismatches fail with a nonzero status without silently replacing existing files or saving invalid downloads. | Cached-file, corrupt-file, network-failure tests, and a repeat acquisition run. |
| C-04 | Raw PDFs are excluded from Git and Docker builds. Automated downloader tests use mocked network calls and require no database, real credentials, or paid APIs. | Ignore rules, pytest, and the actual CI run. |

## Acceptance criteria — retrieval and answers (planned)

| ID | Requirement | Evidence to add |
| --- | --- | --- |
| R-01 | Each ingested document has a source URL, identifier, version or content hash, and extraction metadata. Re-ingestion does not silently duplicate identical content. | Ingestion records and integration tests. |
| R-02 | Each chunk retains its source identity and original page metadata. Chunking and embedding configuration are recorded. | Stored records and reproducible ingestion configuration. |
| R-03 | A supported answer uses structured output and includes at least one citation. Every material factual claim has supporting evidence. | Schema validation and citation/groundedness evaluation. |
| R-04 | Every citation resolves to an actually retrieved document/page/chunk. A valid-looking citation alone is not sufficient: the cited text must support the claim. | Citation validation and annotated evaluation cases. |
| R-05 | When evidence is insufficient, the response uses an explicit `insufficient_evidence` outcome and states that the answer cannot be determined from the documents. It does not invent coverage, limits, exclusions, or citations. | Unanswerable and out-of-scope evaluation cases. |
| R-06 | Materially conflicting policy versions or ambiguous document scope are surfaced or clarified rather than silently combined. | Conflict and ambiguity cases. |
| R-07 | Provider/service failures are represented as operational errors, distinct from evidence-based abstention. | Error-contract integration tests. |

## Acceptance criteria — evaluation and delivery (planned)

- **E-01:** Maintain 40–50 versioned questions with expected answers or abstention, supporting source references, and answerability labels.
- **E-02:** Keep tuning questions separate from the held-out comparison set. Record corpus, model/provider, prompt, chunking, embedding, and reranking configuration for each run.
- **E-03:** Report answer correctness, citation support/groundedness, retrieval quality, latency distribution, token usage, and estimated cost per query. State the scoring method and limitations, including any LLM judge.
- **E-04:** Compare a recorded baseline with controlled chunking/model/reranking changes; publish actual results and regressions without inventing improvements or a success threshold after seeing the results.
- **D-01:** Add request IDs and operational metrics without logging credentials or real personal records.
- **D-02:** Add automated image builds, AWS deployment instructions and teardown steps, budget alerts, and a documented database-hosting choice before calling the cloud milestone complete.
- **D-03:** Expose the same application capabilities through an MCP tool with an explicit input/output schema; document discovery and integration tradeoffs against REST.

## Change discipline

Before implementing a behavior change, update or add the relevant acceptance criterion. Include implementation and proportionate validation in the same reviewable change. Update README when the completed scope changes. A CI workflow file is evidence of configuration; a successful run is evidence of execution.
