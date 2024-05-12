from flask import Flask, render_template, jsonify, request
import os
import random
import pandas as pd
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

# Load the audio folder path
audio_folder = 'audio/000'

# Load the features and filenames
data = pd.read_csv('audio_features1.csv')
features = data.drop(columns=['filename'])
filenames = data['filename']

# Load the Nearest Neighbors model
model = NearestNeighbors(n_neighbors=5, algorithm='auto', metric='euclidean')
model.fit(features)

@app.route('/')
def index():
    # Get list of random songs from audio folder
    random_songs = random.sample(os.listdir(audio_folder), 10)
    return render_template('1.html', random_songs=random_songs)

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    selected_song = request.form['selected_song']
    selected_song_index = filenames[filenames == selected_song].index[0]
    sample_features = features.iloc[[selected_song_index]]
    distances, indices = model.kneighbors(sample_features)
    
    min_distance = min(distances[0])  # Get the minimum distance
    max_distance = max(distances[0])  # Get the maximum distance
    
    # Ensure the similarity scores are between 10% and 100%
    min_similarity = 0.1
    max_similarity = 1.0
    
    recommendations = [(filenames[i], max(min_similarity, min(max_similarity, (max_distance - distance) / (max_distance - min_distance)))) for distance, i in zip(distances[0], indices[0])]
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)
    recommendations = recommendations[:5]  # Get top 5 recommendations
    print("Recommendations:", recommendations)
    return jsonify(recommendations)

@app.route('/nearest_neighbors', methods=['POST'])
def get_nearest_neighbors():
    selected_song = request.form['selected_song']
    selected_song_index = filenames[filenames == selected_song].index[0]
    sample_features = features.iloc[[selected_song_index]]
    distances, indices = model.kneighbors(sample_features)
    neighbors = [filenames[i] for i in indices[0] if i != selected_song_index]
    print("Nearest Neighbors:", neighbors)
    return jsonify(neighbors[:5])

if __name__ == '__main__':
    app.run(debug=True)
