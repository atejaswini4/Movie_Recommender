
import pandas as pd

from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

from sklearn.cluster import KMeans


# ============================================================
# FILE PATH
# ============================================================

CLEANED_FILE = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System\data\cleaned_movies.csv"


# ============================================================
# LOAD CLEANED DATA
# ============================================================

movies = pd.read_csv(CLEANED_FILE)


print("\n========================================")
print("        FEATURE ENGINEERING")
print("========================================")

print("\nDataset Shape:")
print(movies.shape)


# ============================================================
# SELECT FEATURES
# ============================================================

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


# ============================================================
# HANDLE MISSING VALUES
# ============================================================

movies[categorical_features] = movies[
    categorical_features
].fillna("unknown")

movies[numerical_features] = movies[
    numerical_features
].fillna(0)


# ============================================================
# ONE-HOT ENCODE CATEGORICAL FEATURES
# ============================================================

encoder = OneHotEncoder(
    handle_unknown="ignore"
)

categorical_data = encoder.fit_transform(
    movies[categorical_features]
)


# ============================================================
# SCALE NUMERICAL FEATURES
# ============================================================

scaler = StandardScaler()

numerical_data = scaler.fit_transform(
    movies[numerical_features]
)


# ============================================================
# COMBINE FEATURES
# ============================================================

from scipy.sparse import hstack

feature_matrix = hstack(
    [
        categorical_data,
        numerical_data
    ]
)


print("\nCategorical Features:")
print(categorical_features)

print("\nNumerical Features:")
print(numerical_features)

print("\nFeature Matrix Shape:")
print(feature_matrix.shape)


# ============================================================
# CREATE K-MEANS MODEL
# ============================================================

kmeans = KMeans(
    n_clusters=10,
    random_state=42,
    n_init=10
)


# ============================================================
# TRAIN K-MEANS
# ============================================================

print("\nTraining K-Means...")

movies["cluster"] = kmeans.fit_predict(
    feature_matrix
)


print("K-Means training completed.")


# ============================================================
# DISPLAY CLUSTERS
# ============================================================

print("\n========================================")
print("        CLUSTER RESULTS")
print("========================================")

print(
    movies[
        [
            "title",
            "genres",
            "original_language",
            "cluster"
        ]
    ].head(20)
)


# ============================================================
# CLUSTER COUNTS
# ============================================================

print("\nMovies in Each Cluster:")

print(
    movies["cluster"].value_counts().sort_index()
)


# ============================================================
# SAVE CLUSTERED DATA
# ============================================================

OUTPUT_FILE = r"C:\Users\allam_cqqjtot\OneDrive\Desktop\Movie-Recommendation-System\Movie-Recommendation-System\data\clustered_movies.csv"

movies.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\nClustered dataset saved to:")
print(OUTPUT_FILE)

