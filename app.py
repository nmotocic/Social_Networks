from flask import Flask, render_template , redirect , url_for, session, request
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer import oauth_authorized
from social_network.database.memgraph import Memgraph
from social_network import dbComms
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
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
#FB connection
def fb_login():
	if not facebook.authorized:
		return redirect(url_for("facebook.login"))
	return redirect(url_for('account'))

#TMDB - API
#https://api.themoviedb.org/3/movie/550?api_key=182afe8c78e3f9451e21950e7b29053e
#base+request+key+params
tmdbBase = "https://api.themoviedb.org/3/"
tmdbKey = "?api_key=182afe8c78e3f9451e21950e7b29053e"
tmdbBasePosterPath="https://image.tmdb.org/t/p/original"

#omdb - API
omdbAPI = "https://www.omdbapi.com/?apikey=65f7361a&"
openLibraryAPI = "http://openlibrary.org/"
openLibraryCoverAPI = "http://covers.openlibrary.org/"


#App
@app.before_request
def handleSession():
	authed = False;
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

@app.route('/movies/add/tmdb')
def tmdbGet():
	#Sastavljanje upita
	reqStart = tmdbBase + "movie/"
	reqEnd = tmdbKey
	#Get
	for i in range(550,650,2):
		resp = requests.get("{0}{1}{2}{3}&append_to_response=credits".format(reqStart,str(i),'',reqEnd))
		if resp.ok:
			resp_json = resp.json()
			director=""
			posterPath=tmdbBasePosterPath+resp_json["poster_path"]
			for member in resp_json["credits"]["crew"]:
				if(member["job"]=="Director"):
					director=member["name"]
					break
			#return resp_json
			genres = []
			for genre in resp_json["genres"]:
				genres.append(genre["name"])
			mov=Movie(resp_json["imdb_id"],resp_json["title"],genres,resp_json["release_date"],resp_json["overview"],director,posterPath)
			dbComms.movieCreate(db,mov)
			#Add rating
			dbComms.movieAddRating(db,"TMDB",mov.id,resp_json["vote_average"])
		else:
			continue
	return redirect(url_for('moviesList'))


@app.route('/movies/add/omdb', defaults={"movieTitle" : "Die Hard"})
@app.route('/movies/add/omdb/<movieTitle>')
def omdbGet(movieTitle):
	omdbAPIcall = omdbAPI + "t=" + movieTitle
	resp = requests.get(omdbAPIcall)
	if resp.ok:
		resp_content = resp.content
		resp_json = json.loads(resp_content.decode("utf-8"))
		#return resp_json
		genres = resp_json["Genre"].replace(" ","")
		genres = genres.split(",")
		mov=Movie(resp_json["imdbID"],resp_json["Title"],genres,resp_json["Released"],resp_json["Plot"],resp_json["Director"],resp_json["Poster"])
		dbComms.movieCreate(db,mov)
		#Add ratings
		for rating in resp_json["Ratings"]:
			dbComms.movieAddRating(db,rating["Source"],resp_json["imdbID"],rating["Value"])
		return redirect(url_for('moviesList'))
	else:
		return "Bad request"

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


#Test DB controls
@app.route('/db/prg')
def purge():
	purge_database()
	session.clear()
	session["warning"]=warnings.noWarning()
	return redirect("/")

def purge_database():
	qry = 'MATCH (node) DETACH DELETE node'
	db.execute_query(qry)
	return


#Main
if __name__ == '__main__':
	app.run(debug=True)
