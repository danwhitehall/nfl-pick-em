import os

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client


# ---------------------------------------------------------
# SUPABASE CONNECTION
# ---------------------------------------------------------

load_dotenv()


def get_secret(name):
    """
    Get a secret from Streamlit secrets when deployed,
    falling back to the local .env file when running locally.
    """

    value = os.getenv(name)

    if value:
        return value

    try:
        return st.secrets[name]
    except (KeyError, FileNotFoundError):
        return None


SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")


if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL is missing. "
        "Add it to your local .env file or Streamlit Cloud secrets."
    )


if not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_KEY is missing. "
        "Add it to your local .env file or Streamlit Cloud secrets."
    )


@st.cache_resource
def get_supabase_client(url, key):
    """Create the shared Supabase client once per app process."""

    return create_client(url, key)


supabase = get_supabase_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


# ---------------------------------------------------------
# DATABASE INITIALISATION
# ---------------------------------------------------------


def initialise_database():
    """
    Supabase tables are managed in the Supabase dashboard.
    """

    return


# ---------------------------------------------------------
# GAMES
# ---------------------------------------------------------


def save_games(games):
    """
    Save or update NFL games in Supabase.
    """

    if not games:
        return

    rows = []

    for game in games:

        rows.append(
            {
                "game_id": game["game_id"],
                "season": game["season"],
                "week": game["week"],
                "game_date": str(game["date"]),
                "away_team": game["away_team"],
                "home_team": game["home_team"],
                "away_score": game.get("away_score"),
                "home_score": game.get("home_score"),
                "away_probability": game.get(
                    "away_probability"
                ),
                "home_probability": game.get(
                    "home_probability"
                ),
                "winner": game.get("winner"),
            }
        )

    (
        supabase
        .table("games")
        .upsert(rows)
        .execute()
    )

    # Do not leave result pages showing pre-update game data.
    get_games.clear()
    get_season_games.clear()


@st.cache_data(ttl=60)
def get_games(season, week):
    """
    Get all games for a season and week.
    """

    response = (
        supabase
        .table("games")
        .select(
            """
            game_id,
            season,
            week,
            game_date,
            away_team,
            home_team,
            away_score,
            home_score,
            away_probability,
            home_probability,
            winner
            """
        )
        .eq("season", season)
        .eq("week", week)
        .order("game_date")
        .order("game_id")
        .execute()
    )

    games = []

    for row in response.data:

        games.append(
            {
                "game_id": row["game_id"],
                "season": row["season"],
                "week": row["week"],
                "date": row["game_date"],
                "away_team": row["away_team"],
                "home_team": row["home_team"],
                "away_score": row["away_score"],
                "home_score": row["home_score"],
                "away_probability": row[
                    "away_probability"
                ],
                "home_probability": row[
                    "home_probability"
                ],
                "winner": row["winner"],
            }
        )

    return games


@st.cache_data(ttl=60)
def get_season_games(season, last_week):
    """
    Get all stored games needed for the season results page.
    """

    response = (
        supabase
        .table("games")
        .select(
            """
            game_id,
            season,
            week,
            game_date,
            away_team,
            home_team,
            away_score,
            home_score,
            away_probability,
            home_probability,
            winner
            """
        )
        .eq("season", season)
        .lte("week", last_week)
        .order("week")
        .order("game_date")
        .order("game_id")
        .execute()
    )

    games = []

    for row in response.data:

        games.append(
            {
                "game_id": row["game_id"],
                "season": row["season"],
                "week": row["week"],
                "date": row["game_date"],
                "away_team": row["away_team"],
                "home_team": row["home_team"],
                "away_score": row["away_score"],
                "home_score": row["home_score"],
                "away_probability": row[
                    "away_probability"
                ],
                "home_probability": row[
                    "home_probability"
                ],
                "winner": row["winner"],
            }
        )

    return games


# ---------------------------------------------------------
# PICKS
# ---------------------------------------------------------


def save_pick(
    game_id,
    first_picker,
    first_team,
    second_picker,
    second_team,
):
    """
    Save or update a pick in Supabase.
    """

    row = {
        "game_id": game_id,
        "first_picker": first_picker,
        "first_team": first_team,
        "second_picker": second_picker,
        "second_team": second_team,
    }

    (
        supabase
        .table("picks")
        .upsert(row)
        .execute()
    )

    # A saved or edited pick must appear immediately after rerun.
    get_picks.clear()


def get_pick(game_id):
    """
    Get the pick for one game.
    """

    return get_picks((game_id,)).get(game_id)


@st.cache_data(ttl=60)
def get_picks(game_ids):
    """
    Get picks for many games in one Supabase request.

    ``game_ids`` is a tuple so Streamlit can cache it safely.
    """

    if not game_ids:
        return {}

    response = (
        supabase
        .table("picks")
        .select(
            """
            game_id,
            first_picker,
            first_team,
            second_picker,
            second_team
            """
        )
        .in_("game_id", list(game_ids))
        .execute()
    )

    picks = {}

    for row in response.data:

        picks[row["game_id"]] = {
            "first_picker": row["first_picker"],
            "first_team": row["first_team"],
            "second_picker": row["second_picker"],
            "second_team": row["second_team"],
        }

    return picks
