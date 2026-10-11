"""Create a new Panorama source bundle. Does not install or compile Dota assets."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import secrets
import stat
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

REPOSITORY = Path(__file__).resolve().parents[5]
MANIFEST = Path(__file__).resolve().parents[1] / "bundle-manifest.json"
SOURCE_PREFIX = PurePosixPath("creators/creator-2/01-foundation/02-panorama-capability/src/panorama")
TARGET_PREFIX = PurePosixPath("content/panorama")
MAX_BYTES = 1024 * 1024
MAX_MANIFEST_BYTES = 256 * 1024
MAX_ASSETS = 100
DEVICE_NAME = re.compile(r"^(con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])$", re.IGNORECASE)
HUD_PREFIX = "creators/creator-2/07-match-screen/01-own-cards/src/panorama/"
HUD_SCRIPT_SOURCES = (
    ("02-coach-interface/01-roster-cards", "roster_cards_state.js"),
    ("02-coach-interface/01-roster-cards", "roster_cards.js"),
    ("02-coach-interface/02-status-orders", "orders_state.js"),
    ("02-coach-interface/02-status-orders", "orders_panel.js"),
    ("02-coach-interface/03-control-input", "input_routing.js"),
    ("03-map-view/02-camera-overlays", "camera_native.js"),
    ("03-map-view/02-camera-overlays", "camera_panel.js"),
    ("03-map-view/03-visibility-targets", "targets_state.js"),
    ("03-map-view/03-visibility-targets", "targets_panel.js"),
    ("11-integration/01-ui-binding", "coach_hud_binding.js"),
)
HUD_ASSETS = {
    **{HUD_PREFIX + relative: "content/panorama/" + relative for relative in (
        "layout/custom_game/custom_ui_manifest.xml", "layout/custom_game/coach_hud.xml",
        "styles/custom_game/coach_hud.css")},
    **{"creators/creator-2/" + library + "/src/panorama/scripts/custom_game/" + name:
       "content/panorama/scripts/custom_game/" + name for library, name in HUD_SCRIPT_SOURCES},
}


INTERVENTION_PREFIX = "creators/creator-2/05-intervention-ui/01-request-ack/src/panorama/"
INTERVENTION_ASSETS = {
    **{INTERVENTION_PREFIX + name: "content/panorama/" + name for name in (
        "layout/custom_game/custom_ui_manifest.xml", "layout/custom_game/intervention_request.xml",
        "styles/custom_game/intervention_request.css", "scripts/custom_game/intervention_request_state.js",
        "scripts/custom_game/intervention_request_panel.js")},
    "creators/creator-2/02-coach-interface/02-status-orders/src/panorama/scripts/custom_game/orders_state.js":
        "content/panorama/scripts/custom_game/orders_state.js",
}


def validate_intervention_graph(prepared):
    """Validate the fixed inert manual-request source tree, not native compilation."""
    payloads = {target: raw for _, target, raw in prepared}
    resource = "file://{resources}/"
    manifest_name = "content/panorama/layout/custom_game/custom_ui_manifest.xml"
    layout_name = "content/panorama/layout/custom_game/intervention_request.xml"
    trees = {}
    for name in (manifest_name, layout_name):
        raw = payloads[name].decode("utf-8-sig")
        if "<!DOCTYPE" in raw.upper() or "<!ENTITY" in raw.upper():
            raise ValueError("Manual request XML DTD/entities are not supported")
        trees[name] = ET.fromstring(raw)
        for node in trees[name].iter():
            if (node.text or "").strip() or (node.tail or "").strip():
                raise ValueError("Manual request XML cannot contain executable or mixed text")
    manifest = trees[manifest_name]
    nodes = list(manifest.iter())
    if (len(nodes) != 3 or [n.tag for n in nodes] != ["root", "Panel", "CustomUIElement"] or
            len(manifest) != 1 or len(nodes[1]) != 1 or nodes[1][0] is not nodes[2] or
            nodes[0].attrib or nodes[1].attrib or nodes[2].attrib != {
                "type": "Hud", "layoutfile": resource + "layout/custom_game/intervention_request.xml"}):
        raise ValueError("Manual request manifest must load exactly one declared Hud layout")
    layout = trees[layout_name]
    if layout.tag != "root" or layout.attrib or [n.tag for n in layout] != ["styles", "scripts", "Panel"]:
        raise ValueError("Manual request layout requires styles, scripts and one Panel")
    reached = {manifest_name, layout_name}
    for tag, expected in (("styles", ["styles/custom_game/intervention_request.css"]),
                          ("scripts", ["scripts/custom_game/" + n for n in
                                       ("orders_state.js", "intervention_request_state.js", "intervention_request_panel.js")])):
        section = layout.find(tag)
        if section.attrib or len(section) != len(expected):
            raise ValueError("Manual request include count/section attributes invalid")
        for node, name in zip(section, expected):
            if node.tag != "include" or node.attrib != {"src": resource + name} or len(node):
                raise ValueError("Manual request dependencies must be exact ordered leaf includes")
            reached.add("content/panorama/" + name)
    if reached != set(payloads):
        raise ValueError("Manual request source graph has unreachable resources")
    required = {"ManualRequestRoot": "Panel", "ManualRequestButton": "Button",
                **{"ManualRequest" + name: "Label" for name in
                   ("Recipient", "Mode", "Actor", "State", "Reason", "Message", "Hint")}}
    ids, buttons = {}, []
    attributes = {"Panel": {"id", "class", "hittest", "hittestchildren"},
                  "Label": {"id", "class", "html", "text"}, "Button": {"id", "class", "enabled"}}
    for node in layout.find("Panel").iter():
        if node.tag not in attributes or set(node.attrib) - attributes[node.tag]:
            raise ValueError("Manual request body has unsupported tag or attributes")
        if "id" in node.attrib:
            identity = node.attrib["id"]
            if identity in ids:
                raise ValueError("Manual request IDs must be unique")
            ids[identity] = node.tag
        if node.tag == "Label" and (node.get("html") != "false" or len(node)):
            raise ValueError("Manual request labels must be plain leaf labels")
        if node.tag == "Button":
            buttons.append(node)
    if ids != required or layout.find("Panel").get("id") != "ManualRequestRoot":
        raise ValueError("Manual request requires its exact nine scoped IDs")
    if (len(buttons) != 1 or buttons[0].get("enabled") != "false" or len(buttons[0]) != 1 or
            buttons[0][0].tag != "Label" or buttons[0][0].get("id") != "ManualRequestHint"):
        raise ValueError("Manual request requires one disabled button with its Hint")


def validate_hud_graph(prepared):
    """Check one inert layout and complete dependency graph; never execute JS."""
    payloads = {target: payload for _, target, payload in prepared}
    manifest_name = "content/panorama/layout/custom_game/custom_ui_manifest.xml"
    layout_name = "content/panorama/layout/custom_game/coach_hud.xml"
    roots, edges = {}, {}
    for name in (manifest_name, layout_name):
        raw = payloads[name].decode("utf-8-sig")
        if "<!DOCTYPE" in raw.upper() or "<!ENTITY" in raw.upper():
            raise ValueError("HUD XML DTD/entities are not supported")
        try:
            roots[name] = ET.fromstring(raw)
        except ET.ParseError as error:
            raise ValueError("HUD XML cannot be parsed") from error
        if roots[name].tag != "root":
            raise ValueError("HUD XML must have one root element")
        edges[name] = set()
        for node in roots[name].iter():
            if name == layout_name and (node.tag == "CustomUIElement" or "layoutfile" in node.attrib):
                raise ValueError("HUD layout cannot load another layout or itself")
            if node.tag.lower() in ("run", "script") or any(key.lower().startswith("on") for key in node.attrib):
                raise ValueError("HUD XML must not automatically execute or bind scripts")
            for key, value in node.attrib.items():
                if key not in ("src", "layoutfile"):
                    continue
                prefix = "file://{resources}/"
                if not value.startswith(prefix):
                    raise ValueError("HUD XML references must use local Panorama resources")
                target = (TARGET_PREFIX / portable_path(value[len(prefix):])).as_posix()
                if target not in payloads:
                    raise ValueError("HUD XML reference is not a declared resource")
                edges[name].add(target)
    elements = list(roots[manifest_name].iter("CustomUIElement"))
    if (len(elements) != 1 or elements[0].get("type") != "Hud" or
            elements[0].get("layoutfile") != "file://{resources}/layout/custom_game/coach_hud.xml" or
            edges[manifest_name] != {layout_name}):
        raise ValueError("HUD manifest must load exactly the common HUD layout")
    scripts = roots[layout_name].findall("./scripts/include")
    expected = ["file://{resources}/scripts/custom_game/" + name for _, name in HUD_SCRIPT_SOURCES]
    if [node.get("src") for node in scripts] != expected:
        raise ValueError("HUD scripts must preserve the complete dependency order")
    if [node.get("src") for node in roots[layout_name].findall("./styles/include")] != [
            "file://{resources}/styles/custom_game/coach_hud.css"]:
        raise ValueError("HUD must load the declared common style")
    reached, pending = set(), [manifest_name]
    while pending:
        name = pending.pop()
        if name in reached:
            continue
        reached.add(name)
        pending.extend(edges.get(name, ()))
    if reached != set(payloads):
        raise ValueError("HUD source graph contains an unreachable resource")


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


def read_source(repository: Path, source: str) -> bytes:
    """The bounded path/ancestor policy shared by every copied or composed input."""
    root = repository.resolve()
    relative = portable_path(source)
    actual = root.joinpath(*relative.parts)
    check_ancestors(root, actual)
    if not actual.is_file():
        raise ValueError("Declared source is not a file")
    with actual.open("rb") as handle:
        payload = handle.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("UI resource exceeds 1 MiB")
    return payload


def prepare_preparation(repository: Path, manifest: dict) -> list:
    policy = REPOSITORY / "creators/creator-2/11-integration/02-addon-packaging/tools/preparation_layout.py"
    spec = importlib.util.spec_from_file_location("dota_coach_preparation_layout", policy)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module.prepare(repository, manifest, read_source)


def prepare_assets(repository: Path, manifest: dict) -> list:
    """Validate declared UI paths and read bounded source bytes without writing."""
    root = repository.resolve()
    if isinstance(manifest, dict) and manifest.get("kind") in ("panorama_source_intervention_screen", "panorama_source_voice_text", "panorama_source_orders_timeline", "panorama_source_opponent_roster", "panorama_source_match_observation", "panorama_source_mouse_proposal"):
        filename = {"panorama_source_intervention_screen": "intervention_screen_layout.py",
                    "panorama_source_voice_text": "voice_text_layout.py",
                    "panorama_source_orders_timeline": "orders_timeline_layout.py",
                    "panorama_source_opponent_roster": "opponent_roster_layout.py",
                    "panorama_source_match_observation": "match_observation_layout.py",
                    "panorama_source_mouse_proposal": "mouse_proposal_layout.py"}[manifest["kind"]]
        policy = REPOSITORY / "creators/creator-2/11-integration/02-addon-packaging/tools" / filename
        spec = importlib.util.spec_from_file_location("dota_coach_" + Path(filename).stem, policy)
        module = importlib.util.module_from_spec(spec)
        previous = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous
        return module.prepare(root, manifest, read_source)
    if isinstance(manifest, dict) and manifest.get("kind") == "panorama_source_preparation":
        return prepare_preparation(root, manifest)
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "kind", "assets"}:
        raise ValueError("Unsupported bundle manifest fields")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise ValueError("Unsupported bundle manifest version")
    kind = manifest["kind"]
    if not isinstance(kind, str) or kind not in ("panorama_source_probe", "panorama_source_hud", "panorama_source_intervention"):
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
        if kind == "panorama_source_hud" and HUD_ASSETS.get(source.as_posix()) != target.as_posix():
            raise ValueError("HUD requires the fixed source-to-target mapping")
        if kind == "panorama_source_intervention" and INTERVENTION_ASSETS.get(source.as_posix()) != target.as_posix():
            raise ValueError("Manual request requires the fixed source-to-target mapping")
        if kind == "panorama_source_probe" and (not source.is_relative_to(SOURCE_PREFIX) or source == SOURCE_PREFIX):
            raise ValueError("Source must belong to this UI library")
        if not target.is_relative_to(TARGET_PREFIX) or target == TARGET_PREFIX:
            raise ValueError("Target must belong to content/panorama")
        if source.suffix.lower() not in [".xml", ".js", ".css"] or target.suffix.lower() != source.suffix.lower():
            raise ValueError("Asset must preserve its XML/JS/CSS resource type")
        key = target.as_posix().casefold()
        if any(key == other or key.startswith(other + "/") or other.startswith(key + "/") for other in targets):
            raise ValueError("Duplicate or conflicting Windows destination")
        targets.add(key)
        payload = read_source(root, source.as_posix())
        prepared.append((source.as_posix(), target.as_posix(), payload))

    if kind == "panorama_source_hud":
        if {source: target for source, target, _ in prepared} != HUD_ASSETS:
            raise ValueError("HUD requires all 13 fixed resources")
        validate_hud_graph(prepared)
    if kind == "panorama_source_intervention":
        if {source: target for source, target, _ in prepared} != INTERVENTION_ASSETS:
            raise ValueError("Manual request requires all six fixed resources")
        validate_intervention_graph(prepared)
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
    report = {"schema_version": 1, "kind": manifest["kind"], "complete": True,
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
