import hashlib
import json

import pytest

from scripts import download_corpus, extract_corpus

START = "APPENDIX A(1) TO PART 61"
END = "APPENDIX A(2) TO PART 61"
BODY_PAGES = [
    [
        (132, 600, "NEIGHBOR BEFORE"),
        (132, 585, "Previous policy ends here."),
        (312, 600, START),
        (312, 585, "Included first page."),
    ],
    [
        (132, 600, "Included final page."),
        (132, 585, "Keep the policy amount $250,000."),
        (312, 600, END),
        (312, 585, "NEIGHBOR AFTER"),
    ],
]


def make_pdf(body_pages):
    """Build tiny real PDFs with two columns, labels, headers, and footers."""
    kids = " ".join(f"{4 + 2 * n} 0 R" for n in range(len(body_pages)))
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {len(body_pages)} >>".encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    for index, body in enumerate(body_pages):
        rows = [
            (298, 66, str(156 + index)),
            (132, 626, "44 CFR Ch. I (10-1-25 Edition) Pt. 61"),
            *body,
            (25, 20, "VerDate TEST PUBLISHER FOOTER"),
        ]
        operators = []
        for x, y, text in rows:
            escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            operators.append(f"BT /F1 10 Tf 1 0 0 1 {x} {y} Tm ({escaped}) Tj ET\n")
        stream = "".join(operators).encode("ascii")
        objects.extend(
            [
                (
                    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    "/Resources << /Font << /F1 3 0 R >> >> "
                    f"/Contents {5 + 2 * index} 0 R >>"
                ).encode(),
                f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"endstream",
            ]
        )
    result = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, value in enumerate(objects, start=1):
        offsets.append(len(result))
        result.extend(f"{number} 0 obj\n".encode() + value + b"\nendobj\n")
    xref = len(result)
    result.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode())
    result.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(result)


@pytest.fixture
def source_factory(tmp_path):
    def create(pages=None, **changes):
        pages = BODY_PAGES if pages is None else pages
        payload = make_pdf(pages)
        manifest = download_corpus.load_manifest(
            download_corpus.PROJECT_ROOT / "docs" / "corpus.json"
        )
        values = manifest.documents[0].model_dump(mode="json")
        values.update(
            document_id="test-policy",
            filename="test-policy.pdf",
            title="Synthetic test policy",
            source_url="https://www.govinfo.gov/test-policy.pdf",
            sha256=hashlib.sha256(payload).hexdigest(),
            size_bytes=len(payload),
            pdf_pages=len(pages),
            printed_page_range=f"156-{155 + len(pages)}",
            extraction={"profile": "cfr-plain-v1", "start_marker": START, "end_marker": END},
        )
        values.update(changes)
        document = download_corpus.SourceDocument.model_validate(values)
        source_dir = tmp_path / "raw"
        source_dir.mkdir(exist_ok=True)
        (source_dir / document.filename).write_bytes(payload)
        return document, source_dir

    return create


def test_real_pdf_extraction_keeps_identity_and_only_target_section(source_factory):
    document, source_dir = source_factory()
    records = extract_corpus.extract_document(document, "test-corpus", source_dir)

    assert [record.pdf_page_number for record in records] == [1, 2]
    assert [record.printed_page_label for record in records] == ["156", "157"]
    assert records[0].text == START + "\nIncluded first page."
    assert records[1].text == "Included final page.\nKeep the policy amount $250,000."
    for record in records:
        assert record.corpus_id == "test-corpus"
        assert record.document_id == document.document_id
        assert record.source_sha256 == document.sha256
        assert record.source_url == document.source_url
        assert record.text_sha256 == hashlib.sha256(record.text.encode()).hexdigest()
        assert "NEIGHBOR" not in record.text
        assert "VerDate" not in record.text
        assert "44 CFR Ch." not in record.text
        assert record.extraction.parser == "pypdf"
        assert record.extraction.parser_version


def test_excluded_pages_do_not_renumber_pdf_positions(source_factory):
    pages = [[(132, 600, "Only neighboring material on this page.")], *BODY_PAGES]
    document, source_dir = source_factory(pages=pages)
    records = extract_corpus.extract_document(document, "test-corpus", source_dir)

    assert [record.pdf_page_number for record in records] == [2, 3]
    assert [record.printed_page_label for record in records] == ["157", "158"]
    assert records[0].page_id == "test-policy:page:2"


def test_wrapped_end_heading_is_excluded(source_factory):
    pages = [BODY_PAGES[0], [
        (132, 600, "Included final page."),
        (132, 585, "Still part of this policy."),
        (312, 600, "APPENDIX A(2) TO"),
        (312, 585, "PART 61"),
        (312, 570, "NEIGHBOR AFTER"),
    ]]
    document, source_dir = source_factory(pages=pages)
    records = extract_corpus.extract_document(document, "test-corpus", source_dir)
    assert records[-1].text == "Included final page.\nStill part of this policy."


@pytest.mark.parametrize(
    ("start", "end", "error"),
    [
        ("MISSING START", END, "found 0"),
        (START, "MISSING END", "found 0"),
        (END, START, "end precedes its start"),
    ],
)
def test_uncertain_boundaries_fail(source_factory, start, end, error):
    document, source_dir = source_factory(extraction={
        "profile": "cfr-plain-v1", "start_marker": start, "end_marker": end,
    })
    with pytest.raises(ValueError, match=error):
        extract_corpus.extract_document(document, "test-corpus", source_dir)


def test_duplicate_section_heading_fails(source_factory):
    pages = [BODY_PAGES[0], [
        (132, 600, START), (132, 585, "Duplicate heading."),
        (312, 600, END), (312, 585, "NEIGHBOR AFTER"),
    ]]
    document, source_dir = source_factory(pages=pages)
    with pytest.raises(ValueError, match="found 2"):
        extract_corpus.extract_document(document, "test-corpus", source_dir)


def test_heading_prefix_does_not_select_a_different_part(source_factory):
    pages = [[
        (132, 600, "APPENDIX A(1) TO PART 610"),
        (132, 585, "Different part with the same heading prefix."),
        (312, 600, END),
    ]]
    document, source_dir = source_factory(pages=pages)
    with pytest.raises(ValueError, match="found 0"):
        extract_corpus.extract_document(document, "test-corpus", source_dir)


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"pdf_pages": 3}, "page count differs"),
        ({"printed_page_range": "200-201"}, "label mismatch"),
        ({"extraction": None}, "no reviewed extraction configuration"),
    ],
)
def test_metadata_mismatch_fails(source_factory, changes, error):
    document, source_dir = source_factory(**changes)
    with pytest.raises(ValueError, match=error):
        extract_corpus.extract_document(document, "test-corpus", source_dir)


def test_blank_body_fails_instead_of_silently_omitting_page(source_factory):
    document, source_dir = source_factory(pages=[[]])
    with pytest.raises(ValueError, match="missing text"):
        extract_corpus.extract_document(document, "test-corpus", source_dir)


def test_hash_is_verified_before_parsing(source_factory, monkeypatch):
    document, source_dir = source_factory(sha256="0" * 64)

    def unexpected_parse(*args, **kwargs):
        raise AssertionError("Unverified bytes must not reach the PDF parser")

    monkeypatch.setattr(extract_corpus, "PdfReader", unexpected_parse)
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        extract_corpus.extract_document(document, "test-corpus", source_dir)


def test_jsonl_is_deterministic_and_repeat_run_keeps_one_file(source_factory, tmp_path):
    document, source_dir = source_factory()
    first = extract_corpus.extract_document(document, "test-corpus", source_dir)
    output = tmp_path / "processed" / "test-policy.pages.jsonl"
    extract_corpus.write_records(output, first)
    original_bytes = output.read_bytes()
    second = extract_corpus.extract_document(document, "test-corpus", source_dir)

    result = extract_corpus.write_records(output, second)

    assert result.endswith("unchanged)")
    assert output.read_bytes() == original_bytes
    assert len(output.read_text().splitlines()) == 2
    decoded = [extract_corpus.PageRecord.model_validate_json(line) for line in output.read_text().splitlines()]
    assert decoded == first
    assert list(output.parent.iterdir()) == [output]


def test_cli_preserves_previous_outputs_if_another_document_fails(source_factory, tmp_path, capsys):
    first, source_dir = source_factory()
    second, _ = source_factory(
        document_id="test-policy-two", filename="test-policy-two.pdf",
        extraction={"profile": "cfr-plain-v1", "start_marker": "MISSING", "end_marker": END},
    )
    manifest = download_corpus.load_manifest(
        download_corpus.PROJECT_ROOT / "docs" / "corpus.json"
    ).model_dump(mode="json")
    manifest["documents"] = [first.model_dump(mode="json"), second.model_dump(mode="json")]
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    previous = output_dir / "test-policy.pages.jsonl"
    previous.write_bytes(b"previous successful output\n")

    result = extract_corpus.main([
        "--manifest", str(manifest_path), "--input-dir", str(source_dir),
        "--output-dir", str(output_dir),
    ])

    assert result == 1
    assert "MISSING" in capsys.readouterr().err
    assert previous.read_bytes() == b"previous successful output\n"
    assert list(output_dir.iterdir()) == [previous]


def test_failed_file_publication_preserves_previous_output(source_factory, tmp_path, monkeypatch):
    document, source_dir = source_factory()
    records = extract_corpus.extract_document(document, "test-corpus", source_dir)
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    previous = output_dir / "test-policy.pages.jsonl"
    previous.write_bytes(b"previous successful output\n")

    def disk_failure(*args, **kwargs):
        raise OSError("simulated disk failure")

    monkeypatch.setattr(type(previous), "replace", disk_failure)
    with pytest.raises(OSError, match="simulated disk failure"):
        extract_corpus.write_records(previous, records)
    assert previous.read_bytes() == b"previous successful output\n"
    assert list(output_dir.iterdir()) == [previous]
