import pandas as pd
import joblib

MOVIES_FILE = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System\data\cleaned_movies.csv"

MODEL_FILE = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System\models\random_forest_model.pkl"

PREPROCESSOR_FILE = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System\models\random_forest_preprocessor.pkl"

movies = pd.read_csv(
    MOVIES_FILE
)

model = joblib.load(
    MODEL_FILE
)

preprocessor = joblib.load(
    PREPROCESSOR_FILE
)

categorical_features = [
    "genres",
    "original_language"
]

numerical_features = [
    "popularity",
    "vote_average",
    "vote_count",
    "release_year"
]


def predict_movie_preference(movie_title):

    matches = movies[
        movies["title"].astype(str).str.lower()
        == movie_title.lower()
    ]

    if matches.empty:
        return None

    movie = matches.iloc[0]

    movie_data = pd.DataFrame(
        [{
            "genres": movie["genres"],
            "original_language": movie["original_language"],
            "popularity": movie["popularity"],
            "vote_average": movie["vote_average"],
            "vote_count": movie["vote_count"],
            "release_year": movie["release_year"]
        }]
    )

    movie_data[categorical_features] = movie_data[
        categorical_features
    ].fillna("Unknown")

    movie_data[numerical_features] = movie_data[
        numerical_features
    ].fillna(0)

    features = preprocessor.transform(
        movie_data
    )

    prediction = model.predict(
        features
    )[0]

    probability = model.predict_proba(
        features
    )[0][1]

    return {
        "title": movie["title"],
        "prediction": int(prediction),
        "preference_score": probability,
        "rating": movie["vote_average"],
        "year": movie["release_year"],
        "genres": movie["genres"]
    }


if __name__ == "__main__":

    movie_title = input(
        "Enter movie title: "
    )

    result = predict_movie_preference(
        movie_title
    )

    if result is None:

        print(
            "\nMovie not found."
        )

    else:

        print(
            "\n========================================"
        )

        print(
            "       MOVIE PREFERENCE PREDICTION"
        )

        print(
            "========================================"
        )

        print(
            "\nMovie:",
            result["title"]
        )

        print(
            "Rating:",
            result["rating"]
        )

        print(
            "Year:",
            int(result["year"])
            if pd.notna(result["year"])
            else "Unknown"
        )

        print(
            "Genres:",
            result["genres"]
        )

        print(
            "Preference Score:",
            round(
                result["preference_score"],
                3
            )
        )

        if result["prediction"] == 1:

            print(
                "Prediction: Preferred"
            )

        else:

            print(
                "Prediction: Not Preferred"
            )