"""Bounded read-only file evidence; never verifies a loaded Dota map or geometry."""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import stat
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[5]
C1_HELPER = (REPOSITORY / "creators/creator-1/01-foundation/01-environment-audit"
             / "tools/inspect_environment.py")
_spec = importlib.util.spec_from_file_location("dota_coach_map_environment", C1_HELPER)
environment = importlib.util.module_from_spec(_spec)
_bytecode = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    _spec.loader.exec_module(environment)
finally:
    sys.dont_write_bytecode = _bytecode

KINDS = {".vmap": "source_candidate", ".vmap_c": "compiled_candidate",
         ".nav": "navigation_candidate", ".vnav": "navigation_candidate",
         ".vnav_c": "navigation_candidate"}


def absolute(path):
    """Normalize dots without resolving symlinks before checking ancestors."""
    return Path(os.path.abspath(path))


def checked(path):
    """Existing path with no link/reparse ancestor; return its own lstat."""
    path = absolute(path)
    info = None
    for parent in reversed([path, *path.parents]):
        info = parent.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("link_or_reparse_skipped")
    return info


def identity(info):
    # Windows 3.12 exposes creation time explicitly; legacy ctime can differ
    # between path and descriptor APIs. Keep POSIX metadata-change semantics.
    stamp = (getattr(info, "st_birthtime_ns", info.st_ctime_ns)
             if sys.platform == "win32" else info.st_ctime_ns)
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, stamp


def metadata_identity(info):
    """Same-API snapshots still detect ctime-only changes on every platform."""
    return identity(info) + (info.st_ctime_ns,)


def appstate_values(text):
    """Strict bounded KeyValues structure; reuse C1 for quoted scalar decoding."""
    tokens = []
    pattern = re.compile(r'\s+|//[^\r\n]*|"(?:\\.|[^"\\])*"|[{}]')
    text = text.lstrip("\ufeff")
    position = 0
    while position < len(text):
        match = pattern.match(text, position)
        if not match:
            return None
        token = match.group(0)
        if token[0] in '"{}':
            tokens.append(token)
        position = match.end()
    if len(tokens) < 3 or tokens[:2] != ['"AppState"', '{']:
        return None
    result = {}
    stack = [result]
    position = 2
    while position < len(tokens):
        token = tokens[position]
        if token == "}":
            stack.pop()
            position += 1
            if not stack:
                return result if position == len(tokens) else None
            continue
        if not token.startswith('"') or position + 1 == len(tokens):
            return None
        key = environment.quoted_value('"key" ' + token, "key")
        if key in stack[-1]:
            return None
        value = tokens[position + 1]
        if value == "{":
            child = {}
            stack[-1][key] = child
            stack.append(child)
            if len(stack) > 64:
                return None
        elif value.startswith('"'):
            stack[-1][key] = value
        else:
            return None
        position += 2
    return None


def build_evidence(root, library):
    result = {"status": "not_supplied", "build_id": None}
    if library is None:
        return result
    library = absolute(library)
    manifest = library / "steamapps/appmanifest_570.acf"
    result["status"] = "manifest_unavailable"
    try:
        info = checked(manifest)
        if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
            result["status"] = "invalid_manifest"
            return result
        with manifest.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            if identity(opened) != identity(info):
                result["status"] = "manifest_changed"
                return result
            data = stream.read(65537)
            if len(data) > 65536 or metadata_identity(os.fstat(stream.fileno())) != metadata_identity(opened) or \
                    metadata_identity(checked(manifest)) != metadata_identity(info):
                result["status"] = "manifest_changed"
                return result
        text = data.decode("utf-8", errors="replace")
        values = appstate_values(text)
        if not values or any(not isinstance(values.get(key), str)
                             for key in ["appid", "installdir", "buildid"]):
            result["status"] = "invalid_manifest"
            return result
        def scalar(key):
            return environment.quoted_value('"' + key + '" ' + values[key], key)
        install = scalar("installdir")
        build = scalar("buildid")
        if scalar("appid") != "570" or not install or \
                not build or not re.fullmatch(r"[0-9]{1,32}", build):
            result["status"] = "invalid_manifest"
            return result
        # One installation folder, independent of the host's path separator.
        if install in [".", ".."] or any(c in install for c in "/\\:"):
            result["status"] = "invalid_manifest"
            return result
        game = library / "steamapps/common" / install
        checked(game)
        if game.resolve() != root.resolve():
            result["status"] = "installation_mismatch"
            return result
        result.update(status="associated", build_id=build)
    except ValueError:
        result["status"] = "link_or_reparse_skipped"
    except OSError:
        pass
    return result


def inspect_maps(dota_root: Path, steam_library: Path | None = None, *, max_entries=2000,
                 max_files=80, max_hash_bytes=16777216, max_file_hash_bytes=4194304) -> dict:
    limits = [("max_entries", max_entries, 100000), ("max_files", max_files, 1000),
              ("max_hash_bytes", max_hash_bytes, 268435456),
              ("max_file_hash_bytes", max_file_hash_bytes, 67108864)]
    for name, value, cap in limits:
        if type(value) is not int or not 1 <= value <= cap:
            raise ValueError(name + " must be an integer in 1.." + str(cap))
    root = absolute(dota_root)
    report = {"schema_version": 1, "dota_root": str(root), "directory_exists": False,
              "game_directory_observed": False, "locations": [], "resources": [],
              "issues": [], "entries_examined": 0, "hash_bytes_read": 0,
              "truncated": False, "status": "root_unavailable", "actual_loaded_map": None,
              "patch": None, "runtime_verified": False, "geometry_verified": False,
              "compatibility_verified": False,
              "concept_reference": {"patch": "7.40", "runtime_evidence": False},
              "build_evidence": {"status": "not_supplied", "build_id": None}}

    def issue(path, reason):
        report["issues"].append({"path": path.relative_to(root).as_posix()
                                 if path.is_relative_to(root) else ".", "status": reason})

    def info(path):
        try:
            return checked(path)
        except FileNotFoundError:
            return None
        except ValueError:
            issue(path, "link_or_reparse_skipped")
        except OSError:
            issue(path, "unreadable")
        return None

    initial = info(root)
    if not initial or not stat.S_ISDIR(initial.st_mode):
        return report
    report["directory_exists"] = True
    report["build_evidence"] = build_evidence(root, steam_library)
    game = info(root / "game/dota")
    if not game or not stat.S_ISDIR(game.st_mode):
        issue(root / "game/dota", "missing_game_directory")
        return report
    report["game_directory_observed"] = True

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

    def digest(path, before):
        if before.st_size > max_file_hash_bytes:
            return None, "size_limit"
        if before.st_size > max_hash_bytes - report["hash_bytes_read"]:
            return None, "total_limit"
        sha = hashlib.sha256()
        try:
            with path.open("rb") as stream:
                opened = os.fstat(stream.fileno())
                if identity(opened) != identity(before):
                    return None, "changed"
                remaining = before.st_size
                while remaining:
                    data = stream.read(min(65536, remaining))
                    report["hash_bytes_read"] += len(data)
                    if not data:
                        return None, "changed"
                    remaining -= len(data)
                    sha.update(data)
                if metadata_identity(os.fstat(stream.fileno())) != metadata_identity(opened) or \
                        metadata_identity(checked(path)) != metadata_identity(before):
                    return None, "changed"
            return sha.hexdigest(), "complete"
        except (ValueError, OSError):
            return None, "unreadable"

    def candidate(path, tree, scope, kind, data):
        if not stat.S_ISREG(data.st_mode):
            issue(path, "special_file_skipped")
            return
        sha, status = digest(path, data)
        report["resources"].append({"path": path.relative_to(root).as_posix(), "tree": tree,
            "scope": scope, "kind": kind, "size_bytes": data.st_size,
            "mtime_ns": data.st_mtime_ns, "sha256": sha, "hash_status": status})
        if status in ["changed", "unreadable"]:
            issue(path, status)
        if len(report["resources"]) >= max_files:
            report["truncated"] = True

    def walk(directory, tree, scope, archives=False):
        first = info(directory)
        report["locations"].append({"path": directory.relative_to(root).as_posix(),
            "present": bool(first and stat.S_ISDIR(first.st_mode)), "tree": tree, "scope": scope})
        if not first or not stat.S_ISDIR(first.st_mode):
            return
        if not consume():
            return
        pending = [directory]
        while pending and not report["truncated"]:
            current = pending.pop()
            if not info(current):
                continue
            for path in entries(current):
                data = info(path)
                if data is None:
                    continue
                if stat.S_ISDIR(data.st_mode):
                    if not archives:
                        pending.append(path)
                else:
                    kind = ("archive_candidate" if path.suffix.lower() == ".vpk" else None) \
                        if archives else KINDS.get(path.suffix.lower())
                    if kind:
                        candidate(path, tree, scope, kind, data)
                if report["truncated"]:
                    return

    for tree in ["content", "game"]:
        walk(root / tree / "dota/maps", tree, "core")
        if report["truncated"]:
            break
        addons = root / tree / "dota_addons"
        data = info(addons)
        report["locations"].append({"path": addons.relative_to(root).as_posix(),
            "present": bool(data and stat.S_ISDIR(data.st_mode)), "tree": tree, "scope": "addon"})
        if data and stat.S_ISDIR(data.st_mode):
            if consume():
                for addon in entries(addons):
                    data = info(addon)
                    if data and stat.S_ISDIR(data.st_mode):
                        walk(addon / "maps", tree, "addon")
                    if report["truncated"]:
                        break
        if report["truncated"]:
            break
        if tree == "game":
            walk(root / "game/dota", tree, "core", archives=True)
    report["resources"].sort(key=lambda row: row["path"])
    partial = report["truncated"] or report["issues"] or (steam_library is not None and
              report["build_evidence"]["status"] != "associated")
    report["status"] = "partial_inventory" if partial else "inventory_only"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dota-root", required=True, type=Path)
    parser.add_argument("--steam-library", type=Path)
    parser.add_argument("--output", type=Path, help="New report outside the installation; no overwrite")
    for name, default in [("entries", 2000), ("files", 80),
                          ("hash-bytes", 16777216), ("file-hash-bytes", 4194304)]:
        parser.add_argument("--max-" + name, type=int, default=default)
    args = parser.parse_args()
    try:
        root = absolute(args.dota_root)
        if args.output:
            output = absolute(args.output)
            checked(output.parent)
            try:
                checked(root)
            except FileNotFoundError:
                pass
            protected = [root]
            if args.steam_library:
                library = absolute(args.steam_library)
                checked(library)
                protected.append(library)
            if root.parent.name.lower() == "common" and root.parent.parent.name.lower() == "steamapps":
                protected.append(root.parent.parent.parent)
            if any(output.is_relative_to(p) for p in protected):
                raise ValueError("Output must be outside the installation and known Steam library")
        report = inspect_maps(root, args.steam_library, max_entries=args.max_entries,
                              max_files=args.max_files, max_hash_bytes=args.max_hash_bytes,
                              max_file_hash_bytes=args.max_file_hash_bytes)
        text = json.dumps(report, ensure_ascii=args.output is None, indent=2) + "\n"
        if args.output:
            with output.open("x", encoding="utf-8") as stream:
                stream.write(text)
        else:
            print(text, end="")
    except ValueError as error:
        print("Invalid audit input: " + str(error), file=sys.stderr)
        return 2
    except FileExistsError:
        print("Output already exists; choose a new report filename.", file=sys.stderr)
        return 2
    except OSError:
        print("Cannot access paths or output; check permissions and an existing output parent.", file=sys.stderr)
        return 2
    return 0 if report["status"] == "inventory_only" else 1


if __name__ == "__main__":
    raise SystemExit(main())
