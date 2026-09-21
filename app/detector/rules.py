"""Detection rule definitions — 9 regex-based rule sets."""

import re
from dataclasses import dataclass, field
from typing import Pattern


@dataclass
class Rule:
    name: str
    severity: str          # CRITICAL | HIGH | MEDIUM | LOW | INFO
    patterns: list[Pattern]
    event_type: str


def _c(patterns: list[str], flags: int = re.IGNORECASE) -> list[Pattern]:
    return [re.compile(p, flags) for p in patterns]


RULES: list[Rule] = [
    Rule(
        name="SQL Injection",
        severity="CRITICAL",
        event_type="sql_injection",
        patterns=_c([
            r"union\s+select", r"or\s+1\s*=\s*1", r"drop\s+table",
            r"insert\s+into", r"--\s*$", r"xp_cmdshell", r"exec\s*\(",
        ]),
    ),
    Rule(
        name="Brute Force",
        severity="CRITICAL",
        event_type="brute_force",
        patterns=_c([r"brute.?force", r"account.locked", r"too many failed"]),
    ),
    Rule(
        name="Malware",
        severity="CRITICAL",
        event_type="malware",
        patterns=_c([
            r"ransomware", r"reverse.shell", r"mimikatz", r"meterpreter",
            r"netcat", r"powershell.*-enc", r"base64.*decode",
        ]),
    ),
    Rule(
        name="SSH Auth Failure",
        severity="HIGH",
        event_type="ssh_auth_failure",
        patterns=_c([
            r"sshd.*failed", r"failed.*sshd", r"too many auth",
            r"invalid public key", r"preauth.*disconnect",
        ]),
    ),
    Rule(
        name="XSS",
        severity="HIGH",
        event_type="xss",
        patterns=_c([
            r"<script", r"onerror\s*=", r"onload\s*=",
            r"javascript:", r"alert\s*\(", r"document\.cookie",
        ]),
    ),
    Rule(
        name="Suspicious IP",
        severity="HIGH",
        event_type="suspicious_ip",
        patterns=_c([r"blacklisted.ip", r"threat.intel", r"malicious.ip", r"blocklist"]),
    ),
    Rule(
        name="Unauthorized Access",
        severity="HIGH",
        event_type="unauthorized_access",
        patterns=_c([r"access.denied", r"sudo.*failed", r"permission.denied", r"403.forbidden"]),
    ),
    Rule(
        name="Port Scan",
        severity="MEDIUM",
        event_type="port_scan",
        patterns=_c([r"\bnmap\b", r"port.scan", r"masscan", r"zmap", r"syn.flood"]),
    ),
    Rule(
        name="Failed Login",
        severity="MEDIUM",
        event_type="failed_login",
        patterns=_c([
            r"failed.login", r"invalid.user", r"authentication.failure",
            r"login.failed", r"bad.password",
        ]),
    ),
]
