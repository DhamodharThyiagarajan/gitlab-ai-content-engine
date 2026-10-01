from pathlib import Path


def test_sample_inputs_and_templates_exist():
    root = Path(__file__).resolve().parents[2]
    assert (root / "data" / "sample_inputs" / "release_notes.txt").exists()
    assert (root / "data" / "sample_docs" / "audit-log-export.md").is_file()
    assert (root / "data" / "style_guides" / "product-documentation.md").is_file()
    assert (root / "data" / "content_templates" / "release-notes.md").is_file()
    assert (root / "docs" / "api_documentation.md").exists()
