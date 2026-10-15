"""Offline research import types. No engine/network side effects."""
import json
import re
from dataclasses import dataclass
from pathlib import Path


class DemImportError(Exception):
    def __init__(self, code: int, reason: str):
        super().__init__(reason)
        self.code, self.reason = code, reason


def canonical_json(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')
    except (ValueError, TypeError, UnicodeError) as exc:
        raise DemImportError(4, 'noncanonical_data') from exc


def uint64_decimal(value: int | str) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise DemImportError(4, 'invalid_uint64')
    if isinstance(value, str) and not re.fullmatch(r'0|[1-9][0-9]{0,19}', value):
        raise DemImportError(4, 'noncanonical_uint64')
    n = int(value)
    if not 0 <= n < 2 ** 64:
        raise DemImportError(4, 'uint64_overflow')
    return str(n)


@dataclass(frozen=True)
class InputSpec:
    input: Path
    match_id: int
    account_id: int
    lock: Path
    config: Path
    output: Path


@dataclass(frozen=True)
class Limits:
    max_input_bytes: int = 2147483648
    max_output_bytes: int = 536870912
    max_states: int = 2000000
    max_events: int = 2000000
    timeout_seconds: int = 300
    max_stderr_bytes: int = 1048576
    max_line_bytes: int = 65536
    java_heap_mib: int = 512
    max_windows: int = 1000
    max_index_entries: int = 10000


@dataclass
class ImportContext:
    spec: InputSpec
    limits: Limits
    hashes: dict[str, str]
    runtime: dict
    config: dict


@dataclass(frozen=True)
class ImportResult:
    status: str
    cache_key: str
    counts: dict
    data_hashes: dict
    output: str


@dataclass(frozen=True)
class EpisodeResult:
    index_count: int
    window_record_count: int
    data_hashes: dict[str, str]
