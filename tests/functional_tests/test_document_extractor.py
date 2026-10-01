import pytest

from backend.app.services.document_extractor import extract_document


def test_extracts_markdown_with_source_reference():
    result = extract_document("release.md", b"# Release\n\nNew audit log export.")

    assert result.filename == "release.md"
    assert result.source_refs == ["release.md#text"]
    assert "[SOURCE: release.md | TEXT]" in result.text
    assert "New audit log export." in result.text


@pytest.mark.parametrize(
    ("filename", "content", "message"),
    [
        ("empty.txt", b"  \n", "text document is empty"),
        ("image.pdf", b"not a pdf", "PDF"),
        ("notes.exe", b"data", "Unsupported file type"),
    ],
)
def test_rejects_invalid_or_empty_documents(filename, content, message):
    with pytest.raises(ValueError, match=message):
        extract_document(filename, content)