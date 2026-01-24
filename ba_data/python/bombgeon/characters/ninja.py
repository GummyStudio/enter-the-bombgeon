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

import random

# pylint: disable=super-init-not-called


class FastPunch(CharacterSkill):
    """cool lil punch"""

    cooldown_time = 0.2

    def perform(self, spaz: BombgeonCharBase) -> None:
        spaz._punched_nodes = set()

        spaz.node.punch_pressed = True
        spaz.node.punch_pressed = False

        spaz.node.hold_position_pressed = True
        bs.timer(0.1, bs.Call(setattr, spaz.node, 'hold_position_pressed', False))


class Jump(CharacterSkill):
    """basic jump"""

    cooldown_time = 0.1

    def perform(self, spaz: BombgeonCharBase) -> None:
        # do a standard jump
        spaz.node.jump_pressed = True
        spaz.node.jump_pressed = False


class TimeTravel(CharacterSkill):
    """Tracer Overwatch"""

    cooldown_time = 20
    show_cooldown = True

    def __init__(self):
        super().__init__()
        self.texture_icon = bs.gettexture('backIcon')
        self.ticks: int = 0
        self.tick_timer: bs.Timer = None

    def perform(self, spaz: BombgeonCharBase) -> None:
        self.ticks = 0
        def tick():
            if not spaz.is_alive():
                spaz.light.delete()
                self.tick_timer = None
                return
            spaz.light.position = spaz.node.position
            spaz.light.radius = self.ticks * 0.008
            self.ticks += 1

            if self.ticks == 25:
                spaz.teleport()
                self.tick_timer = None
                spaz.light.delete()
                return
        spaz.light = bs.newnode('light', attrs={'color': spaz.node.color})
        self.tick_timer = bs.Timer(0.1, tick, repeat=True)


class Dash(CharacterSkill):
    """dashing it"""
    def __init__(self):
        super().__init__()
        self.pos: list[float, float, float] = None
        self.texture_icon = bs.gettexture('buttonBomb')

    cooldown_time = 5.3
    show_cooldown = True

    def perform(self, spaz: BombgeonCharBase) -> None:
        def boom():
            if self.pos:
                Blast(
                    self.pos,
                    blast_radius=1.6,
                    source_player=spaz.source_player,

                )

        self.pos = spaz.node.position
        bs.timer(0.3, boom)
        xforce = 35
        yforce = 5
        spaz.node.handlemessage(
                "impulse",
                spaz.node.position[0],
                spaz.node.position[1],
                spaz.node.position[2],
                0,
                25,
                0,
                yforce,
                0.05,
                0,
                0,
                0,
                20 * 400,
                0,
        )
        v = spaz.node.velocity
        for _ in range(50):
            spaz.node.handlemessage(
                    "impulse",
                    spaz.node.position[0],
                    spaz.node.position[1],
                    spaz.node.position[2],
                    0,
                    25,
                    0,
                    xforce,
                    0.05,
                    0,
                    0,
                    v[0] * 15 * 2,
                    0,
                    v[2] * 15 * 2,
            )



class NinjaCharacter(BombgeonCharBase):
    """Spaz character."""

    # Rule of thumb: Don't use ``super().*``; instead, run ``BombgeonCharBase.*(self)``.
    # We inject character-based functions on runtime and python doesn't like that a lot.
    health = 450
    shields = 200
    armor = 50
    retain_vanilla = False
    speed = 0.55

    skill_punch = FastPunch
    skill_jump = Jump
    skill_bomb = Dash
    skill_grab = TimeTravel

    def __init__(self):
        # To define character specific variables, do ``def __init__(self)``
        # without calling anything but your own variables, and the system
        # will handle it accordingly.
        self._punch_power_scale *= 1.1
        # pos, hp, shields, and armor
        self.positions: list[tuple[float, float, float], int, int, int] = []
        self.stepping_timer: bs.Timer | None = None
        bs.timer(0.1, self.save_position, repeat=True)

    def teleport(self):
        if not self.positions or not self.exists() or self.stepping_timer:
            return

        # haha fuck you loser
        self.node.invincible = True
        self.actionable = False

        
        rewind_states = list(reversed(self.positions))
        self.positions.clear()

        index = 0

        def step():
            nonlocal index
            if not self.exists():
                return

            # final
            if index >= len(rewind_states):
                self.node.invincible = False
                self.stepping_timer = None
                self.actionable = True
                return

            pos, hp, shield, armor = rewind_states[index]

            
            self.node.handlemessage(bs.StandMessage((
                pos[0],
                pos[1]-1,
                pos[2]
            ), random.uniform(-255, 255)))
            self.hitpoints = hp
            self.shieldHP = shield
            self.armorHP = armor

            index += 1

        self.stepping_timer = bs.Timer(0.0035, step, repeat=True)
    
    def save_position(self):
        if not self.exists():
            return
        self.positions.append(
            [
                self.node.position,
                self.hitpoints,
                self.shieldHP,
                self.armorHP,
            ]
        )

        if len(self.positions) == 40:
            self.positions.pop(0)

    def handle_death(self, msg) -> None:
        # custom death logic here
        if not self._dead:
            print("im so dead rn")
        # don't forget to call the original function afterwards or else
        # you'll remain with a half-dead, half-alive spaz.
        BombgeonCharBase.handle_death(self, msg)


# Registering character for usage
sounds = [
        "ninjaAttack1",
        "ninjaAttack2",
        "ninjaAttack3",
        "ninjaAttack4",
        "ninjaAttack5",
        "ninjaAttack6",
        "ninjaAttack7",
]
spaz_appearance = BombgeonAppearance(
    color_texture="ninjaColor",
    color_mask_texture="ninjaColorMask",
    icon_texture="ninjaIcon",
    icon_mask_texture="ninjaIconColorMask",
    head_mesh="ninjaHead",
    torso_mesh="ninjaTorso",
    pelvis_mesh="ninjaPelvis",
    upper_arm_mesh="ninjaUpperArm",
    forearm_mesh="ninjaForeArm",
    hand_mesh="ninjaHand",
    upper_leg_mesh="ninjaUpperLeg",
    lower_leg_mesh="ninjaLowerLeg",
    toes_mesh="ninjaToes",
    jump_sounds=sounds,
    attack_sounds=sounds,
    impact_sounds=[
        "ninjaHit1",
        "ninjaHit2",
        "ninjaHit3",
        "ninjaHit4",
        "ninjaHit5",
        "ninjaHit6",
        "ninjaHit7",
        "ninjaHit8",
    ],
    death_sounds=["ninjaDeath1"],
    pickup_sounds=sounds,
    fall_sounds=["ninjaFall1"],
    style="ninja",
)

BombgeonCharacterEntry("Snake Shadow", NinjaCharacter, spaz_appearance)
