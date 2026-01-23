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
from bascenev1lib.actor.spaz import PunchHitMessage, Spaz, PickupMessage

import random

# pylint: disable=super-init-not-called


class Punch(CharacterSkill):
    """cool lil punch"""

    cooldown_time = 1.2

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

    cooldown_time = 1.0

    def perform(self, spaz: BombgeonCharBase) -> None:
        # do a standard jump
        spaz.node.jump_pressed = True
        spaz.node.jump_pressed = False


class UndergroundDive(CharacterSkill):
    """bbombp"""

    cooldown_time = 16
    show_cooldown = True

    def __init__(self):
        super().__init__()
        # Gotta define it here or else problems
        self.texture_icon = bs.gettexture("shrapnel1Color")

    def perform(self, spaz: BombgeonCharBase) -> None:

        def getout():
            spaz.actionable = True
            spaz.node.jump_pressed = True
            spaz.node.jump_pressed = False

            spaz.node.head_mesh = bs.getmesh("cyborgHead")
            spaz.node.torso_mesh = bs.getmesh("cyborgTorso")
            spaz.node.pelvis_mesh = bs.getmesh("cyborgPelvis")
            spaz.node.upper_arm_mesh = bs.getmesh("cyborgUpperArm")
            spaz.node.forearm_mesh = bs.getmesh("cyborgForeArm")
            spaz.node.hand_mesh = bs.getmesh("cyborgHand")
            spaz.node.upper_leg_mesh = bs.getmesh("cyborgUpperLeg")
            spaz.node.lower_leg_mesh = bs.getmesh("cyborgLowerLeg")
            spaz.node.toes_mesh = bs.getmesh("cyborgToes")
            spaz.node.invincible = False
            spaz.gravelsound.delete()
            spaz.smoke.delete()
            spaz.node.run = 0.0

        def getin():
            if not spaz.is_alive():
                return
            spaz.node.head_mesh = None
            spaz.node.torso_mesh = None
            spaz.node.pelvis_mesh = None
            spaz.node.upper_arm_mesh = None
            spaz.node.forearm_mesh = None
            spaz.node.hand_mesh = None
            spaz.node.upper_leg_mesh = None
            spaz.node.lower_leg_mesh = None
            spaz.node.toes_mesh = None
            spaz.node.invincible = True
            spaz.gravelsound = bs.newnode(
                "sound",
                attrs={"sound": bs.getsound("gravelSkid"), "volume": 0.75},
            )
            spaz.smoke = bs.newnode(
                "flash",
                attrs={
                    "position": spaz.node.position,
                    "size": 0.3,
                    "color": spaz.node.color,
                },
            )
            _ = 0.1
            times = 45
            for i in range(times):
                bs.timer(_ * i, tick)

            bs.timer(_ * times, getout)

        def tick():
            if not spaz.is_alive():
                spaz.gravelsound.delete()
                spaz.smoke.delete()
                return
            spaz.node.run = 1.0
            bs.emitfx(
                position=spaz.node.position,
                velocity=(0, 2, 0),
                count=int(4.0 + random.random() * 8),
                scale=1,
                spread=1.0,
                chunk_type="rock",
            )
            spaz.armor_drain_rate *= 1.1
            def undrain():
                spaz.armor_drain_rate /= 1.1
            bs.timer(0.5, undrain)

            for _ in range(50):
                v = spaz.node.velocity
                spaz.node.handlemessage(
                    "impulse",
                    spaz.node.position[0],
                    spaz.node.position[1],
                    spaz.node.position[2],
                    0,
                    25,
                    0,
                    -15,
                    0.05,
                    0,
                    0,
                    0,
                    20 * 400,
                    0,
                )

            spaz.smoke.position = spaz.node.position

        spaz.actionable = False
        spaz.node.jump_pressed = True
        spaz.node.jump_pressed = False
        bs.timer(0.3, getin)


class GrabDash(CharacterSkill):
    """grab"""

    cooldown_time = 9
    show_cooldown = True

    def __init__(self):
        super().__init__()
        # Gotta define it here or else problems
        self.texture_icon = bs.gettexture("achievementSuperPunch")

    def perform(self, spaz: BombgeonCharBase) -> None:
        def grab():

            spaz.node.pickup_pressed = True
            spaz.node.pickup_pressed = False

        bs.timer(0.2, grab)
        xforce = 55
        yforce = 2
        for _ in range(50):
            v = spaz.node.velocity
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

        def sparkies():
            if spaz.node.exists():
                bs.emitfx(
                    position=spaz.node.position,
                    chunk_type="sweat",
                    count=5,
                    scale=1,
                    spread=0.6,
                )
                bs.emitfx(
                    position=spaz.node.position,
                    chunk_type="spark",
                    count=5,
                    scale=1.0,
                    spread=0.1,
                )

        bs.timer(0.01, bs.Call(sparkies))
        bs.timer(0.1, bs.Call(sparkies))
        bs.timer(0.2, bs.Call(sparkies))
        random.choice(SpazFactory.get().foot_impact_sounds).play(
            position=spaz.node.position
        )

        explode_sounds = (
            bs.getsound("explosion01"),
            bs.getsound("explosion02"),
            bs.getsound("explosion03"),
            bs.getsound("explosion04"),
            bs.getsound("explosion05"),
        )
        debris_fall_sound = bs.getsound("debrisFall")

        random.choice(explode_sounds).play(position=spaz.node.position)
        debris_fall_sound.play(position=spaz.node.position)


class B9000Character(BombgeonCharBase):
    """B9000 character."""

    # Rule of thumb: Don't use ``super().*``; instead, run ``BombgeonCharBase.*(self)``.
    # We inject character-based functions on runtime and python doesn't like that a lot.
    health = 100
    shields = 0
    armor = 5850
    retain_vanilla = False
    speed = 0.85

    skill_punch = Punch
    skill_jump = Jump
    skill_bomb = UndergroundDive
    skill_grab = GrabDash

    def __init__(self):
        # To define character specific variables, do ``def __init__(self)``
        # without calling anything but your own variables, and the system
        # will handle it accordingly.
        self._punch_power_scale *= 0.85
        # self.bomb_type = 'normal_modified'

        self.armor_drain_rate = 80

        self._armor_drain_timer = bs.Timer(1.0, bs.WeakCall(self._armor_drain_tick), repeat=True)


    def _armor_drain_tick(self):
                                # eh, dont do it if we stunned
        if not self.is_alive() or self.stunned:
            return
        if self.armorHP < 500:
            return
        self.armorHP = int(max(0, self.armorHP - self.armor_drain_rate))

    def custom_handlemessage(self, msg) -> bool:
        if isinstance(msg, PunchHitMessage):

            node = bs.getcollision().opposingnode

            # ow
            if node.getdelegate(Spaz) and (node not in self._punched_nodes):
                self.armor_drain_rate *= 1.8
                def undrain():
                    self.armor_drain_rate /= 1.8
                bs.timer(1.0, undrain)

            return False

        elif isinstance(msg, PickupMessage):
            if not self.node:
                return False

            try:
                collision = bs.getcollision()
                opposingnode = collision.opposingnode
                opposingbody = collision.opposingbody
            except bs.NotFoundError:
                return True

            # Don't allow picking up of invincible dudes.
            try:
                if opposingnode.invincible:
                    return True
            except Exception:
                pass

            other_dude = opposingnode.getdelegate(Spaz)
            assert isinstance(other_dude, Spaz)

            if opposingnode.getnodetype() == "spaz" and other_dude:
                # grab them and do som damage
                self.actionable = False
                self.node.hold_body = opposingbody
                self.node.hold_node = opposingnode
                self.node.invincible = True
                other_dude.stunned = True

                def hurt():
                    self.armorHP += 34
                   
                    other_dude.handlemessage(
                        bs.HitMessage(self.node, flat_damage=45)
                    )

                def actionable():
                    other_dude.stunned = False
                    self.node.hold_node = None
                    self.actionable = True
                    self.node.invincible = False

                _ = 0.2
                times = 12
                for i in range(times):
                    bs.timer(_ * i, hurt)

                bs.timer(_ * times, actionable)

                return True

            return False

        elif isinstance(msg, bs.DieMessage):
            self.handle_death(msg)
            return False
        else:
            return False

    def handle_death(self, msg) -> None:

        if not self._dead:
            self._safe_play_sound(bs.getsound("b900Die1"), 2)
            self._safe_play_sound(bs.getsound("b900Die2"), 2)
            SpazFactory.get().splatter_sound.play(
                1.0,
                position=self.node.position,
            )
            bs.emitfx(
                position=self.node.position,
                chunk_type="sweat",
                count=15,
                scale=1.2,
                spread=1.6,
            )
            bs.emitfx(
                position=self.node.position,
                chunk_type="spark",
                count=15,
                scale=1.0,
                spread=0.1,
            )
            self.node.shattered = 2
            Blast(
                self.node.position,
                (0, 0, 0),
                0.5,
            )


# Registering character for usage
sounds = ["cyborg1", "cyborg2", "cyborg3", "cyborg4"]
spaz_appearance = BombgeonAppearance(
    color_texture="cyborgColor",
    color_mask_texture="cyborgColorMask",
    icon_texture="cyborgIcon",
    icon_mask_texture="cyborgIconColorMask",
    head_mesh="cyborgHead",
    torso_mesh="cyborgTorso",
    pelvis_mesh="cyborgPelvis",
    upper_arm_mesh="cyborgUpperArm",
    forearm_mesh="cyborgForeArm",
    hand_mesh="cyborgHand",
    upper_leg_mesh="cyborgUpperLeg",
    lower_leg_mesh="cyborgLowerLeg",
    toes_mesh="cyborgToes",
    jump_sounds=sounds,
    attack_sounds=sounds,
    impact_sounds=[
        "cyborgHit1",
        "cyborgHit2",
    ],
    death_sounds=["cyborgDeath"],
    pickup_sounds=sounds,
    fall_sounds=["cyborgFall"],
    style="cyborg",
)

BombgeonCharacterEntry("B9000", B9000Character, spaz_appearance)
