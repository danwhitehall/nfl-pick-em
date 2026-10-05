import streamlit as st

from database import (
    initialise_database,
    get_games,
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
    page_title="Weekly Results",
    page_icon="🏆",
    layout="centered",
)


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

initialise_database()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🏆 Weekly Results")

st.caption(
    f"{SEASON} NFL Season • "
    f"{PLAYER_1} & {PLAYER_2}"
)


# ---------------------------------------------------------
# WEEK SELECTOR
# ---------------------------------------------------------

selected_week = st.selectbox(
    "Select week:",
    options=list(range(1, CURRENT_WEEK + 1)),
    index=CURRENT_WEEK - 1,
    format_func=lambda week: f"Week {week}",
)


# ---------------------------------------------------------
# LOAD GAMES
# ---------------------------------------------------------

games = get_games(
    SEASON,
    selected_week,
)

picks = get_picks(
    tuple(game["game_id"] for game in games)
)


if not games:

    st.info(
        f"No games have been added to the database "
        f"for Week {selected_week} yet."
    )

    st.stop()


# ---------------------------------------------------------
# CALCULATE RESULTS
# ---------------------------------------------------------

dan_wins = 0
fran_wins = 0

completed_games = 0
played_games = 0
pending_games = 0
tied_games = 0

results = []


for game in games:

    pick = picks.get(game["game_id"])

    # -----------------------------------------------------
    # GAME NOT PART OF PICK 'EM
    # -----------------------------------------------------

    if pick is None:

        results.append(
            {
                "game": (
                    f"{game['away_team']} @ "
                    f"{game['home_team']}"
                ),
                "away_team": game["away_team"],
                "home_team": game["home_team"],
                "away_score": game.get("away_score"),
                "home_score": game.get("home_score"),
                "winner": game["winner"],
                "dan_pick": None,
                "fran_pick": None,
                "result": "Not played",
                "winner_player": None,
            }
        )

        continue

    played_games += 1

    # -----------------------------------------------------
    # WORK OUT EACH PLAYER'S PICK
    # -----------------------------------------------------

    if pick["first_picker"] == PLAYER_1:

        dan_pick = pick["first_team"]
        fran_pick = pick["second_team"]

    else:

        fran_pick = pick["first_team"]
        dan_pick = pick["second_team"]

    winner = game["winner"]

    away_score = game.get("away_score")
    home_score = game.get("home_score")

    # -----------------------------------------------------
    # DETERMINE WHETHER GAME HAS FINISHED
    # -----------------------------------------------------
    #
    # A game is finished if both scores exist.
    #
    # This is important because winner == None can mean
    # either:
    #
    #   1. The game hasn't finished
    #   2. The game finished tied
    #
    # We use the scores to tell those apart.
    # -----------------------------------------------------

    game_finished = (
        away_score is not None
        and home_score is not None
    )

    # -----------------------------------------------------
    # GAME NOT FINISHED
    # -----------------------------------------------------

    if not game_finished:

        pending_games += 1

        results.append(
            {
                "game": (
                    f"{game['away_team']} @ "
                    f"{game['home_team']}"
                ),
                "away_team": game["away_team"],
                "home_team": game["home_team"],
                "away_score": away_score,
                "home_score": home_score,
                "winner": None,
                "dan_pick": dan_pick,
                "fran_pick": fran_pick,
                "result": "Pending",
                "winner_player": None,
            }
        )

        continue

    # -----------------------------------------------------
    # COMPLETED GAME
    # -----------------------------------------------------

    completed_games += 1

    # -----------------------------------------------------
    # TIED GAME
    # -----------------------------------------------------

    if winner is None:

        tied_games += 1

        results.append(
            {
                "game": (
                    f"{game['away_team']} @ "
                    f"{game['home_team']}"
                ),
                "away_team": game["away_team"],
                "home_team": game["home_team"],
                "away_score": away_score,
                "home_score": home_score,
                "winner": None,
                "dan_pick": dan_pick,
                "fran_pick": fran_pick,
                "result": "Tie",
                "winner_player": None,
            }
        )

        continue

    # -----------------------------------------------------
    # DETERMINE WINNING PLAYER
    # -----------------------------------------------------

    if dan_pick == winner:

        dan_wins += 1
        winner_player = PLAYER_1

    elif fran_pick == winner:

        fran_wins += 1
        winner_player = PLAYER_2

    else:

        winner_player = None

    results.append(
        {
            "game": (
                f"{game['away_team']} @ "
                f"{game['home_team']}"
            ),
            "away_team": game["away_team"],
            "home_team": game["home_team"],
            "away_score": away_score,
            "home_score": home_score,
            "winner": winner,
            "dan_pick": dan_pick,
            "fran_pick": fran_pick,
            "result": "Complete",
            "winner_player": winner_player,
        }
    )


# ---------------------------------------------------------
# MONEY
# ---------------------------------------------------------

dan_money = dan_wins * STAKE
fran_money = fran_wins * STAKE


if dan_money > fran_money:

    weekly_balance = (
        dan_money - fran_money
    )

    balance_text = (
        f"{PLAYER_1} is ahead by "
        f"£{weekly_balance:.2f}"
    )

elif fran_money > dan_money:

    weekly_balance = (
        fran_money - dan_money
    )

    balance_text = (
        f"{PLAYER_2} is ahead by "
        f"£{weekly_balance:.2f}"
    )

else:

    weekly_balance = 0

    balance_text = "It's currently tied"


# ---------------------------------------------------------
# WEEKLY SCORE
# ---------------------------------------------------------

st.subheader(
    f"Week {selected_week}"
)


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


st.info(
    f"💷 **{balance_text}**"
)


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

summary_col1, summary_col2, summary_col3 = (
    st.columns(3)
)


with summary_col1:

    st.metric(
        "Games played",
        played_games,
    )


with summary_col2:

    st.metric(
        "Completed",
        completed_games,
    )


with summary_col3:

    st.metric(
        "Pending",
        pending_games,
    )


if tied_games > 0:

    st.caption(
        f"🤝 {tied_games} game"
        f"{'s' if tied_games != 1 else ''} "
        f"ended in a tie."
    )


st.divider()


# ---------------------------------------------------------
# GAME RESULTS
# ---------------------------------------------------------

st.subheader(
    "Game Results"
)


for result in results:

    game_name = result["game"]

    away_team = result["away_team"]
    home_team = result["home_team"]

    away_score = result["away_score"]
    home_score = result["home_score"]

    # -----------------------------------------------------
    # SCORE DISPLAY
    # -----------------------------------------------------

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
            f"{away_team} — {home_team}"
        )

    # -----------------------------------------------------
    # NOT PLAYED
    # -----------------------------------------------------

    if result["result"] == "Not played":

        with st.expander(
            f"⬜ {game_name}"
        ):

            st.write(
                f"🏈 {score_text}"
            )

            st.caption(
                "This NFL game was not part of "
                f"{PLAYER_1} & {PLAYER_2}'s Pick 'Em."
            )

            if result["winner"]:

                st.write(
                    f"🏆 Winner: **{result['winner']}**"
                )

        continue

    # -----------------------------------------------------
    # PENDING
    # -----------------------------------------------------

    if result["result"] == "Pending":

        with st.expander(
            f"⏳ {game_name}"
        ):

            st.write(
                f"🏈 {score_text}"
            )

            st.write(
                f"**{PLAYER_1}:** "
                f"{result['dan_pick']}"
            )

            st.write(
                f"**{PLAYER_2}:** "
                f"{result['fran_pick']}"
            )

            st.warning(
                "The game has not been completed yet."
            )

        continue

    # -----------------------------------------------------
    # TIED GAME
    # -----------------------------------------------------

    if result["result"] == "Tie":

        with st.expander(
            f"🤝 {game_name}"
        ):

            st.write(
                f"🏈 {score_text}"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.info(
                    f"**{PLAYER_1}**\n\n"
                    f"🏈 {result['dan_pick']}"
                )

            with col2:

                st.info(
                    f"**{PLAYER_2}**\n\n"
                    f"🏈 {result['fran_pick']}"
                )

            st.divider()

            st.write(
                "🤝 **Game ended in a tie**"
            )

            st.caption(
                "No winner — no pick is awarded for this game."
            )

        continue

    # -----------------------------------------------------
    # COMPLETED GAME
    # -----------------------------------------------------

    winner_player = result[
        "winner_player"
    ]

    if winner_player == PLAYER_1:

        heading = f"🟢 {game_name}"

    else:

        heading = f"🔵 {game_name}"

    with st.expander(
        heading
    ):

        # -------------------------------------------------
        # FINAL SCORE
        # -------------------------------------------------

        st.markdown(
            f"### 🏈 {away_team} "
            f"**{away_score}** — "
            f"**{home_score}** {home_team}"
        )

        st.divider()

        # -------------------------------------------------
        # PLAYER PICKS
        # -------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            if (
                result["dan_pick"]
                == result["winner"]
            ):

                st.success(
                    f"**{PLAYER_1}**\n\n"
                    f"🏆 {result['dan_pick']}"
                )

            else:

                st.error(
                    f"**{PLAYER_1}**\n\n"
                    f"❌ {result['dan_pick']}"
                )

        with col2:

            if (
                result["fran_pick"]
                == result["winner"]
            ):

                st.success(
                    f"**{PLAYER_2}**\n\n"
                    f"🏆 {result['fran_pick']}"
                )

            else:

                st.error(
                    f"**{PLAYER_2}**\n\n"
                    f"❌ {result['fran_pick']}"
                )

        st.divider()

        # -------------------------------------------------
        # WINNER
        # -------------------------------------------------

        st.write(
            f"🏆 Winner: **{result['winner']}**"
        )

        if winner_player:

            st.success(
                f"💷 **{winner_player} wins "
                f"£{STAKE:.2f}**"
            )


# ---------------------------------------------------------
# WEEKLY SETTLEMENT
# ---------------------------------------------------------

if completed_games > 0:

    st.divider()

    st.subheader(
        "💷 Weekly Settlement"
    )

    if dan_wins > fran_wins:

        amount = (
            dan_wins - fran_wins
        ) * STAKE

        st.success(
            f"**{PLAYER_2} owes "
            f"{PLAYER_1} £{amount:.2f}**"
        )

    elif fran_wins > dan_wins:

        amount = (
            fran_wins - dan_wins
        ) * STAKE

        st.success(
            f"**{PLAYER_1} owes "
            f"{PLAYER_2} £{amount:.2f}**"
        )

    else:

        st.info(
            "Nobody owes anything — "
            "the week is tied."
        )

