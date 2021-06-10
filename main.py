from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

URL_DATABASE = "https://api.themoviedb.org/3/search/movie"
API_KEY = "Your_api_key"
DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
DB_MOVIE_INFO = "https://api.themoviedb.org/3/movie"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

db.create_all()


class EditMovieForm(FlaskForm):
    rating = StringField(label="Your Rating Out of 10 e.g. 6.5", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    review = StringField(label="Your Review", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    submit = SubmitField("Done")


class FindMovieForm(FlaskForm):
    new_movie = StringField(label="Movie Title", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    submit = SubmitField("Add movie")


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = EditMovieForm()
    movie_id = request.args.get("id")
    print(movie_id)
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_to_find = form.new_movie.data
        response = requests.get(URL_DATABASE, params={"api_key": API_KEY, "query": movie_to_find}).json()
        data = response["results"]
        return render_template("select.html", options=data)

    return render_template("add.html", form=form)


@app.route("/find")
def find_movie():
    movie_id = request.args.get("id")
    if movie_id:
        movie_url = f"{DB_MOVIE_INFO}/{movie_id}"
        response = requests.get(movie_url, params={"api_key": API_KEY})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{DB_IMAGE_URL}{data['poster_path']}",
            description=data['overview']
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)
