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
import random
from bascenev1lib.actor import spaz
# pylint: disable=super-init-not-called


class HealingPunch(CharacterSkill):
    """A punch that can heal teammates, but weak on its own"""

    cooldown_time = 0.5

    def perform(self, spaz: BombgeonCharBase) -> None:
        spaz._punched_nodes = set()

        spaz.node.punch_pressed = True
        spaz.node.punch_pressed = False



class Jump(CharacterSkill):
    """basic jump"""

    cooldown_time = 0.1

    def perform(self, spaz: BombgeonCharBase) -> None:
        # do a standard jump
        spaz.node.jump_pressed = True
        spaz.node.jump_pressed = False


class Throw(CharacterSkill):
    """has a bomb, throw it."""

    cooldown_time = 0.1

    def perform(self, spaz: BombgeonCharBase) -> None:
        if spaz.node.hold_node:
            spaz.node.pickup_pressed = True
            spaz.node.pickup_pressed = False


class HealingBomb(CharacterSkill):
    """dashing it"""

    cooldown_time = 0.1

    def perform(self, spaz: BombgeonCharBase) -> None:
        spaz.node.bomb_pressed = True
        if not spaz.node.hold_node:
            spaz.drop_bomb()
        spaz.node.bomb_pressed = False



class ZoeCharacter(BombgeonCharBase):
    """Zoe character."""

    # Rule of thumb: Don't use ``super().*``; instead, run ``BombgeonCharBase.*(self)``.
    # We inject character-based functions on runtime and python doesn't like that a lot.
    health = 1000
    shields = 200
    armor = 0
    retain_vanilla = False
    speed = 0.7

    skill_punch = HealingPunch
    skill_jump = Jump
    skill_bomb = HealingBomb
    skill_grab = Throw

    def __init__(self):
        # To define character specific variables, do ``def __init__(self)``
        # without calling anything but your own variables, and the system
        # will handle it accordingly.
        self._punch_power_scale *= 0.7
        self.bomb_type = 'healing_bomb'
        self.bomb_count = 5

    def custom_handlemessage(self, msg):
        if isinstance(msg, spaz.PunchHitMessage):
            if not self.node:
                return False
            node = bs.getcollision().opposingnode

            # Don't want to physically affect powerups.
            if node.getdelegate(spaz.PowerupBox):
                return True

            # Only allow one hit per node per punch.
            if node and (node not in self._punched_nodes):
                punch_momentum_angular = (
                    self.node.punch_momentum_angular * self._punch_power_scale
                )
                punch_power = self.node.punch_power * self._punch_power_scale

                # Ok here's the deal:  we pass along our base velocity for use
                # in the impulse damage calculations since that is a more
                # predictable value than our fist velocity, which is rather
                # erratic. However, we want to actually apply force in the
                # direction our fist is moving so it looks better. So we still
                # pass that along as a direction. Perhaps a time-averaged
                # fist-velocity would work too?.. perhaps should try that.

                # If its something besides another spaz, just do a muffled
                # punch sound.
                if node.getnodetype() != 'spaz':
                    sounds = SpazFactory.get().impact_sounds_medium
                    sound = sounds[random.randrange(len(sounds))]
                    sound.play(1.0, position=self.node.position)

                ppos = self.node.punch_position
                punchdir = self.node.punch_velocity
                vel = self.node.punch_momentum_linear

                self._punched_nodes.add(node)

              
                other_spaz = node.getdelegate(spaz.Spaz) 

                if other_spaz:
                    assert isinstance(other_spaz, spaz.Spaz)
                    other_team = other_spaz.team

                    if other_team == self.team:
                        
                        other_spaz.healing(7.6, False, 1.3)
                    else:
                        node.handlemessage(
                            bs.HitMessage(
                                pos=ppos,
                                velocity=vel,
                                magnitude=punch_power * punch_momentum_angular * 110.0,
                                velocity_magnitude=punch_power * 40,
                                radius=0,
                                srcnode=self.node,
                                source_player=self.source_player,
                                force_direction=punchdir,
                                hit_type='punch',
                                hit_subtype=(
                                    'super_punch'
                                    if self._has_boxing_gloves
                                    else 'default'
                                ),
                            )
                        )

                
                

                # Also apply opposite to ourself for the first punch only.
                # This is given as a constant force so that it is more
                # noticeable for slower punches where it matters. For fast
                # awesome looking punches its ok if we punch 'through'
                # the target.
                mag = -400.0
                if self._hockey:
                    mag *= 0.5
                if len(self._punched_nodes) == 1:
                    self.node.handlemessage(
                        'kick_back',
                        ppos[0],
                        ppos[1],
                        ppos[2],
                        punchdir[0],
                        punchdir[1],
                        punchdir[2],
                        mag,
                    )
            return False
        else:
            return False
    


spaz_appearance = BombgeonAppearance(
    color_texture="zoeColor",
    color_mask_texture="zoeColorMask",
    icon_texture="zoeIcon",
    icon_mask_texture="zoeIconColorMask",
    head_mesh="zoeHead",
    torso_mesh="zoeTorso",
    pelvis_mesh="zoePelvis",
    upper_arm_mesh="zoeUpperArm",
    forearm_mesh="zoeForeArm",
    hand_mesh="zoeHand",
    upper_leg_mesh="zoeUpperLeg",
    lower_leg_mesh="zoeLowerLeg",
    toes_mesh="zoeToes",
    jump_sounds=["zoeJump01", "zoeJump02", "zoeJump03", "zoeJump04"],
    attack_sounds=[
        "zoeAttack01",
        "zoeAttack02",
        "zoeAttack03",
    ],
    impact_sounds=[
        "zoeImpact01",
        "zoeImpact02",
        "zoeImpact03",
        "zoeImpact04",
    ],
    death_sounds=["zoeDeath01"],
    pickup_sounds=["zoePickup01"],
    fall_sounds=["zoeFall01"],
    style="female",
)

BombgeonCharacterEntry("Zoe", ZoeCharacter, spaz_appearance)
