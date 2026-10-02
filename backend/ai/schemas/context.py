from typing import Any
from pydantic import BaseModel, Field


class ContextSchema(BaseModel):
    summary: str = ""
    facts: list[Any] = Field(default_factory=list)
    changes: list[Any] = Field(default_factory=list)
    requirements: list[Any] = Field(default_factory=list)
    entities: list[Any] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    contradictions: list[Any] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
