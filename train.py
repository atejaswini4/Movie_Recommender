import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, precision_score, recall_score

MOVIES_FILE = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System\data\cleaned_movies.csv"

RATINGS_FILE = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System\data\ratings_small.csv.zip"

LINKS_FILE = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System\data\links_small.csv"

MODEL_FILE = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System\models\random_forest_model.pkl"

PREPROCESSOR_FILE = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System\models\random_forest_preprocessor.pkl"

print("Loading movies dataset...")

movies = pd.read_csv(
    MOVIES_FILE
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

links["tmdbId"] = pd.to_numeric(
    links["tmdbId"],
    errors="coerce"
)

links = links.dropna(
    subset=["tmdbId"]
)

links["tmdbId"] = links["tmdbId"].astype(int)

ratings["preferred"] = (
    ratings["rating"] >= 4.0
).astype(int)

ratings = ratings.merge(
    links[["movieId", "tmdbId"]],
    on="movieId",
    how="inner"
)

ratings = ratings.merge(
    movies,
    left_on="tmdbId",
    right_on="id",
    how="inner"
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

data = ratings[
    categorical_features +
    numerical_features +
    ["preferred"]
].copy()

data[categorical_features] = data[
    categorical_features
].fillna("Unknown")

data[numerical_features] = data[
    numerical_features
].fillna(0)

X = data[
    categorical_features +
    numerical_features
]

y = data[
    "preferred"
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)

X = preprocessor.fit_transform(
    X
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

print("\nTraining Random Forest...")

model.fit(
    X_train,
    y_train
)

predictions = model.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    predictions
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)

print("\nRandom Forest Training Complete")

print(
    "\nTraining Samples:",
    X_train.shape[0]
)

print(
    "Testing Samples:",
    X_test.shape[0]
)

print(
    "\nAccuracy:",
    round(accuracy, 4)
)

print(
    "Precision:",
    round(precision, 4)
)

print(
    "Recall:",
    round(recall, 4)
)

joblib.dump(
    model,
    MODEL_FILE
)

joblib.dump(
    preprocessor,
    PREPROCESSOR_FILE
)

print(
    "\nRandom Forest model saved."
)

print(
    "Model:",
    MODEL_FILE
)

print(
    "Preprocessor:",
    PREPROCESSOR_FILE
)