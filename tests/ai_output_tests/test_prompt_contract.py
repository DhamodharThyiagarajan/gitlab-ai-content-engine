from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.orchestration.workflow import ContextReaderAgent


def test_prompt_layer_exists():
    root = Path(__file__).resolve().parents[2]
    required = [
        "context_reader.md",
        "documentation_writer.md",
        "technical_reviewer.md",
        "tone_optimizer.md",
        "publishing_coordinator.md",
    ]
    for item in required:
        assert (root / "ai" / "prompts" / item).exists()


def test_context_reader_fallback_keeps_source_reference():
    source = "[SOURCE: release.md | TEXT]\nAudit exports include the actor and timestamp."

    result = ContextReaderAgent(ai=None)._fallback(source)

    assert result["source_refs"] == ["release.md | TEXT"]
    assert result["facts"][0]["source_refs"] == ["release.md | TEXT"]
    assert "actor and timestamp" in result["facts"][0]["fact"]
