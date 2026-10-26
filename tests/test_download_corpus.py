import hashlib
import io
import json
from urllib.error import URLError

import pytest
from pydantic import ValidationError

from scripts import download_corpus

PDF_BYTES = b"%PDF-1.7\npublic corpus test bytes\n%%EOF\n"


@pytest.fixture
def document():
    return download_corpus.SourceDocument(
        document_id="test-policy",
        title="Test policy",
        source_url="https://www.govinfo.gov/test-policy.pdf",
        author="Test government author",
        publisher="Test publisher",
        edition_date="2025-10-01",
        language="en",
        section_reference="Test section",
        filename="test-policy.pdf",
        sha256=hashlib.sha256(PDF_BYTES).hexdigest(),
        size_bytes=len(PDF_BYTES),
        pdf_pages=1,
        printed_page_range="1",
        boundary_note="Test metadata; bytes do not represent a parsed PDF.",
    )


def test_download_and_repeat_verify_cached_file(document, tmp_path, monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request.full_url, timeout))
        return io.BytesIO(PDF_BYTES)

    monkeypatch.setattr(download_corpus, "urlopen", fake_urlopen)
    first = download_corpus.download_document(document, tmp_path)
    second = download_corpus.download_document(document, tmp_path)

    assert (tmp_path / document.filename).read_bytes() == PDF_BYTES
    assert first.startswith("downloaded ")
    assert second.endswith("(cached)")
    assert calls == [(str(document.source_url), 30)]
    assert list(tmp_path.glob("*.part")) == []


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        (b"<html>Access denied</html>", "not a PDF"),
        (PDF_BYTES[:-1], "unexpected file size"),
        (PDF_BYTES.replace(b"test", b"fake"), "SHA-256 mismatch"),
    ],
)
def test_invalid_download_is_not_saved(document, tmp_path, monkeypatch, payload, error):
    monkeypatch.setattr(
        download_corpus, "urlopen", lambda *args, **kwargs: io.BytesIO(payload)
    )

    with pytest.raises(ValueError, match=error):
        download_corpus.download_document(document, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_corrupt_cache_is_preserved_and_reported(document, tmp_path, monkeypatch):
    destination = tmp_path / document.filename
    corrupt = PDF_BYTES.replace(b"test", b"fake")
    destination.write_bytes(corrupt)

    def unexpected_download(*args, **kwargs):
        raise AssertionError("An existing file must be verified before any download")

    monkeypatch.setattr(download_corpus, "urlopen", unexpected_download)
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        download_corpus.download_document(document, tmp_path)
    assert destination.read_bytes() == corrupt


@pytest.mark.parametrize("filename", ["../outside.pdf", "/tmp/outside.pdf"])
def test_manifest_rejects_output_path_escape(document, filename):
    values = document.model_dump()
    values["filename"] = filename
    with pytest.raises(ValidationError, match="filename must be"):
        download_corpus.SourceDocument.model_validate(values)


def test_manifest_rejects_duplicate_documents(document):
    manifest = download_corpus.load_manifest(
        download_corpus.PROJECT_ROOT / "docs" / "corpus.json"
    ).model_dump()
    manifest["documents"] = [document.model_dump(), document.model_dump()]
    with pytest.raises(ValidationError, match="Duplicate document_id"):
        download_corpus.CorpusManifest.model_validate(manifest)


def test_cli_reports_network_failure(document, tmp_path, monkeypatch, capsys):
    manifest = download_corpus.load_manifest(
        download_corpus.PROJECT_ROOT / "docs" / "corpus.json"
    ).model_dump(mode="json")
    manifest["documents"] = [document.model_dump(mode="json")]
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    output_dir = tmp_path / "raw"

    def unavailable(*args, **kwargs):
        raise URLError("service unavailable")

    monkeypatch.setattr(download_corpus, "urlopen", unavailable)
    result = download_corpus.main(
        ["--manifest", str(manifest_path), "--output-dir", str(output_dir)]
    )

    assert result == 1
    assert "service unavailable" in capsys.readouterr().err
    assert not output_dir.exists()
