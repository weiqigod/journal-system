"""Durable workflow state in SQLite.

Workflow state is saved as rows of JSON, one per record, keyed by collection
and ID (for example `obligations/ob12`), so the file can be read with the
sqlite3 shell. When an operation commits, the rows it changed are written in
one SQLite transaction; if the process dies first, the file still holds the
previous committed state.

Each commit compares every row with its value before the operation, which
costs time in proportion to the whole state. That is acceptable for this
prototype, not for production volumes.
"""

from __future__ import annotations

import dataclasses
import enum
import json
import sqlite3
from datetime import datetime

from . import model

_TYPES = {cls.__name__: cls for cls in vars(model).values()
          if isinstance(cls, type) and (dataclasses.is_dataclass(cls) or issubclass(cls, enum.Enum))}


def encode(value):
    if dataclasses.is_dataclass(value):
        return {"__type": type(value).__name__,
                **{f.name: encode(getattr(value, f.name)) for f in dataclasses.fields(value)}}
    if isinstance(value, enum.Enum):
        return {"__enum": type(value).__name__, "value": value.value}
    if isinstance(value, datetime):
        return {"__datetime": value.isoformat()}
    if isinstance(value, (set, frozenset)):
        return {"__set": sorted(value)}
    if isinstance(value, tuple):
        return {"__tuple": [encode(item) for item in value]}
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {"__dict": {key: encode(item) for key, item in value.items()}}
    return value


def decode(value):
    if isinstance(value, list):
        return [decode(item) for item in value]
    if not isinstance(value, dict):
        return value
    if "__type" in value:
        cls = _TYPES[value["__type"]]
        return cls(**{key: decode(item) for key, item in value.items() if key != "__type"})
    if "__enum" in value:
        return _TYPES[value["__enum"]](value["value"])
    if "__datetime" in value:
        return datetime.fromisoformat(value["__datetime"])
    if "__set" in value:
        return set(value["__set"])
    if "__tuple" in value:
        return tuple(decode(item) for item in value["__tuple"])
    if "__dict" in value:
        return {key: decode(item) for key, item in value["__dict"].items()}
    raise ValueError(f"unknown encoded value {value!r}")


def rows(state) -> dict[str, str]:
    """Flatten workflow state into rows: one per dict entry, list item, or set member; scalars under `meta/`."""
    flat = {}
    for f in dataclasses.fields(state):
        value = getattr(state, f.name)
        if isinstance(value, dict):
            items = value.items()
        elif isinstance(value, list):
            items = ((f"{index:09d}", item) for index, item in enumerate(value))
        elif isinstance(value, set):
            items = ((member, True) for member in value)
        else:
            flat[f"meta/{f.name}"] = json.dumps(encode(value), sort_keys=True)
            continue
        for key, item in items:
            flat[f"{f.name}/{key}"] = json.dumps(encode(item), sort_keys=True)
    return flat


class WorkflowStore:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path, isolation_level=None)
        self.connection.execute("PRAGMA synchronous = FULL")
        self.connection.execute("CREATE TABLE IF NOT EXISTS workflow (key TEXT PRIMARY KEY, doc TEXT NOT NULL)")

    def load(self, state_type):
        """The last committed state, or None for a new file."""
        found = self.connection.execute("SELECT key, doc FROM workflow ORDER BY key").fetchall()
        if not found:
            return None
        state = state_type()
        for key, doc in found:
            collection, _, item = key.partition("/")
            value = decode(json.loads(doc))
            if collection == "meta":
                setattr(state, item, value)
                continue
            target = getattr(state, collection)
            if isinstance(target, dict):
                target[item] = value
            elif isinstance(target, list):
                target.append(value)
            else:
                target.add(item)
        return state

    def save(self, before, after) -> None:
        old, new = rows(before), rows(after)
        changed = [(key, doc) for key, doc in new.items() if old.get(key) != doc]
        removed = [(key,) for key in old.keys() - new.keys()]
        if not changed and not removed:
            return
        cursor = self.connection.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        try:
            cursor.executemany("INSERT OR REPLACE INTO workflow (key, doc) VALUES (?, ?)", changed)
            cursor.executemany("DELETE FROM workflow WHERE key = ?", removed)
            cursor.execute("COMMIT")
        except BaseException:
            cursor.execute("ROLLBACK")
            raise

    def close(self) -> None:
        self.connection.close()
