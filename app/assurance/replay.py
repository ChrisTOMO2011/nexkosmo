from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Callable, Generic, TypeVar

StateT = TypeVar("StateT")


@dataclass(frozen=True, slots=True)
class ReplayEnvelope:
    schema_version: int
    code_ref: str
    config_ref: str
    events: tuple[dict[str, Any], ...]

    def canonical_json(self) -> str:
        payload = {
            "schema_version": self.schema_version,
            "code_ref": self.code_ref,
            "config_ref": self.config_ref,
            "events": self.events,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ReplayResult(Generic[StateT]):
    envelope_digest: str
    final_state: StateT


def replay(
    envelope: ReplayEnvelope,
    *,
    initial_state: StateT,
    reducer: Callable[[StateT, dict[str, Any]], StateT],
) -> ReplayResult[StateT]:
    state = initial_state
    for event in envelope.events:
        state = reducer(state, event)
    return ReplayResult(envelope_digest=envelope.digest(), final_state=state)
