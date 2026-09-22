# 🎬 Movie Recommendation System

A Machine Learning based Movie Recommendation System that recommends similar movies based on a movie selected by the user.

The system combines **K-Means Clustering, K-Nearest Neighbors (KNN), and Random Forest** to generate and rank movie recommendations. Movie posters are retrieved using the **TMDB API** and displayed through an interactive **Streamlit** web application.

## 🚀 Features

- Select a movie from the available dataset
- Filter movies by language
- Generate 5 to 10 movie recommendations
- Group similar movies using K-Means Clustering
- Find similar movies using KNN
- Calculate preference scores using Random Forest
- Rank recommendations using a combined score
- Display movie posters using TMDB
- Display movie ratings, release years, genres, and similarity scores
- Interactive Streamlit user interface

## 🧠 Machine Learning Algorithms

### 1. K-Means Clustering

K-Means Clustering groups movies with similar characteristics into clusters.

The clustering process uses features such as:

- Genres
- Original language
- Popularity
- Vote average
- Vote count
- Release year
- User rating statistics

When a user selects a movie, the system identifies its cluster and uses movies from the same cluster as recommendation candidates.

### 2. K-Nearest Neighbors

KNN is used to find movies that are similar to the selected movie.

The system creates feature vectors for movies and uses **cosine distance** to identify the nearest movies within the selected cluster.

The similarity score is calculated from the distance between the selected movie and candidate movies.

### 3. Random Forest

Random Forest is used to calculate a movie preference score.

The model is trained using user ratings:

- Rating >= 4.0 → Preferred
- Rating < 4.0 → Not Preferred

The Random Forest model uses:

- Genres
- Original language
- Popularity
- Vote average
- Vote count
- Release year

The model produces a preference probability for each recommended movie.

### 🔢 Final Recommendation Score

The final recommendation score combines KNN similarity and the Random Forest preference score.

```text
Final Score =
0.7 × Similarity
+
0.3 × Preference Score