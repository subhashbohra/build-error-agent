import re


def analyze_logs(logs: str) -> dict:
    """Return simple findings from log text."""
    findings = {}

    # Common Python tracebacks
    tb = re.search(r"Traceback \(most recent call last\):[\s\S]{0,2000}?(?=\n\S|$)", logs)
    if tb:
        findings["python_traceback"] = tb.group(0)

    # Compiler errors (gcc/clang)
    cc_errs = re.findall(r"^[^\n]*error: .*$(?:\n^[^\n]*$)?", logs, flags=re.MULTILINE)
    if cc_errs:
        findings["cc_errors"] = cc_errs[:10]

    # Java stacktrace
    if "Exception in thread" in logs or "at java." in logs:
        findings["java_exception"] = True

    # Test failures (pytest / junit)
    if "FAILED" in logs and "pytest" in logs:
        findings["pytest_failed"] = True

    # Out of memory
    if "OutOfMemoryError" in logs or "Killed" in logs:
        findings["oom"] = True

    # Build tool specific keywords
    for kw in ["npm ERR!", "gradle", "mvn", "error: cannot find symbol"]:
        if kw in logs:
            findings.setdefault("tool_signatures", []).append(kw)

    return findings
