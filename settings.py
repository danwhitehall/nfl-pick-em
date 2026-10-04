import nflreadpy as nfl


# ---------------------------------------------------------
# NFL PICK 'EM SETTINGS
# ---------------------------------------------------------

# NFL season
SEASON = 2026

# Players
PLAYER_1 = "Dan"
PLAYER_2 = "Fran"

# Amount won per correct pick
STAKE = 0.50


# ---------------------------------------------------------
# AUTOMATIC CURRENT WEEK
# ---------------------------------------------------------

CURRENT_WEEK = nfl.get_current_week()