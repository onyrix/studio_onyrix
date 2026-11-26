"""Role definitions: pitch ranges, polyphony, default GM programs and density targets.

Defaults follow CLAUDE.md section 6.5; every field is overridable with `role_spec(role, ...)`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from app.core.model import Role


@dataclass(frozen=True)
class RoleSpec:
    role: Role
    low: int  # lowest allowed MIDI pitch (inclusive)
    high: int  # highest allowed MIDI pitch (inclusive)
    max_polyphony: int  # simultaneous onsets allowed; 1 = monophonic
    program: int  # default GM program (ignored for drums)
    target_notes_per_bar: float  # D* in the scorer
    is_drum: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.low <= self.high <= 127:
            raise ValueError(f"invalid pitch range {self.low}..{self.high}")
        if self.max_polyphony < 1:
            raise ValueError("max_polyphony must be >= 1")
        if self.target_notes_per_bar <= 0:
            raise ValueError("target_notes_per_bar must be > 0")

    @property
    def monophonic(self) -> bool:
        return self.max_polyphony == 1


ROLE_SPECS: dict[Role, RoleSpec] = {
    Role.BASS: RoleSpec(Role.BASS, 28, 55, 1, 33, 4.0),
    Role.CHORDS: RoleSpec(Role.CHORDS, 48, 79, 6, 0, 8.0),
    Role.PAD: RoleSpec(Role.PAD, 48, 84, 6, 89, 4.0),
    Role.LEAD: RoleSpec(Role.LEAD, 60, 96, 1, 80, 4.0),
    Role.DRUMS: RoleSpec(Role.DRUMS, 35, 81, 6, 0, 12.0, is_drum=True),
    Role.OTHER: RoleSpec(Role.OTHER, 36, 96, 6, 0, 4.0),
}


def role_spec(role: Role | str, **overrides: Any) -> RoleSpec:
    spec = ROLE_SPECS[Role(role)]
    return replace(spec, **overrides) if overrides else spec
