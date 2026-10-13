"""C1-05-02 reproducible import: raw -> normalized (+computed kept separate).

Only the confirmed publicMatches shape is accepted (OpenDota public feed,
no key, terms as audited in C1-05-01). Every normalized record carries its
source and transform version; re-import never duplicates (match_id key).
Unfinished matches (duration 0) and invalid team lists are quarantined,
not silently patched. No patch field exists in the feed — recorded as a gap.
"""
import copy

TRANSFORM_VERSION = "c1-import-v1"

REQUIRED_FIELDS = ("match_id", "match_seq_num", "duration",
                   "radiant_team", "dire_team")


def is_valid_teams(record):
    for side in ("radiant_team", "dire_team"):
        team = record.get(side)
        if (not isinstance(team, list) or len(team) != 5
                or not all(isinstance(h, int) and h >= 0 for h in team)):
            return False
        if all(h == 0 for h in team):
            return False
    return True


def normalize_record(record):
    """Return normalized dict or (None, quarantine_reason)."""
    if not isinstance(record, dict):
        return None, "not-a-dict"
    for field in REQUIRED_FIELDS:
        if field not in record:
            return None, f"missing-{field}"
    if record.get("duration", 0) <= 0:
        return None, "unfinished"
    if not is_valid_teams(record):
        return None, "bad-teams"
    norm = {
        "match_id": record["match_id"],
        "match_seq_num": record["match_seq_num"],
        "duration": record["duration"],
        "radiant_win": record.get("radiant_win"),
        "radiant_team": list(record["radiant_team"]),
        "dire_team": list(record["dire_team"]),
        "source": "opendota-publicMatches",
        "transform": TRANSFORM_VERSION,
        "patch": None,  # gap: feed carries no patch field (see C1-05-01)
    }
    return norm, "ok"


def import_batch(raw_records, existing_ids=()):
    """Split raw records; returns (normalized, quarantined, computed_note)."""
    seen = set(existing_ids)
    normalized, quarantined = [], []
    for rec in raw_records:
        mid = rec.get("match_id") if isinstance(rec, dict) else None
        if mid in seen:
            quarantined.append({"match_id": mid, "reason": "duplicate"})
            continue
        norm, reason = normalize_record(rec)
        if norm is None:
            quarantined.append({"match_id": mid, "reason": reason})
            continue
        seen.add(mid)
        normalized.append(norm)
    computed_note = ("computed features live outside this step; "
                     "only raw + normalized are stored here")
    return normalized, quarantined, computed_note


if __name__ == "__main__":
    import json
    import sys
    raw = json.load(open(sys.argv[1], encoding="utf-8"))
    recs = raw.get("sample", raw) if isinstance(raw, dict) else raw
    norm, quar, _ = import_batch(recs)
    print(json.dumps({"normalized": len(norm),
                      "quarantined": len(quar),
                      "reasons": sorted({q["reason"] for q in quar})}))
