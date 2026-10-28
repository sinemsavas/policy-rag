# Initial public corpus

## Scope and edition

The first collection contains three FEMA National Flood Insurance Program (NFIP) Standard Flood Insurance Policy forms. Sources are the GovInfo annual Code of Federal Regulations, Title 44, Part 61, revised **October 1, 2025**. The question-answering scope will be limited to this recorded edition.

The documents are English regulatory policy forms without filled customer applications, declarations, or claims. Similar clauses across the three forms will make document selection and form-specific differences useful retrieval checks.

| Document ID | Form | Section | PDF pages | Printed CFR pages |
| --- | --- | --- | --- | --- |
| `nfip-dwelling-2025-10-01` | [Dwelling Form](https://www.govinfo.gov/content/pkg/CFR-2025-title44-vol1/pdf/CFR-2025-title44-vol1-part61-appA1.pdf) | Appendix A(1) | 16 | 156-171 |
| `nfip-general-property-2025-10-01` | [General Property Form](https://www.govinfo.gov/content/pkg/CFR-2025-title44-vol1/pdf/CFR-2025-title44-vol1-part61-appA2.pdf) | Appendix A(2) | 15 | 171-185 |
| `nfip-rcbap-2025-10-01` | [Residential Condominium Building Association Policy](https://www.govinfo.gov/content/pkg/CFR-2025-title44-vol1/pdf/CFR-2025-title44-vol1-part61-appA3.pdf) | Appendix A(3) | 16 | 185-200 |

[corpus.json](corpus.json) records each source URL, stable document ID, edition, SHA-256, byte size, page count, section reference, and boundary notes. The 47 PDF pages include overlapping boundary pages; they are not 47 distinct policy pages.

## Reuse review

Reviewed on **October 26, 2026**. [GovInfo's public-domain and copyright policy](https://www.govinfo.gov/about/policies) explains the U.S. government-work basis under 17 U.S.C. 105 and the exception for third-party material. These files contain FEMA regulatory policy text; no third-party copyright notices were identified during text inspection. The reuse basis recorded in the manifest applies to that regulatory text in the United States. Government seals, branding, and third-party material are outside this review.

The repository distributes the catalogue and download command. Original PDFs stay in local `data/raw/` and are excluded from Git and the Docker build context. Adding a different source requires its own provenance and reuse review.

## Download and verify

From the repository root, after installing the existing dependencies:

```bash
uv sync --locked --group dev
uv run --locked python -m scripts.download_corpus
```

The command downloads three files into `data/raw/` using only the existing project dependencies and Python's standard library. No database, LLM key, or paid service is needed.

For every response it checks the PDF header, recorded byte size, and SHA-256 before saving through a temporary file. Download reads are bounded and have a timeout. A repeat run verifies cached files and skips their downloads.

A changed or damaged file produces a nonzero exit status. Existing mismatched files are preserved for inspection rather than silently replaced. If the publisher changes a source, review that change before updating the manifest; do not replace a pinned hash merely to make an error disappear.

The downloader verifies bytes, not PDF structure or policy semantics. Page counts and printed page ranges were checked separately with a PDF reader during corpus review.

## Extraction constraints

- Pages have two text columns and contain line-break hyphenation and publisher headers/footers.
- The first and last pages can include neighboring sections. Appendix A(1) includes neighboring section 61.17 and the beginning of A(2); A(2) includes parts of A(1) and A(3); A(3) includes parts of A(2) and Part 62.
- Extraction must select the intended appendix body without silently attaching neighboring text to that form.
- Keep the original, one-based PDF page position for citations. Printed CFR labels are separate metadata: PDF page 1 of the Dwelling file is printed page 156.
- Preserve the unmodified source and its hash so extraction changes remain reproducible.

**Current status:** source selection, provenance, verified acquisition, page/section extraction, and [page-contained chunking](chunking.md) are implemented. [Extraction notes](extraction.md) describe the page-preserving JSONL command and its validation. Embeddings, database ingestion, and retrieval remain to be implemented. The [project guide](project-guide.md) explains the complete current pipeline and links to the development history and next milestones.

## Validation

`tests/test_download_corpus.py` checks repeated downloads, rejected HTML/truncated/changed content, corrupt cached files, filename traversal, duplicate document IDs, and a network failure. Tests use synthetic bytes and mocked network calls, so CI does not depend on GovInfo availability.

Run the complete current test suite:

```bash
uv run --locked python -m pytest -q
```
