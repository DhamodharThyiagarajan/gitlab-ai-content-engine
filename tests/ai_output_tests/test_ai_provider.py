
import pytest

from app.services.ai_provider import AIProvider


@pytest.mark.anyio
async def test_ai_provider_mock_generation():
    provider = AIProvider()

    result = await provider.generate(
        system="You are a documentation assistant.",
        user="Generate documentation for a test document. Title: Test Document. Source: Test source content.",
    )

    assert result is not None
    assert isinstance(result, str)
    assert len(result.strip()) > 0

    assert "Test Document" in result
    assert "Overview" in result
    assert "Executive summary" in result
    assert "recommendations" in result
    assert "Supporting context" in result
    assert "Review note" in result

