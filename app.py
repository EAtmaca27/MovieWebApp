import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from models import db, User
from data_manager import DataManager

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.urandom(24)

db.init_app(app)
data_manager = DataManager()

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", users=users)


@app.route("/users/add", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        name = request.form.get("name").strip()
        existing = User.query.filter(db.func.lower(User.name) == name.lower()).first()
        if existing:
            flash(f"A user named '{name}' already exists.", "error")
            return render_template("add_user.html")
        data_manager.create_user(name)
        flash(f"User '{name}' was created successfully!", "success")
        return redirect(url_for("index"))
    return render_template("add_user.html")


@app.route("/users/<int:user_id>/movies")
def user_movies(user_id):
    movies = data_manager.get_movies(user_id)
    user = User.query.get_or_404(user_id)
    return render_template("user_movies.html", user=user, movies=movies)


@app.route("/users/<int:user_id>/movies/add", methods=["GET", "POST"])
def add_movie(user_id):
    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year") or None
        movie = data_manager.add_movie(title, user_id, year)
        if movie is None:
            flash(f"Movie '{title}' not found. Check the title or your API key.", "error")
            return render_template("add_movie.html", user_id=user_id)
        flash(f"'{movie.name}' was added successfully!", "success")
        return redirect(url_for("user_movies", user_id=user_id))
    return render_template("add_movie.html", user_id=user_id)


@app.route("/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id, movie_id):
    name = request.form.get("name").strip()
    data_manager.update_movie(movie_id, name)
    flash(f"Movie updated successfully!", "success")
    return redirect(url_for("user_movies", user_id=user_id))


@app.route("/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(movie_id)
    flash("Movie deleted.", "success")
    return redirect(url_for("user_movies", user_id=user_id))


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    data_manager.delete_user(user_id)
    flash("User deleted.", "success")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
