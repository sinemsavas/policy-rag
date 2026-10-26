import hashlib
import json

import pytest
from pydantic import ValidationError

from scripts import chunk_corpus
from scripts.download_corpus import PROJECT_ROOT, load_manifest
from scripts.extract_corpus import ExtractionMetadata, PageRecord


def make_page(document, corpus_id, number, text):
    first_label = int(document.printed_page_range.split("-")[0])
    return PageRecord(
        corpus_id=corpus_id,
        page_id=f"{document.document_id}:page:{number}",
        document_id=document.document_id,
        title=document.title,
        section_reference=document.section_reference,
        edition_date=document.edition_date,
        source_url=document.source_url,
        source_sha256=document.sha256,
        pdf_page_number=number,
        printed_page_label=str(first_label + number - 1),
        text=text,
        text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        extraction=ExtractionMetadata(
            profile=document.extraction.profile,
            parser_version="synthetic-test-version",
            config_sha256=chunk_corpus.fingerprint_json(document.extraction.model_dump()),
        ),
    )


@pytest.fixture
def page_factory():
    manifest = load_manifest(PROJECT_ROOT / "docs" / "corpus.json")

    def create(text, number=1):
        return make_page(manifest.documents[0], manifest.corpus_id, number, text)

    return create


@pytest.mark.parametrize(
    "values",
    [
        {"max_chars": 0},
        {"max_chars": -1},
        {"overlap_chars": -1},
        {"max_chars": 10, "overlap_chars": 10},
        {"max_chars": 10, "overlap_chars": 11},
        {"max_chars": True},
        {"max_chars": 12.5},
    ],
)
def test_invalid_limits_are_rejected(values):
    with pytest.raises(ValidationError):
        chunk_corpus.ChunkingConfig.model_validate(values)


@pytest.mark.parametrize("limits", [(32, 0), (32, 8), (32, 31), (1, 0)])
@pytest.mark.parametrize("text", [
    "one two three four five six seven eight nine. " * 7,
    "İstanbul café naïve 😊\nAnkara ödeme koşulları. " * 5,
    "x" * 131,
    "start" + " \n\t" * 50 + "end",
    "trans-\nfer the full policy amount $250,000.\nKeep all punctuation.",
])
def test_chunks_preserve_spans_cover_content_and_respect_limits(page_factory, limits, text):
    config = chunk_corpus.ChunkingConfig(max_chars=limits[0], overlap_chars=limits[1])
    page = page_factory(text)
    chunks = chunk_corpus.chunk_page(page, config)

    covered = set()
    previous = None
    for index, chunk in enumerate(chunks, start=1):
        assert chunk.text == text[chunk.char_start:chunk.char_end]
        assert 0 < len(chunk.text) <= config.max_chars
        assert chunk.text.strip()
        assert chunk.chunk_index == index
        assert chunk.page_id == page.page_id
        assert chunk.pdf_page_number == page.pdf_page_number
        assert chunk.printed_page_label == page.printed_page_label
        assert chunk.source_url == page.source_url
        assert chunk.source_sha256 == page.source_sha256
        assert chunk.page_text_sha256 == page.text_sha256
        assert chunk.text_sha256 == hashlib.sha256(chunk.text.encode()).hexdigest()
        assert chunk.chunking.config_sha256 == config.fingerprint()
        assert chunk.chunking.fingerprint() == config.fingerprint()
        expected_overlap = max(0, previous.char_end - chunk.char_start) if previous else 0
        assert chunk.overlap_previous_chars == expected_overlap
        assert expected_overlap <= config.overlap_chars
        if previous:
            assert chunk.char_start > previous.char_start
            assert chunk.char_end > previous.char_end
        covered.update(range(chunk.char_start, chunk.char_end))
        previous = chunk

    assert chunks
    assert all(index in covered for index, char in enumerate(text) if not char.isspace())
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)
    assert [chunk.model_dump_json() for chunk in chunks] == [
        chunk.model_dump_json() for chunk in chunk_corpus.chunk_page(page, config)
    ]


def test_prefers_word_boundaries_and_records_actual_overlap(page_factory):
    text = "one two three four five six seven eight nine ten eleven twelve"
    config = chunk_corpus.ChunkingConfig(max_chars=20, overlap_chars=7)
    chunks = chunk_corpus.chunk_page(page_factory(text), config)

    for chunk in chunks:
        assert chunk.char_end == len(text) or text[chunk.char_end].isspace()
        assert chunk.char_start == 0 or text[chunk.char_start - 1].isspace() or text[chunk.char_start].isspace()
    assert any(chunk.overlap_previous_chars > 0 for chunk in chunks)
    assert any(chunk.overlap_previous_chars < config.overlap_chars for chunk in chunks[1:])


@pytest.mark.parametrize("change", ["source", "extraction", "parser", "page", "text"])
def test_lineage_changes_produce_different_ids(page_factory, change):
    page = page_factory("Repeated policy text. " * 10)
    config = chunk_corpus.ChunkingConfig(max_chars=40, overlap_chars=10)
    original = chunk_corpus.chunk_page(page, config)
    revised = page.model_copy(deep=True)
    if change == "source":
        revised.source_sha256 = "0" * 64
    elif change == "extraction":
        revised.extraction.config_sha256 = "1" * 64
    elif change == "parser":
        revised.extraction.parser_version = "another-test-version"
    elif change == "page":
        revised.pdf_page_number = 2
        revised.printed_page_label = "157"
        revised.page_id = revised.document_id + ":page:2"
    else:
        revised.text += "changed"
        revised.text_sha256 = hashlib.sha256(revised.text.encode()).hexdigest()

    updated = chunk_corpus.chunk_page(revised, config)
    assert {c.chunk_id for c in original}.isdisjoint(c.chunk_id for c in updated)


def test_other_config_changes_ids_even_for_short_unchanged_text(page_factory):
    page = page_factory("Short text.")
    first = chunk_corpus.chunk_page(page, chunk_corpus.ChunkingConfig(max_chars=40, overlap_chars=10))
    second = chunk_corpus.chunk_page(page, chunk_corpus.ChunkingConfig(max_chars=60, overlap_chars=10))
    assert first[0].text == second[0].text
    assert first[0].chunk_id != second[0].chunk_id


@pytest.fixture
def inputs(tmp_path):
    values = load_manifest(PROJECT_ROOT / "docs" / "corpus.json").model_dump(mode="json")
    values["documents"] = values["documents"][:2]
    for document in values["documents"]:
        first = int(document["printed_page_range"].split("-")[0])
        document["pdf_pages"] = 2
        document["printed_page_range"] = f"{first}-{first + 1}"
    manifest_path = tmp_path / "corpus.json"
    manifest_path.write_text(json.dumps(values), encoding="utf-8")
    manifest = load_manifest(manifest_path)
    input_dir = tmp_path / "processed"
    input_dir.mkdir()
    for document in manifest.documents:
        pages = [make_page(
            document, manifest.corpus_id, number,
            (document.extraction.start_marker + "\n" if number == 1 else "")
            + (f"PAGE_{number}_ONLY Policy coverage and exclusions. " * 4),
        ) for number in (1, 2)]
        path = input_dir / f"{document.document_id}.pages.jsonl"
        path.write_text("\n".join(page.model_dump_json() for page in pages) + "\n", encoding="utf-8")
    output_dir = tmp_path / "chunks"
    config_path = tmp_path / "chunking.json"
    config_path.write_text('{"profile":"page-char-v1","max_chars":64,"overlap_chars":16}', encoding="utf-8")
    args = ["--manifest", str(manifest_path), "--config", str(config_path),
            "--input-dir", str(input_dir), "--output-dir", str(output_dir)]
    return manifest, input_dir, output_dir, args


@pytest.mark.parametrize("damage", [
    "text", "source", "label", "page_id", "extraction", "parser",
    "missing_first", "missing_last", "duplicate", "reordered", "blank_line", "invalid_json",
])
def test_bad_page_artifacts_fail_before_outputs(inputs, damage, capsys):
    manifest, input_dir, output_dir, args = inputs
    document = manifest.documents[0]
    path = input_dir / f"{document.document_id}.pages.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines()]
    if damage == "text":
        records[0]["text"] += "tampered"
    elif damage == "source":
        records[0]["source_sha256"] = "0" * 64
    elif damage == "label":
        records[0]["printed_page_label"] = "999"
    elif damage == "page_id":
        records[0]["page_id"] = "wrong-page"
    elif damage == "extraction":
        records[0]["extraction"]["config_sha256"] = "0" * 64
    elif damage == "parser":
        records[1]["extraction"]["parser_version"] = "different-test-version"
    elif damage == "missing_first":
        records = records[1:]
    elif damage == "missing_last":
        records = records[:1]
    elif damage == "duplicate":
        records[1] = records[0]
    elif damage == "reordered":
        records.reverse()
    lines = [json.dumps(record) for record in records]
    if damage == "blank_line":
        lines.insert(1, "")
    elif damage == "invalid_json":
        lines[0] = "not JSON"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert chunk_corpus.main(args) == 1
    assert "Corpus chunking failed:" in capsys.readouterr().err
    assert not output_dir.exists()


def test_cli_repeats_deterministically_and_keeps_configs_separate(inputs):
    manifest, input_dir, output_dir, args = inputs
    assert chunk_corpus.main(args) == 0
    first_dir = output_dir / "page-char-v1-64-16"
    original = {path.name: path.read_bytes() for path in first_dir.iterdir()}
    report = json.loads(original["report.json"])
    assert report["total_pages"] == 4
    total_chunks = 0
    for document in manifest.documents:
        source_path = input_dir / f"{document.document_id}.pages.jsonl"
        parents = {p.page_id: p for p in [PageRecord.model_validate_json(line) for line in source_path.read_text().splitlines()]}
        filename = document.document_id + ".chunks.jsonl"
        chunks = [chunk_corpus.ChunkRecord.model_validate_json(line) for line in original[filename].splitlines()]
        for chunk in chunks:
            parent = parents[chunk.page_id]
            assert chunk.text == parent.text[chunk.char_start:chunk.char_end]
            assert not ("PAGE_1_ONLY" in chunk.text and "PAGE_2_ONLY" in chunk.text)
        summary = next(item for item in report["documents"] if item["document_id"] == document.document_id)
        assert summary["page_artifact_sha256"] == hashlib.sha256(source_path.read_bytes()).hexdigest()
        assert summary["chunks_sha256"] == hashlib.sha256(original[filename]).hexdigest()
        assert summary["chunks"] == len(chunks)
        total_chunks += len(chunks)
    assert report["total_chunks"] == total_chunks

    assert chunk_corpus.main(args) == 0
    assert {p.name: p.read_bytes() for p in first_dir.iterdir()} == original
    assert chunk_corpus.main(args + ["--max-chars", "48", "--overlap-chars", "8"]) == 0
    second_dir = output_dir / "page-char-v1-48-8"
    assert second_dir.exists()
    assert {p.name: p.read_bytes() for p in first_dir.iterdir()} == original
    second_report = json.loads((second_dir / "report.json").read_text())
    assert second_report["chunking"]["config_sha256"] != report["chunking"]["config_sha256"]


def test_failed_second_document_preserves_previous_outputs(inputs, monkeypatch):
    manifest, input_dir, output_dir, args = inputs
    assert chunk_corpus.main(args) == 0
    before = {p.relative_to(output_dir): p.read_bytes() for p in output_dir.rglob("*") if p.is_file()}
    path = input_dir / (manifest.documents[1].document_id + ".pages.jsonl")
    path.write_text("bad input\n", encoding="utf-8")

    def unexpected_publication(*args, **kwargs):
        raise AssertionError("All inputs must be validated before publication")

    monkeypatch.setattr(chunk_corpus, "write_bytes", unexpected_publication)
    assert chunk_corpus.main(args) == 1
    assert {p.relative_to(output_dir): p.read_bytes() for p in output_dir.rglob("*") if p.is_file()} == before


def test_atomic_write_failure_preserves_existing_file(tmp_path, monkeypatch):
    output = tmp_path / "record.jsonl"
    output.write_bytes(b"previous output\n")

    def unavailable(*args, **kwargs):
        raise OSError("simulated disk failure")

    monkeypatch.setattr(type(output), "replace", unavailable)
    with pytest.raises(OSError, match="simulated disk failure"):
        chunk_corpus.write_bytes(output, b"new output\n")
    assert output.read_bytes() == b"previous output\n"
    assert list(tmp_path.iterdir()) == [output]
