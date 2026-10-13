"""C1-10-02 diagnostics: minimal, secret-free, reproducible reports.

Every error links to the command and versions that produced it. The report
carries only what a reproduction needs — never tokens, keys, full
environment dumps or personal data. Fields with forbidden names are
dropped, not masked-in-place, so a leak fails loudly at build time.
"""
ALLOWED_TOP_FIELDS = ("error", "orderId", "versions", "steps",
                      "transform", "gate", "bundle")
FORBIDDEN_HINTS = ("token", "key", "secret", "password", "steamid",
                   "account_id", "personaname", "avatar", "env")


def build_report(error, order_id, versions, steps):
    """Return (report | None, reason). Pure, no I/O."""
    if not error or not isinstance(versions, dict):
        return None, "bad-input"
    if not isinstance(steps, list) or not steps:
        return None, "no-steps"
    report = {"error": str(error), "orderId": order_id,
              "versions": dict(versions), "steps": list(steps)}
    blob = repr(report).lower()
    for hint in FORBIDDEN_HINTS:
        if hint in blob:
            return None, f"forbidden:{hint}"
    for key in list(report):
        if key not in ALLOWED_TOP_FIELDS:
            return None, f"field-not-allowed:{key}"
    return report, "ok"


def reproduce_plan(report):
    """Return the ordered reproduction procedure for a report."""
    if not isinstance(report, dict) or "steps" not in report:
        return None
    return [f"step{i + 1}:{s}" for i, s in enumerate(report["steps"])]
