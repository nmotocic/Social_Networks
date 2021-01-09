import os
import json
import requests
import sys
from flask import Flask, render_template, redirect, url_for, session, request
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.contrib.github import make_github_blueprint, github
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
	if not facebook.authorized and not twitter.authorized:
		return redirect(url_for("twitter.login"))
	return redirect(url_for("profile"))

# FB connector
# app.config["FACEBOOK_OAUTH_CLIENT_ID"] = "3468111173224517"
# app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = "7ea8279bf9d5de409cdf843e58ba0409"
app.config["FACEBOOK_OAUTH_CLIENT_ID"] = "141269584858"
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = "f9343613c08bce71b9540819a11478fd"
facebook_bp = make_facebook_blueprint(rerequest_declined_permissions=True)
facebook_bp.rerequest_declined_permissions = True
app.register_blueprint(facebook_bp, url_prefix="/login")
# FB connection
@app.route("/facebook")
def fb_login():
	if not facebook.authorized and not twitter.authorized:
		return redirect(url_for("facebook.login"))
	return redirect(url_for("profile"))

#GitHub connector
github_blueprint = make_github_blueprint(client_id="3fd3ed5da5ba6866d500",client_secret="3d9bb861579f18533b71d261628b195205e67388")
app.register_blueprint(github_blueprint, url_prefix='/github_login')

@app.route("/github")
def github_login():
	if not github.authorized:
		return redirect(url_for('github.login'))
	return redirect(url_for("profile"))

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
	userAvatar=""
	if twitter.authorized and not authed:
		resp = twitter.get(
			"account/verify_credentials.json", params={"include_email": "true"}
		)
		if resp.ok:
			authed = True
			resp_json = resp.json()
			userName = resp_json["screen_name"]
			userEmail = resp_json["email"]
			userAvatar = resp_json["profile_image_url"]
	elif facebook.authorized and not authed:
		resp = facebook.get("/me?fields=id,name,email,picture,birthday")
		if resp.ok and resp.text:
			authed = True
			resp_json = resp.json()
			userName = resp_json["name"]
			userEmail = ""
			if "email" in resp_json:
				userEmail = resp_json["email"]
			userAvatar = resp_json["picture"]["data"]["url"]
	elif github.authorized and not authed:
		resp = github.get('/user')
		if resp.ok:
			authed=True
			resp_json = resp.json()
			userName = resp_json["login"]
			userEmail = resp_json["email"]
			userAvatar = resp_json["avatar_url"]
	if authed and userEmail:
		res = dbComms.userCheck(db, userEmail)
		if res == False:
			dbComms.userCreate(db, userName, userEmail,userAvatar)
		if "userName" not in session or "userEmail" not in session:
			user = dbComms.userGetByEmail(db,userEmail)
			session["userName"] = user.username
			session["userEmail"] = userEmail
			session["userAvatar"] = user.avatarUrl
	if "warning" in session:
		session["warningMsg"] = session["warning"]
		session["warning"] = warnings.noWarning()
	else:
		session["warningMsg"] = warnings.noWarning()
		session["warning"] = warnings.noWarning()

@app.context_processor
def inject_user():
	if "userAvatar" in session and "userName" in session:
		return dict(sessionData={"avatar":session["userAvatar"],"username":session["userName"]})
	else:
		return dict(sessionData={"avatar":"","username":"Guest"})

# Route for search movies page
@app.route('/find')
def find():
	# only movies rated in the last week (604800 == seconds in a week)
	lst = dbComms.movieGetRecentlyRated(db, 604800)
	return render_template("findMovies.html", list = lst, list_title="Trending Movies:")

# Route for movie detail display page
@app.route('/movie/<imdb_id>')
def movie(imdb_id):
	omdbAPIcall = omdbAPI + "i=" + imdb_id
	resp = requests.get(omdbAPIcall)
	# only ratings in the last week (604800 == seconds in a week)
	ratingDictLatest = dbComms.movieGetUserRatings(db, imdb_id, lastSeconds=604800)
	# all ratings
	ratingDictOverall = dbComms.movieGetUserRatings(db, imdb_id)
	if resp.ok:
		resp_content = resp.content
		resp_json = json.loads(resp_content.decode("utf-8"))
		buttonStatus=["movie-interaction-button","movie-interaction-button","movie-interaction-button"]
		if "userEmail" in session:
			email = session["userEmail"]
			rating = dbComms.userGetRating(db,email,imdb_id)
			if rating == 0:
				buttonStatus[1]="movie-interaction-button active"
			elif rating == 1:
				buttonStatus[0]="movie-interaction-button active"
			if dbComms.userCheckFavorited(db,email,imdb_id):
				buttonStatus[2]="movie-interaction-button active"
			#return buttonStatus[0]
		return render_template("movieDisplay.html", movie_data_json=resp_json, buttonStatus=buttonStatus, ratingsLatest=ratingDictLatest, ratingsOverall=ratingDictOverall)
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
	if len(recommendations) == 0:
		return redirect("/")
	return render_template("movieDiscover.html", list=recommendations)

# Route for user profile page
@app.route('/profile')
def profile():
	if "userEmail" in session:
		email = session["userEmail"]
		usr = dbComms.userGetByEmail(db,email)
		positive = dbComms.userGetPositiveRatedMovies(db,email)
		negative = dbComms.userGetNegativeRatedMovies(db,email)
		favorite = dbComms.userGetAllFavorited(db,email)
		return render_template("userProfile.html",user=usr,
			positive=len(positive),negative=len(negative),favorite=len(favorite))
	return redirect("/")

# Route for user liked list page
@app.route('/liked')
def liked():
	if "userEmail" in session:
		email = session["userEmail"]
		movieList = dbComms.userGetPositiveRatedMovies(db,email)
		return render_template("likedList.html",movies=movieList)
	return redirect("/")

# Route for user disliked list page
@app.route('/dislike')
def dislike():
	if "userEmail" in session:
		email = session["userEmail"]
		movieList = dbComms.userGetNegativeRatedMovies(db,email)
		return render_template("dislikedList.html",movies=movieList)
	return redirect("/")

# Route for user bookmarked list page
@app.route('/bookmarked')
def booked():
	if "userEmail" in session:
		email = session["userEmail"]
		movieList = dbComms.userGetAllFavorited(db,email)
		return render_template("bookmarkedList.html",movies=movieList)
	return redirect("/")

# Route for login page
@app.route('/login')
def login():
	return render_template("login.html")
"""
@app.route('/fb_login')
def fb_login():
	if not facebook.authorized:
		return redirect(url_for("facebook.login"))
	resp = facebook.get("/me?fields=id,name,email,picture,location")
	if resp.ok and resp.text:
		resp_json = resp.json()
		user_id = resp_json["id"]
		user_name = resp_json["name"]
		userEmail = ""
		if "email" in resp_json:
			user_mail = resp_json["email"]
		user_picture = resp_json["picture"]["data"]["url"]
		user_location = resp_json["location"]["name"].split(", ")
		user_country = user_location[-1]
		user_node = db_operations.get_user_by_fb_id(db, user_id)
		if user_node is None and userEmail:
			db_operations.add_user(db, user_id, user_name, user_mail, user_picture)
		session['userid'] = user_id
		return redirect(url_for("find"))
	else:
		return "<h1>Request failed</h1>"
"""
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
	if "userEmail" in session:
		return redirect(url_for("profile"))
	return render_template("login.html", warning=session["warningMsg"])


@app.route("/logout")
def logout():
	session.clear()
	session["warning"] = warnings.noWarning()
	return redirect(url_for("index"))

@app.route("/explore/<genre>/<page>")
def explore(genre, page):
	limit=10
	try:
		page=int(page)
	except:
		return redirect("/explore/all/0")
	genreList = dbComms.genreGetAll(db)
	if(genre=="all"):
		movieList = dbComms.movieGetAll(db,page=page,limit=limit)
	else:
		movieList = dbComms.movieGetByGenre(db,genre,page=page,limit=limit)
	if genre == "all":
		title = "All Movies"
	else:
		title = genre.capitalize() + " Movies"
	if len(movieList)<limit:
		max_page=page
	else:
		max_page=page+1
	return render_template("databaseExplore.html", current_genre=genre, current_title=title, current_page=page, max_page=max_page, genreList=genreList, movieList=movieList)

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

@app.route("/srch/<srchString>")
def search(srchString):
	ret = movieApiController.apiTmdbSearch(db, srchString)
	return render_template("findMovies.html", list=ret, list_title="Search Results For: '" + srchString + "'")

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

@app.route("/test")
def test():
	resp = github.get('/user')
	return resp.json()

# TODO
@app.route("/db/init")
def initDatabase():
	dbTestInfo.addOmdbMovies(db)
	dbTestInfo.addTmdbMovies(db)
	#dbTestInfo.addTestUsers(db)
	#dbTestInfo.addTestLikes(db)
	#dbTestInfo.addRandomVotes(db)
	dbTestInfo.addPrefUsers(db)
	dbTestInfo.addAllPrefVotes(db)
	return redirect("/")

@app.route("/db/rand")
def initRandom():
	#dbTestInfo.addOmdbMovies(db)
	#dbTestInfo.addTmdbMovies(db)
	dbTestInfo.addTestUsers(db)
	dbTestInfo.addTestLikes(db)
	dbTestInfo.addRandomVotes(db)
	return redirect("/")

# Main
if __name__ == "__main__":
	app.run(debug=True)
