# ../gungame/plugins/custom/gg_winner_menu/gg_winner_menu.py

"""Plugin that allows the winner of the match to choose the next game-mode."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from random import choice, sample

# Source.Python
from engines.server import queue_command_string
from events import Event
from filters.players import PlayerIter
from listeners import OnLevelEnd, OnLevelInit
from menus import SimpleMenu, SimpleOption
from players.entity import Player

# GunGame
from gungame.core.messages.manager import message_manager
from gungame.core.players.dictionary import player_dictionary
from gungame.core.plugins.manager import gg_plugin_manager

# Plugin
from . import database


# =============================================================================
# >> CLASSES
# =============================================================================
class _WinnerManager(dict):
    """Dictionary used to determine who chooses next gamemode."""

    game_mode = None
    _count = min(9, len(database))

    def send_menu_to_team_winner(self, winning_team):
        """Determine the team winner and send the winner menu."""
        userid = _winner_manager.get(winning_team)
        if userid is None:
            players = [
                player.userid for player in PlayerIter()
                if player.team_index == winning_team
            ]

            # This should never happen
            if not players:
                self.game_mode = choice(database.keys())
                return

            userid = choice(players)
        self.send_winner_menu(player_dictionary[userid])

    def send_winner_menu(self, player):
        """Send the winner menu to the winning player."""
        gamemode_choices = database.keys()
        if player.is_fake_client():
            self.set_choice(player, choice(gamemode_choices))
            return

        winner_menu.clear()
        for num, item in enumerate(
            sample(gamemode_choices, self._count),
            start=1,
        ):
            winner_menu.append(
                SimpleOption(
                    choice_index=num,
                    text=item,
                    value=item,
                )
            )
        winner_menu.send(player.index)

    def set_choice(self, player, value):
        """Store the next game mode and send a message about the choice."""
        self.game_mode = value
        message_manager.chat_message(
            message='WinnerMenu:Chosen',
            index=player.index,
            name=player.name,
            gamemode=self.game_mode,
        )

    def set_next_game_mode(self):
        """Set the next game mode."""
        current = database.get(self.game_mode)
        if current is not None:
            queue_command_string(f'exec {current}')
        self.game_mode = None
        self.clear()

_winner_manager = _WinnerManager()


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event('round_start')
def _clear_reasons(game_event):
    _winner_manager.clear()


@Event('player_death')
def _player_death(game_event):
    if not gg_plugin_manager.is_team_game:
        return

    attacker = game_event['attacker']
    userid = game_event['userid']
    if attacker in (0, userid):
        return

    killer_team = player_dictionary[attacker].team_index
    if killer_team == player_dictionary[userid].team_index:
        return

    _winner_manager[killer_team] = attacker


@Event('bomb_exploded', 'bomb_defused', 'hostage_rescued')
def _objective_event(game_event):
    player = player_dictionary[game_event['userid']]
    _winner_manager[player.team_index] = player.userid


# =============================================================================
# >> GUNGAME EVENTS
# =============================================================================
@Event('gg_win')
def _individual_win(game_event):
    _winner_manager.send_winner_menu(player_dictionary[game_event['winner']])


@Event('gg_team_win')
def _team_win(game_event):
    _winner_manager.send_menu_to_team_winner(game_event['winner'])


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnLevelInit
def _level_init(map_name):
    _winner_manager.set_next_game_mode()


@OnLevelEnd
def _level_end():
    winner_menu.close()


# =============================================================================
# >> MENU CALLBACKS
# =============================================================================
def _chosen_game_mode(parent_menu, index, menu_choice):
    _winner_manager.set_choice(Player(index), menu_choice.value)

winner_menu = SimpleMenu(select_callback=_chosen_game_mode)
winner_menu.title = message_manager['WinnerMenu:Menu']
