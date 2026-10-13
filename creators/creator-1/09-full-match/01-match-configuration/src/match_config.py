"""C1-09-01 version binding: one launch owns actors, map, rules, content."""


def bind_version(config):
    """Return (bound, reason). Pure check, no engine."""
    if not isinstance(config, dict):
        return None, "not-a-dict"
    for field in ("launchVersion", "map", "patch", "rosters", "content"):
        if field not in config:
            return None, f"missing-{field}"
    if not config["launchVersion"]:
        return None, "empty-version"
    if config["patch"] is None:
        return None, "patch-unconfirmed"
    rosters = config["rosters"]
    if (not isinstance(rosters, list) or len(rosters) != 2
            or not all(isinstance(r, list) and len(r) == 5
                       for r in rosters)):
        return None, "need-two-fives"
    bound = dict(config)
    bound["bound"] = True
    return bound, "ok"
