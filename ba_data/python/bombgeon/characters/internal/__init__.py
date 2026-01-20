"""Custom Bombgeon character; main module with shared functions."""

from __future__ import annotations

import functools
from enum import Enum
from abc import abstractmethod
from dataclasses import dataclass, field
from inspect import isfunction
from types import MethodType
from typing import Any, Optional, Sequence, Type, Union, override

import bascenev1 as bs
from bascenev1lib.actor import spaz
from bascenev1lib.actor.spazappearance import Appearance

from bombgeon.utils import AVAILABLE_STYLES


class _ChrBtn(Enum):
    PUNCH = "punch"
    GRAB = "grab"
    BOMB = "bomb"
    JUMP = "jump"


class BombgeonCharBase(spaz.Spaz):
    """Bombgeon character with unique qualities."""

    # basic stats
    health: int = 1000
    shields: int = 0
    armor: int = 0
    speed: float = 1.0

    # skills to inputs
    skill_punch: Optional[Type[CharacterSkill]] = None
    skill_grab: Optional[Type[CharacterSkill]] = None
    skill_bomb: Optional[Type[CharacterSkill]] = None
    skill_jump: Optional[Type[CharacterSkill]] = None

    retain_vanilla: bool = True
    """if True, any unassigned skills with fallback to vanilla spaz moves."""

    def _character_method_override(self, character: str):
        """Get functions and variables from an extenral class
        according to the character we are currently using.
        """
        # it's a pretty ugly fix but it gets the job done.
        for char in get_bombgeon_roster():
            if not character == char.name:
                continue
            for name, method in char.character.__dict__.items():
                if name.startswith("__"):
                    if name == "__init__":
                        method(self)
                    continue
                if isfunction(method):
                    setattr(self, name, MethodType(method, self))
                else:
                    setattr(self, name, method)
            return
        raise NameError(
            f'no bombgeon charbase matches for character "{character}"'
        )

    def __init__(
        self,
        color: Sequence[float] = (0.5, 0.5, 0.5),
        highlight: Sequence[float] = (0.5, 0.5, 0.5),
        character: str = "Spaz",
        source_player: bs.Player | None = None,
        start_invincible: bool = True,
        can_accept_powerups: bool = True,
        powerups_expire: bool = False,
        demo_mode: bool = False,
    ):
        super().__init__(
            color,
            highlight,
            character,
            source_player,
            start_invincible,
            can_accept_powerups,
            powerups_expire,
            demo_mode,
        )
        self._character_method_override(character)

        self.hitpoints = self.hitpoints_max = self.health
        self.shieldHP = self.shieldHP_max = self.shields
        self.armorHP = self.armorHP_max = self.armor

        self._skills: dict[_ChrBtn, Optional[CharacterSkill]] = {
            _ChrBtn.PUNCH: None,
            _ChrBtn.GRAB: None,
            _ChrBtn.BOMB: None,
            _ChrBtn.JUMP: None,
        }
        self._define_skills()

    def _define_skills(self) -> None:
        skill_table: list[tuple[_ChrBtn, Optional[Type[CharacterSkill]]]] = [
            (_ChrBtn.PUNCH, self.skill_punch),
            (_ChrBtn.GRAB, self.skill_grab),
            (_ChrBtn.BOMB, self.skill_bomb),
            (_ChrBtn.JUMP, self.skill_jump),
        ]

        for _skill_button, _skill_slot in skill_table:
            if not self.retain_vanilla:
                # if we don't want to retain vanilla actions, override
                # any unassigned skills with an empty character skill
                if _skill_slot is None:
                    _skill_slot = CharacterSkill

            if _skill_slot is not None:
                self._skills[_skill_button] = _skill_slot()

    @override
    def on_punch_press(self) -> None:
        self._handle_skill(_ChrBtn.PUNCH)

    @override
    def on_pickup_press(self) -> None:
        self._handle_skill(_ChrBtn.GRAB)

    @override
    def on_bomb_press(self) -> None:
        self._handle_skill(_ChrBtn.BOMB)

    @override
    def on_jump_press(self) -> None:
        self._handle_skill(_ChrBtn.JUMP)

    def can_do_action(self) -> bool:
        """Return if we can perform actions and skills.
        AKA if we exist, are alive and aren't stunned.
        """
        return (
            self.exists() and self.is_alive() and not self.node.knockout > 0.0 and not self.frozen
        )

    def _handle_skill(self, skill_input: _ChrBtn) -> Any:
        if not self.can_do_action():
            return

        # get our skill that should exist by now
        skill = self._skills.get(skill_input)
        if skill is None:
            # if we got nothin', we probably want to retain
            # vanilla actions. fall back to those.
            match skill_input:
                case _ChrBtn.PUNCH:
                    super().on_punch_press()
                case _ChrBtn.GRAB:
                    super().on_pickup_press()
                case _ChrBtn.BOMB:
                    super().on_bomb_press()
                case _ChrBtn.JUMP:
                    super().on_jump_press()
            return

        if skill.can_perform():
            skill.perform(self)

    def _handle_movement(self) -> None: ...

    def on_expire(self) -> None:
        """Additional expire logic."""
        # clear our skills to prevent any funny business.
        self._skills = {}
        return super().on_expire()
    
    def handlemessage(self, msg): return super().handlemessage(msg)


class CharacterSkill:
    """A bombgeon character's skill.

    Should be assigned to an input.
    By default, does nothing; to implement functionality, override
    the ``perform(char)`` function to whatever you want it to do.
    """

    cooldown_time: float = 1.0
    """Cooldown time in seconds."""

    def __init__(self) -> None:
        self._last_use: float = -9999.9

    def can_perform(self) -> bool:
        """A character has requested to use this ability, check
        if we have the time to do so and return so as output.
        """
        _t = bs.time()
        if self._last_use > _t:
            return False

        self._last_use = _t + self.cooldown_time
        return True

    @abstractmethod
    def perform(self, spaz: BombgeonCharBase) -> None:
        """Perform this skill."""


# Write to BombSquad's spaz character with our own
spaz.Spaz = BombgeonCharBase

_LOGGING = True

_BOMBGEON_CHARACTER_ENTRIES: list[BombgeonCharacterEntry] = []


@dataclass
class BombgeonAppearance:
    """Create and fill out one of these suckers to define a spaz appearance."""

    color_texture: str = ""
    color_mask_texture: str = ""
    icon_texture: str = ""
    icon_mask_texture: str = ""
    head_mesh: str = ""
    torso_mesh: str = ""
    pelvis_mesh: str = ""
    upper_arm_mesh: str = ""
    forearm_mesh: str = ""
    hand_mesh: str = ""
    upper_leg_mesh: str = ""
    lower_leg_mesh: str = ""
    toes_mesh: str = ""
    jump_sounds: list[str] = field(default_factory=list)
    attack_sounds: list[str] = field(default_factory=list)
    impact_sounds: list[str] = field(default_factory=list)
    death_sounds: list[str] = field(default_factory=list)
    pickup_sounds: list[str] = field(default_factory=list)
    fall_sounds: list[str] = field(default_factory=list)
    style: AVAILABLE_STYLES = "spaz"
    default_color: Optional[tuple[float, float, float]] = None
    default_highlight: Optional[tuple[float, float, float]] = None


@dataclass
class BombgeonCharacterEntry:
    """An entry for a Bombgeon character.
    Defines and makes a character playable.
    """

    name: str
    character: Type[BombgeonCharBase]
    appearance: Union[Appearance, BombgeonAppearance]

    def __post_init__(self) -> None:
        if self in _BOMBGEON_CHARACTER_ENTRIES:
            raise ValueError(f'"{self}" already registered.')

        _BOMBGEON_CHARACTER_ENTRIES.append(self)
        if _LOGGING:
            print('registered bombgeon char: "%s"', self)


def get_bombgeon_roster() -> list[BombgeonCharacterEntry]:
    """Get all registered bombgeon characters."""
    return _BOMBGEON_CHARACTER_ENTRIES


def apply_bombgeon_roster():
    """Apply our bombgeon roster to the character roster."""
    assert bs.app.classic
    bs.app.classic.spaz_appearances = {}

    for entry in get_bombgeon_roster():
        assert entry.appearance is Appearance
        bs.app.classic.spaz_appearances[entry.name] = entry.appearance

    