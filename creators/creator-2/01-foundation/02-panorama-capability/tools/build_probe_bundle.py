"""Create a new Panorama source bundle. Does not install or compile Dota assets."""
import argparse
import datetime
import hashlib
import json
import os
import re
import secrets
import stat
import sys
from pathlib import Path, PurePosixPath

REPOSITORY = Path(__file__).resolve().parents[5]
MANIFEST = Path(__file__).resolve().parents[1] / "bundle-manifest.json"
SOURCE_PREFIX = PurePosixPath("creators/creator-2/01-foundation/02-panorama-capability/src/panorama")
TARGET_PREFIX = PurePosixPath("content/panorama")
MAX_BYTES = 1024 * 1024
MAX_MANIFEST_BYTES = 256 * 1024
MAX_ASSETS = 100
DEVICE_NAME = re.compile(r"^(con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])$", re.IGNORECASE)


def portable_path(value):
    if not isinstance(value, str) or not value:
        raise ValueError("Manifest paths must be nonempty strings")
    if any(char in value for char in '\\:<>"|?*') or any(ord(char) < 32 for char in value):
        raise ValueError("Manifest path contains nonportable characters")
    parts = value.split("/")
    if any(not part or part in [".", ".."] or part.rstrip(". ") != part or
           DEVICE_NAME.fullmatch(part.split(".")[0].rstrip(" ")) for part in parts):
        raise ValueError("Manifest path contains invalid or reserved segments")
    return PurePosixPath(value)


def check_ancestors(root, path, allow_missing=False):
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            if allow_missing:
                continue
            raise
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Symlink/reparse point is outside bundle policy")


def output_path(repository, output):
    root = repository.resolve()
    target = output if output.is_absolute() else root / output
    target = Path(os.path.abspath(target))
    boundary = root / "build/dota_coach"
    if not target.is_relative_to(boundary) or target == boundary:
        raise ValueError("Output must be a new child of build/dota_coach")
    check_ancestors(root, target, allow_missing=True)
    if target.exists() or target.is_symlink():
        raise FileExistsError("Existing bundle output is preserved")
    return target


def prepare_assets(repository: Path, manifest: dict) -> list:
    """Validate declared UI paths and read bounded source bytes without writing."""
    root = repository.resolve()
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "kind", "assets"}:
        raise ValueError("Unsupported bundle manifest fields")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise ValueError("Unsupported bundle manifest version")
    if manifest["kind"] != "panorama_source_probe":
        raise ValueError("Unsupported bundle kind")
    entries = manifest["assets"]
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_ASSETS:
        raise ValueError("Bundle must contain 1 to 100 declared assets")

    prepared = []
    targets = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"source", "target"}:
            raise ValueError("Asset requires source and target")
        source = portable_path(entry["source"])
        target = portable_path(entry["target"])
        if not source.is_relative_to(SOURCE_PREFIX) or source == SOURCE_PREFIX:
            raise ValueError("Source must belong to this UI library")
        if not target.is_relative_to(TARGET_PREFIX) or target == TARGET_PREFIX:
            raise ValueError("Target must belong to content/panorama")
        if source.suffix.lower() not in [".xml", ".js", ".css"] or target.suffix.lower() != source.suffix.lower():
            raise ValueError("Asset must preserve its XML/JS/CSS resource type")
        key = target.as_posix().casefold()
        if any(key == other or key.startswith(other + "/") or other.startswith(key + "/") for other in targets):
            raise ValueError("Duplicate or conflicting Windows destination")
        targets.add(key)
        actual = root.joinpath(*source.parts)
        check_ancestors(root, actual)
        if not actual.is_file():
            raise ValueError("Declared source is not a file")
        with actual.open("rb") as handle:
            payload = handle.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise ValueError("UI resource exceeds 1 MiB")
        prepared.append((source.as_posix(), target.as_posix(), payload))

    return prepared


def build_bundle(repository: Path, manifest: dict, output: Path) -> dict:
    root = repository.resolve()
    target_root = output_path(root, output)
    prepared = prepare_assets(root, manifest)

    # All paths and bytes are checked before any output is created.
    target_root.parent.mkdir(parents=True, exist_ok=True)
    target_root.mkdir()
    assets = []
    for source, target, payload in prepared:
        destination = target_root.joinpath(*PurePosixPath(target).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as handle:
            handle.write(payload)
        assets.append({"source": source, "target": target, "bytes": len(payload),
                       "sha256": hashlib.sha256(payload).hexdigest()})
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    report = {"schema_version": 1, "kind": "panorama_source_probe", "complete": True,
              "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "manifest_sha256": hashlib.sha256(canonical).hexdigest(),
              "source2_compiled": False, "runtime_verified": False, "assets": assets}
    with (target_root / "bundle-report.json").open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=REPOSITORY)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, help="New child of repository/build/dota_coach")
    args = parser.parse_args()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output or args.repository.resolve() / "build/dota_coach" / ("probe-ui-" + stamp + "-" + secrets.token_hex(3))
    try:
        with args.manifest.open("rb") as handle:
            raw = handle.read(MAX_MANIFEST_BYTES + 1)
        if len(raw) > MAX_MANIFEST_BYTES:
            raise ValueError("Manifest exceeds 256 KiB")
        report = build_bundle(args.repository, json.loads(raw.decode("utf-8")), output)
    except (OSError, ValueError) as error:
        print("Bundle not completed: " + str(error), file=sys.stderr)
        return 2
    actual = output if output.is_absolute() else args.repository.resolve() / output
    print(json.dumps({"output": str(actual), "assets": len(report["assets"]),
                      "source2_compiled": False, "runtime_verified": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
