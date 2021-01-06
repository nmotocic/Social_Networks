from flask import Flask, render_template , redirect , url_for, session, request
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer import oauth_authorized
from social_network.database.memgraph import Memgraph
from social_network import dbComms
from social_network import dbTestInfo
from social_network import movieApiController
from social_network import warnings
from social_network.dbModels import User,Movie,Genre
from flask_scss import Scss
import os
import requests
import json

#App settings 
app = Flask(__name__)
#Scss(app)
app.config['SECRET_KEY'] = 'maxseCretPliz18882'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#Database
#Zvati svaki put prije pristupa bazi?
db = Memgraph()

#Twitter connector
twitter_bp = make_twitter_blueprint(api_key='AckLZqFrceE6E2EctXUF1Bmly' , api_secret='CJlkvc0xfQYi731uICahGIJ9mrSw7zYYu7S3EmB7CCftkDASSr')
app.register_blueprint(twitter_bp, url_prefix='/twitter_login')
#Twitter connection
@app.route('/twitter')
def twitter_login():
	if not twitter.authorized:
		return redirect(url_for('twitter.login'))
	return redirect(url_for('account'))
#FB connector
app.config['FACEBOOK_OAUTH_CLIENT_ID'] = ''
app.config['FACEBOOK_OAUTH_CLIENT_SECRET'] = ''
facebook_bp = make_facebook_blueprint(rerequest_declined_permissions=True)
facebook_bp.rerequest_declined_permissions = True
app.register_blueprint(facebook_bp, url_prefix="/login")
#FB connection
def fb_login():
	if not facebook.authorized:
		return redirect(url_for("facebook.login"))
	return redirect(url_for('account'))


#App
@app.before_request
def handleSession():
	if "userEmail" in session:
		authed = True
	else:
		authed = False
	if twitter.authorized:
		resp = twitter.get("account/verify_credentials.json", params={"include_email" : "true"})
		if resp.ok:
			authed = True
			resp_json = resp.json()
			userName = resp_json["screen_name"]
			userEmail = resp_json["email"]
	elif facebook.authorized:
		resp = facebook.get("/me?fields=name,email")
		if resp.ok and reps.text:
			authed = True
			resp_json = resp.json()
			userName = resp_json["name"]
			userEmail = resp_json["email"]
	if authed:
		res = dbComms.userCheck(db,userEmail)
		if  res==False:
			dbComms.userCreate(db,userName,userEmail)
		if "userName" not in session or "userEmail" not in session:
			session["userName"] = dbComms.userGetByEmail(db,userEmail).username
			session["userEmail"] = userEmail		
	if("warning" in session):
		session["warningMsg"]=session["warning"]
		session["warning"]=warnings.noWarning()
	else:
		session["warningMsg"]=warnings.noWarning()
		session["warning"]=warnings.noWarning()


@app.route('/')
@app.route('/index')
def index():
	return render_template("index.html", warning=session["warningMsg"])

@app.route('/logout')
def logout():
	session.clear()
	session["warning"]=warnings.noWarning()
	return redirect(url_for('index'))

@app.route('/account', methods=["POST","GET"])
def account():
	if(twitter.authorized==False):
		session["warning"]=warnings.noLogin()
		return redirect(url_for('index'))
	if request.method == "POST":
		if(request.form["nameInput"]!=""):
			#Change name and session info
			session["userName"] = dbComms.userChangeName(db,session["userEmail"],request.form["nameInput"])
			return redirect(url_for('account'))
	return render_template("account.html",user=session["userName"])

#Movies
#TMDB
@app.route('/movies', methods=["POST","GET"])
def moviesList():
	if(twitter.authorized==False):
		session["warning"]=warnings.noLogin()
		return redirect(url_for('index'))
	#Set filter
	filtered=""
	if request.method == "POST":
		retFilt = dbComms.genreGetAll(db)
		if("genre" in request.form):
			filtered=request.form["genre"]
			ret = dbComms.movieGetByGenre(db,filtered)
		else:
			ret = dbComms.movieGetAll(db)
		return render_template("movieList.html", list=ret, filter=retFilt, filtered=filtered)		
	else:
		ret = dbComms.movieGetAll(db)
		retFilt = dbComms.genreGetAll(db)
		return render_template("movieList.html", list=ret, filter=retFilt)

@app.route('/movies/add/tmdb/<movieId>')
def tmdbAdd(movieId):
	movieApiController.apiTmdbAddById(db,movieId)
	return redirect(url_for('moviesList'))

@app.route('/movies/add/omdb', defaults={"movieTitle" : "Die Hard"})
@app.route('/movies/add/omdb/<movieTitle>')
def omdbAdd(movieTitle):
	movieApiController.apiOmdbAddByTitle(db,movieTitle)
	return redirect(url_for('moviesList'))

#Default vraca Die Hard
@app.route('/movies/rating', defaults={"movieId":"tt0095016"})
@app.route('/movies/rating/<movieId>')
def getRating(movieId):
	return dbComms.movieGetRating(db,movieId)


@app.route('/movies/favorite/<movieId>')
def setFavoriteMovie(movieId=0):
	if(twitter.authorized==False):
		session["warning"]=warnings.noLogin()
		return redirect(url_for('index'))
	dbComms.userFavoritesMovie(db,session["userEmail"],movieId)
	return redirect(url_for('moviesList'))

@app.route('/movies/un-favorite/<movieId>')
def removeFavoriteMovie(movieId=0):
	if(twitter.authorized==False):
		session["warning"]=warnings.noLogin()
		return redirect(url_for('index'))
	dbComms.userUnFavoritesMovie(db,session["userEmail"],movieId)
	return redirect(url_for('favoriteMoviesList'))

@app.route('/movies/favorites')
def favoriteMoviesList():
	if(twitter.authorized==False):
		session["warning"]=warnings.noLogin()
		return redirect(url_for('index'))
	ret = dbComms.movieGetAllFavorited(db,session["userEmail"])
	return render_template("movieFavs.html", list=ret)

#Test method
@app.route('/movies/favoritesX')
def favoriteMoviesListLimited():
	if(twitter.authorized==False):
		session["warning"]=warnings.noLogin()
		return redirect(url_for('index'))
	ret = dbComms.movieGetFavoritedLimited(db,session["userEmail"])
	return render_template("movieFavs.html", list=ret)

@app.route('/movies/like')
def testRate():
	ret = dbComms.movieGetRecentlyRated(db)
	return render_template("movieFavs.html", list=ret);

#Test DB controls
@app.route('/db/prg')
def purge():
	purgeDatabase()
	session.clear()
	session["warning"]=warnings.noWarning()
	return redirect("/")

def purgeDatabase():
	qry = 'MATCH (node) DETACH DELETE node'
	db.execute_query(qry)
	return

#TODO
@app.route('/db/init')
def initDatabase():
	dbTestInfo.addOmdbMovies(db)
	dbTestInfo.addTmdbMovies(db)
	dbTestInfo.addTestUsers(db)
	dbTestInfo.addTestLikes(db)
	dbTestInfo.addRandomVotes(db)
	return redirect("/")

#Main
if __name__ == '__main__':
	app.run(debug=True)
