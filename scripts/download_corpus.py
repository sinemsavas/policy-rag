"""Download the reviewed public corpus and verify its recorded fingerprints."""

import argparse
import hashlib
import sys
import tempfile
from datetime import date
from http.client import HTTPException
from pathlib import Path
from typing import Literal
from urllib.error import URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_SOURCE_BYTES = 5 * 1024 * 1024


class SourceDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1)
    source_url: HttpUrl
    author: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    edition_date: date
    language: Literal["en"]
    section_reference: str = Field(min_length=1)
    filename: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size_bytes: int = Field(gt=0, le=MAX_SOURCE_BYTES)
    pdf_pages: int = Field(gt=0)
    printed_page_range: str = Field(min_length=1)
    boundary_note: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_location(self) -> "SourceDocument":
        if self.source_url.scheme != "https":
            raise ValueError("Corpus sources must use HTTPS")
        if self.filename != f"{self.document_id}.pdf":
            raise ValueError("filename must be document_id followed by .pdf")
        return self


class ReuseReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewed_on: date
    basis: str = Field(min_length=1)
    evidence_url: HttpUrl
    scope_note: str = Field(min_length=1)


class CorpusManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1]
    corpus_id: str = Field(min_length=1)
    reuse_review: ReuseReview
    documents: list[SourceDocument] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_documents(self) -> "CorpusManifest":
        ids = [document.document_id for document in self.documents]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate document_id in corpus manifest")
        return self


def load_manifest(path: Path) -> CorpusManifest:
    return CorpusManifest.model_validate_json(path.read_text(encoding="utf-8"))


def verify_payload(document: SourceDocument, payload: bytes) -> None:
    if not payload.startswith(b"%PDF-"):
        raise ValueError(f"{document.document_id}: response is not a PDF")
    if len(payload) != document.size_bytes:
        raise ValueError(f"{document.document_id}: unexpected file size")
    if hashlib.sha256(payload).hexdigest() != document.sha256:
        raise ValueError(f"{document.document_id}: SHA-256 mismatch")


def download_document(document: SourceDocument, output_dir: Path) -> str:
    destination = output_dir / document.filename
    if destination.exists():
        with destination.open("rb") as existing:
            verify_payload(document, existing.read(document.size_bytes + 1))
        return f"verified {document.filename} (cached)"

    request = Request(
        str(document.source_url),
        headers={"User-Agent": "policy-rag/0.1 (public corpus download)"},
    )
    with urlopen(request, timeout=30) as response:
        payload = response.read(document.size_bytes + 1)
    verify_payload(document, payload)

    output_dir.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output_dir, prefix=document.document_id + "-", suffix=".part", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(payload)
        temporary_path.replace(destination)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return f"downloaded {document.filename} ({len(payload)} bytes)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=PROJECT_ROOT / "docs" / "corpus.json"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=PROJECT_ROOT / "data" / "raw"
    )
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.manifest)
        for document in manifest.documents:
            print(download_document(document, args.output_dir))
    except (ValueError, OSError, URLError, HTTPException) as exc:
        print(f"Corpus download failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
