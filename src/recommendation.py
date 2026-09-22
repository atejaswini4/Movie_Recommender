import pandas as pd
import joblib

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import hstack, csr_matrix

BASE_DIR = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System"

MOVIES_FILE = BASE_DIR + r"\data\clustered_movies.csv"
MODEL_FILE = BASE_DIR + r"\models\random_forest_model.pkl"
PREPROCESSOR_FILE = BASE_DIR + r"\models\random_forest_preprocessor.pkl"

movies = pd.read_csv(MOVIES_FILE)

rf_model = joblib.load(MODEL_FILE)
rf_preprocessor = joblib.load(PREPROCESSOR_FILE)

categorical_features = [
    "genres",
    "original_language"
]

numerical_features = [
    "popularity",
    "vote_average",
    "vote_count",
    "release_year",
    "user_rating_average",
    "user_rating_count"
]

movies[categorical_features] = movies[categorical_features].fillna("Unknown")
movies[numerical_features] = movies[numerical_features].fillna(0)

encoder = OneHotEncoder(handle_unknown="ignore")
categorical_matrix = encoder.fit_transform(
    movies[categorical_features]
)

scaler = StandardScaler()
numerical_matrix = scaler.fit_transform(
    movies[numerical_features]
)

numerical_matrix = csr_matrix(numerical_matrix)

feature_matrix = hstack(
    [
        categorical_matrix,
        numerical_matrix
    ]
).tocsr()


def get_genres(genre_text):
    if pd.isna(genre_text):
        return []

    genre_text = str(genre_text)

    if genre_text == "Unknown":
        return []

    return [
        genre.strip()
        for genre in genre_text.split(",")
        if genre.strip()
    ]


def calculate_genre_similarity(selected_genres, movie_genres):
    if not selected_genres or not movie_genres:
        return 0

    selected_set = set(selected_genres)
    movie_set = set(movie_genres)

    common = selected_set.intersection(movie_set)

    return len(common) / len(selected_set)


def recommend_movies(
    movie_title,
    language="All",
    number_of_movies=5
):
    if language == "All":
        language_movies = movies.copy()
    else:
        language_movies = movies[
            movies["original_language"] == language
        ].copy()

    if language_movies.empty:
        return []

    matches = language_movies[
        language_movies["title"]
        .astype(str)
        .str.lower()
        .str.strip()
        == movie_title.lower().strip()
    ]

    if matches.empty:
        return []

    selected_index = matches.index[0]

    selected_movie = movies.loc[selected_index]

    selected_cluster = selected_movie["cluster"]

    selected_genres = get_genres(
        selected_movie["genres"]
    )

    selected_rating = float(
        selected_movie["vote_average"]
    )

    cluster_movies = language_movies[
        language_movies["cluster"] == selected_cluster
    ].copy()

    if cluster_movies.empty:
        return []

    candidate_positions = cluster_movies.index.tolist()

    selected_candidate_position = candidate_positions.index(
        selected_index
    )

    candidate_matrix = feature_matrix[
        candidate_positions
    ]

    knn = NearestNeighbors(
        metric="cosine",
        algorithm="brute"
    )

    knn.fit(candidate_matrix)

    neighbor_count = min(
        len(candidate_positions),
        number_of_movies + 1
    )

    distances, indices = knn.kneighbors(
        candidate_matrix[selected_candidate_position],
        n_neighbors=neighbor_count
    )

    recommendations = []

    for distance, candidate_position in zip(
        distances[0],
        indices[0]
    ):
        actual_index = candidate_positions[
            candidate_position
        ]

        if actual_index == selected_index:
            continue

        movie = movies.loc[actual_index]

        movie_data = pd.DataFrame(
            [
                {
                    "genres": movie["genres"],
                    "original_language": movie["original_language"],
                    "popularity": movie["popularity"],
                    "vote_average": movie["vote_average"],
                    "vote_count": movie["vote_count"],
                    "release_year": movie["release_year"]
                }
            ]
        )

        rf_features = rf_preprocessor.transform(
            movie_data
        )

        preference_probability = rf_model.predict_proba(
            rf_features
        )[0][1]

        similarity = max(
            0,
            1 - distance
        )

        movie_genres = get_genres(
            movie["genres"]
        )

        genre_similarity = calculate_genre_similarity(
            selected_genres,
            movie_genres
        )

        rating_difference = abs(
            selected_rating -
            float(movie["vote_average"])
        )

        rating_similarity = max(
            0,
            1 - (rating_difference / 10)
        )

        final_score = (
            0.7 * similarity
            + 0.3 * preference_probability
        )

        reasons = []

        if (
            movie["original_language"]
            == selected_movie["original_language"]
        ):
            reasons.append("Same language")

        if genre_similarity > 0:
            reasons.append("Similar genre")

        if rating_similarity >= 0.8:
            reasons.append("Similar rating")

        if movie["cluster"] == selected_cluster:
            reasons.append("Same ML cluster")

        if not reasons:
            reasons.append("Similar movie characteristics")

        recommendations.append(
            {
                "title": movie["title"],
                "similarity": similarity,
                "similarity_percent": round(
                    similarity * 100,
                    1
                ),
                "preference_score": preference_probability,
                "final_score": final_score,
                "poster_path": movie["poster_path"],
                "tmdbId": movie["tmdbId"],
                "vote_average": movie["vote_average"],
                "release_year": movie["release_year"],
                "genres": movie["genres"],
                "original_language": movie["original_language"],
                "cluster": movie["cluster"],
                "popularity": movie["popularity"],
                "reasons": reasons
            }
        )

    recommendations = sorted(
        recommendations,
        key=lambda x: x["final_score"],
        reverse=True
    )

    return recommendations[:number_of_movies]