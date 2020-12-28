from flask import Flask, render_template , redirect , url_for, session, request
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.consumer import oauth_authorized
from social_network.database.memgraph import Memgraph
from social_network import dbComms
from social_network import warnings
from social_network.dbModels import User,Movie,Genre
import os
import mgclient
import requests
import json
import base64

#App settings 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'maxseCretPliz18882'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#Database
db = Memgraph()


#End DB
#Twitter connector
twitter_bp = make_twitter_blueprint(api_key='AckLZqFrceE6E2EctXUF1Bmly' , api_secret='CJlkvc0xfQYi731uICahGIJ9mrSw7zYYu7S3EmB7CCftkDASSr')
app.register_blueprint(twitter_bp, url_prefix='/twitter_login')
#Twitter connection
@app.route('/twitter')
def twitter_login():
	if not twitter.authorized:
		return redirect(url_for('twitter.login'))
	return redirect(url_for('account'))

#TMDB - API
#https://api.themoviedb.org/3/movie/550?api_key=182afe8c78e3f9451e21950e7b29053e
#base+request+key+params
tmdbBase = "https://api.themoviedb.org/3/"
tmdbKey = "?api_key=182afe8c78e3f9451e21950e7b29053e"

#Shazam - API
spClientId = "8ad4e813697940b7806adc4527aedf26"
spSecret = "9246628e5260400aa796a05f55944e42"
spPayload = {'grant_type': 'client_credentials'}



#App
@app.before_request
def handleSession():
	if(twitter.authorized):
		if("userName" not in session):
			account_info = twitter.get("account/verify_credentials.json", params={"include_email" : "true"})
			if account_info.ok:
				account_info_json = account_info.json()
				res = dbComms.userCheck(db,account_info_json['email'])
				if  res==False:
					dbComms.userCreate(db,account_info_json['screen_name'],account_info_json['email'])
				session["userName"] = dbComms.userGetByEmail(db,account_info_json["email"]).username
				session["userEmail"] =account_info_json['email']
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
#Music
@app.route('/music', methods=["POST","GET"])
def trackList():
	if(twitter.authorized==False):
		session["warning"]=warnings.noLogin()
		return redirect(url_for('index'))
	filtered=""
	retFilt = dbComms.artistGetAll(db)
	if request.method == "POST":
		if("artist" in request.form):
			filtered=request.form["artist"]
			filtered = dbComms.artistGetById(db,filtered)
			ret = dbComms.trackGetByArtist(db,filtered)
		else:
			ret = dbComms.trackGetAll(db)
		return render_template("songList.html", list=ret, filter=retFilt, filtered=filtered)		
	else:
		ret = dbComms.trackGetAll(db)
		return render_template("songList.html", list=ret, filter=retFilt)

@app.route('/music/online-search/', methods=["POST","GET"])
@app.route('/music/online-search/<qry>', methods=["POST","GET"])
def trackSearch(qry=""):
	if(twitter.authorized==False):
		session["warning"]=warnings.noLogin()
		return redirect(url_for('index'))
	filtered=qry
	retFilt = dbComms.artistGetAll(db)
	if request.method == "POST":
		qry = request.form["qry"]
		return redirect(url_for('trackSearch', qry=qry))	
	else:
		if(qry!=""):
			#Get token
			response=requests.post('https://accounts.spotify.com/api/token/', data=spPayload, auth = (spClientId, spSecret)).json()
			myToken = "{0} {1}".format(response["token_type"],response["access_token"])
			#Make request
			response=requests.get('https://api.spotify.com/v1/search?q={0}&type=track&limit=10'.format(qry), headers={'Authorization': myToken}).json()
			ret = dbComms.trackCreateBulk(db,response["tracks"]["items"])
			return render_template("songListOnline.html", list=ret)
		else:
			ret = []
			return render_template("songListOnline.html", list=ret, filter=retFilt)


@app.route('/music/add-samples')
def spotGet():
	if(twitter.authorized==False):
		session["warning"]=warnings.noLogin()
		return redirect(url_for('index'))
	response=requests.post('https://accounts.spotify.com/api/token/', data=spPayload, auth = (spClientId, spSecret)).json()
	myToken = "{0} {1}".format(response["token_type"],response["access_token"])
	response=requests.get('https://api.spotify.com/v1/search?q=AmaLee&type=track&limit=10', headers={'Authorization': myToken}).json()
	ret = dbComms.trackCreateBulk(db,response["tracks"]["items"])
	response=requests.get('https://api.spotify.com/v1/search?q=Jonathan Young&type=track&limit=10', headers={'Authorization': myToken}).json()
	ret = dbComms.trackCreateBulk(db,response["tracks"]["items"])
	response=requests.get('https://api.spotify.com/v1/search?q=NateWantsToBattle&type=track&limit=10', headers={'Authorization': myToken}).json()
	ret = dbComms.trackCreateBulk(db,response["tracks"]["items"])
	response=requests.get('https://api.spotify.com/v1/search?q=Caleb Hyles&type=track&limit=10', headers={'Authorization': myToken}).json()
	ret = dbComms.trackCreateBulk(db,response["tracks"]["items"])
	return redirect(url_for('trackList'))
#Movies
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

@app.route('/movies/add-samples')
def tmdbGet():
	reqStart = tmdbBase + "movie/"
	reqEnd = tmdbKey

	for i in range(550,650,2):
		req = requests.get("{0}{1}{2}{3}".format(reqStart,str(i),'',reqEnd))
		if(req.status_code != 200):
			continue
		req = req.json()
		return req
		mov=Movie(req["id"],req["title"],req["genres"],req["release_date"],req["overview"])
		dbComms.movieCreate(db,mov)
	return redirect(url_for('moviesList'))
 
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


#Test functions
@app.route('/tw')
def test():
	res = dbComms.userGetByEmail(db,"")
	return res
    
@app.route('/protected')
def protected():
	if(twitter.authorized==True):
		return render_template("protectedPage.html")
	session["warning"]=warnings.noLogin()
	return redirect(url_for('index'))


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
