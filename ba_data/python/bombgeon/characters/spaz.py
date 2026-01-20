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

from bascenev1lib.actor.spazfactory import SpazFactory
from bascenev1lib.actor.bomb import Bomb

# pylint: disable=super-init-not-called


class Punch(CharacterSkill):
    """cool lil punch"""
    cooldown_time = 0.6

    def perform(self, spaz: BombgeonCharBase) -> None:
        spaz._punched_nodes = set()
        spaz.node.punch_pressed = True
        spaz.node.punch_pressed = False
        if not spaz.node.hold_node:
                bs.timer(
                    0.1,
                    bs.WeakCall(
                        spaz._safe_play_sound,
                        SpazFactory.get().swish_sound,
                        0.8,
                    ),
                )

class Jump(CharacterSkill):
    """basic jump"""

    cooldown_time = 0.2

    def perform(self, spaz: BombgeonCharBase) -> None:
        # do a standard jump
        spaz.node.jump_pressed = True
        spaz.node.jump_pressed = False

class Bomb2(CharacterSkill):
    """bbombp"""

    cooldown_time = 0.0

    def perform(self, spaz: BombgeonCharBase) -> None:
        # do a standard jump
        spaz.node.bomb_pressed = True
        spaz.node.bomb_pressed = False
        if not spaz.node.hold_node:
            spaz.drop_bomb()

class Grab(CharacterSkill):
    """grab"""

    cooldown_time = 0.0

    def perform(self, spaz: BombgeonCharBase) -> None:
        # do a standard jump
        spaz.node.pickup_pressed = True
        spaz.node.pickup_pressed = False
     
        
        
        

class SpazCharacter(BombgeonCharBase):
    """Spaz character."""

    # Rule of thumb: Don't use ``super().*``; instead, run ``BombgeonCharBase.*(self)``.
    # We inject character-based functions on runtime and python doesn't like that a lot.
    health = 1000
    shields = 400
    armor = 150
    retain_vanilla = False
    speed = 0.9

            

    skill_punch = Punch
    skill_jump =  Jump
    skill_bomb=  Bomb2
    skill_grab=Grab
    
    def __init__(self):
        # To define character specific variables, do ``def __init__(self)``
        # without calling anything but your own variables, and the system
        # will handle it accordingly.
        self._punch_power_scale *= 0.8
        self.bomb_type = 'normal_modified'
    
    def handle_death(self, msg) -> None:
        # custom death logic here
        if not self._dead:
            print('im so dead rn')
        # don't forget to call the original function afterwards or else
        # you'll remain with a half-dead, half-alive spaz.
        BombgeonCharBase.handle_death(self, msg)


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
