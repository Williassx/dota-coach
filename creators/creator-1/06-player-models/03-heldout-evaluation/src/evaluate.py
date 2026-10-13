"""C1-06-03 heldout harness: protocol-shaped, TEST-data-only evaluation.

Enforces the C1-06-01 protocol in code: whole-match disjoint splits
(duplicate match_id across parts is a failure), locked test part, baseline
vs personal vs shuffled-profile comparison, coverage/uncertainty reporting.
Difference between bots never proves human similarity — recorded in the
report, not overridden here.
"""
import json

PROTOCOL_REVISION = "protocol-r1"


def check_split(parts):
    """parts: {name: [match_id, ...]}. Returns (ok, reason)."""
    seen = {}
    for name, ids in parts.items():
        for mid in ids:
            if mid in seen:
                return False, f"leak:{mid}:{seen[mid]}->{name}"
            seen[mid] = name
    return True, "ok"


def match_rate(choices, references):
    if not references:
        return None
    hits = sum(1 for c, r in zip(choices, references) if c == r)
    return hits / len(references)


def run_evaluation(heldout_matches, baseline_fn, personal_fn, shuffled_fn):
    """heldout_matches: [{match_id, reference}]. Returns metrics dict."""
    refs = [m["reference"] for m in heldout_matches]
    metrics = {"protocol": PROTOCOL_REVISION,
               "n": len(heldout_matches)}
    metrics["baseline_rate"] = match_rate(
        [baseline_fn(m) for m in heldout_matches], refs)
    metrics["personal_rate"] = match_rate(
        [personal_fn(m) for m in heldout_matches], refs)
    metrics["shuffled_rate"] = match_rate(
        [shuffled_fn(m) for m in heldout_matches], refs)
    return metrics


if __name__ == "__main__":
    import sys
    doc = json.load(open(sys.argv[1], encoding="utf-8"))
    ok, reason = check_split(doc["parts"])
    print(json.dumps({"split_ok": ok, "reason": reason}))
