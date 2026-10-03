from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

@dataclass
class AgentResult:
    name: str
    output: dict | str


# ============================================================
# HELPERS
# ============================================================

def clean_markdown(text: str) -> str:
    """Normalize Markdown returned by the AI."""

    if not text:
        return ""

    text = str(text).strip()

    replacements = {
        r"\*\*": "**",
        r"\*": "*",
        r"\`": "`",
        r"\_": "_",
        r"\|": "|",
        r"\#": "#",
        r"\>": ">",
        r"\---": "---",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize AI-generated numbered lists such as:
    # 1) item / 2) item
    # into bullet lists to avoid broken numbering.
    text = re.sub(
        r"(?m)^\s*\d+[\.\)]\s+",
        "- ",
        text,
    )

    return text.strip()


def document_metadata() -> dict:
    """Generate real backend timestamp in IST."""

    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)

    return {
        "date": now.strftime("%d %B %Y"),
        "time": now.strftime("%I:%M:%S %p"),
        "timezone": "IST",
        "iso": now.isoformat(),
    }


def fact_text(item) -> str:
    """Extract readable claim from different AI JSON structures."""

    if isinstance(item, dict):
        return str(
            item.get("fact")
            or item.get("claim")
            or item.get("text")
            or item.get("description")
            or ""
        ).strip()

    return str(item).strip()


def fact_sources(item) -> list[str]:
    """Extract source references from different AI JSON structures."""

    if not isinstance(item, dict):
        return []

    refs = (
        item.get("source_refs")
        or item.get("sources")
        or item.get("source")
        or []
    )

    if isinstance(refs, str):
        return [refs]

    if isinstance(refs, list):
        return [str(x).strip() for x in refs if str(x).strip()]

    return []


def clean_review_items(items) -> list[str]:
    """Return non-empty, readable review findings from model output."""
    if not isinstance(items, list):
        items = [items] if items else []
    cleaned = []
    for item in items:
        value = fact_text(item)
        if value:
            cleaned.append(value)
    return cleaned


def clean_source_refs(refs) -> list[str]:
    """Keep citations short; source chunks belong in evidence, not references."""
    if not isinstance(refs, list):
        refs = [refs] if refs else []
    cleaned = []
    for ref in refs:
        if isinstance(ref, dict):
            ref = ref.get("source_ref") or ref.get("source") or ref.get("filename") or ""
        value = str(ref).strip()
        if not value:
            continue
        # Model output sometimes copies a complete extracted source chunk into
        # source_refs. Retain only its citation header.
        match = re.match(r"\[SOURCE:\s*([^\]]+)\]", value, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
        if len(value) > 180:
            value = value[:177].rstrip() + "..."
        if value not in cleaned:
            cleaned.append(value)
    return cleaned


def normalize_review_payload(payload, fallback_source_refs=None) -> dict:
    """Normalize AI review payloads into the frontend-safe shape used by the review screen."""
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"notes": payload}
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        payload = {"notes": str(payload)}

    source_refs = clean_source_refs(payload.get("source_refs") or fallback_source_refs or [])
    supported_information = payload.get("supported_information")
    if not supported_information and "supported_sections" in payload:
        supported_information = payload.get("supported_sections")
    if not supported_information and "facts" in payload:
        supported_information = payload.get("facts")

    normalized_supported = []
    for item in supported_information or []:
        if isinstance(item, dict):
            fact = fact_text(item)
            refs = clean_source_refs(fact_sources(item))
            if fact:
                normalized_supported.append({"fact": fact, "source_refs": refs})
        elif isinstance(item, str) and item.strip():
            normalized_supported.append({"fact": item.strip(), "source_refs": []})

    context_gaps = clean_review_items(payload.get("context_gaps") or payload.get("missing_information") or payload.get("gaps") or [])
    technical_risks = clean_review_items(payload.get("technical_risks") or payload.get("risks") or payload.get("risk_flags") or [])
    unsupported_claims = clean_review_items(payload.get("unsupported_claims") or payload.get("unsupported") or [])

    normalized = {
        "verdict": payload.get("verdict") or payload.get("status") or "NEEDS_REVIEW",
        "risks": technical_risks,
        "technical_risks": technical_risks,
        "unsupported_claims": unsupported_claims,
        "missing_information": context_gaps,
        "context_gaps": context_gaps,
        "supported_sections": payload.get("supported_sections") or [item["fact"] for item in normalized_supported],
        "supported_information": normalized_supported,
        "source_refs": source_refs,
        "quality_score": payload.get("quality_score"),
        "generated_at": payload.get("generated_at"),
        "human_approval_required": payload.get("human_approval_required", True),
    }
    for key, value in payload.items():
        if key not in normalized:
            normalized[key] = value
    return normalized


def format_facts(facts) -> str:
    """Pretty-print evidence instead of Python dictionaries."""

    if not facts:
        return "- No structured evidence was extracted."

    output = []

    for item in facts:
        claim = fact_text(item)

        if not claim:
            continue

        output.append(f"- {claim}")

        for source in fact_sources(item):
            output.append(f"  - 📚 Source: {source}")

    return "\n".join(output) or "- No structured evidence was extracted."


def format_items(items, empty_message: str) -> str:
    """Create deterministic Markdown bullet lists."""

    cleaned = []

    for item in items or []:
        if isinstance(item, dict):
            value = (
                item.get("fact")
                or item.get("claim")
                or item.get("description")
                or item.get("text")
                or json.dumps(item, ensure_ascii=False)
            )
        else:
            value = str(item)

        value = str(value).strip()

        if value:
            cleaned.append(value)

    if not cleaned:
        return f"- {empty_message}"

    return "\n".join(f"- {x}" for x in cleaned)


# ============================================================


# ============================================================
# DETERMINISTIC GROUNDING GUARD (runs in every AI mode)
# ============================================================

_CLAIM_PATTERNS = [
    r"/api/[\w./:{}-]+",                # API paths
    r"\b\d+(?:\.\d+)+\b",                # versions such as 17.5
    r"\b\d+(?:[.,]\d+)?\s?(?:MB|GB|KB|%|ms|seconds?|minutes?|hours?|days?)\b",  # metrics
]


def ungrounded_claims(document: str, source: str) -> list[str]:
    """Find versions, API paths and metrics in the document that are absent from the source.

    This is a cheap, model-independent safety net: anything it returns is surfaced
    to the reviewer as an unsupported-claim flag.
    """
    src = (source or "").lower()
    found: list[str] = []
    for pattern in _CLAIM_PATTERNS:
        for match in re.findall(pattern, document or "", flags=re.IGNORECASE):
            token = match.strip().rstrip(".,;:)")
            if token and token.lower() not in src and token not in found:
                found.append(token)
    return [f"Not found in source material: {t}" for t in found[:15]]


_GAP_HINT = re.compile(
    r"not (?:been )?(?:confirmed|described|specified|documented)|open question|unknown|\bTBD\b|to be decided",
    re.IGNORECASE,
)


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if re.search(r"[A-Za-z0-9]{3}", s)]


def gap_hint(sentence: str) -> bool:
    return bool(_GAP_HINT.search(sentence))
