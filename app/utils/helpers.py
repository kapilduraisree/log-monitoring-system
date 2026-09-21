"""Utility helpers — IP extraction (IPv4 + IPv6)."""

import re
from typing import Optional

# Full IPv4 pattern
_IPV4 = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
# Full IPv6 patterns (standard + compressed)
_IPV6_FULL = r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"
_IPV6_COMPRESSED = r"\b(?:[0-9a-fA-F]{1,4}:)*::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}\b"
_IPV6_LOOPBACK = r"\b::1\b"

_IP_RE = re.compile(
    f"({_IPV4}|{_IPV6_FULL}|{_IPV6_COMPRESSED}|{_IPV6_LOOPBACK})"
)


def extract_ip(text: str) -> Optional[str]:
    """Return the first IP address found in *text*, or None."""
    if not text:
        return None
    match = _IP_RE.search(text)
    return match.group(1) if match else None


def extract_all_ips(text: str) -> list[str]:
    """Return all unique IP addresses found in *text*."""
    if not text:
        return []
    return list(dict.fromkeys(m.group(1) for m in _IP_RE.finditer(text)))
