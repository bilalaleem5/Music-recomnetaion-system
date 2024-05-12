from flask import Flask, render_template, request, jsonify
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

# Load the reduced features from the CSV file
features_df = pd.read_csv('audio_features1.csv')

# Separate the filename column
filenames = features_df['filename']
features = features_df.drop(columns=['filename'])

# Normalize features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Initialize ANN model for nearest neighbors
n_neighbors = 5  # Number of neighbors to consider
ann_model = NearestNeighbors(n_neighbors=n_neighbors, algorithm='auto', metric='euclidean')
ann_model.fit(scaled_features)

@app.route('/')
def index():
    # Randomly select 10 songs
    random_songs = np.random.choice(filenames, 10, replace=False)
    return render_template('1.html', random_songs=random_songs)

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    selected_song = request.form['selected_song']
    selected_index = filenames[filenames == selected_song].index[0]

    # Calculate similarities with the selected audio
    selected_features = scaled_features[selected_index]
    similarities = cosine_similarity([selected_features], scaled_features)[0]

    # Get indices of top 5 similar audio files
    top_indices = np.argsort(similarities)[-6:-1][::-1]  # Top 5 indices excluding the selected audio itself

    # Prepare recommendations
    recommendations = []
    for idx in top_indices:
        recommendation = (filenames.iloc[idx], similarities[idx])
        recommendations.append(recommendation)

    return jsonify(recommendations)

@app.route('/nearest_neighbors', methods=['POST'])
def get_nearest_neighbors():
    selected_song = request.form['selected_song']
    selected_index = filenames[filenames == selected_song].index[0]

    # Find nearest neighbors for the selected audio
    distances, indices = ann_model.kneighbors([scaled_features[selected_index]])

    # Get the filenames of nearest neighbors
    nearest_neighbor_filenames = filenames.iloc[indices[0]].tolist()
    return jsonify(nearest_neighbor_filenames)

if __name__ == '__main__':
    app.run(debug=True)
