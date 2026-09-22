import os
import requests
import streamlit as st
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_FILE)

try:
    TMDB_API_KEY = st.secrets.get("TMDB_API_KEY")
except Exception:
    TMDB_API_KEY = None

if not TMDB_API_KEY:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_poster_url(poster_path):
    if not poster_path:
        return None

    poster_path = str(poster_path).strip()

    if poster_path == "":
        return None

    if poster_path.lower() == "nan":
        return None

    if poster_path.startswith("http"):
        return poster_path

    if not poster_path.startswith("/"):
        poster_path = "/" + poster_path

    return f"{IMAGE_BASE_URL}{poster_path}"


def check_poster(url):
    if not url:
        return False

    try:
        response = requests.get(
            url,
            timeout=15,
            stream=True
        )

        return response.status_code == 200

    except requests.exceptions.RequestException:
        return False


def get_movie_by_tmdb_id(tmdb_id):
    if not TMDB_API_KEY or not tmdb_id:
        return None

    try:
        tmdb_id = int(float(tmdb_id))
    except (ValueError, TypeError):
        return None

    url = f"{BASE_URL}/movie/{tmdb_id}"

    params = {
        "api_key": TMDB_API_KEY
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            return None

        return response.json()

    except requests.exceptions.RequestException:
        return None


def search_movie(movie_name, year=None):
    if not TMDB_API_KEY:
        return []

    url = f"{BASE_URL}/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_name,
        "include_adult": False
    }

    if year:
        try:
            params["year"] = int(float(year))
        except (ValueError, TypeError):
            pass

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            return []

        return response.json().get(
            "results",
            []
        )

    except requests.exceptions.RequestException:
        return []


def find_poster_in_results(results):
    for result in results:
        poster_path = result.get("poster_path")

        if not poster_path:
            continue

        poster_url = get_poster_url(
            poster_path
        )

        if check_poster(poster_url):
            return poster_url

    return None


def get_movie_poster(
    movie_name,
    year=None,
    dataset_poster=None,
    tmdb_id=None
):
    dataset_url = get_poster_url(
        dataset_poster
    )

    if check_poster(dataset_url):
        return dataset_url

    if tmdb_id:
        movie_data = get_movie_by_tmdb_id(
            tmdb_id
        )

        if movie_data:
            poster_path = movie_data.get(
                "poster_path"
            )

            poster_url = get_poster_url(
                poster_path
            )

            if check_poster(poster_url):
                return poster_url

    results = search_movie(movie_name)

    poster = find_poster_in_results(
        results
    )

    if poster:
        return poster

    if year:
        results = search_movie(
            movie_name,
            year
        )

        poster = find_poster_in_results(
            results
        )

        if poster:
            return poster

    return None