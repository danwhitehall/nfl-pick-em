import streamlit as st

from database import (
    initialise_database,
    save_games,
    get_games,
    save_pick,
    get_pick,
)

from nfl_data import (
    get_week_games,
    get_past_week_games,
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
    page_title="Dan & Fran NFL Pick 'Em",
    page_icon="🏈",
    layout="centered",
)


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

initialise_database()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🏈 Dan & Fran NFL Pick 'Em'")

st.caption(
    f"Week {CURRENT_WEEK} • £{STAKE:.2f} per game"
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("Week")

    st.write(
        f"**NFL {SEASON} — Week {CURRENT_WEEK}**"
    )

    st.divider()

    st.header("Players")

    st.write(f"👤 {PLAYER_1}")
    st.write(f"👤 {PLAYER_2}")

    st.divider()

    st.write(
        "The first picker alternates between "
        "Dan and Fran for each game."
    )

    st.divider()

    update_data = st.button(
        "🔄 Update NFL Data",
        use_container_width=True,
    )

    st.divider()

    manage_past_games = st.checkbox(
        "⚙️ Manage Past Games"
    )


# ---------------------------------------------------------
# UPDATE CURRENT NFL DATA
# ---------------------------------------------------------

if update_data:

    with st.spinner(
        f"Updating NFL Week {CURRENT_WEEK}..."
    ):

        try:

            games = get_week_games(
                SEASON,
                CURRENT_WEEK,
            )

            save_games(games)

            completed_games = sum(
                1
                for game in games
                if game.get("winner") is not None
            )

            games_with_odds = sum(
                1
                for game in games
                if (
                    game.get("away_probability")
                    is not None
                    and
                    game.get("home_probability")
                    is not None
                )
            )

            st.success(
                f"✅ Updated {len(games)} games."
            )

            st.info(
                f"🏆 {completed_games} completed • "
                f"📊 {games_with_odds} with current odds"
            )

        except Exception as error:

            st.error(
                "❌ Unable to update NFL data."
            )

            st.exception(error)


# ---------------------------------------------------------
# MANAGE PAST GAMES
# ---------------------------------------------------------

if manage_past_games:

    st.header("⚙️ Manage Past Games")

    st.write(
        "Add only the games that Dan and Fran actually "
        "played. You do not need to add every NFL game."
    )

    st.divider()

    # -----------------------------------------------------
    # WEEK SELECTOR
    # -----------------------------------------------------

    historical_week = st.selectbox(
        "Choose NFL week:",
        options=list(range(1, CURRENT_WEEK)),
        format_func=lambda week: f"Week {week}",
        key="historical_week",
    )

    load_past_games = st.button(
        f"Load Week {historical_week}",
        use_container_width=True,
    )

    if load_past_games:

        with st.spinner(
            f"Loading Week {historical_week}..."
        ):

            past_games = get_past_week_games(
                SEASON,
                historical_week,
            )

            save_games(past_games)

        st.success(
            f"Loaded {len(past_games)} NFL games "
            f"from Week {historical_week}."
        )

    # -----------------------------------------------------
    # GET STORED GAMES
    # -----------------------------------------------------

    past_games = get_games(
        SEASON,
        historical_week,
    )

    if not past_games:

        st.info(
            f"Week {historical_week} hasn't been loaded yet. "
            f"Click **Load Week {historical_week}** above."
        )

    else:

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        played_count = 0

        for game in past_games:

            if get_pick(
                game["game_id"]
            ) is not None:

                played_count += 1

        st.subheader(
            f"Week {historical_week}"
        )

        st.write(
            f"**{played_count} of {len(past_games)} "
            f"NFL games added to your Pick 'Em.**"
        )

        if played_count == 0:

            st.info(
                "None of these games have been added yet. "
                "Open the games you actually played."
            )

        else:

            st.success(
                f"✅ {played_count} game"
                f"{'s' if played_count != 1 else ''} "
                "already added"
            )

        st.divider()

        # -------------------------------------------------
        # HISTORICAL GAMES
        # -------------------------------------------------

        for game_number, game in enumerate(
            past_games,
            start=1,
        ):

            game_id = game["game_id"]

            existing_pick = get_pick(
                game_id
            )

            winner = game.get("winner")

            away_score = game.get("away_score")
            home_score = game.get("home_score")

            # -------------------------------------------------
            # GAME ALREADY ADDED
            # -------------------------------------------------

            if existing_pick:

                first_picker = existing_pick[
                    "first_picker"
                ]

                first_team = existing_pick[
                    "first_team"
                ]

                second_picker = existing_pick[
                    "second_picker"
                ]

                second_team = existing_pick[
                    "second_team"
                ]

                winner_text = ""

                if winner:

                    if first_team == winner:

                        winner_picker = first_picker

                    elif second_team == winner:

                        winner_picker = second_picker

                    else:

                        winner_picker = None

                    if winner_picker:

                        winner_text = (
                            f"🏆 Winner: **{winner}**  \n"
                            f"💷 **{winner_picker} wins "
                            f"£{STAKE:.2f}**"
                        )

                    else:

                        winner_text = (
                            f"🏆 Winner: **{winner}**"
                        )

                else:

                    winner_text = (
                        "⏳ Result not available"
                    )

                with st.expander(
                    f"✅ {game['away_team']} @ "
                    f"{game['home_team']}"
                ):

                    st.success(
                        "**Already added to Pick 'Em**"
                    )

                    # -------------------------------------------------
                    # HISTORICAL SCORE
                    # -------------------------------------------------

                    if (
                        away_score is not None
                        and home_score is not None
                    ):

                        st.markdown(
                            f"### 🏈 "
                            f"{game['away_team']} "
                            f"**{away_score}** — "
                            f"{game['home_team']} "
                            f"**{home_score}**"
                        )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.markdown(
                            f"**{first_picker}** picked"
                        )

                        st.markdown(
                            f"### {first_team}"
                        )

                    with col2:

                        st.markdown(
                            f"**{second_picker}** gets"
                        )

                        st.markdown(
                            f"### {second_team}"
                        )

                    st.divider()

                    st.markdown(
                        winner_text
                    )

                    # -------------------------------------------------
                    # EDIT HISTORICAL PICK
                    # -------------------------------------------------

                    editing = st.session_state.get(
                        f"editing_past_{game_id}",
                        False,
                    )

                    if not editing:

                        edit_pick = st.button(
                            "✏️ Edit Pick",
                            key=f"edit_past_{game_id}",
                            use_container_width=True,
                        )

                        if edit_pick:

                            st.session_state[
                                f"editing_past_{game_id}"
                            ] = True

                            st.rerun()

                    if st.session_state.get(
                        f"editing_past_{game_id}",
                        False,
                    ):

                        st.divider()

                        st.markdown(
                            "### ✏️ Edit Historical Pick"
                        )

                        st.caption(
                            "Change who picked first and/or "
                            "which team they selected."
                        )

                        edited_first_picker = st.selectbox(
                            "Who picked first?",
                            options=[
                                PLAYER_1,
                                PLAYER_2,
                            ],
                            index=(
                                0
                                if first_picker == PLAYER_1
                                else 1
                            ),
                            key=f"edit_past_picker_{game_id}",
                        )

                        if (
                            edited_first_picker
                            == PLAYER_1
                        ):

                            edited_second_picker = PLAYER_2

                        else:

                            edited_second_picker = PLAYER_1

                        st.info(
                            f"**{edited_first_picker} picks first.** "
                            f"{edited_second_picker} automatically gets "
                            "the other team."
                        )

                        edited_first_team = st.radio(
                            f"What did {edited_first_picker} pick?",
                            options=[
                                game["away_team"],
                                game["home_team"],
                            ],
                            index=(
                                0
                                if first_team
                                == game["away_team"]
                                else 1
                            ),
                            horizontal=True,
                            key=f"edit_past_team_{game_id}",
                        )

                        if (
                            edited_first_team
                            == game["away_team"]
                        ):

                            edited_second_team = (
                                game["home_team"]
                            )

                        else:

                            edited_second_team = (
                                game["away_team"]
                            )

                        st.caption(
                            f"{edited_second_picker} will get "
                            f"**{edited_second_team}**."
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            save_edit = st.button(
                                "💾 Save Changes",
                                key=f"save_edit_past_{game_id}",
                                use_container_width=True,
                            )

                        with col2:

                            cancel_edit = st.button(
                                "Cancel",
                                key=f"cancel_edit_past_{game_id}",
                                use_container_width=True,
                            )

                        if save_edit:

                            save_pick(
                                game_id=game_id,
                                first_picker=edited_first_picker,
                                first_team=edited_first_team,
                                second_picker=edited_second_picker,
                                second_team=edited_second_team,
                            )

                            st.session_state[
                                f"editing_past_{game_id}"
                            ] = False

                            st.success(
                                "Historical pick updated!"
                            )

                            st.rerun()

                        if cancel_edit:

                            st.session_state[
                                f"editing_past_{game_id}"
                            ] = False

                            st.rerun()

            # -------------------------------------------------
            # GAME NOT YET ADDED
            # -------------------------------------------------

            else:

                with st.expander(
                    f"⬜ {game['away_team']} @ "
                    f"{game['home_team']}"
                ):

                    st.markdown(
                        "**Not added to your Pick 'Em yet.**"
                    )

                    # -------------------------------------------------
                    # HISTORICAL SCORE
                    # -------------------------------------------------

                    if (
                        away_score is not None
                        and home_score is not None
                    ):

                        st.markdown(
                            f"### 🏈 "
                            f"{game['away_team']} "
                            f"**{away_score}** — "
                            f"{game['home_team']} "
                            f"**{home_score}**"
                        )

                    if winner:

                        st.success(
                            f"🏆 Winner: **{winner}**"
                        )

                    else:

                        st.warning(
                            "This game does not have "
                            "a completed result yet."
                        )

                    st.divider()

                    st.markdown(
                        "**Was this game part of "
                        "your Pick 'Em?**"
                    )

                    first_picker = st.selectbox(
                        "Who picked first?",
                        options=[
                            PLAYER_1,
                            PLAYER_2,
                        ],
                        key=f"past_first_picker_{game_id}",
                    )

                    if first_picker == PLAYER_1:

                        second_picker = PLAYER_2

                    else:

                        second_picker = PLAYER_1

                    st.info(
                        f"**{first_picker} picks first.** "
                        f"{second_picker} automatically gets "
                        "the other team."
                    )

                    selected_team = st.radio(
                        f"What did {first_picker} pick?",
                        options=[
                            game["away_team"],
                            game["home_team"],
                        ],
                        horizontal=True,
                        key=f"past_pick_{game_id}",
                    )

                    if (
                        selected_team
                        == game["away_team"]
                    ):

                        other_team = game["home_team"]

                    else:

                        other_team = game["away_team"]

                    st.caption(
                        f"{second_picker} will get "
                        f"**{other_team}**."
                    )

                    add_game = st.button(
                        "➕ Add This Game",
                        key=f"add_past_{game_id}",
                        use_container_width=True,
                    )

                    if add_game:

                        save_pick(
                            game_id=game_id,
                            first_picker=first_picker,
                            first_team=selected_team,
                            second_picker=second_picker,
                            second_team=other_team,
                        )

                        st.success(
                            "Historical game added!"
                        )

                        st.rerun()

        st.divider()

        st.success(
            "When you've finished adding your past games, "
            "untick **Manage Past Games** in the sidebar."
        )

    st.stop()


# ---------------------------------------------------------
# LOAD CURRENT WEEK GAMES
# ---------------------------------------------------------

games = get_games(
    SEASON,
    CURRENT_WEEK,
)


if not games:

    st.warning(
        "No games are currently stored."
    )

    st.info(
        "Click **Update NFL Data** in the sidebar."
    )

    st.stop()


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

completed_picks = 0

for game in games:

    if get_pick(
        game["game_id"]
    ) is not None:

        completed_picks += 1


st.metric(
    "Picks made",
    f"{completed_picks} / {len(games)}",
)


st.divider()


# ---------------------------------------------------------
# CURRENT WEEK GAMES
# ---------------------------------------------------------

for game_number, game in enumerate(
    games,
    start=1,
):

    game_id = game["game_id"]

    away_team = game["away_team"]
    home_team = game["home_team"]

    away_probability = game[
        "away_probability"
    ]

    home_probability = game[
        "home_probability"
    ]

    away_score = game.get("away_score")
    home_score = game.get("home_score")
    winner = game.get("winner")

    # -----------------------------------------------------
    # ALTERNATING FIRST PICKER
    # -----------------------------------------------------

    if game_number % 2 == 1:

        first_picker = PLAYER_1
        second_picker = PLAYER_2

    else:

        first_picker = PLAYER_2
        second_picker = PLAYER_1

    # -----------------------------------------------------
    # EXISTING PICK
    # -----------------------------------------------------

    existing_pick = get_pick(
        game_id
    )

    # -----------------------------------------------------
    # GAME HEADER
    # -----------------------------------------------------

    if (
        away_score is not None
        and home_score is not None
    ):

        st.subheader(
            f"🏈 {away_team} {away_score} — "
            f"{home_team} {home_score}"
        )

        if winner:

            st.caption(
                f"🏆 Winner: **{winner}**"
            )

    else:

        st.subheader(
            f"🏈 {away_team} @ {home_team}"
        )

    st.caption(
        f"{game['date']} • Game {game_number}"
    )

    # -----------------------------------------------------
    # GAME STATUS
    # -----------------------------------------------------

    if (
        away_score is not None
        and home_score is not None
    ):

        if winner:

            st.success(
                f"🏆 Final — {winner} won"
            )

        else:

            st.warning(
                "🏈 Final — game ended tied"
            )

    else:

        st.caption(
            "⏳ Game not completed"
        )

    # -----------------------------------------------------
    # PROBABILITIES
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"**{away_team}**"
        )

        if away_probability is not None:

            st.metric(
                "Win probability",
                f"{away_probability * 100:.1f}%",
            )

        else:

            st.metric(
                "Win probability",
                "Unavailable",
            )

    with col2:

        st.markdown(
            f"**{home_team}**"
        )

        if home_probability is not None:

            st.metric(
                "Win probability",
                f"{home_probability * 100:.1f}%",
            )

        else:

            st.metric(
                "Win probability",
                "Unavailable",
            )

    # -----------------------------------------------------
    # EXISTING PICK / CHANGE PICK
    # -----------------------------------------------------

    if existing_pick:

        st.success(
            f"**{existing_pick['first_picker']}** "
            f"picked **{existing_pick['first_team']}**\n\n"
            f"**{existing_pick['second_picker']}** "
            f"gets **{existing_pick['second_team']}**"
        )

        # -------------------------------------------------
        # PICK RESULT
        # -------------------------------------------------

        if winner:

            if (
                existing_pick["first_team"]
                == winner
            ):

                winning_player = (
                    existing_pick["first_picker"]
                )

            elif (
                existing_pick["second_team"]
                == winner
            ):

                winning_player = (
                    existing_pick["second_picker"]
                )

            else:

                winning_player = None

            if winning_player:

                st.success(
                    f"💷 **{winning_player} wins "
                    f"£{STAKE:.2f}**"
                )

            else:

                st.warning(
                    "Neither pick matched the winner."
                )

        elif (
            away_score is not None
            or home_score is not None
        ):

            st.info(
                "🏈 Game in progress"
            )

        else:

            st.caption(
                "⏳ Result pending"
            )

        # -------------------------------------------------
        # CHANGE PICK
        # -------------------------------------------------

        editing = st.session_state.get(
            f"editing_{game_id}",
            False,
        )

        if not editing:

            change_pick = st.button(
                "✏️ Change Pick",
                key=f"change_{game_id}",
                use_container_width=True,
            )

            if change_pick:

                st.session_state[
                    f"editing_{game_id}"
                ] = True

                st.rerun()

        if st.session_state.get(
            f"editing_{game_id}",
            False,
        ):

            st.info(
                f"**{existing_pick['first_picker']}**, "
                "choose your new team:"
            )

            with st.form(
                key=f"edit_pick_form_{game_id}"
            ):

                selected_team = st.radio(
                    "Choose your team:",
                    options=[
                        away_team,
                        home_team,
                    ],
                    index=(
                        0
                        if existing_pick["first_team"]
                        == away_team
                        else 1
                    ),
                    horizontal=True,
                    key=f"edit_radio_{game_id}",
                )

                col1, col2 = st.columns(2)

                with col1:

                    save_changes = (
                        st.form_submit_button(
                            "Save Changes",
                            use_container_width=True,
                        )
                    )

                with col2:

                    cancel_changes = (
                        st.form_submit_button(
                            "Cancel",
                            use_container_width=True,
                        )
                    )

                if save_changes:

                    if selected_team == away_team:

                        other_team = home_team

                    else:

                        other_team = away_team

                    save_pick(
                        game_id=game_id,
                        first_picker=existing_pick[
                            "first_picker"
                        ],
                        first_team=selected_team,
                        second_picker=existing_pick[
                            "second_picker"
                        ],
                        second_team=other_team,
                    )

                    st.session_state[
                        f"editing_{game_id}"
                    ] = False

                    st.rerun()

                if cancel_changes:

                    st.session_state[
                        f"editing_{game_id}"
                    ] = False

                    st.rerun()

    # -----------------------------------------------------
    # NEW PICK
    # -----------------------------------------------------

    else:

        st.info(
            f"**{first_picker} picks first**"
        )

        with st.form(
            key=f"pick_form_{game_id}"
        ):

            selected_team = st.radio(
                f"{first_picker}, choose your team:",
                options=[
                    away_team,
                    home_team,
                ],
                horizontal=True,
                key=f"pick_radio_{game_id}",
            )

            submitted = st.form_submit_button(
                "Save Pick",
                use_container_width=True,
            )

            if submitted:

                if selected_team == away_team:

                    other_team = home_team

                else:

                    other_team = away_team

                save_pick(
                    game_id=game_id,
                    first_picker=first_picker,
                    first_team=selected_team,
                    second_picker=second_picker,
                    second_team=other_team,
                )

                st.rerun()

    st.divider()


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.caption(
    "£0.50 per game • Dan vs Fran"
)