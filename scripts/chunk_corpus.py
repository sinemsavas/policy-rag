"""Create reproducible, page-contained chunks from the reviewed page records."""

import argparse
import hashlib
import json
import re
import sys
import tempfile
from bisect import bisect_left, bisect_right
from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scripts.download_corpus import PROJECT_ROOT, SourceDocument, load_manifest
from scripts.extract_corpus import PageRecord, unique_marker

MAX_PAGE_FILE_BYTES = 10 * 1024 * 1024


def fingerprint_json(value: dict) -> str:
    encoded = json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class ChunkingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: Literal["page-char-v1"] = "page-char-v1"
    max_chars: int = Field(default=1200, strict=True, ge=1, le=100_000)
    overlap_chars: int = Field(default=200, strict=True, ge=0)

    @model_validator(mode="after")
    def overlap_is_smaller_than_window(self) -> "ChunkingConfig":
        if self.overlap_chars >= self.max_chars:
            raise ValueError("overlap_chars must be smaller than max_chars")
        return self

    def fingerprint(self) -> str:
        return fingerprint_json(self.model_dump(exclude={"config_sha256"}))

    def run_name(self) -> str:
        return f"{self.profile}-{self.max_chars}-{self.overlap_chars}"


class ChunkingMetadata(ChunkingConfig):
    config_sha256: str


class ChunkRecord(PageRecord):
    # Inherited text/hash fields describe this chunk; retain its parent hash below.
    chunk_id: str
    chunk_index: int = Field(ge=1)
    page_text_sha256: str
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    overlap_previous_chars: int = Field(ge=0)
    chunking: ChunkingMetadata

    @model_validator(mode="after")
    def consistent_span(self) -> "ChunkRecord":
        if self.char_end - self.char_start != len(self.text):
            raise ValueError("Chunk text length does not match its character offsets")
        if not self.text.strip() or len(self.text) > self.chunking.max_chars:
            raise ValueError("Chunk text must be nonblank and respect max_chars")
        if self.overlap_previous_chars > self.chunking.overlap_chars:
            raise ValueError("Chunk overlap exceeds the configured maximum")
        return self


def character_spans(text: str, config: ChunkingConfig) -> Iterator[tuple[int, int]]:
    """Prefer whole words; keep hard bounds and make progress on long tokens."""
    words = list(re.finditer(r"\S+", text))
    starts = [word.start() for word in words]
    ends = [word.end() for word in words]
    word_ends = set(ends)
    start = 0
    while start < len(text):
        hard_end = min(start + config.max_chars, len(text))
        end = hard_end
        if hard_end < len(text):
            index = bisect_right(ends, hard_end) - 1
            if index >= 0 and ends[index] > start + config.overlap_chars:
                end = ends[index]
        yield start, end
        if end == len(text):
            break

        candidate = max(start + 1, end - config.overlap_chars)
        if end in word_ends:
            index = bisect_left(starts, candidate)
            # Whole words may reduce overlap; never exceed the character budget.
            candidate = starts[index] if index < len(starts) and starts[index] < end else end
        start = candidate


def chunk_page(page: PageRecord, config: ChunkingConfig) -> list[ChunkRecord]:
    if not page.text.strip():
        raise ValueError(f"{page.page_id}: page text is blank")
    actual_hash = hashlib.sha256(page.text.encode("utf-8")).hexdigest()
    if actual_hash != page.text_sha256:
        raise ValueError(f"{page.page_id}: page text SHA-256 mismatch")

    metadata = ChunkingMetadata(**config.model_dump(), config_sha256=config.fingerprint())
    parent = page.model_dump(exclude={"text", "text_sha256"})
    chunks = []
    previous_end = 0
    for start, end in character_spans(page.text, config):
        selected = page.text[start:end]
        if not selected.strip():
            continue
        text_hash = hashlib.sha256(selected.encode("utf-8")).hexdigest()
        identity = {
            "corpus_id": page.corpus_id,
            "document_id": page.document_id,
            "edition_date": page.edition_date.isoformat(),
            "section_reference": page.section_reference,
            "page_id": page.page_id,
            "source_sha256": page.source_sha256,
            "page_text_sha256": page.text_sha256,
            "extraction": page.extraction.model_dump(),
            "chunking_config_sha256": config.fingerprint(),
            "char_start": start,
            "char_end": end,
            "text_sha256": text_hash,
        }
        chunks.append(ChunkRecord(
            **parent,
            text=selected,
            text_sha256=text_hash,
            chunk_id="chunk_" + fingerprint_json(identity),
            chunk_index=len(chunks) + 1,
            page_text_sha256=page.text_sha256,
            char_start=start,
            char_end=end,
            overlap_previous_chars=max(0, previous_end - start) if chunks else 0,
            chunking=metadata,
        ))
        previous_end = end
    return chunks


def load_pages(
    document: SourceDocument, corpus_id: str, input_dir: Path
) -> tuple[list[PageRecord], str]:
    path = input_dir / f"{document.document_id}.pages.jsonl"
    with path.open("rb") as source:
        payload = source.read(MAX_PAGE_FILE_BYTES + 1)
    if len(payload) > MAX_PAGE_FILE_BYTES:
        raise ValueError(f"{path.name}: page file exceeds the local corpus limit")
    if document.extraction is None:
        raise ValueError(f"{document.document_id}: no reviewed extraction configuration")
    label_range = re.fullmatch(r"([1-9]\d*)(?:-([1-9]\d*))?", document.printed_page_range)
    if label_range is None:
        raise ValueError(f"{document.document_id}: unsupported printed page range")
    first_label = int(label_range[1])
    last_label = int(label_range[2] or label_range[1])
    if last_label - first_label + 1 != document.pdf_pages:
        raise ValueError(f"{document.document_id}: printed range and page count disagree")

    expected = {
        "corpus_id": corpus_id,
        "document_id": document.document_id,
        "title": document.title,
        "section_reference": document.section_reference,
        "edition_date": document.edition_date,
        "source_url": document.source_url,
        "source_sha256": document.sha256,
    }
    config_hash = fingerprint_json(document.extraction.model_dump())
    pages = []
    for line_number, line in enumerate(payload.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"{path.name}: blank JSONL record on line {line_number}")
        page = PageRecord.model_validate_json(line)
        if any(getattr(page, key) != value for key, value in expected.items()):
            raise ValueError(f"{path.name}: source metadata mismatch on line {line_number}")
        if page.pdf_page_number != line_number:
            raise ValueError(f"{path.name}: missing, duplicate, or out-of-order page")
        if page.page_id != f"{document.document_id}:page:{page.pdf_page_number}":
            raise ValueError(f"{path.name}: inconsistent page_id")
        if page.printed_page_label != str(first_label + page.pdf_page_number - 1):
            raise ValueError(f"{path.name}: printed page label mismatch")
        if (
            page.extraction.config_sha256 != config_hash
            or page.extraction.profile != document.extraction.profile
            or not page.extraction.parser_version.strip()
            or (pages and page.extraction != pages[0].extraction)
        ):
            raise ValueError(f"{path.name}: extraction metadata mismatch")
        if hashlib.sha256(page.text.encode("utf-8")).hexdigest() != page.text_sha256:
            raise ValueError(f"{path.name}: page text SHA-256 mismatch")
        if not page.text.strip():
            raise ValueError(f"{path.name}: blank page text")
        pages.append(page)
    # The initial reviewed forms contain selected text on every original PDF page.
    if len(pages) != document.pdf_pages:
        raise ValueError(f"{path.name}: incomplete page file; rerun extraction")
    if unique_marker(pages[0].text, document.extraction.start_marker).start() != 0:
        raise ValueError(f"{path.name}: target appendix does not start at the first record")
    return pages, hashlib.sha256(payload).hexdigest()


def write_bytes(path: Path, payload: bytes) -> str:
    if path.exists() and path.read_bytes() == payload:
        return "verified"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=path.stem + "-", suffix=".tmp", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(payload)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return "written"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=PROJECT_ROOT / "docs" / "corpus.json")
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "docs" / "chunking.json")
    parser.add_argument("--input-dir", type=Path, default=PROJECT_ROOT / "data" / "processed")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "data" / "chunks")
    parser.add_argument("--max-chars", type=int)
    parser.add_argument("--overlap-chars", type=int)
    args = parser.parse_args(argv)

    try:
        values = json.loads(args.config.read_text(encoding="utf-8"))
        for name in ("max_chars", "overlap_chars"):
            if getattr(args, name) is not None:
                values[name] = getattr(args, name)
        config = ChunkingConfig.model_validate(values)
        manifest = load_manifest(args.manifest)
        prepared = []
        summaries = []
        for document in manifest.documents:
            pages, artifact_hash = load_pages(document, manifest.corpus_id, args.input_dir)
            chunks = [chunk for page in pages for chunk in chunk_page(page, config)]
            payload = ("\n".join(chunk.model_dump_json() for chunk in chunks) + "\n").encode("utf-8")
            prepared.append((document.document_id, payload, len(chunks)))
            summaries.append({
                "document_id": document.document_id,
                "source_sha256": document.sha256,
                "page_artifact_sha256": artifact_hash,
                "extraction": pages[0].extraction.model_dump(),
                "input_pages": len(pages),
                "input_characters": sum(len(page.text) for page in pages),
                "chunks": len(chunks),
                "chunk_characters_including_overlap": sum(len(c.text) for c in chunks),
                "max_chunk_characters": max(len(c.text) for c in chunks),
                "max_actual_overlap_characters": max(c.overlap_previous_chars for c in chunks),
                "chunks_sha256": hashlib.sha256(payload).hexdigest(),
            })

        run_dir = args.output_dir / config.run_name()
        for document_id, payload, count in prepared:
            path = run_dir / f"{document_id}.chunks.jsonl"
            action = write_bytes(path, payload)
            print(f"{action} {path.name} ({count} chunks)")
        report = {
            "schema_version": 1,
            "corpus_id": manifest.corpus_id,
            "chunking": {**config.model_dump(), "config_sha256": config.fingerprint()},
            "total_pages": sum(doc["input_pages"] for doc in summaries),
            "total_chunks": sum(doc["chunks"] for doc in summaries),
            "documents": summaries,
        }
        report_payload = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        write_bytes(run_dir / "report.json", report_payload)
        print(f"report: {run_dir / 'report.json'}")
    except (ValueError, OSError, TypeError) as exc:
        print(f"Corpus chunking failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
