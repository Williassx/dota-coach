"""Read-only Git/Steam inventory. This does not validate the Dota runtime."""
import argparse
import datetime
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

WINDOWS_REPOSITORY = r"D:\AI\dota2coach"


def quoted_value(text, key):
    match = re.search(r'"' + re.escape(key) + r'"\s*"((?:\\.|[^"\\])*)"', text)
    return match.group(1).replace("\\\\", "\\").replace('\\"', '"') if match else None


def steam_libraries(root: Path) -> list:
    libraries = [root]
    vdf = root / "steamapps" / "libraryfolders.vdf"
    if vdf.is_file():
        text = vdf.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r'"path"\s*"((?:\\.|[^"\\])*)"', text):
            libraries.append(Path(match.group(1).replace("\\\\", "\\").replace('\\"', '"')))
    unique = []
    keys = set()
    for library in libraries:
        key = os.path.normcase(str(library.resolve()))
        if key not in keys:
            keys.add(key)
            unique.append(library)
    return unique


def inspect_dota_library(library: Path) -> dict:
    manifest = library / "steamapps" / "appmanifest_570.acf"
    result = {"library": str(library), "manifest_found": manifest.is_file(),
              "runtime_verified": False}
    if not manifest.is_file():
        result["status"] = "manifest_not_found"
        return result
    try:
        text = manifest.read_text(encoding="utf-8", errors="replace")
    except OSError:
        result["status"] = "manifest_unreadable"
        return result
    install = quoted_value(text, "installdir")
    common = (library / "steamapps" / "common").resolve()
    game = (common / install).resolve() if install else None
    if not game or not game.is_relative_to(common) or game == common:
        result["status"] = "invalid_install_directory"
        return result
    result.update({"status": "inventory_only", "build_id": quoted_value(text, "buildid"),
                   "game_path": str(game), "game_directory_exists": game.is_dir(),
                   "game_addons_exists": (game / "game" / "dota_addons").is_dir(),
                   "content_addons_exists": (game / "content" / "dota_addons").is_dir(),
                   "workshop_tools_runtime": "not_verified"})
    return result


def git_output(repository, *arguments):
    try:
        result = subprocess.run(["git", "--no-optional-locks", "-C", str(repository), *arguments],
                                capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=15)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def expected_origin(remote):
    if not remote:
        return False
    if remote.startswith("git@github.com:"):
        project = remote.split(":", 1)[1]
    else:
        parsed = urlsplit(remote)
        if parsed.scheme not in ("https", "ssh") or parsed.hostname != "github.com":
            return False
        project = parsed.path.lstrip("/")
    return project.removesuffix(".git").rstrip("/").lower() == "williassx/dota-coach"


def inspect_git(repository: Path) -> dict:
    root = git_output(repository, "rev-parse", "--show-toplevel")
    status = git_output(repository, "status", "--porcelain") if root else None
    return {"git_available": shutil.which("git") is not None, "is_repository": bool(root),
            "version": git_output(repository, "--version"),
            "repository_matches_path": bool(root) and Path(root).resolve() == repository.resolve(),
            "head": git_output(repository, "rev-parse", "HEAD") if root else None,
            "branch": git_output(repository, "symbolic-ref", "--short", "HEAD") if root else None,
            "dirty": bool(status) if status is not None else None,
            "status_entries": len(status.splitlines()) if status else 0,
            "origin_matches_expected": expected_origin(
                git_output(repository, "config", "--get", "remote.origin.url")) if root else False}


def discover_steam_roots():
    if platform.system() != "Windows":
        return []
    import winreg
    roots = []
    locations = [(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
                 (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath")]
    for hive, key, value in locations:
        for view in [0, winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY]:
            try:
                with winreg.OpenKey(hive, key, 0, winreg.KEY_READ | view) as registry:
                    path = Path(winreg.QueryValueEx(registry, value)[0])
                    if path not in roots:
                        roots.append(path)
            except OSError:
                continue
    return roots


def build_report(repository: Path, steam_roots: list) -> dict:
    libraries = []
    issues = []
    for root in steam_roots:
        try:
            for library in steam_libraries(root):
                if library not in libraries:
                    libraries.append(library)
        except OSError:
            issues.append({"steam_root": str(root), "status": "library_index_unreadable"})
    return {"schema_version": 1,
            "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "system": platform.system(), "python_version": platform.python_version(),
            "repository": str(repository.resolve()), "git": inspect_git(repository),
            "windows_repository": WINDOWS_REPOSITORY,
            "windows_access": "local_windows_runtime" if platform.system() == "Windows"
            else "not_accessible_from_this_runtime",
            "steam_roots": [str(root) for root in steam_roots],
            "dota_libraries": [inspect_dota_library(library) for library in libraries],
            "issues": issues, "runtime_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--steam-root", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, help="Create a new JSON report; never overwrite")
    arguments = parser.parse_args()
    roots = arguments.steam_root or discover_steam_roots()
    report = json.dumps(build_report(arguments.repository, roots), ensure_ascii=False, indent=2)
    if arguments.output:
        try:
            with arguments.output.open("x", encoding="utf-8") as target:
                target.write(report + "\n")
        except OSError:
            print("Report was not written: target exists or cannot be created.", file=sys.stderr)
            return 2
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
