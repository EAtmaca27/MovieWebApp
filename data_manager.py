import os
import requests

from dotenv import load_dotenv
from models import db, User, Movie

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

class DataManager:
    def create_user(self, name):
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return user


    def get_movies(self, user_id):
        return Movie.query.filter_by(user_id=user_id).all()


    def add_movie(self, title, user_id):
        api_key = os.getenv("OMDB_API_KEY")
        response = requests.get(f"https://www.omdbapi.com/?t={title}&apikey={api_key}")
        data = response.json()
        if data.get("Response") == "False":
            return None
        movie = Movie(
            name=data["Title"],
            director=data["Director"],
            year=int(data["Year"][:4]),
            url=data["Poster"],
            user_id=user_id
        )
        db.session.add(movie)
        db.session.commit()
        return movie


    def update_movie(self, movie_id, new_title):
        movie = Movie.query.get(movie_id)
        if movie:
            for key, value in new_title.items():
                setattr(movie, key, value)


    def delete_movie(self, movie_id):
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()