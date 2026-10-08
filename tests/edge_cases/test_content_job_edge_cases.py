
import pytest
from pydantic import ValidationError

from app.api.content_jobs import JobIn


def test_job_rejects_title_shorter_than_three_characters():
    with pytest.raises(ValidationError):
        JobIn(
            title="AB",
            content_type="documentation",
            audience="developers",
            source_text="This is valid source text.",
        )


def test_job_rejects_source_text_shorter_than_ten_characters():
    with pytest.raises(ValidationError):
        JobIn(
            title="Valid Title",
            content_type="documentation",
            audience="developers",
            source_text="Short",
        )


def test_job_accepts_minimum_valid_input():
    job = JobIn(
        title="ABC",
        content_type="documentation",
        audience="developers",
        source_text="1234567890",
    )

    assert job.title == "ABC"
    assert job.source_text == "1234567890"

