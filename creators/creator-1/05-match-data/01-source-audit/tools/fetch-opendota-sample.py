"""Fetch small OpenDota samples for C1-05-01 (public API, no mass collection)."""
import argparse
import json
import urllib.request
from pathlib import Path

ENDPOINTS = {
    "herostats": "https://api.opendota.com/api/heroStats",
    "publicmatches": "https://api.opendota.com/api/publicMatches",
}
LIMITS = {"herostats": 3, "publicmatches": 5}
FIELD_LIMITS = {"herostats": 25, "publicmatches": None}


def fetch(url: str):
    request = urllib.request.Request(
        url, headers={"User-Agent": "dota-coach-c10501-audit/1 (sample fetch)"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", choices=sorted(ENDPOINTS), default="herostats")
    arguments = parser.parse_args()
    fixture_dir = Path(__file__).resolve().parents[1] / "fixtures"
    target = fixture_dir / ("opendota-" + arguments.endpoint + "-sample.json")

    if target.exists():
        print("Fixture already exists; not overwriting:", target)
        return 2
    data = fetch(ENDPOINTS[arguments.endpoint])
    if not isinstance(data, list):
        print("Unexpected payload shape; nothing written.")
        return 3

    field_limit = FIELD_LIMITS[arguments.endpoint]
    if field_limit is None:
        sample = data[: LIMITS[arguments.endpoint]]
    else:
        sample = [
            {key: record.get(key) for key in sorted(record)[:field_limit]}
            for record in data[: LIMITS[arguments.endpoint]]
        ]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as handle:
        json.dump({
            "source": ENDPOINTS[arguments.endpoint],
            "record_count": len(data),
            "sample_count": len(sample),
            "description": "small trimmed sample; not a full dataset, no personal data"
            if arguments.endpoint == "publicmatches"
            else "first fields of the first records; not a full dataset",
            "sample": sample,
        }, handle, ensure_ascii=False, indent=2)
    print("written:", target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
