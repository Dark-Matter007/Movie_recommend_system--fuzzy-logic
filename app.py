from flask import Flask, render_template, request
import os
import csv
import math
from random import shuffle, choice
from pathlib import Path

app = Flask(__name__)

# Global movies dictionary
movies = {}

# Define base directory path
base_dir = Path(r'C:\Users\surig\Desktop\Fuzzy-1\Movie_recommend\ml-latest-small')

# Function to read CSV files
def readCSV(fn):
    lis = []
    file_path = base_dir / fn
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            lis.append(row)
    return lis

# Function to create the movies dictionary
def createMovieDict():
    movieList = [x[:2] for x in readCSV('movies.csv')]
    for i in movieList:
        m = " ".join(i[1].split(" ")[:-1])
        movies[i[0]] = m.lower()

# Function to parse user ratings
def parseUsers():
    userRatings = readCSV('ratings.csv')
    users = {}
    for i in userRatings:
        u = i[0]
        m = movies[i[1]]
        r = float(i[2]) / 5
        if u in users:
            users[u][m] = r
        else:
            users[u] = {m: r}
    return users

# Function to compare similarity between two users
def sim(a, b):
    aMovies = set(a.keys())
    bMovies = set(b.keys())
    both = list(aMovies.intersection(bMovies))
    if len(both) <= 0:
        return 0
    aFuzz = [a[m] for m in both]
    bFuzz = [b[m] for m in both]
    dot_product = sum([aFuzz[i] * bFuzz[i] for i in range(len(aFuzz))])
    magnitude_a = math.sqrt(sum([x**2 for x in aFuzz]))
    magnitude_b = math.sqrt(sum([x**2 for x in bFuzz]))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0
    return dot_product / (magnitude_a * magnitude_b)

# Function to compare ratings
def compareRatings(ratings, user):
    simVal = []
    for k, v in ratings.items():
        simVal.append((k, sim(v, user)))
    simVal.sort(key=lambda x: x[1], reverse=True)
    return simVal[:25]

# Function to get rated movies
def getRatedMovies(ratingList, userId):
    return ratingList[userId].keys()

# Function to suggest movies
def suggestMovies(ratingList, matches, user):
    watchedMovies = set(user.keys())
    suggested = []
    for match in matches:
        suggested += getRatedMovies(ratingList, match[0])
    suggested = set(suggested) - watchedMovies
    return list(suggested)[:15]

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')  # Or your home page template


# Route for recommendations
@app.route('/recommend', methods=['POST'])
def recommend():
    createMovieDict()
    ratings = parseUsers()

    # Get user input
    use_random = request.form.get('random') == 'y'
    userRatings = {}
    if use_random:
        random_user = choice(list(ratings.keys()))
        userRatings = ratings.pop(random_user)
    else:
        movie = request.form['movies'].lower()
        rating = float(request.form['movie_ratings']) / 5
        userRatings[movie] = rating

    # Find matches and suggest movies
    matches = compareRatings(ratings, userRatings)
    suggestedMovies = suggestMovies(ratings, matches, userRatings)

    return render_template('recommendations.html', suggestedMovies=suggestedMovies)

if __name__ == '__main__':
    app.run(debug=True)
