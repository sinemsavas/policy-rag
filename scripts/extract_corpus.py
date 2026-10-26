"""Extract appendix text into page records from the reviewed CFR corpus."""

import argparse
import hashlib
import io
import json
import re
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Literal

import pypdf
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from scripts.download_corpus import (
    PROJECT_ROOT,
    SourceDocument,
    load_manifest,
    verify_payload,
)


class ExtractionMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: Literal["cfr-plain-v1"]
    parser: Literal["pypdf"] = "pypdf"
    parser_version: str
    config_sha256: str


class PageRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    corpus_id: str
    page_id: str
    document_id: str
    title: str
    section_reference: str
    edition_date: date
    source_url: HttpUrl
    source_sha256: str
    pdf_page_number: int = Field(ge=1)
    printed_page_label: str
    text: str = Field(min_length=1)
    text_sha256: str
    extraction: ExtractionMetadata


def clean_cfr_page(raw_text: str, expected_label: str) -> str:
    """Remove only the reviewed CFR publisher lines; preserve body line breaks."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if len(lines) < 4 or lines[0] != expected_label:
        raise ValueError(f"Expected printed page {expected_label}; missing text or label mismatch")
    if "44 CFR Ch. I" not in lines[1] and not lines[1].startswith(
        "Fed. Emergency Mgmt. Agency, DHS"
    ):
        raise ValueError(f"Printed page {expected_label}: unrecognized CFR header")
    footers = [i for i, line in enumerate(lines) if line.startswith("VerDate ")]
    if len(footers) != 1 or footers[0] < 3:
        raise ValueError(f"Printed page {expected_label}: missing or ambiguous publisher footer")
    body = "\n".join(lines[2:footers[0]])
    if not body.strip():
        raise ValueError(f"Printed page {expected_label}: no extractable body text")
    return body


def unique_marker(text: str, marker: str) -> re.Match[str]:
    # Literal headings may wrap across lines, but must begin at a line boundary.
    pattern = re.compile(
        r"^" + r"\s+".join(re.escape(word) for word in marker.split()) + r"[ \t]*$",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"Expected one section marker {marker!r}; found {len(matches)}")
    return matches[0]


def extract_document(
    document: SourceDocument, corpus_id: str, input_dir: Path
) -> list[PageRecord]:
    config = document.extraction
    if config is None:
        raise ValueError(f"{document.document_id}: no reviewed extraction configuration")

    with (input_dir / document.filename).open("rb") as source:
        payload = source.read(document.size_bytes + 1)
    verify_payload(document, payload)
    reader = PdfReader(io.BytesIO(payload), strict=True)
    if reader.is_encrypted:
        raise ValueError(f"{document.document_id}: encrypted PDFs are unsupported")
    if len(reader.pages) != document.pdf_pages:
        raise ValueError(f"{document.document_id}: PDF page count differs from manifest")

    label_range = re.fullmatch(r"([1-9]\d*)(?:-([1-9]\d*))?", document.printed_page_range)
    if label_range is None:
        raise ValueError(f"{document.document_id}: unsupported printed page range")
    first_label = int(label_range[1])
    last_label = int(label_range[2] or label_range[1])
    if last_label - first_label + 1 != document.pdf_pages:
        raise ValueError(f"{document.document_id}: printed range and page count disagree")

    page_texts = []
    for index, page in enumerate(reader.pages):
        if page.rotation != 0:
            raise ValueError(f"{document.document_id}: rotated pages need a separate profile")
        page_texts.append(
            clean_cfr_page(page.extract_text() or "", str(first_label + index))
        )

    joined = "\n".join(page_texts)
    start = unique_marker(joined, config.start_marker).start()
    end = unique_marker(joined, config.end_marker).start()
    if end <= start:
        raise ValueError(f"{document.document_id}: section end precedes its start")

    canonical_config = json.dumps(
        config.model_dump(), sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    metadata = ExtractionMetadata(
        profile=config.profile,
        parser_version=pypdf.__version__,
        config_sha256=hashlib.sha256(canonical_config.encode("utf-8")).hexdigest(),
    )
    records = []
    offset = 0
    for index, body in enumerate(page_texts):
        low, high = max(start, offset), min(end, offset + len(body))
        selected = joined[low:high].strip() if low < high else ""
        if selected:
            number = index + 1
            records.append(
                PageRecord(
                    corpus_id=corpus_id,
                    page_id=f"{document.document_id}:page:{number}",
                    document_id=document.document_id,
                    title=document.title,
                    section_reference=document.section_reference,
                    edition_date=document.edition_date,
                    source_url=document.source_url,
                    source_sha256=document.sha256,
                    pdf_page_number=number,
                    printed_page_label=str(first_label + index),
                    text=selected,
                    text_sha256=hashlib.sha256(selected.encode("utf-8")).hexdigest(),
                    extraction=metadata,
                )
            )
        offset += len(body) + 1
    if not records:
        raise ValueError(f"{document.document_id}: section produced no page records")
    return records


def write_records(path: Path, records: list[PageRecord]) -> str:
    payload = ("\n".join(record.model_dump_json() for record in records) + "\n").encode("utf-8")
    if path.exists() and path.read_bytes() == payload:
        return f"verified {path.name} ({len(records)} pages, unchanged)"

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
    return f"extracted {path.name} ({len(records)} pages)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=PROJECT_ROOT / "docs" / "corpus.json")
    parser.add_argument("--input-dir", type=Path, default=PROJECT_ROOT / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "data" / "processed")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        # Validate and extract the entire small corpus before replacing any output.
        documents = [
            (document, extract_document(document, manifest.corpus_id, args.input_dir))
            for document in manifest.documents
        ]
        for document, records in documents:
            path = args.output_dir / f"{document.document_id}.pages.jsonl"
            print(write_records(path, records))
    except (ValueError, OSError, PyPdfError) as exc:
        print(f"Corpus extraction failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
