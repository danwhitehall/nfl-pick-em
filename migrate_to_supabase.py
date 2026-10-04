import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client
import os


# ---------------------------------------------------------
# LOAD ENVIRONMENT
# ---------------------------------------------------------

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing from .env")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY is missing from .env")


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


# ---------------------------------------------------------
# LOCAL DATABASE
# ---------------------------------------------------------

DB_PATH = Path(__file__).parent / "nfl_pick_em.db"

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"Could not find local database: {DB_PATH}"
    )


connection = sqlite3.connect(DB_PATH)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()


# ---------------------------------------------------------
# MIGRATE GAMES
# ---------------------------------------------------------

print()
print("========================================")
print("Migrating games...")
print("========================================")

cursor.execute(
    """
    SELECT
        game_id,
        season,
        week,
        game_date,
        away_team,
        home_team,
        away_probability,
        home_probability,
        winner,
        updated_at
    FROM games
    """
)

game_rows = cursor.fetchall()

games = []

for row in game_rows:

    games.append(
        {
            "game_id": row["game_id"],
            "season": row["season"],
            "week": row["week"],
            "game_date": row["game_date"],
            "away_team": row["away_team"],
            "home_team": row["home_team"],
            "away_probability": row["away_probability"],
            "home_probability": row["home_probability"],
            "winner": row["winner"],
            "updated_at": row["updated_at"],
        }
    )


print(f"Found {len(games)} games locally.")


if games:

    response = (
        supabase
        .table("games")
        .upsert(games)
        .execute()
    )

    print(
        f"Uploaded {len(response.data)} games."
    )


# ---------------------------------------------------------
# MIGRATE PICKS
# ---------------------------------------------------------

print()
print("========================================")
print("Migrating picks...")
print("========================================")

cursor.execute(
    """
    SELECT
        game_id,
        first_picker,
        first_team,
        second_picker,
        second_team,
        created_at,
        updated_at
    FROM picks
    """
)

pick_rows = cursor.fetchall()

picks = []

for row in pick_rows:

    picks.append(
        {
            "game_id": row["game_id"],
            "first_picker": row["first_picker"],
            "first_team": row["first_team"],
            "second_picker": row["second_picker"],
            "second_team": row["second_team"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
    )


print(f"Found {len(picks)} picks locally.")


if picks:

    response = (
        supabase
        .table("picks")
        .upsert(picks)
        .execute()
    )

    print(
        f"Uploaded {len(response.data)} picks."
    )


# ---------------------------------------------------------
# CLOSE SQLITE
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# VERIFY
# ---------------------------------------------------------

print()
print("========================================")
print("Verifying Supabase...")
print("========================================")


games_response = (
    supabase
    .table("games")
    .select("game_id")
    .execute()
)

picks_response = (
    supabase
    .table("picks")
    .select("game_id")
    .execute()
)


print(
    f"Supabase games: {len(games_response.data)}"
)

print(
    f"Supabase picks: {len(picks_response.data)}"
)


print()
print("========================================")
print("MIGRATION COMPLETE")
print("========================================")