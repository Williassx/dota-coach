"""Verify a Panorama source bundle against current sources; never install or compile."""
import argparse
import hashlib
import json
import os
import stat
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

# Importing the adjacent helper must not write bytecode into the checkout.
sys.dont_write_bytecode = True
from build_probe_bundle import (MANIFEST, MAX_BYTES, MAX_MANIFEST_BYTES, REPOSITORY,
                                check_ancestors, portable_path, prepare_assets)


def read_bounded(path: Path, limit: int) -> bytes:
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        raise ValueError("File exceeds verification limit: " + path.name)
    return data


def check_tree(bundle: Path, expected: set):
    directories = {parent.as_posix() for name in expected for parent in PurePosixPath(name).parents
                   if parent != PurePosixPath(".")}
    seen = set()
    stack = [bundle]
    while stack:
        with os.scandir(stack.pop()) as entries:
            for entry in entries:
                path = Path(entry.path)
                name = path.relative_to(bundle).as_posix()
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                    raise ValueError("Symlink/reparse point is outside bundle policy")
                if stat.S_ISDIR(info.st_mode) and name in directories:
                    stack.append(path)
                elif stat.S_ISREG(info.st_mode) and name in expected:
                    seen.add(name)
                else:
                    raise ValueError("Unexpected bundle entry: " + name)
    if seen != expected:
        raise ValueError("Declared bundle resource or report is missing")


def verify_bundle(repository: Path, manifest: dict, bundle: Path) -> dict:
    root = repository.resolve()
    bundle = Path(os.path.abspath(bundle if bundle.is_absolute() else root / bundle))
    boundary = root / "build/dota_coach"
    if not bundle.is_relative_to(boundary) or bundle == boundary:
        raise ValueError("Bundle must be a child of build/dota_coach")
    check_ancestors(root, bundle)
    prepared = prepare_assets(root, manifest)
    expected = {target for _, target, _ in prepared} | {"bundle-report.json"}
    check_tree(bundle, expected)
    report = json.loads(read_bounded(bundle / "bundle-report.json", MAX_MANIFEST_BYTES).decode("utf-8"))
    fields = {"schema_version", "kind", "complete", "generated_at_utc", "manifest_sha256",
              "source2_compiled", "runtime_verified", "assets"}
    if not isinstance(report, dict) or set(report) != fields:
        raise ValueError("Unsupported bundle report fields")
    if (type(report["schema_version"]) is not int or report["schema_version"] != 1 or
            report["kind"] != "panorama_source_probe" or report["complete"] is not True or
            report["source2_compiled"] is not False or report["runtime_verified"] is not False or
            not isinstance(report["generated_at_utc"], str) or not report["generated_at_utc"]):
        raise ValueError("Invalid source-only bundle report status")
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    if report["manifest_sha256"] != hashlib.sha256(canonical).hexdigest():
        raise ValueError("Bundle does not match current manifest")
    assets = report["assets"]
    if not isinstance(assets, list) or len(assets) != len(prepared):
        raise ValueError("Bundle report asset list does not match manifest")
    metadata = {}
    for asset in assets:
        if not isinstance(asset, dict) or set(asset) != {"source", "target", "bytes", "sha256"}:
            raise ValueError("Invalid bundle report asset")
        target = portable_path(asset["target"]).as_posix()
        if target in metadata:
            raise ValueError("Duplicate bundle report asset")
        metadata[target] = asset
    if set(metadata) != expected - {"bundle-report.json"}:
        raise ValueError("Bundle report targets do not match manifest")

    xml_links = 0
    for source, target, current in prepared:
        data = read_bounded(bundle / target, MAX_BYTES)
        if data != current:
            raise ValueError("Bundle resource does not match current source: " + target)
        asset = metadata[target]
        if (asset["source"] != source or type(asset["bytes"]) is not int or
                asset["bytes"] != len(data) or asset["sha256"] != hashlib.sha256(data).hexdigest()):
            raise ValueError("Bundle resource metadata does not match: " + target)
        if PurePosixPath(target).suffix.lower() != ".xml":
            continue
        text = data.decode("utf-8-sig")
        if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
            raise ValueError("XML DTD/entities are not supported")
        for node in ET.fromstring(text).iter():
            for key, value in node.attrib.items():
                if key not in ["src", "layoutfile"]:
                    continue
                prefix = "file://{resources}/"
                if not value.startswith(prefix):
                    raise ValueError("XML reference must use local Panorama resources")
                relative = portable_path(value[len(prefix):])
                resolved = (PurePosixPath("content/panorama") / relative).as_posix()
                if resolved not in metadata:
                    raise ValueError("XML reference is not a declared bundle resource")
                xml_links += 1
    return {"package_verified": True, "assets": len(prepared), "xml_resource_links": xml_links,
            "source2_compiled": False, "runtime_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=REPOSITORY)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = json.loads(read_bounded(args.manifest, MAX_MANIFEST_BYTES).decode("utf-8"))
        result = verify_bundle(args.repository, manifest, args.bundle)
    except (OSError, ValueError, ET.ParseError, RecursionError) as error:
        print("Bundle verification failed: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
