import pandas as pd
import ast
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MOVIES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "movies_metadata.csv.zip"
)

RATINGS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "ratings_small.csv.zip"
)

LINKS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "links_small.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "cleaned_movies.csv"
)


def load_data():

    print("Loading movies dataset...")

    movies = pd.read_csv(
        MOVIES_FILE,
        compression="zip",
        low_memory=False
    )

    print("Movies shape:", movies.shape)

    print("\nLoading ratings dataset...")

    ratings = pd.read_csv(
        RATINGS_FILE,
        compression="zip"
    )

    print("Ratings shape:", ratings.shape)

    print("\nLoading links dataset...")

    links = pd.read_csv(
        LINKS_FILE
    )

    print("Links shape:", links.shape)

    return movies, ratings, links


def clean_genres(value):

    try:

        genres = ast.literal_eval(value)

        if isinstance(genres, list):

            return " ".join(
                genre["name"]
                for genre in genres
                if isinstance(genre, dict)
                and "name" in genre
            )

    except (
        ValueError,
        SyntaxError,
        TypeError
    ):

        pass

    return "Unknown"


def preprocess():

    movies, ratings, links = load_data()

    columns = [
        "id",
        "title",
        "genres",
        "original_language",
        "overview",
        "popularity",
        "release_date",
        "vote_average",
        "vote_count",
        "poster_path"
    ]

    movies = movies[columns].copy()

    movies["id"] = pd.to_numeric(
        movies["id"],
        errors="coerce"
    )

    movies["popularity"] = pd.to_numeric(
        movies["popularity"],
        errors="coerce"
    )

    movies["vote_average"] = pd.to_numeric(
        movies["vote_average"],
        errors="coerce"
    )

    movies["vote_count"] = pd.to_numeric(
        movies["vote_count"],
        errors="coerce"
    )

    movies["release_date"] = pd.to_datetime(
        movies["release_date"],
        errors="coerce"
    )

    movies["release_year"] = movies[
        "release_date"
    ].dt.year

    movies["genres"] = movies[
        "genres"
    ].apply(
        clean_genres
    )

    movies["title"] = movies[
        "title"
    ].fillna("Unknown")

    movies["original_language"] = movies[
        "original_language"
    ].fillna("Unknown")

    movies["overview"] = movies[
        "overview"
    ].fillna("")

    movies["popularity"] = movies[
        "popularity"
    ].fillna(0)

    movies["vote_average"] = movies[
        "vote_average"
    ].fillna(0)

    movies["vote_count"] = movies[
        "vote_count"
    ].fillna(0)

    movies["release_year"] = movies[
        "release_year"
    ].fillna(0)

    movies["poster_path"] = movies[
        "poster_path"
    ].fillna("")

    movies = movies.dropna(
        subset=["id"]
    )

    movies = movies.drop_duplicates(
        subset=["id"]
    )

    links["movieId"] = pd.to_numeric(
        links["movieId"],
        errors="coerce"
    )

    links["tmdbId"] = pd.to_numeric(
        links["tmdbId"],
        errors="coerce"
    )

    links = links.dropna(
        subset=["tmdbId"]
    )

    links["tmdbId"] = links[
        "tmdbId"
    ].astype(int)

    links = links[
        ["movieId", "tmdbId"]
    ].drop_duplicates(
        subset=["tmdbId"]
    )

    ratings_summary = ratings.groupby(
        "movieId"
    ).agg(
        user_rating_average=(
            "rating",
            "mean"
        ),
        user_rating_count=(
            "rating",
            "count"
        )
    ).reset_index()

    movies = movies.merge(
        links,
        left_on="id",
        right_on="tmdbId",
        how="left"
    )

    movies = movies.drop(
        columns=["movieId"],
        errors="ignore"
    )

    movies = movies.merge(
        ratings_summary,
        left_on="tmdbId",
        right_on="movieId",
        how="left"
    )

    movies = movies.drop(
        columns=["movieId"],
        errors="ignore"
    )

    movies["user_rating_average"] = movies[
        "user_rating_average"
    ].fillna(0)

    movies["user_rating_count"] = movies[
        "user_rating_count"
    ].fillna(0)

    movies["tmdbId"] = movies[
        "tmdbId"
    ].fillna(movies["id"])

    movies["tmdbId"] = movies[
        "tmdbId"
    ].astype(int)

    movies = movies[
        [
            "id",
            "tmdbId",
            "title",
            "genres",
            "original_language",
            "overview",
            "popularity",
            "release_date",
            "vote_average",
            "vote_count",
            "poster_path",
            "release_year",
            "user_rating_average",
            "user_rating_count"
        ]
    ]

    movies.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\nCleaned dataset saved successfully."
    )

    print(
        "Output:",
        OUTPUT_FILE
    )

    print(
        "Shape:",
        movies.shape
    )

    print(
        "\nColumns:"
    )

    print(
        movies.columns.tolist()
    )

    print(
        "\nMovies with TMDB IDs:",
        movies["tmdbId"].notna().sum()
    )

    print(
        "Movies with posters:",
        (
            movies["poster_path"].astype(str).str.strip() != ""
        ).sum()
    )


if __name__ == "__main__":

    preprocess()