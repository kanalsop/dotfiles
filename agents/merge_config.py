#!/usr/bin/env python3
"""Merge a managed JSON or TOML config into a target file that the agent also writes to.

Keys from the source override the target; nested tables merge recursively, other values
(including arrays) are replaced. Keys only present in the target are kept. Requires Python 3.11+.
"""

import argparse
import json
import re
import shutil
import sys
import tomllib
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

BARE_KEY = re.compile(r"[A-Za-z0-9_-]+")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="print the action without writing")
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    print(merge_file(args.source, args.target, args.dry_run))
    return 0


def merge_file(source: Path, target: Path, dry_run: bool) -> str:
    """Merge source into target and return a one-line report."""
    codec = JsonCodec if source.suffix == ".json" else TomlCodec
    current = codec.load(target.read_text()) if target.exists() else None
    merged = deep_merge(current or {}, codec.load(source.read_text()))
    if merged == current:
        return f"unchanged: {target}"
    if dry_run:
        return f"[dry-run] merged: {target} <- {source}"
    backup = backup_file(target) if target.exists() else None
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(codec.dump(merged))
    suffix = f" (backup: {backup})" if backup else ""
    return f"merged: {target} <- {source}{suffix}"


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def backup_file(path: Path) -> Path:
    backup = path.with_name(f"{path.name}.bak.{datetime.now():%Y%m%d%H%M%S}")
    shutil.copy2(path, backup)
    return backup


class JsonCodec:
    @staticmethod
    def load(text: str) -> dict[str, Any]:
        return json.loads(text)

    @staticmethod
    def dump(data: dict[str, Any]) -> str:
        return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


class TomlCodec:
    @staticmethod
    def load(text: str) -> dict[str, Any]:
        return tomllib.loads(text)

    @staticmethod
    def dump(data: dict[str, Any]) -> str:
        lines: list[str] = []
        _emit_body(lines, [], data)
        return "\n".join(lines).lstrip("\n") + "\n"


def _emit_body(lines: list[str], path: list[str], table: dict[str, Any]) -> None:
    """Emit scalars before sub-tables, as TOML requires keys to precede nested headers."""
    nested = {key: value for key, value in table.items() if _is_table(value) or _is_table_array(value)}
    for key, value in table.items():
        if key not in nested:
            lines.append(f"{_key(key)} = {_value(value)}")
    for key, value in nested.items():
        if _is_table(value):
            _emit_table(lines, [*path, key], value)
    for key, value in nested.items():
        if _is_table_array(value):
            for item in value:
                lines += ["", f"[[{_dotted([*path, key])}]]"]
                _emit_body(lines, [*path, key], item)


def _emit_table(lines: list[str], path: list[str], table: dict[str, Any]) -> None:
    has_scalars = any(not (_is_table(v) or _is_table_array(v)) for v in table.values())
    if has_scalars or not table:
        lines += ["", f"[{_dotted(path)}]"]
    _emit_body(lines, path, table)


def _is_table(value: Any) -> bool:
    return isinstance(value, dict)


def _is_table_array(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, dict) for item in value)


def _dotted(path: list[str]) -> str:
    return ".".join(map(_key, path))


def _key(key: str) -> str:
    return key if BARE_KEY.fullmatch(key) else _string(key)


def _string(text: str) -> str:
    return json.dumps(text, ensure_ascii=False).replace("\x7f", "\\u007f")


def _value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return _string(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, list):
        return "[" + ", ".join(map(_value, value)) + "]"
    if isinstance(value, dict):
        pairs = ", ".join(f"{_key(k)} = {_value(v)}" for k, v in value.items())
        return "{ " + pairs + " }" if pairs else "{}"
    raise TypeError(f"unsupported TOML value: {value!r}")


if __name__ == "__main__":
    sys.exit(main())
