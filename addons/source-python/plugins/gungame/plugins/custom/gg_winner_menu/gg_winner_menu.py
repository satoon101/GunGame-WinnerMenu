# ../gungame/plugins/custom/gg_winner_menu/gg_winner_menu.py

"""."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from random import choice, sample

# Source.Python
from engines.server import queue_command_string
from events import Event
from listeners import OnLevelEnd, OnLevelInit
from menus import SimpleMenu, SimpleOption
from players.entity import Player

# GunGame
from gungame.core.messages import message_manager
from gungame.core.players.dictionary import player_dictionary
from gungame.core.plugins.manager import gg_plugin_manager

# Plugin
from . import database


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
_game_mode = None
_count = min(9, len(database))
_reason_dictionary = {}


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event('round_end')
def _round_end(game_event):
    if not gg_plugin_manager.is_team_game:
        return


@Event('round_start')
def _clear_reasons(game_event):
    _reason_dictionary.clear()


@Event('player_death')
def _player_death(game_event):
    if not gg_plugin_manager.is_team_game:
        return

    attacker = game_event['attacker']
    userid = game_event['userid']
    if attacker in (0, userid):
        return

    killer_team = player_dictionary[attacker].team
    if killer_team == player_dictionary[userid].team:
        return

    _reason_dictionary[killer_team] = attacker


# =============================================================================
# >> GUNGAME EVENTS
# =============================================================================
@Event('gg_win')
def _individual_win(game_event):
    _send_winner_menu(player_dictionary[game_event['winner']])


@Event('gg_team_win')
def _team_win(game_event):
    winning_team = game_event['winner']


@Event('gg_level_up')
def _level_up(game_event):
    if not gg_plugin_manager.is_team_game:
        return


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnLevelInit
def _level_init(map_name):
    global _game_mode
    current = database.get(_game_mode)
    if current is not None:
        queue_command_string('exec {cfg}'.format(cfg=current))
    _game_mode = None
    _reason_dictionary.clear()


@OnLevelEnd
def _level_end():
    winner_menu.close()


# =============================================================================
# >> MENU CALLBACKS
# =============================================================================
def _chosen_game_mode(parent_menu, index, menu_choice):
    _set_choice(Player(index), menu_choice.value)

winner_menu = SimpleMenu(select_callback=_chosen_game_mode)
winner_menu.title = message_manager['WinnerMenu:Menu']


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def _send_winner_menu(player):
    if player.is_fake_client():
        _set_choice(player, choice(database))
        return

    winner_menu.clear()
    for num, item in enumerate(sample(list(database), _count), start=1):
        winner_menu.append(
            SimpleOption(
                choice_index=num,
                text=item,
                value=item,
            )
        )
    winner_menu.send(player.index)


def _set_choice(player, value):
    global _game_mode
    _game_mode = value
    message_manager.chat_message(
        message='WinnerMenu:Chosen',
        index=player.index,
        name=player.name,
        gamemode=_game_mode,
    )
