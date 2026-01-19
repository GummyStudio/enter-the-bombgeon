"""Spaz character."""

from typing import Any
import bascenev1 as bs

from bascenev1lib.actor.bomb import Blast
from .internal import (
    BombgeonCharBase,
    BombgeonAppearance,
    BombgeonCharacterEntry,
    CharacterSkill,
)

# pylint: disable=super-init-not-called


class ExplosivePunch(CharacterSkill):
    """A punch that summons an explosion at the end."""

    cooldown_time = 5.0

    def perform(self, spaz: BombgeonCharBase) -> None:
        spaz.node.punch_pressed = True
        spaz.node.punch_pressed = False

        def the_blast():
            if not spaz.can_do_action():
                # you need to be active to have a punch_position, apparently?
                return
            Blast(spaz.node.punch_position).autoretain()

        def _safesetattr(node: bs.Node | None, attr: str, val: Any) -> None:
            if node:
                setattr(node, attr, val)

        bs.timer(0.19, bs.Call(_safesetattr, spaz.node, "invincible", True))
        bs.timer(0.20, the_blast)
        bs.timer(0.21, bs.Call(_safesetattr, spaz.node, "invincible", False))


class SleepyJump(CharacterSkill):
    """A weak jump that stuns you."""

    cooldown_time = 3.0

    def perform(self, spaz: BombgeonCharBase) -> None:
        # do a standard jump
        spaz.node.jump_pressed = True
        spaz.node.jump_pressed = False
        # apply awesome force
        spaz.node.handlemessage(
            'kick_back',
            spaz.node.position[0],
            spaz.node.position[1]-1,
            spaz.node.position[2],
            0,
            1,
            0,
            750,
        )
        # stun lol
        bs.timer(0.01, lambda: spaz.node.handlemessage("knockout", 600))


class SpazCharacter(BombgeonCharBase):
    """Spaz character."""

    # Rule of thumb: Don't use ``super().*``; instead, run ``BombgeonCharBase.*(self)``.
    # We inject character-based functions on runtime and python doesn't like that a lot.
    health = 500
    retain_vanilla = False

    skill_punch = ExplosivePunch
    skill_jump = SleepyJump

    def __init__(self):
        # To define character specific variables, do ``def __init__(self)``
        # without calling anything but your own variables, and the system
        # will handle it accordingly.
        ...


# Registering character for usage

spaz_appearance = BombgeonAppearance(
    color_texture="neoSpazColor",
    color_mask_texture="neoSpazColorMask",
    icon_texture="neoSpazIcon",
    icon_mask_texture="neoSpazIconColorMask",
    head_mesh="neoSpazHead",
    torso_mesh="neoSpazTorso",
    pelvis_mesh="neoSpazPelvis",
    upper_arm_mesh="neoSpazUpperArm",
    forearm_mesh="neoSpazForeArm",
    hand_mesh="neoSpazHand",
    upper_leg_mesh="neoSpazUpperLeg",
    lower_leg_mesh="neoSpazLowerLeg",
    toes_mesh="neoSpazToes",
    jump_sounds=["spazJump01", "spazJump02", "spazJump03", "spazJump04"],
    attack_sounds=[
        "spazAttack01",
        "spazAttack02",
        "spazAttack03",
        "spazAttack04",
    ],
    impact_sounds=[
        "spazImpact01",
        "spazImpact02",
        "spazImpact03",
        "spazImpact04",
    ],
    death_sounds=["spazDeath01"],
    pickup_sounds=["spazPickup01"],
    fall_sounds=["spazFall01"],
    style="spaz",
)

BombgeonCharacterEntry("Spaz", SpazCharacter, spaz_appearance)
