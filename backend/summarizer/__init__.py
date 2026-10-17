"""Denira Desktop Summarizer Package."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.summarizer.groq_client import (
        AsyncSummarizer,
        SynthesizedCard,
        count_words,
        normalize_headline,
        normalize_summary,
    )
    from backend.summarizer.prompt_template import (
        SYSTEM_PROMPT,
        VALID_GENRES,
        format_user_prompt,
    )


def __getattr__(name: str):
    if name in (
        "AsyncSummarizer",
        "SynthesizedCard",
        "count_words",
        "normalize_headline",
        "normalize_summary",
        "GROQ_MODEL",
        "DEFAULT_GROQ_MODEL",
        "FALLBACK_GROQ_MODEL",
    ):
        import backend.summarizer.groq_client as gc

        return getattr(gc, name)
    if name in ("SYSTEM_PROMPT", "VALID_GENRES", "format_user_prompt"):
        import backend.summarizer.prompt_template as pt

        return getattr(pt, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AsyncSummarizer",
    "SynthesizedCard",
    "count_words",
    "normalize_headline",
    "normalize_summary",
    "GROQ_MODEL",
    "DEFAULT_GROQ_MODEL",
    "FALLBACK_GROQ_MODEL",
    "SYSTEM_PROMPT",
    "VALID_GENRES",
    "format_user_prompt",
]
