"""Bounded read-only Panorama inventory; does not verify the Dota runtime."""
import argparse
import importlib.util
import json
import os
import stat
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[5]
C1_HELPER = (REPOSITORY / "creators/creator-1/01-foundation/01-environment-audit"
             / "tools/inspect_environment.py")
_spec = importlib.util.spec_from_file_location("dota_coach_environment_audit", C1_HELPER)
environment = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(environment)

RESOURCE_KINDS = {".xml": "source", ".js": "source", ".css": "source",
                  ".vxml_c": "compiled", ".vjs_c": "compiled", ".vcss_c": "compiled"}


def inspect_panorama(dota_root: Path, max_entries=2000, max_files=80) -> dict:
    report = {"dota_root": str(dota_root), "directory_exists": False,
              "runtime_verified": False, "resources": [], "issues": [],
              "entries_examined": 0, "truncated": False, "addon_roots": []}
    if max_entries < 1 or max_files < 1:
        raise ValueError("Inventory limits must be positive")

    def issue(path, status):
        try:
            relative = str(path.relative_to(dota_root))
        except ValueError:
            relative = "."
        report["issues"].append({"path": relative, "status": status})

    def no_link(path):
        try:
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                issue(path, "link_or_escape_skipped")
                return False
            return True
        except FileNotFoundError:
            return False
        except OSError:
            issue(path, "unreadable")
            return False

    if not no_link(dota_root):
        return report
    try:
        root = dota_root.resolve()
        report["directory_exists"] = dota_root.is_dir()
    except (OSError, RuntimeError):
        issue(dota_root, "unreadable")
        return report
    if not report["directory_exists"]:
        return report

    def safe(path):
        if not no_link(path):
            return False
        try:
            if not path.resolve().is_relative_to(root):
                issue(path, "link_or_escape_skipped")
                return False
            return True
        except (OSError, RuntimeError):
            issue(path, "unreadable")
            return False

    def consume():
        if report["entries_examined"] >= max_entries:
            report["truncated"] = True
            return False
        report["entries_examined"] += 1
        return True

    def entries(directory):
        try:
            with os.scandir(directory) as iterator:
                for entry in iterator:
                    if not consume():
                        return
                    yield Path(entry.path)
        except OSError:
            issue(directory, "unreadable")

    def walk(directory, tree):
        pending = [directory]
        while pending and not report["truncated"]:
            current = pending.pop()
            if not safe(current):
                continue
            for path in entries(current):
                if not safe(path):
                    continue
                if path.is_dir():
                    pending.append(path)
                elif path.suffix.lower() in RESOURCE_KINDS and path.is_file():
                    report["resources"].append({"tree": tree,
                        "path": path.relative_to(dota_root).as_posix(),
                        "kind": RESOURCE_KINDS[path.suffix.lower()]})
                    if len(report["resources"]) >= max_files:
                        report["truncated"] = True
                if report["truncated"]:
                    return

    for tree in ["content", "game"]:
        tree_path = dota_root / tree
        addons = tree_path / "dota_addons"
        if not consume() or not safe(tree_path) or not tree_path.is_dir():
            continue
        if not consume() or not safe(addons) or not addons.is_dir():
            continue
        report["addon_roots"].append(str(addons))
        for addon in entries(addons):
            if not safe(addon) or not addon.is_dir():
                continue
            panorama = addon / "panorama"
            if consume() and safe(panorama) and panorama.is_dir():
                walk(panorama, tree)
            if report["truncated"]:
                break
        if report["truncated"]:
            break
    report["resources"].sort(key=lambda resource: resource["path"])
    return report


def build_report(repository: Path, steam_roots: list, dota_roots: list) -> dict:
    base = environment.build_report(repository, steam_roots)
    roots = list(dota_roots)
    roots.extend(Path(item["game_path"]) for item in base["dota_libraries"]
                 if item.get("game_directory_exists"))
    unique = []
    keys = set()
    for root in roots:
        key = os.path.normcase(os.path.abspath(root))
        if key not in keys:
            keys.add(key)
            unique.append(root)
    return {"schema_version": 1, "environment": base, "runtime_verified": False,
            "panorama_installations": [inspect_panorama(root) for root in unique]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=REPOSITORY)
    parser.add_argument("--steam-root", type=Path, action="append", default=[])
    parser.add_argument("--dota-root", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, help="Create a new report; never overwrite")
    args = parser.parse_args()
    roots = args.steam_root or environment.discover_steam_roots()
    report = json.dumps(build_report(args.repository, roots, args.dota_root),
                        ensure_ascii=False, indent=2)
    if args.output:
        try:
            with args.output.open("x", encoding="utf-8") as target:
                target.write(report + "\n")
        except OSError:
            print("Report was not written: target exists or cannot be created.", file=sys.stderr)
            return 2
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
