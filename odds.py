import os

import requests
import streamlit as st
from dotenv import load_dotenv


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


API_KEY = get_secret("ODDS_API_KEY")

if not API_KEY:
    raise ValueError(
        "ODDS_API_KEY is missing. "
        "Add it to your local .env file or Streamlit Cloud secrets."
    )


URL = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"


# The Odds API names -> nflverse abbreviations
TEAM_NAME_TO_ABBR = {
    "Arizona Cardinals": "ARI",
    "Atlanta Falcons": "ATL",
    "Baltimore Ravens": "BAL",
    "Buffalo Bills": "BUF",
    "Carolina Panthers": "CAR",
    "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN",
    "Cleveland Browns": "CLE",
    "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN",
    "Detroit Lions": "DET",
    "Green Bay Packers": "GB",
    "Houston Texans": "HOU",
    "Indianapolis Colts": "IND",
    "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC",
    "Las Vegas Raiders": "LV",
    "Los Angeles Chargers": "LAC",
    "Los Angeles Rams": "LA",
    "Miami Dolphins": "MIA",
    "Minnesota Vikings": "MIN",
    "New England Patriots": "NE",
    "New Orleans Saints": "NO",
    "New York Giants": "NYG",
    "New York Jets": "NYJ",
    "Philadelphia Eagles": "PHI",
    "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF",
    "Seattle Seahawks": "SEA",
    "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN",
    "Washington Commanders": "WAS",
}


def get_nfl_odds():
    """
    Get current NFL moneyline odds from The Odds API.
    """

    params = {
        "apiKey": API_KEY,
        "regions": "uk",
        "markets": "h2h",
        "oddsFormat": "decimal",
    }

    response = requests.get(
        URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def calculate_probabilities(game):
    """
    Calculate consensus win probabilities for an NFL game.

    Probabilities are calculated by:
    1. Converting decimal odds into implied probabilities.
    2. Removing the bookmaker margin.
    3. Averaging the normalised probabilities across bookmakers.
    """

    probabilities = {}

    for bookmaker in game.get("bookmakers", []):

        for market in bookmaker.get("markets", []):

            if market["key"] != "h2h":
                continue

            outcomes = market["outcomes"]

            if len(outcomes) != 2:
                continue

            raw_probabilities = {}

            for outcome in outcomes:

                team = outcome["name"]
                odds = outcome["price"]

                raw_probabilities[team] = 1 / odds

            total_probability = sum(
                raw_probabilities.values()
            )

            for team, probability in raw_probabilities.items():

                normalised_probability = (
                    probability / total_probability
                )

                if team not in probabilities:
                    probabilities[team] = []

                probabilities[team].append(
                    normalised_probability
                )

    consensus = {}

    for team, values in probabilities.items():

        consensus[team] = (
            sum(values) / len(values)
        )

    return consensus


def get_odds_games():
    """
    Get NFL games from The Odds API and convert them
    into a simple dictionary keyed by away/home team.
    """

    games = get_nfl_odds()

    odds_games = {}

    for game in games:

        away_name = game["away_team"]
        home_name = game["home_team"]

        away_abbr = TEAM_NAME_TO_ABBR.get(away_name)
        home_abbr = TEAM_NAME_TO_ABBR.get(home_name)

        if not away_abbr or not home_abbr:
            continue

        probabilities = calculate_probabilities(game)

        if not probabilities:
            continue

        away_probability = probabilities.get(away_name)
        home_probability = probabilities.get(home_name)

        if away_probability is None or home_probability is None:
            continue

        key = (away_abbr, home_abbr)

        odds_games[key] = {
            "away_team_name": away_name,
            "home_team_name": home_name,
            "away_probability": away_probability,
            "home_probability": home_probability,
            "commence_time": game.get("commence_time"),
        }

    return odds_games