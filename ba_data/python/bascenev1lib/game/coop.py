# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 8
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING, override

import bascenev1 as bs

from bascenev1lib.actor.spaz import Spaz
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.gameutils import SharedObjects
from enum import Enum
from bascenev1lib.actor.spazfactory import SpazFactory
from bascenev1lib.actor.spazbot import (
    SpazBotSet,
    BomberBot,
    BrawlerBot
)

from bascenev1lib.actor.flag import Flag

if TYPE_CHECKING:
    from typing import Any, Sequence


class Player(bs.Player['Team']):
    """Our player type for this game."""


class Team(bs.Team[Player]):
    """Our team type for this game."""


class CoopGame(bs.CoopGameActivity[Player, Team]):
    """Co-op game where players try to survive attacking waves of enemies."""

    name = 'Coop'
    description = 'Defeat all enemies.'

    tips: list[str | bs.GameTip] = [
        'Hold any button to run.'
        '  (Trigger buttons work well if you have them)',
        'Try tricking enemies into killing eachother or running off cliffs.',
        'Try \'Cooking off\' bombs for a second or two before throwing them.',
        'It\'s easier to win with a friend or two helping.',
        'If you stay in one place, you\'re toast. Run and dodge to survive..',
        'Practice using your momentum to throw bombs more accurately.',
        'Your punches do much more damage if you are running or spinning.',
    ]

    # Show messages when players die since it matters here.
    announce_player_deaths = True

    def __init__(self, settings: dict):
        settings['map'] = 'Test Map'
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._score_to_win = 300
        self._swipsound = bs.getsound('swip')
        
        self.default_music = bs.MusicType.HOCKEY
        self._flag_region_material = bs.Material()
        self._flag_region_material.add_actions(
            conditions=('they_have_material', SpazFactory.get().spaz_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                (
                    'call',
                    'at_connect',
                    bs.Call(self._handle_player_flag_region_collide, True),
                ),
                (
                    'call',
                    'at_disconnect',
                    bs.Call(self._handle_player_flag_region_collide, False),
                ),
            ),
        )
        self.bot_ticks = 0
        self.teams_touching: list[Team] = []
        self._flag_pos: Sequence[float] | None = [0, 0.7, 0]
        self._flag: Flag | None = None
        self._flag_light: bs.Node | None = None
        self._countdownsounds = {
            10: bs.getsound('announceTen'),
            9: bs.getsound('announceNine'),
            8: bs.getsound('announceEight'),
            7: bs.getsound('announceSeven'),
            6: bs.getsound('announceSix'),
            5: bs.getsound('announceFive'),
            4: bs.getsound('announceFour'),
            3: bs.getsound('announceThree'),
            2: bs.getsound('announceTwo'),
            1: bs.getsound('announceOne'),
        }
        self._bots: SpazBotSet = None
        

    @override
    def get_instance_description(self) -> str | Sequence:
        return 'Crush ${ARG1} of your enemies.', self._score_to_win

    @override
    def get_instance_description_short(self) -> str | Sequence:
        return 'kill ${ARG1} enemies', self._score_to_win

    @override
    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()
        
    def _handle_player_flag_region_collide(self, colliding: bool) -> None:
        try:
            spaz = bs.getcollision().opposingnode.getdelegate(Spaz, True)
            assert isinstance(spaz, Spaz)
        except bs.NotFoundError:
            return

        if not spaz.is_alive():
            return

        team = spaz.team

        # Track which teams are touching the flag
        if colliding:
            self.teams_touching.append(team)
            self._swipsound.play()
        else:
            self.teams_touching.remove(team)

        # if bots touch and no player touch, we are peaking
        is_bot = team != self.teams[0]
        players_contesting = self.teams[0] in self.teams_touching

        if colliding and is_bot and not players_contesting:
            if self._flag.node:
                self._flag.node.color = (1, 0, 0)
        else:
            if self._flag.node:
                self._flag.node.color = (0, 0, 1)

    def tick(self):
        if self._flag.node.color == (1, 0, 0):
            self.bot_ticks += 1
        self._update_scoreboard()

    def on_transition_in(self):
        super().on_transition_in()
        self._bots = SpazBotSet()



    @override
    def on_begin(self) -> None:
        super().on_begin()
        
        Flag.project_stand(self._flag_pos)
        self._flag = Flag(
            position=self._flag_pos, touchable=False, color=(1, 1, 1)
        )
        self._flag_light = bs.newnode(
            'light',
            attrs={
                'position': self._flag_pos,
                'intensity': 0.2,
                'height_attenuated': False,
                'radius': 0.4,
                'color': (0.2, 0.2, 0.2),
            },
        )
        # Flag region.
        flagmats = [self._flag_region_material, SharedObjects.get().region_material]
        bs.newnode(
            'region',
            attrs={
                'position': self._flag_pos,
                'scale': (1.8, 1.8, 1.8),
                'type': 'sphere',
                'materials': flagmats,
            },
        )
        self._bots.spawn_bot(BrawlerBot, self._flag_pos, 3)
        
        bs.timer(0.1, self.tick, repeat=True)

      
        self._update_scoreboard()

    @override
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.PlayerDiedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)
            self.respawn_player(player)

            killer = msg.getkillerplayer(Player)
            if killer is None:
                return None

            self._update_scoreboard()


        else:
            return super().handlemessage(msg)
        return None

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(
                team, 
                score=self._score_to_win, 
                max_score=max(1, self.bot_ticks), 
                show_value=True, 
                flash=True, 
                countdown=True
            )

    @override
    def end_game(self) -> None:
        results = bs.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
