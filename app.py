import os
import pandas as pd
import requests
import streamlit as st
from io import BytesIO
from src.recommendation import recommend_movies
from src.tmdb_api import get_movie_poster

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MOVIES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "clustered_movies.csv"
)

movies = pd.read_csv(MOVIES_FILE)

language_names = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "ml": "Malayalam",
    "kn": "Kannada",
    "bn": "Bengali",
    "mr": "Marathi",
    "pa": "Punjabi",
    "gu": "Gujarati",
    "ur": "Urdu",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "es": "Spanish",
    "ru": "Russian"
}

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = ""

if "selected_language" not in st.session_state:
    st.session_state.selected_language = "Telugu"

if "details_movie" not in st.session_state:
    st.session_state.details_movie = None

dark_mode = st.session_state.theme == "dark"

if dark_mode:
    background = "#07111f"
    surface = "#0d192b"
    surface2 = "#132238"
    border = "#243754"
    text = "#f4f7ff"
    muted = "#9eabc0"
    accent = "#7567ff"
    accent2 = "#9a65ff"
    input_bg = "#0d192b"
else:
    background = "#f5f7fb"
    surface = "#ffffff"
    surface2 = "#eef2f8"
    border = "#d8dfeb"
    text = "#172033"
    muted = "#647084"
    accent = "#5d4bdd"
    accent2 = "#7955d9"
    input_bg = "#ffffff"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {background};
        color: {text};
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stSidebar"] {{
        background: {surface};
        border-right: 1px solid {border};
    }}

    .brand {{
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 8px 4px 24px 4px;
    }}

    .brand-icon {{
        font-size: 31px;
    }}

    .brand-name {{
        font-size: 21px;
        font-weight: 800;
        color: {text};
    }}

    .brand-name span {{
        color: {accent2};
    }}

    .brand-sub {{
        font-size: 11px;
        color: {muted};
        margin-top: 2px;
    }}

    .hero {{
        min-height: 235px;
        border-radius: 20px;
        padding: 48px 55px;
        margin-bottom: 22px;
        border: 1px solid {border};
        background:
            linear-gradient(
                90deg,
                rgba(5,13,26,0.98) 0%,
                rgba(8,17,33,0.93) 46%,
                rgba(20,24,57,0.63) 100%
            ),
            radial-gradient(
                circle at 82% 30%,
                rgba(122,89,255,0.65),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #101e3a,
                #29184f
            );
        overflow: hidden;
        position: relative;
    }}

    .hero:after {{
        content: "";
        position: absolute;
        right: -80px;
        top: -110px;
        width: 450px;
        height: 450px;
        border-radius: 50%;
        background: radial-gradient(
            circle,
            rgba(137,99,255,0.28),
            transparent 65%
        );
    }}

    .hero-title {{
        position: relative;
        z-index: 2;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 9px;
        color: #ffffff;
    }}

    .hero-title span {{
        color: #927bff;
    }}

    .hero-text {{
        position: relative;
        z-index: 2;
        color: #d7ddec;
        font-size: 15px;
        line-height: 1.65;
        max-width: 620px;
    }}

    .section-title {{
        font-size: 24px;
        font-weight: 800;
        color: {text};
        margin: 25px 0 8px 0;
    }}

    .section-sub {{
        color: {muted};
        font-size: 13px;
        margin-bottom: 18px;
    }}

    .panel {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 20px;
        height: 100%;
    }}

    .panel-title {{
        font-size: 17px;
        font-weight: 750;
        color: {text};
        margin-bottom: 5px;
    }}

    .panel-sub {{
        color: {muted};
        font-size: 12px;
        margin-bottom: 15px;
    }}

    .movie-card {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 14px;
        overflow: hidden;
        height: 100%;
        margin-bottom: 18px;
    }}

    .movie-card-content {{
        padding: 12px;
    }}

    .movie-card-title {{
        font-size: 15px;
        font-weight: 750;
        color: {text};
        min-height: 40px;
        line-height: 1.3;
    }}

    .movie-meta {{
        color: {muted};
        font-size: 12px;
        margin-top: 5px;
    }}

    .rating {{
        color: #ffd43b;
        font-weight: 700;
    }}

    .tag {{
        display: inline-block;
        background: {surface2};
        border: 1px solid {border};
        color: {muted};
        border-radius: 20px;
        padding: 4px 8px;
        margin: 4px 3px 0 0;
        font-size: 10px;
    }}

    .why-box {{
        margin-top: 10px;
        background: {surface2};
        border-radius: 10px;
        padding: 10px;
        border: 1px solid {border};
    }}

    .why-title {{
        font-size: 11px;
        font-weight: 750;
        color: {text};
        margin-bottom: 5px;
    }}

    .why-item {{
        font-size: 10px;
        color: {muted};
        margin: 3px 0;
    }}

    .why-item span {{
        color: #35d39a;
        font-weight: 800;
    }}

    .metric-card {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 14px;
        padding: 18px;
        height: 100%;
    }}

    .metric-name {{
        font-size: 12px;
        color: {muted};
    }}

    .metric-value {{
        font-size: 26px;
        font-weight: 800;
        color: {text};
        margin-top: 4px;
    }}

    .algorithm-card {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 14px;
        padding: 20px;
        height: 100%;
    }}

    .algorithm-icon {{
        font-size: 29px;
        margin-bottom: 8px;
    }}

    .algorithm-name {{
        font-size: 16px;
        font-weight: 800;
        color: {text};
    }}

    .algorithm-text {{
        color: {muted};
        font-size: 12px;
        line-height: 1.55;
        margin-top: 7px;
    }}

    .stat-number {{
        font-size: 25px;
        font-weight: 800;
        color: {text};
    }}

    .stat-label {{
        font-size: 11px;
        color: {muted};
    }}

    .footer {{
        border-top: 1px solid {border};
        margin-top: 35px;
        padding: 20px 4px;
        color: {muted};
        font-size: 11px;
        text-align: center;
    }}

    div[data-testid="stImage"] {{
        border-radius: 12px;
        overflow: hidden;
    }}

    div[data-testid="stImage"] img {{
        border-radius: 12px;
        object-fit: cover;
    }}

    .stButton > button {{
        border-radius: 9px;
        border: 1px solid {border};
        background: {surface2};
        color: {text};
        font-weight: 650;
        min-height: 40px;
    }}

    .stButton > button:hover {{
        border-color: {accent};
        color: {text};
    }}

    div[data-baseweb="select"] > div {{
        background: {input_bg};
        border-color: {border};
        color: {text};
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: {surface2};
        border-radius: 20px;
        padding: 8px 18px;
        color: {muted};
    }}

    .stTabs [aria-selected="true"] {{
        background: {accent};
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

def get_language_code(language):
    for code, name in language_names.items():
        if name == language:
            return code
    return language.lower()

def get_language_movies(language):
    if language == "All":
        return movies.copy()

    code = get_language_code(language)

    return movies[
        movies["original_language"].astype(str).str.lower()
        == code.lower()
    ].copy()

def get_poster_data(movie):
    poster_url = get_movie_poster(
        movie["title"],
        movie["release_year"],
        movie["poster_path"],
        movie["tmdbId"]
    )

    if not poster_url:
        return None

    try:
        response = requests.get(
            poster_url,
            timeout=15
        )

        if response.status_code == 200:
            return BytesIO(
                response.content
            )

    except requests.exceptions.RequestException:
        return None

    return None

def render_movie_card(movie, index):
    poster_data = get_poster_data(movie)

    if poster_data:
        st.image(
            poster_data,
            use_container_width=True
        )
    else:
        st.markdown(
            f"""
            <div style="
                height:260px;
                display:flex;
                align-items:center;
                justify-content:center;
                background:{surface2};
                border-radius:12px;
                color:{muted};
                font-size:13px;
            ">
                🎬 Poster unavailable
            </div>
            """,
            unsafe_allow_html=True
        )

    title = str(
        movie["title"]
    )

    rating = float(
        movie["vote_average"]
        if pd.notna(movie["vote_average"])
        else 0
    )

    year = (
        int(movie["release_year"])
        if pd.notna(movie["release_year"])
        else "N/A"
    )

    genres = str(
        movie["genres"]
    )

    genre_parts = [
        item.strip()
        for item in genres.split(",")
        if item.strip()
    ]

    genre_html = ""

    for genre in genre_parts[:3]:
        genre_html += (
            f'<span class="tag">{genre}</span>'
        )

    st.markdown(
        f"""
        <div class="movie-card-content">
            <div class="movie-card-title">{title}</div>
            <div class="movie-meta">
                <span class="rating">★ {rating:.1f}</span>
                &nbsp; • &nbsp; {year}
            </div>
            <div>{genre_html}</div>
            <div class="why-box">
                <div class="why-title">Why recommended?</div>
                <div class="why-item">
                    <span>✓</span> Similar genre
                </div>
                <div class="why-item">
                    <span>✓</span> Similar rating
                </div>
                <div class="why-item">
                    <span>✓</span> Similar characteristics
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "View Details",
        key=f"details_{index}_{title}",
        use_container_width=True
    ):
        st.session_state.details_movie = movie
        st.rerun()

def render_recommendations(recommendations):
    if not recommendations:
        st.warning(
            "No recommendations found."
        )
        return

    st.markdown(
        '<div class="section-title">✨ Recommended Movies</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="section-sub">
            Recommendations based on
            <b>{st.session_state.selected_movie}</b>
            in
            <b>{st.session_state.selected_language}</b>.
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Most Similar",
            "Highly Rated",
            "Popular Picks"
        ]
    )

    with tab1:
        ordered = sorted(
            recommendations,
            key=lambda x: x["final_score"],
            reverse=True
        )

        columns = st.columns(
            min(5, len(ordered))
        )

        for index, movie in enumerate(
            ordered[:10]
        ):
            with columns[
                index % len(columns)
            ]:
                render_movie_card(
                    movie,
                    index
                )

    with tab2:
        ordered = sorted(
            recommendations,
            key=lambda x: x["vote_average"]
            if pd.notna(x["vote_average"])
            else 0,
            reverse=True
        )

        columns = st.columns(
            min(5, len(ordered))
        )

        for index, movie in enumerate(
            ordered[:10]
        ):
            with columns[
                index % len(columns)
            ]:
                render_movie_card(
                    movie,
                    100 + index
                )

    with tab3:
        ordered = sorted(
            recommendations,
            key=lambda x: x["popularity"]
            if pd.notna(x["popularity"])
            else 0,
            reverse=True
        )

        columns = st.columns(
            min(5, len(ordered))
        )

        for index, movie in enumerate(
            ordered[:10]
        ):
            with columns[
                index % len(columns)
            ]:
                render_movie_card(
                    movie,
                    200 + index
                )

def render_home():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                Movie <span>Recommendation System</span>
            </div>
            <div class="hero-text">
                Find your next favorite movie using Machine Learning.
                Select a language, choose a movie you like, add optional
                preferences, and discover similar movies with posters,
                ratings, genres, and recommendation scores.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">🎯 Build Your Recommendation</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">Follow the three simple steps below.</div>',
        unsafe_allow_html=True
    )

    first, second, third = st.columns(
        [1, 1, 1]
    )

    with first:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">① Select Language</div>
                <div class="panel-sub">
                    Choose the movie language or industry.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        language_options = [
            "Telugu",
            "Hindi",
            "Tamil",
            "Malayalam",
            "Kannada",
            "English"
        ]

        selected_language = st.selectbox(
            "Language",
            language_options,
            index=(
                language_options.index(
                    st.session_state.selected_language
                )
                if st.session_state.selected_language
                in language_options
                else 0
            ),
            label_visibility="collapsed"
        )

        st.session_state.selected_language = selected_language

    language_movies = get_language_movies(
        st.session_state.selected_language
    )

    movie_titles = sorted(
        language_movies["title"]
        .dropna()
        .astype(str)
        .unique()
    )

    with second:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">② Select a Movie</div>
                <div class="panel-sub">
                    Choose a movie that you already like.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if movie_titles:
            selected_movie = st.selectbox(
                "Movie",
                movie_titles,
                index=(
                    movie_titles.index(
                        st.session_state.selected_movie
                    )
                    if st.session_state.selected_movie
                    in movie_titles
                    else 0
                ),
                label_visibility="collapsed"
            )

            st.session_state.selected_movie = selected_movie

    genre_values = set()

    for value in movies["genres"].dropna():
        for genre in str(value).split(","):
            genre = genre.strip()

            if genre:
                genre_values.add(genre)

    genre_options = [
        "Any"
    ] + sorted(
        genre_values
    )

    with third:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">③ Optional Preferences</div>
                <div class="panel-sub">
                    Add filters to refine your recommendations.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        selected_genre = st.selectbox(
            "Genre",
            genre_options
        )

        selected_rating = st.selectbox(
            "Minimum Rating",
            [
                "Any",
                "5.0",
                "6.0",
                "7.0",
                "8.0"
            ]
        )

        selected_year = st.selectbox(
            "Release Year",
            ["Any"] +
            sorted(
                [
                    int(year)
                    for year in movies["release_year"].dropna().unique()
                    if 1900 <= int(year) <= 2026
                ],
                reverse=True
            )
        )

        selected_popularity = st.selectbox(
            "Popularity",
            [
                "Any",
                "High",
                "Medium"
            ]
        )

    st.markdown("")

    if st.button(
        "✨ Get Recommendations",
        use_container_width=True
    ):

        with st.spinner(
            "Finding movies similar to your selection..."
        ):

            language_code = get_language_code(
                st.session_state.selected_language
            )

            results = recommend_movies(
                st.session_state.selected_movie,
                language_code,
                10
            )

        if selected_rating != "Any":
            results = [
                movie
                for movie in results
                if pd.notna(movie["vote_average"])
                and movie["vote_average"] >= float(selected_rating)
            ]

        if selected_genre != "Any":
            results = [
                movie
                for movie in results
                if selected_genre.lower()
                in str(movie["genres"]).lower()
            ]

        if selected_year != "Any":
            results = [
                movie
                for movie in results
                if pd.notna(movie["release_year"])
                and int(movie["release_year"]) == int(selected_year)
            ]

        if selected_popularity == "High":
            threshold = movies["popularity"].quantile(0.75)

            results = [
                movie
                for movie in results
                if pd.notna(movie["popularity"])
                and movie["popularity"] >= threshold
            ]

        elif selected_popularity == "Medium":
            threshold = movies["popularity"].quantile(0.40)

            results = [
                movie
                for movie in results
                if pd.notna(movie["popularity"])
                and movie["popularity"] >= threshold
            ]

        if not results:
            results = recommend_movies(
                st.session_state.selected_movie,
                language_code,
                10
            )

        st.session_state.recommendations = results

    if st.session_state.recommendations:

        st.markdown(
            f"""
            <div class="panel" style="margin-top:22px;">
                🎬 <b>Selected Movie:</b>
                {st.session_state.selected_movie}
                &nbsp;&nbsp; | &nbsp;&nbsp;
                🌍 <b>Language:</b>
                {st.session_state.selected_language}
                &nbsp;&nbsp; | &nbsp;&nbsp;
                🍿 <b>Recommendations:</b>
                {len(st.session_state.recommendations)}
            </div>
            """,
            unsafe_allow_html=True
        )

        render_recommendations(
            st.session_state.recommendations
        )

    st.markdown(
        '<div class="section-title">💡 How It Works</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">Three machine learning techniques work together to generate the recommendations.</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="algorithm-card">
                <div class="algorithm-icon">🟢</div>
                <div class="algorithm-name">
                    K-Means Clustering
                </div>
                <div class="algorithm-text">
                    Groups movies with similar characteristics and
                    identifies the cluster containing the selected movie.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="algorithm-card">
                <div class="algorithm-icon">🔵</div>
                <div class="algorithm-name">
                    K-Nearest Neighbors
                </div>
                <div class="algorithm-text">
                    Finds movies closest to the selected movie using
                    cosine similarity within the selected cluster.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="algorithm-card">
                <div class="algorithm-icon">🟣</div>
                <div class="algorithm-name">
                    Random Forest
                </div>
                <div class="algorithm-text">
                    Calculates a preference probability which contributes
                    to the final recommendation ranking.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section-title">📊 Project Statistics</div>',
        unsafe_allow_html=True
    )

    total_movies = len(movies)
    total_languages = movies["original_language"].nunique()
    total_clusters = (
        movies["cluster"].nunique()
        if "cluster" in movies.columns
        else 0
    )
    average_rating = movies["vote_average"].mean()

    stat1, stat2, stat3, stat4 = st.columns(4)

    with stat1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="stat-number">
                    {total_movies:,}
                </div>
                <div class="stat-label">
                    Movies
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with stat2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="stat-number">
                    {total_languages}
                </div>
                <div class="stat-label">
                    Languages
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with stat3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="stat-number">
                    {total_clusters}
                </div>
                <div class="stat-label">
                    Movie Clusters
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with stat4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="stat-number">
                    {average_rating:.1f}
                </div>
                <div class="stat-label">
                    Average Rating
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_explore():
    st.markdown(
        '<div class="section-title">🔎 Explore Movies</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">Search and browse movies from the dataset.</div>',
        unsafe_allow_html=True
    )

    language = st.selectbox(
        "Language",
        ["All"] +
        sorted(
            [
                language_names.get(
                    str(code),
                    str(code).upper()
                )
                for code in movies["original_language"]
                .dropna()
                .astype(str)
                .unique()
            ]
        )
    )

    search = st.text_input(
        "Search Movie",
        placeholder="Type a movie title..."
    )

    filtered = get_language_movies(
        language
    )

    if search:
        filtered = filtered[
            filtered["title"].astype(str).str.contains(
                search,
                case=False,
                na=False
            )
        ]

    filtered = filtered.sort_values(
        "vote_average",
        ascending=False
    ).head(20)

    if filtered.empty:
        st.info(
            "No movies found."
        )
        return

    columns = st.columns(5)

    for index, (_, movie) in enumerate(
        filtered.iterrows()
    ):
        with columns[
            index % 5
        ]:
            render_movie_card(
                movie.to_dict(),
                500 + index
            )

def render_dataset_insights():
    st.markdown(
        '<div class="section-title">📊 Dataset Insights</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">Explore statistics from the movie dataset.</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Movies",
            f"{len(movies):,}"
        )

    with col2:
        st.metric(
            "Languages",
            movies["original_language"].nunique()
        )

    with col3:
        st.metric(
            "Average Rating",
            f"{movies['vote_average'].mean():.2f}"
        )

    with col4:
        st.metric(
            "Average Popularity",
            f"{movies['popularity'].mean():.2f}"
        )

    st.markdown(
        '<div class="section-title">🌍 Movies by Language</div>',
        unsafe_allow_html=True
    )

    language_counts = (
        movies["original_language"]
        .value_counts()
        .head(10)
    )

    language_counts.index = [
        language_names.get(
            str(code),
            str(code).upper()
        )
        for code in language_counts.index
    ]

    st.bar_chart(
        language_counts
    )

    st.markdown(
        '<div class="section-title">⭐ Rating Distribution</div>',
        unsafe_allow_html=True
    )

    rating_data = (
        movies["vote_average"]
        .dropna()
        .round(1)
        .value_counts()
        .sort_index()
    )

    st.line_chart(
        rating_data
    )

def render_model_performance():
    st.markdown(
        '<div class="section-title">⚙️ Model Performance</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">Measured results from the trained Random Forest model.</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-name">
                    Accuracy
                </div>
                <div class="metric-value">
                    64.79%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-name">
                    Precision
                </div>
                <div class="metric-value">
                    65.26%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-name">
                    Recall
                </div>
                <div class="metric-value">
                    67.76%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section-title">🧠 Recommendation Pipeline</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="algorithm-card">
                <div class="algorithm-icon">🟢</div>
                <div class="algorithm-name">
                    K-Means
                </div>
                <div class="algorithm-text">
                    Creates groups of movies with similar feature
                    characteristics.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="algorithm-card">
                <div class="algorithm-icon">🔵</div>
                <div class="algorithm-name">
                    KNN
                </div>
                <div class="algorithm-text">
                    Finds the nearest movies using cosine distance
                    within the selected cluster.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="algorithm-card">
                <div class="algorithm-icon">🟣</div>
                <div class="algorithm-name">
                    Random Forest
                </div>
                <div class="algorithm-text">
                    Produces a preference probability used in the
                    final recommendation score.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_about():
    st.markdown(
        '<div class="section-title">ℹ️ About</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">
                🎬 Movie Recommendation System
            </div>
            <br>
            <div class="algorithm-text">
                This project is a Machine Learning based movie
                recommendation system that recommends movies similar
                to a movie selected by the user.
                <br><br>
                K-Means Clustering identifies a group of similar movies.
                KNN finds movies that are closest to the selected movie.
                Random Forest provides a preference score that contributes
                to the final recommendation ranking.
                <br><br>
                Streamlit is used to create the interactive application
                and TMDB is used to retrieve movie posters.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">🛠️ Technologies Used</div>',
        unsafe_allow_html=True
    )

    technologies = [
        "Python",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "SciPy",
        "Streamlit",
        "TMDB API",
        "Joblib",
        "Requests"
    ]

    columns = st.columns(3)

    for index, technology in enumerate(
        technologies
    ):
        with columns[
            index % 3
        ]:
            st.markdown(
                f"""
                <div class="metric-card" style="margin-bottom:12px;">
                    <div class="metric-name">
                        Technology
                    </div>
                    <div class="metric-value"
                         style="font-size:18px;">
                        {technology}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

def render_details():
    if st.session_state.details_movie is None:
        return

    movie = st.session_state.details_movie

    st.markdown("---")

    st.markdown(
        '<div class="section-title">🎬 Movie Details</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(
        [1, 2]
    )

    with left:
        poster_data = get_poster_data(
            movie
        )

        if poster_data:
            st.image(
                poster_data,
                use_container_width=True
            )

    with right:
        st.markdown(
            f"## {movie['title']}"
        )

        rating = float(
            movie["vote_average"]
            if pd.notna(movie["vote_average"])
            else 0
        )

        year = (
            int(movie["release_year"])
            if pd.notna(movie["release_year"])
            else "N/A"
        )

        st.write(
            f"⭐ Rating: {rating:.1f}"
        )

        st.write(
            f"📅 Release Year: {year}"
        )

        st.write(
            f"🎭 Genres: {movie['genres']}"
        )

        language = language_names.get(
            str(movie["original_language"]),
            str(movie["original_language"]).upper()
        )

        st.write(
            f"🌍 Language: {language}"
        )

        if pd.notna(
            movie["popularity"]
        ):
            st.write(
                f"📈 Popularity: {movie['popularity']:.2f}"
            )

        if "similarity" in movie:
            st.write(
                f"📊 Similarity: {movie['similarity']:.2f}"
            )

        if "preference_score" in movie:
            st.write(
                f"🤖 Preference Score: {movie['preference_score']:.2f}"
            )

    if st.button(
        "Close Details",
        use_container_width=True
    ):
        st.session_state.details_movie = None
        st.rerun()

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🎬</div>
            <div>
                <div class="brand-name">
                    Movie <span>Recommender</span>
                </div>
                <div class="brand-sub">
                    Find Your Next Favorite Movie
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    page_options = [
        "🏠 Home",
        "✨ Recommendations",
        "🔎 Explore",
        "📊 Dataset Insights",
        "⚙️ Model Performance",
        "ℹ️ About"
    ]

    selected_page = st.radio(
        "Navigation",
        page_options,
        index=0,
        label_visibility="collapsed"
    )

    if selected_page == "🏠 Home":
        st.session_state.page = "Home"

    elif selected_page == "✨ Recommendations":
        st.session_state.page = "Recommendations"

    elif selected_page == "🔎 Explore":
        st.session_state.page = "Explore"

    elif selected_page == "📊 Dataset Insights":
        st.session_state.page = "Dataset Insights"

    elif selected_page == "⚙️ Model Performance":
        st.session_state.page = "Model Performance"

    else:
        st.session_state.page = "About"

    st.markdown("---")

    if st.button(
        "☀️ Light Mode"
        if dark_mode
        else "🌙 Dark Mode",
        use_container_width=True
    ):
        st.session_state.theme = (
            "light"
            if dark_mode
            else "dark"
        )
        st.rerun()

if st.session_state.page == "Home":
    render_home()

elif st.session_state.page == "Recommendations":

    st.markdown(
        '<div class="section-title">✨ Recommendations</div>',
        unsafe_allow_html=True
    )

    if st.session_state.recommendations:
        render_recommendations(
            st.session_state.recommendations
        )
    else:
        st.info(
            "Go to Home, select a movie and click Get Recommendations."
        )

elif st.session_state.page == "Explore":
    render_explore()

elif st.session_state.page == "Dataset Insights":
    render_dataset_insights()

elif st.session_state.page == "Model Performance":
    render_model_performance()

elif st.session_state.page == "About":
    render_about()

render_details()

st.markdown(
    """
    <div class="footer">
        🎬 Movie Recommendation System
        &nbsp; • &nbsp;
        Built with Machine Learning
    </div>
    """,
    unsafe_allow_html=True
)