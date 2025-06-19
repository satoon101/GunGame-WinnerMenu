# ../gungame/plugins/custom/gg_winner_menu/__init__.py

"""The winner of the match gets to choose the next game-mode."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Site-package
from configobj import ConfigObj

# GunGame
from gungame.core.messages.manager import message_manager
from gungame.core.paths import GUNGAME_CFG_PATH

# Plugin
from .info import info

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
database = ConfigObj(GUNGAME_CFG_PATH / info.name + ".ini")

_base_game_modes = {
    "DeathMatch": "deathmatch",
    "Elimination": "elimination",
    "Elimination Objectives": "elimination_objectives",
    "Free for All": "ffa",
    "Free for All DeathMatch": "ffa_deathmatch",
    "Free for All Elimination": "ffa_elimination",
    "Regular": "normal",
    "Objectives": "objectives",
    "TeamPlay": "teamplay",
    "TeamPlay DeathMatch": "teamplay_deathmatch",
    "TeamPlay Elimination": "teamplay_elimination",
    "TeamPlay Elimination Objectives": "teamplay_elimination_objectives",
    "TeamPlay Objectives": "teamplay_objectives",
    "TeamWork": "teamwork",
    "TeamWork Elimination": "teamwork_elimination",
    "Objectives Elimination": "teamwork_elimination_objectives",
    "TeamWork Objectives": "teamwork_objectives",
}


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def _create_database_file():
    database.initial_comment = (
        message_manager["WinnerMenu:Header"].get_string().splitlines()
    )
    database.update(_base_game_modes)
    database.write()


if not database:
    _create_database_file()
