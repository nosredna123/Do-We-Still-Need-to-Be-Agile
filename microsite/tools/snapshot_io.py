"""Strict public JSON/CSV serialization and contract validation helpers."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import TypeAlias

Scalar: TypeAlias = str | int | float | bool | None
Row: TypeAlias = dict[str, Scalar]


class ContractError(ValueError):
    """An explicit public contract validation failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def obj(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ContractError("Expected a JSON object")
    require(all(isinstance(k, str) for k in value), "Expected string object keys")
    return dict(value)


def array(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ContractError("Expected a JSON array")
    return list(value)


def text(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError("Expected a nonempty string")
    return value


def strict_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ContractError(f"Nonfinite JSON constant: {value}")


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs,
                      parse_constant=reject_constant)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def resolved(path: Path) -> Path:
    absolute = path.absolute()
    require(not any(p.is_symlink() for p in (absolute, *absolute.parents)),
            "Symlink paths are not accepted")
    return absolute.resolve()



def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False, indent=2) + "\n").encode("utf-8")


def csv_bytes(rows: list[Row]) -> bytes:
    require(bool(rows), "Cannot serialize an empty required dataset")
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    columns = list(rows[0])
    writer.writerow(columns)
    for row in rows:
        require(list(row) == columns, "Inconsistent output schema")
        cells = []
        for value in row.values():
            if isinstance(value, str):
                require(not value.lstrip(" ").startswith(("\t", "\r", "\n"))
                        and not value.lstrip().startswith(("=", "+", "-", "@")),
                        "Spreadsheet-unsafe text requires reviewed export handling")
            cells.append("" if value is None else ("true" if value is True else "false" if value is False else value))
        writer.writerow(cells)
    return stream.getvalue().encode("utf-8")

