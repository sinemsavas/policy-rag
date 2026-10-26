# Page-preserving corpus extraction

## Run locally

Run from the repository root with the locked dependencies and downloaded sources:

```bash
uv sync --locked --group dev
uv run --locked python -m scripts.download_corpus
uv run --locked python -m scripts.extract_corpus
```

The extractor writes one `<document_id>.pages.jsonl` file per source into local `data/processed/`. JSONL has one JSON object per line; each object contains the selected text from one original PDF page. Both source PDFs and generated page files are excluded from Git and Docker builds.

## Scope and boundaries

The `cfr-plain-v1` profile supports the reviewed, unrotated, text-based CFR files in [corpus.json](corpus.json). Each document specifies a literal start heading and the heading that ends its section.

The parser's [text-extraction documentation](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) describes plain mode and PDF layout limitations. Profile behavior is validated against the locked sources below.

The pipeline:

1. Verify the original PDF header, byte size, and SHA-256 before parsing.
2. Check the PDF page count and printed page range against the manifest.
3. Extract each page in pypdf's plain mode. For these reviewed files, content-stream order reads the left column before the right.
4. Validate the printed page label and CFR header, then remove only the publisher header and the `VerDate` footer block.
5. Require exactly one start heading and one later end heading. Headings may wrap across lines.
6. Keep the target appendix from its start heading up to, but excluding, the next section heading. Keep page boundaries and original one-based PDF positions.
7. Validate all source documents before writing outputs. Replace each completed JSONL file atomically; identical files are left unchanged on repeat runs.

The first and last source pages contain material from neighboring sections. They are trimmed at the section headings rather than discarded: a boundary page may contain valid text for two different forms. Each form receives only its own text.

Body line breaks and line-end hyphenation are retained for now. Normalization for chunking will be a separate, reviewable step. The profile requires extractable text, expected headers, and matching labels; blank/scanned pages, rotated pages, ambiguous headings, and unexpected metadata produce an error for review.

## Record contract

| Field | Meaning |
| --- | --- |
| `schema_version`, `corpus_id` | Output schema and collection identity. |
| `page_id` | Stable `<document_id>:page:<original_pdf_position>` identity. |
| `document_id`, `title`, `section_reference` | Source form identity and intended appendix. |
| `edition_date`, `source_url`, `source_sha256` | Edition, original source address, and verified PDF fingerprint. |
| `pdf_page_number` | Original one-based PDF position, used to open the correct source page. |
| `printed_page_label` | Printed CFR label, kept separately from PDF position. |
| `text`, `text_sha256` | Selected page text and its fingerprint. |
| `extraction` | Profile name, parser/version, and canonical extraction-configuration fingerprint. |

For example, the Dwelling file's PDF page 1 has printed label `156`. If a source page is excluded because it falls outside the target section, later pages keep their original numbers.

Outputs include no run timestamps, so the same source bytes, configuration, and parser version produce reproducible JSONL. Changes to cleanup rules require a new profile version; changes to markers update the configuration fingerprint. A future database loader must use source and extraction fingerprints along with page identity when handling revisions.

## Inspect a record

```bash
uv run --locked python - <<'PY'
import json
from pathlib import Path

path = Path("data/processed/nfip-dwelling-2025-10-01.pages.jsonl")
record = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
print(record["document_id"])
print("PDF page:", record["pdf_page_number"])
print("Printed page:", record["printed_page_label"])
print(record["text"][:300])
PY
```

## Validation

Automated tests create small real PDFs locally, with two columns, publisher lines, and neighboring policy sections. They check section isolation, wrapped/missing/duplicate/reversed headings, original page positions, fingerprint and metadata failures, empty text, deterministic JSONL, and preservation of previous outputs when another document fails. CI needs no network, downloaded corpus, database, or API credentials.

The real reviewed corpus was also extracted locally with pypdf 6.21.2 and its font support:

| Form | Page records | Original PDF positions | Printed labels |
| --- | --- | --- | --- |
| Dwelling | 16 | 1-16 | 156-171 |
| General Property | 15 | 1-15 | 171-185 |
| RCBAP | 16 | 1-16 | 185-200 |

These 47 records contain section-trimmed text; some source boundary pages overlap. They are page records for later chunking, not an answer-quality evaluation.

GovInfo's source PDFs produce pypdf's `Xref table not zero-indexed` warning. The parser corrects the object numbering; source hashes, labels, page counts, and section markers are still checked. The warning is left visible.

Database ingestion, chunks, embeddings, and retrieval are the next milestones.
