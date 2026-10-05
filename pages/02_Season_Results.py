import streamlit as st

from database import (
    initialise_database,
    get_season_games,
    get_picks,
)

from settings import (
    SEASON,
    CURRENT_WEEK,
    PLAYER_1,
    PLAYER_2,
    STAKE,
)


# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="Season Results",
    page_icon="📊",
    layout="centered",
)


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

initialise_database()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("📊 Season Results")

st.caption(
    f"{SEASON} NFL Season • "
    f"{PLAYER_1} vs {PLAYER_2}"
)


# ---------------------------------------------------------
# SEASON TOTALS
# ---------------------------------------------------------

total_dan_wins = 0
total_fran_wins = 0

total_games_played = 0
total_games_completed = 0
total_pending = 0
total_tied = 0

weekly_results = []

season_games = get_season_games(
    SEASON,
    CURRENT_WEEK,
)

games_by_week = {}

for game in season_games:

    games_by_week.setdefault(
        game["week"],
        [],
    ).append(game)


season_picks = get_picks(
    tuple(game["game_id"] for game in season_games)
)


# ---------------------------------------------------------
# LOOP THROUGH WEEKS
# ---------------------------------------------------------

for week in range(
    1,
    CURRENT_WEEK + 1,
):

    games = games_by_week.get(week, [])

    dan_wins = 0
    fran_wins = 0

    played_games = 0
    completed_games = 0
    pending_games = 0
    tied_games = 0

    week_games = []

    for game in games:

        pick = season_picks.get(game["game_id"])

        # -------------------------------------------------
        # NO PICK 'EM ENTRY
        # -------------------------------------------------

        if pick is None:
            continue

        played_games += 1

        # -------------------------------------------------
        # WORK OUT EACH PLAYER'S PICK
        # -------------------------------------------------

        if pick["first_picker"] == PLAYER_1:

            dan_pick = pick["first_team"]
            fran_pick = pick["second_team"]

        else:

            fran_pick = pick["first_team"]
            dan_pick = pick["second_team"]

        winner = game["winner"]

        away_score = game.get("away_score")
        home_score = game.get("home_score")

        # -------------------------------------------------
        # DETERMINE IF GAME HAS FINISHED
        # -------------------------------------------------

        game_finished = (
            away_score is not None
            and home_score is not None
        )

        # -------------------------------------------------
        # PENDING GAME
        # -------------------------------------------------

        if not game_finished:

            pending_games += 1

            week_games.append(
                {
                    "away_team": game["away_team"],
                    "home_team": game["home_team"],
                    "away_score": away_score,
                    "home_score": home_score,
                    "dan_pick": dan_pick,
                    "fran_pick": fran_pick,
                    "winner": None,
                    "winner_player": None,
                    "status": "Pending",
                }
            )

            continue

        # -------------------------------------------------
        # COMPLETED GAME
        # -------------------------------------------------

        completed_games += 1

        # -------------------------------------------------
        # TIED GAME
        # -------------------------------------------------

        if winner is None:

            tied_games += 1

            week_games.append(
                {
                    "away_team": game["away_team"],
                    "home_team": game["home_team"],
                    "away_score": away_score,
                    "home_score": home_score,
                    "dan_pick": dan_pick,
                    "fran_pick": fran_pick,
                    "winner": None,
                    "winner_player": None,
                    "status": "Tie",
                }
            )

            continue

        # -------------------------------------------------
        # WINNING PLAYER
        # -------------------------------------------------

        if dan_pick == winner:

            dan_wins += 1
            winner_player = PLAYER_1

        elif fran_pick == winner:

            fran_wins += 1
            winner_player = PLAYER_2

        else:

            winner_player = None

        week_games.append(
            {
                "away_team": game["away_team"],
                "home_team": game["home_team"],
                "away_score": away_score,
                "home_score": home_score,
                "dan_pick": dan_pick,
                "fran_pick": fran_pick,
                "winner": winner,
                "winner_player": winner_player,
                "status": "Complete",
            }
        )

    # -----------------------------------------------------
    # WEEK MONEY
    # -----------------------------------------------------

    dan_money = dan_wins * STAKE
    fran_money = fran_wins * STAKE

    # -----------------------------------------------------
    # ADD TO SEASON TOTALS
    # -----------------------------------------------------

    total_dan_wins += dan_wins
    total_fran_wins += fran_wins

    total_games_played += played_games
    total_games_completed += completed_games
    total_pending += pending_games
    total_tied += tied_games

    weekly_results.append(
        {
            "week": week,
            "played": played_games,
            "completed": completed_games,
            "pending": pending_games,
            "tied": tied_games,
            "dan_wins": dan_wins,
            "fran_wins": fran_wins,
            "dan_money": dan_money,
            "fran_money": fran_money,
            "games": week_games,
        }
    )


# ---------------------------------------------------------
# SEASON MONEY
# ---------------------------------------------------------

total_dan_money = (
    total_dan_wins * STAKE
)

total_fran_money = (
    total_fran_wins * STAKE
)


# ---------------------------------------------------------
# SEASON SCORE
# ---------------------------------------------------------

st.subheader(
    "🏆 Season Score"
)

col1, col2 = st.columns(2)

with col1:

    st.metric(
        PLAYER_1,
        f"{total_dan_wins} wins",
    )

with col2:

    st.metric(
        PLAYER_2,
        f"{total_fran_wins} wins",
    )


# ---------------------------------------------------------
# SEASON SETTLEMENT
# ---------------------------------------------------------

if total_dan_money > total_fran_money:

    amount = (
        total_dan_money
        - total_fran_money
    )

    st.success(
        f"💷 **{PLAYER_2} owes "
        f"{PLAYER_1} £{amount:.2f}**"
    )

elif total_fran_money > total_dan_money:

    amount = (
        total_fran_money
        - total_dan_money
    )

    st.success(
        f"💷 **{PLAYER_1} owes "
        f"{PLAYER_2} £{amount:.2f}**"
    )

else:

    st.info(
        "💷 **The season is currently tied.**"
    )


# ---------------------------------------------------------
# SEASON STATISTICS
# ---------------------------------------------------------

st.divider()

st.subheader(
    "Season Statistics"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Games played",
        total_games_played,
    )

with col2:

    st.metric(
        "Completed",
        total_games_completed,
    )

with col3:

    st.metric(
        "Pending",
        total_pending,
    )


if total_tied > 0:

    st.caption(
        f"🤝 {total_tied} game"
        f"{'s' if total_tied != 1 else ''} "
        f"ended in a tie."
    )


# ---------------------------------------------------------
# WIN RATE
# ---------------------------------------------------------

if total_games_completed > 0:

    dan_win_rate = (
        total_dan_wins
        / total_games_completed
        * 100
    )

    fran_win_rate = (
        total_fran_wins
        / total_games_completed
        * 100
    )

    st.divider()

    st.subheader(
        "Win Rate"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            PLAYER_1,
            f"{dan_win_rate:.1f}%",
        )

    with col2:

        st.metric(
            PLAYER_2,
            f"{fran_win_rate:.1f}%",
        )


# ---------------------------------------------------------
# WEEK-BY-WEEK
# ---------------------------------------------------------

st.divider()

st.subheader(
    "📅 Week-by-Week"
)


# Running season totals
running_dan_wins = 0
running_fran_wins = 0


for week_result in weekly_results:

    week = week_result["week"]

    played = week_result["played"]
    completed = week_result["completed"]
    pending = week_result["pending"]
    tied = week_result["tied"]

    dan_wins = week_result["dan_wins"]
    fran_wins = week_result["fran_wins"]

    dan_money = week_result["dan_money"]
    fran_money = week_result["fran_money"]

    week_games = week_result["games"]

    # -----------------------------------------------------
    # UPDATE RUNNING TOTAL
    # -----------------------------------------------------

    running_dan_wins += dan_wins
    running_fran_wins += fran_wins

    running_dan_money = (
        running_dan_wins * STAKE
    )

    running_fran_money = (
        running_fran_wins * STAKE
    )

    running_balance = (
        running_dan_money
        - running_fran_money
    )

    # -----------------------------------------------------
    # NO GAMES
    # -----------------------------------------------------

    if played == 0:

        with st.expander(
            f"Week {week}"
        ):

            st.caption(
                "No Pick 'Em games recorded."
            )

        continue

    # -----------------------------------------------------
    # WEEK WINNER
    # -----------------------------------------------------

    if dan_wins > fran_wins:

        title = (
            f"🟢 Week {week} — "
            f"{PLAYER_1} +£"
            f"{dan_money - fran_money:.2f}"
        )

    elif fran_wins > dan_wins:

        title = (
            f"🔵 Week {week} — "
            f"{PLAYER_2} +£"
            f"{fran_money - dan_money:.2f}"
        )

    else:

        title = (
            f"⚪ Week {week} — Tied"
        )

    # -----------------------------------------------------
    # WEEK DETAILS
    # -----------------------------------------------------

    with st.expander(title):

        # -------------------------------------------------
        # WEEK SCORE
        # -------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                PLAYER_1,
                f"{dan_wins} wins",
            )

        with col2:

            st.metric(
                PLAYER_2,
                f"{fran_wins} wins",
            )

        st.caption(
            f"{played} Pick 'Em games • "
            f"{completed} completed • "
            f"{pending} pending"
        )

        if tied > 0:

            st.caption(
                f"🤝 {tied} tied game"
                f"{'s' if tied != 1 else ''}"
            )

        # -------------------------------------------------
        # WEEK SETTLEMENT
        # -------------------------------------------------

        if dan_wins > fran_wins:

            amount = (
                dan_wins - fran_wins
            ) * STAKE

            st.success(
                f"💷 {PLAYER_2} owes "
                f"{PLAYER_1} £{amount:.2f} "
                f"for this week."
            )

        elif fran_wins > dan_wins:

            amount = (
                fran_wins - dan_wins
            ) * STAKE

            st.success(
                f"💷 {PLAYER_1} owes "
                f"{PLAYER_2} £{amount:.2f} "
                f"for this week."
            )

        else:

            st.info(
                "💷 Nobody owes anything "
                "for this week."
            )

        # -------------------------------------------------
        # RUNNING SEASON TOTAL
        # -------------------------------------------------

        st.caption(
            "Season total after this week"
        )

        running_col1, running_col2 = (
            st.columns(2)
        )

        with running_col1:

            st.metric(
                PLAYER_1,
                f"{running_dan_wins} wins",
            )

        with running_col2:

            st.metric(
                PLAYER_2,
                f"{running_fran_wins} wins",
            )

        if running_balance > 0:

            st.caption(
                f"Season balance: "
                f"{PLAYER_2} owes "
                f"{PLAYER_1} "
                f"£{abs(running_balance):.2f}"
            )

        elif running_balance < 0:

            st.caption(
                f"Season balance: "
                f"{PLAYER_1} owes "
                f"{PLAYER_2} "
                f"£{abs(running_balance):.2f}"
            )

        else:

            st.caption(
                "Season balance: currently tied"
            )

        st.divider()

        # -------------------------------------------------
        # GAME-BY-GAME RESULTS
        # -------------------------------------------------

        st.write("**Game Results**")

        for game_result in week_games:

            away_team = game_result[
                "away_team"
            ]

            home_team = game_result[
                "home_team"
            ]

            away_score = game_result[
                "away_score"
            ]

            home_score = game_result[
                "home_score"
            ]

            dan_pick = game_result[
                "dan_pick"
            ]

            fran_pick = game_result[
                "fran_pick"
            ]

            winner = game_result[
                "winner"
            ]

            winner_player = game_result[
                "winner_player"
            ]

            status = game_result[
                "status"
            ]

            # ---------------------------------------------
            # GAME NAME
            # ---------------------------------------------

            game_name = (
                f"{away_team} @ {home_team}"
            )

            # ---------------------------------------------
            # SCORE
            # ---------------------------------------------

            if (
                away_score is not None
                and home_score is not None
            ):

                score_text = (
                    f"{away_team} **{away_score}** — "
                    f"**{home_score}** {home_team}"
                )

            else:

                score_text = (
                    f"{away_team} — "
                    f"{home_team}"
                )

            # ---------------------------------------------
            # PENDING
            # ---------------------------------------------

            if status == "Pending":

                st.markdown(
                    f"⏳ **{game_name}**"
                )

                st.write(
                    f"🏈 {score_text}"
                )

                st.write(
                    f"{PLAYER_1}: "
                    f"**{dan_pick}**"
                )

                st.write(
                    f"{PLAYER_2}: "
                    f"**{fran_pick}**"
                )

                st.warning(
                    "Game not completed."
                )

                st.divider()

                continue

            # ---------------------------------------------
            # TIE
            # ---------------------------------------------

            if status == "Tie":

                st.markdown(
                    f"🤝 **{game_name}**"
                )

                st.write(
                    f"🏈 {score_text}"
                )

                st.write(
                    f"{PLAYER_1}: "
                    f"**{dan_pick}**"
                )

                st.write(
                    f"{PLAYER_2}: "
                    f"**{fran_pick}**"
                )

                st.info(
                    "Game ended in a tie — "
                    "no player receives the £0.50."
                )

                st.divider()

                continue

            # ---------------------------------------------
            # COMPLETED
            # ---------------------------------------------

            if winner_player == PLAYER_1:

                icon = "🟢"

            elif winner_player == PLAYER_2:

                icon = "🔵"

            else:

                icon = "⚪"

            st.markdown(
                f"{icon} **{game_name}**"
            )

            st.write(
                f"🏈 {score_text}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if dan_pick == winner:

                    st.success(
                        f"**{PLAYER_1}**\n\n"
                        f"🏆 {dan_pick}"
                    )

                else:

                    st.error(
                        f"**{PLAYER_1}**\n\n"
                        f"❌ {dan_pick}"
                    )

            with col2:

                if fran_pick == winner:

                    st.success(
                        f"**{PLAYER_2}**\n\n"
                        f"🏆 {fran_pick}"
                    )

                else:

                    st.error(
                        f"**{PLAYER_2}**\n\n"
                        f"❌ {fran_pick}"
                    )

            st.write(
                f"🏆 Winner: **{winner}**"
            )

            if winner_player:

                st.caption(
                    f"💷 {winner_player} "
                    f"wins £{STAKE:.2f}"
                )

            st.divider()


# ---------------------------------------------------------
# FINAL SETTLEMENT
# ---------------------------------------------------------

st.divider()

st.subheader(
    "💷 Current Season Settlement"
)


if total_dan_money > total_fran_money:

    amount = (
        total_dan_money
        - total_fran_money
    )

    st.success(
        f"### {PLAYER_2} owes "
        f"{PLAYER_1} £{amount:.2f}"
    )

elif total_fran_money > total_dan_money:

    amount = (
        total_fran_money
        - total_dan_money
    )

    st.success(
        f"### {PLAYER_1} owes "
        f"{PLAYER_2} £{amount:.2f}"
    )

else:

    st.info(
        "### Nobody owes anything — "
        "perfectly tied."
    )

