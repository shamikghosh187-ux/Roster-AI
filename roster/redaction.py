"""Redaction helpers for logs and diagnostics."""
import re
_PATTERNS=((re.compile(r"(sk-[A-Za-z0-9_-]{12,})"),"sk-***"),(re.compile(r"(Bearer\s+)[A-Za-z0-9._-]+",re.I),r"\1***"),(re.compile(r"(?i)(api[_-]?key\s*[=:]\s*)[^\s,;]+"),r"\1***"))
def redact(text:str)->str:
    result=text
    for pattern,replacement in _PATTERNS: result=pattern.sub(replacement,result)
    return result
