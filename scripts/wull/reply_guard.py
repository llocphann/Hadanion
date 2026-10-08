"""Bounded public-output verification before Companion local chat persistence.

The QML shared-model route uses services/WullReplyGuard.js. Keep protocol
sentinel fixtures aligned. No model calls, local data access or extra inference.
"""
import re

_SENTINEL = re.compile(
    r"</?\s*(?:think(?:ing)?|tool_call|tool_result|function_call|system|assistant)\b"
    r"|<\|(?:im_start|im_end|assistant|system|tool)[^>]*\|>"
    r"|\[\s*/?\s*INST\s*\]", re.IGNORECASE,
)
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class UnsafeReply(ValueError):
    pass


def public_text(value):
    if not isinstance(value, str):
        raise UnsafeReply("invalid_text")
    if _SENTINEL.search(value):
        raise UnsafeReply("internal_protocol")
    text = _CONTROL.sub("", value).strip()[:420]
    if not text:
        raise UnsafeReply("empty_text")
    return text
