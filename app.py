import os
import json
import requests
import sys
from flask import Flask, render_template, redirect, url_for, session, request
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer import oauth_authorized
from social_network.database.memgraph import Memgraph
from social_network import db_operations
from social_network import dbComms
from social_network import dbTestInfo
from social_network import movieApiController
from social_network import warnings
from social_network import recommender
from social_network.dbModels import User, Movie, Genre
from flask_scss import Scss

app = Flask(__name__)
app.debug = True
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["SECRET_KEY"] = "maxseCretPliz18882"

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#Database
db = Memgraph()

#SCSS
Scss(app, static_dir='static', asset_dir='assets')

# Twitter connector
twitter_bp = make_twitter_blueprint(
	api_key="AckLZqFrceE6E2EctXUF1Bmly",
	api_secret="CJlkvc0xfQYi731uICahGIJ9mrSw7zYYu7S3EmB7CCftkDASSr",
)
app.register_blueprint(twitter_bp, url_prefix="/twitter_login")
# Twitter connection
@app.route("/twitter")
def twitter_login():
	if not twitter.authorized:
		return redirect(url_for("twitter.login"))
	return redirect(url_for("account"))

# FB connector
app.config["FACEBOOK_OAUTH_CLIENT_ID"] = "3468111173224517"
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = "7ea8279bf9d5de409cdf843e58ba0409"
facebook_bp = make_facebook_blueprint(rerequest_declined_permissions=True)
facebook_bp.rerequest_declined_permissions = True
app.register_blueprint(facebook_bp, url_prefix="/login")
# FB connection
def fb_login():
	if not facebook.authorized:
		return redirect(url_for("facebook.login"))
	return redirect(url_for("account"))

#APIs
omdbAPI = "https://www.omdbapi.com/?apikey=65f7361a&"
openLibraryAPI = "http://openlibrary.org/"
openLibraryCoverAPI = "http://covers.openlibrary.org/"

# App
@app.before_request
def handleSession():
	if "userEmail" in session:
		authed = True
		userEmail = session["userEmail"]
	else:
		authed = False
	if twitter.authorized:
		resp = twitter.get(
			"account/verify_credentials.json", params={"include_email": "true"}
		)
		if resp.ok:
			authed = True
			resp_json = resp.json()
			userName = resp_json["screen_name"]
			userEmail = resp_json["email"]
			userAvatar = resp_json["profile_image_url"]
	elif facebook.authorized:
		resp = facebook.get("/me?fields=name,email")
		if resp.ok and resp.text:
			authed = True
			resp_json = resp.json()
			userName = resp_json["name"]
			userEmail = resp_json["email"]
			userAvatar = resp_json["picture"]["data"]["url"]
	if authed:
		res = dbComms.userCheck(db, userEmail)
		if res == False:
			dbComms.userCreate(db, userName, userEmail,userAvatar)
		if "userName" not in session or "userEmail" not in session:
			session["userName"] = dbComms.userGetByEmail(db, userEmail).username
			session["userEmail"] = userEmail
	if "warning" in session:
		session["warningMsg"] = session["warning"]
		session["warning"] = warnings.noWarning()
	else:
		session["warningMsg"] = warnings.noWarning()
		session["warning"] = warnings.noWarning()

# Route for search movies page
@app.route('/find')
def find():
	# only movies rated in the last week (604800 == seconds in a week)
	lst = dbComms.movieGetRecentlyRated(db, 604800)
	return render_template("findMovies.html", list = lst)

# Route for movie detail display page
@app.route('/movie/<imdb_id>')
def movie(imdb_id):
	omdbAPIcall = omdbAPI + "i=" + imdb_id
	resp = requests.get(omdbAPIcall)
	if resp.ok:
		resp_content = resp.content
		resp_json = json.loads(resp_content.decode("utf-8"))
		return render_template("movieDisplay.html", movie_data_json=resp_json)
	else:
		return "<h1>Request failed</h1>"

@app.route('/movie/<imdb_id>/like')
def movieLike(imdb_id):
	if "userEmail" in session:
		rating = dbComms.userGetRating(db,session["userEmail"],imdb_id)
		if rating is not None:
			if rating == 0:
				dbComms.userRateMovie(db,session["userEmail"],imdb_id,1)
			else:
				dbComms.userUnRateMovie(db,session["userEmail"],imdb_id)
		else:
			dbComms.userRateMovie(db,session["userEmail"],imdb_id,1)
	return redirect("/movie/{0}".format(imdb_id))

@app.route('/movie/<imdb_id>/dislike')
def movieDislike(imdb_id):
	if "userEmail" in session:
		rating = dbComms.userGetRating(db,session["userEmail"],imdb_id)
		if rating is not None:
			if rating == 1:
				dbComms.userRateMovie(db,session["userEmail"],imdb_id,0)
			else:
				dbComms.userUnRateMovie(db,session["userEmail"],imdb_id)
		else:
			dbComms.userRateMovie(db,session["userEmail"],imdb_id,0)
	return redirect("/movie/{0}".format(imdb_id))

@app.route('/movie/<imdb_id>/favorite')
def movieFavorite(imdb_id):
	if "userEmail" in session:
		if (dbComms.userCheckFavorited(db,session["userEmail"],imdb_id)):
			dbComms.userUnFavoritesMovie(db,session["userEmail"],imdb_id)
		else:
			dbComms.userFavoritesMovie(db,session["userEmail"],imdb_id)
	return redirect("/movie/{0}".format(imdb_id))

# Route for movie roulette page
@app.route('/roulette')
def roulette():
	recommendations = []
	if "userEmail" in session:
		current_user_id = dbComms.get_user_id_by_email(db, session["userEmail"])
		recommendations = recommender.get_recommendations(db, current_user_id)
	# if the number of recommendations is zero, just recommend trending/popular movies
	if len(recommendations) == 0:
		recommendations = dbComms.movieGetRecentlyRated(db, 604800)
	# return render_template("movieList.html", list=recommendations)
	return render_template("movieDiscover.html", list=recommendations)

# Route for user profile page
@app.route('/profile')
def profile():
	return render_template("userProfile.html")

# Route for user liked list page
@app.route('/liked')
def liked():
	return render_template("likedList.html")

# Route for user disliked list page
@app.route('/dislike')
def dislike():
	return render_template("dislikedList.html")

# Route for user bookmarked list page
@app.route('/bookmarked')
def booked():
	return render_template("bookmarkedList.html")

# Route for login page
@app.route('/login')
def login():
	return render_template("login.html")

@app.route('/fb_login')
def fb_login():
	if not facebook.authorized:
		return redirect(url_for("facebook.login"))
	resp = facebook.get("/me?fields=id,name,email,picture,birthday")
	if resp.ok and resp.text:
		resp_json = resp.json()
		user_id = resp_json["id"]
		user_name = resp_json["name"]
		user_mail = resp_json["email"]
		user_picture = resp_json["picture"]["data"]["url"]
		user_node = db_operations.get_user_by_fb_id(db, user_id)
		if user_node is None:
			db_operations.add_user(db, user_id, user_name, user_mail, user_picture)
		session['userid'] = user_id
		return redirect(url_for("find"))
	else:
		return "<h1>Request failed</h1>"

@app.route('/movie_api/<movie_title>')
def movie_api(movie_title):
	omdbAPIcall = omdbAPI + "t=" + movie_title
	resp = requests.get(omdbAPIcall)
	if resp.ok:
		resp_content = resp.content
		resp_json = json.loads(resp_content.decode("utf-8"))
		movie_id = resp_json["imdbID"]
		movie_title = resp_json["Title"]
		movie_year = resp_json["Year"]
		movie_director = resp_json["Director"]
		movie_poster = resp_json["Poster"]
		movie_node = db_operations.get_movie_by_imdb_id(db, movie_id)
		if movie_node is None:
			db_operations.add_movie(db, movie_id, movie_title, movie_year, movie_director, movie_poster)
			if 'userid' in session:
				db_operations.connect_user_to_movie(db, session['userid'], movie_id)
		return redirect(url_for("index"))
	else:
		return "<h1>Request failed</h1>"

@app.route("/")
@app.route("/index")
def index():
	return render_template("index.html", warning=session["warningMsg"])


@app.route("/logout")
def logout():
	session.clear()
	session["warning"] = warnings.noWarning()
	return redirect(url_for("index"))


@app.route("/account", methods=["POST", "GET"])
def account():
	if twitter.authorized == False:
		session["warning"] = warnings.noLogin()
		return redirect(url_for("index"))
	if request.method == "POST":
		if request.form["nameInput"] != "":
			# Change name and session info
			session["userName"] = dbComms.userChangeName(
				db, session["userEmail"], request.form["nameInput"]
			)
			return redirect(url_for("account"))
	return render_template("account.html", user=session["userName"])


# Movies
# TMDB
@app.route("/movies", methods=["POST", "GET"])
def moviesList():
	if twitter.authorized == False:
		session["warning"] = warnings.noLogin()
		return redirect(url_for("index"))
	# Set filter
	filtered = ""
	if request.method == "POST":
		retFilt = dbComms.genreGetAll(db)
		if "genre" in request.form:
			filtered = request.form["genre"]
			ret = dbComms.movieGetByGenre(db, filtered)
		else:
			ret = dbComms.movieGetAll(db)
		return render_template(
			"movieList.html", list=ret, filter=retFilt, filtered=filtered
		)
	else:
		ret = dbComms.movieGetAll(db)
		retFilt = dbComms.genreGetAll(db)
		return render_template("movieList.html", list=ret, filter=retFilt)


@app.route("/movies/add/tmdb/<movieId>")
def tmdbAdd(movieId):
	movieApiController.apiTmdbAddById(db, movieId)
	return redirect(url_for("moviesList"))


@app.route("/movies/add/omdb", defaults={"movieTitle": "Die Hard"})
@app.route("/movies/add/omdb/<movieTitle>")
def omdbAdd(movieTitle):
	movieApiController.apiOmdbAddByTitle(db, movieTitle)
	return redirect(url_for("moviesList"))


# Default vraca Die Hard
@app.route("/movies/rating", defaults={"movieId": "tt0095016"})
@app.route("/movies/rating/<movieId>")
def getRating(movieId):
	return dbComms.movieGetRating(db, movieId)


@app.route("/movies/favorite/<movieId>")
def setFavoriteMovie(movieId=0):
	if twitter.authorized == False:
		session["warning"] = warnings.noLogin()
		return redirect(url_for("index"))
	dbComms.userFavoritesMovie(db, session["userEmail"], movieId)
	return redirect(url_for("moviesList"))


@app.route("/movies/un-favorite/<movieId>")
def removeFavoriteMovie(movieId=0):
	if twitter.authorized == False:
		session["warning"] = warnings.noLogin()
		return redirect(url_for("index"))
	dbComms.userUnFavoritesMovie(db, session["userEmail"], movieId)
	return redirect(url_for("favoriteMoviesList"))


@app.route("/movies/favorites")
def favoriteMoviesList():
	if twitter.authorized == False:
		session["warning"] = warnings.noLogin()
		return redirect(url_for("index"))
	ret = dbComms.userGetAllFavorited(db, session["userEmail"])
	return render_template("movieFavs.html", list=ret)


# Test method
@app.route("/movies/favoritesX")
def favoriteMoviesListLimited():
	if twitter.authorized == False:
		session["warning"] = warnings.noLogin()
		return redirect(url_for("index"))
	ret = dbComms.movieGetFavoritedLimited(db, session["userEmail"])
	return render_template("movieFavs.html", list=ret)


@app.route("/movies/like")
def testRate():
	ret = dbComms.movieGetRecentlyRated(db)
	return render_template("movieList.html", list=ret)

@app.route("/srch")
def search():
	ret = movieApiController.apiTmdbSearch(db,"Lord of the Rings")
	return render_template("movieList.html", list=ret)

@app.route("/likeShrek")
def shrekify():
	if twitter.authorized == False:
		session["warning"] = warnings.noLogin()
		return redirect(url_for("index"))
	user = session["userEmail"]
	likes = ["tt0126029", "tt0126029", "tt0385700", "tt0198781"]
	favorites = ["tt0126029"]  # Shrek
	dislikes = ["tt0077766"]  # Jaws 2
	for movie in likes:
		dbComms.userRateMovie(db, user, movie, 1)
	for movie in dislikes:
		dbComms.userRateMovie(db, user, movie, 0)
	for movie in favorites:
		dbComms.userFavoritesMovie(db, user, movie)
	return redirect(url_for("index"))


# Test DB controls
@app.route("/db/prg")
def purge():
	purgeDatabase()
	session.clear()
	session["warning"] = warnings.noWarning()
	return redirect("/")


def purgeDatabase():
	qry = "MATCH (node) DETACH DELETE node"
	db.execute_query(qry)
	return


# TODO
@app.route("/db/init")
def initDatabase():
	dbTestInfo.addOmdbMovies(db)
	dbTestInfo.addTmdbMovies(db)
	dbTestInfo.addTestUsers(db)
	dbTestInfo.addTestLikes(db)
	dbTestInfo.addRandomVotes(db)
	return redirect("/")


# Main
if __name__ == "__main__":
	app.run(debug=True)
