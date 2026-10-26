# Page-contained character chunking

## Run locally

After [page extraction](extraction.md), run from the repository root:

```bash
uv run --locked python -m scripts.chunk_corpus
```

The versioned [baseline config](chunking.json) selects `page-char-v1`, `max_chars=1200`, and `overlap_chars=200`. Counts use Python Unicode characters, separately from UTF-8 bytes and model tokens. Token budgeting will be checked when an embedding model is selected.

Outputs go into `data/chunks/page-char-v1-1200-200/`:

- One `<document_id>.chunks.jsonl` file per policy form.
- A deterministic `report.json` with configuration, source/extraction lineage, input/output file fingerprints, page/chunk counts, and observed size/overlap statistics.

Generated chunks and reports are excluded from Git and Docker builds. No database or external API is needed.

For a second configuration:

```bash
uv run --locked python -m scripts.chunk_corpus --max-chars 800 --overlap-chars 120
```

That run writes to `data/chunks/page-char-v1-800-120/`, preserving the baseline run. `--config` selects another config file; `--output-dir` changes the base output directory. Config requires positive `max_chars` and `0 <= overlap_chars < max_chars`.

## Algorithm and scope

Each page is processed independently. Chunks never merge text across PDF pages or policy forms.

1. Take a window with at most `max_chars` characters.
2. Prefer a complete word ending within that window, while ensuring forward progress.
3. Start the next window within the configured overlap budget, preferring a whole-word start.
4. Split an unusually long unbroken word when needed to respect the hard size cap.
5. Omit whitespace-only windows, and cover every non-whitespace character in the parent page.

Overlap is a maximum: aligning whole words can reduce it, including to zero. Every record stores its actual overlap with the previous chunk on that page. Page endings may produce short chunks.

The baseline uses exact page-text slices, retaining the extraction stage's line breaks and line-end hyphenation. Changes to normalization or splitting rules require a new algorithm profile. Retrieval evaluation will determine whether a different size, overlap, normalization, or cross-page context policy is useful.

Input validation checks page text fingerprints, source/edition metadata, original positions and printed labels, extraction configuration, and consistent parser metadata. For the initial reviewed forms, every original PDF page contains selected text; the CLI requires the complete page sequence recorded in the corpus manifest. Missing, duplicate, reordered, or corrupt records fail before output publication. A future corpus that omits entire source pages will need explicit expected page ranges.

All inputs are validated and chunks are built before publishing outputs. Each completed file is replaced atomically, and the run report is written last. Repeat runs with unchanged inputs/configuration produce byte-identical outputs.

## Record contract

A chunk preserves the source page's corpus/document identity, title, section, edition, source URL/hash, PDF position, printed label, page ID, and extraction metadata. Its `text` and `text_sha256` describe the chunk, with these additional fields:

| Field | Meaning |
| --- | --- |
| `chunk_id` | SHA-256 identity derived from source/extraction lineage, parent text, configuration, offsets, and chunk text. |
| `chunk_index` | One-based chunk position within the parent page. |
| `page_text_sha256` | Fingerprint of the complete parent page text. |
| `char_start`, `char_end` | Half-open offsets into the original page text: `page.text[char_start:char_end]`. |
| `overlap_previous_chars` | Actual overlap with the previous emitted chunk on the same page; zero for the first. |
| `chunking` | Algorithm profile, size/overlap settings, and canonical configuration fingerprint. |

The same text at different source positions has different chunk IDs. Source, extraction, parent text, or configuration changes also change IDs, so later ingestion can distinguish revisions and experiments.

## Inspect a chunk against its parent page

```bash
uv run --locked python - <<'PY'
import json
from pathlib import Path

document = "nfip-dwelling-2025-10-01"
chunk_file = Path("data/chunks/page-char-v1-1200-200") / f"{document}.chunks.jsonl"
chunk = json.loads(chunk_file.read_text(encoding="utf-8").splitlines()[0])
page_file = Path("data/processed") / f"{document}.pages.jsonl"
pages = [json.loads(line) for line in page_file.read_text(encoding="utf-8").splitlines()]
page = next(item for item in pages if item["page_id"] == chunk["page_id"])
assert chunk["text"] == page["text"][chunk["char_start"]:chunk["char_end"]]
print(chunk["chunk_id"])
print("PDF page:", chunk["pdf_page_number"], "Printed:", chunk["printed_page_label"])
print("Characters:", len(chunk["text"]))
print(chunk["text"][:200])
PY
```

## Observed corpus checks

Local runs used the same 47 page records from the locked corpus and extraction profile:

| Max characters / overlap budget | Dwelling | General Property | RCBAP | Total chunks |
| --- | --- | --- | --- | --- |
| 1200 / 200 | 79 | 71 | 75 | 225 |
| 800 / 120 | 115 | 105 | 108 | 328 |

Both real-data runs were checked against their source-page slices, size limits, and overlap budgets. All 213,403 source-page characters were covered in each run; repeating the default run left every output byte unchanged.

These are chunking statistics. Answer correctness, retrieval quality, groundedness, model tokens, latency, and cost remain to be measured in later milestones.

Automated tests cover Unicode, long unbroken words, whitespace gaps, zero/high overlap, exact source slices, content coverage, lineage/configuration identity, invalid inputs, isolated run folders, determinism, and preservation of previous output on failure. CI uses synthetic page artifacts and requires no network, corpus download, database, or paid APIs.
