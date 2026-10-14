"""C1-08-02 hero capabilities: supported set, cooldowns, profile separation.

Hero capabilities are described separately from the human profile: the set
answers what the hero MAY do, never what the person WILL do. Orders cannot
bypass hero limits — unavailable ability, cooldown and incompatible profile
are refused openly. The supported set is a TEST proposal until the actual
patch is established; entries are patch-gated (patch=None means TEST).
"""
import json


def load_set(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def attempt(action_set, hero, action, kind, profile_heroes=(),
            on_cooldown=False):
    """Return (ok, reason). Pure gate, no engine."""
    if action_set.get("patch") is None and not action_set.get("_test_ok"):
        return False, "patch-unconfirmed"
    heroes = action_set.get("heroes", {})
    if hero not in heroes:
        return False, "hero-not-supported"
    if profile_heroes and hero not in profile_heroes:
        return False, "incompatible-profile"
    if on_cooldown:
        return False, "on-cooldown"
    if kind not in ("ability", "item"):
        return False, "bad-kind"
    pool = heroes[hero].get("abilities" if kind == "ability" else "items", [])
    if action not in pool:
        return False, "ability-unavailable"
    return True, "ok"
