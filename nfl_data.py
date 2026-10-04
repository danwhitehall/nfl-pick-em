import nflreadpy as nfl

from odds import get_odds_games


def get_schedule(season):
    """
    Get the NFL schedule for a given season.
    """

    schedule = nfl.load_schedules(
        seasons=season
    )

    return schedule.to_pandas()


def get_week_schedule(season, week):
    """
    Get the schedule for one specific NFL week.
    """

    schedule = get_schedule(
        season
    )

    week_schedule = schedule[
        (schedule["season"] == season)
        & (schedule["week"] == week)
        & (schedule["game_type"] == "REG")
    ].copy()

    return week_schedule


def determine_winner(
    away_team,
    home_team,
    away_score,
    home_score,
):
    """
    Determine the winner from the final scores.

    Returns None if the game has not been completed.
    """

    if (
        away_score is None
        or home_score is None
    ):
        return None

    try:

        if (
            away_score != away_score
            or home_score != home_score
        ):
            return None

    except TypeError:

        return None

    if away_score > home_score:

        return away_team

    if home_score > away_score:

        return home_team

    # Regular-season NFL games can end tied.
    return None


def clean_score(score):
    """
    Convert a schedule score into either an integer
    or None.

    pandas may represent missing scores as NaN.
    """

    if score is None:
        return None

    try:

        if score != score:
            return None

    except TypeError:

        return None

    return int(score)


def get_week_games(season, week):
    """
    Get the schedule for a week and combine it
    with win probabilities from The Odds API.
    """

    schedule = get_week_schedule(
        season,
        week,
    )

    odds_games = get_odds_games()

    games = []

    for _, game in schedule.iterrows():

        away_team = game["away_team"]
        home_team = game["home_team"]

        away_score = clean_score(
            game["away_score"]
        )

        home_score = clean_score(
            game["home_score"]
        )

        key = (
            away_team,
            home_team,
        )

        odds = odds_games.get(key)

        winner = determine_winner(
            away_team,
            home_team,
            away_score,
            home_score,
        )

        game_data = {
            "game_id": game["game_id"],
            "season": season,
            "week": week,
            "date": game["gameday"],
            "away_team": away_team,
            "home_team": home_team,
            "away_score": away_score,
            "home_score": home_score,
            "away_probability": None,
            "home_probability": None,
            "winner": winner,
        }

        if odds is not None:

            game_data["away_probability"] = (
                odds["away_probability"]
            )

            game_data["home_probability"] = (
                odds["home_probability"]
            )

        games.append(game_data)

    return games


def get_past_week_games(season, week):
    """
    Get a historical week's games.

    Historical games do not request bookmaker odds,
    but their final scores are retained.
    """

    schedule = get_week_schedule(
        season,
        week,
    )

    games = []

    for _, game in schedule.iterrows():

        away_team = game["away_team"]
        home_team = game["home_team"]

        away_score = clean_score(
            game["away_score"]
        )

        home_score = clean_score(
            game["home_score"]
        )

        winner = determine_winner(
            away_team,
            home_team,
            away_score,
            home_score,
        )

        games.append(
            {
                "game_id": game["game_id"],
                "season": season,
                "week": week,
                "date": game["gameday"],
                "away_team": away_team,
                "home_team": home_team,
                "away_score": away_score,
                "home_score": home_score,
                "away_probability": None,
                "home_probability": None,
                "winner": winner,
            }
        )

    return games