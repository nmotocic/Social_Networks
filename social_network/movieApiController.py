import requests
import json
from social_network import dbComms
from social_network.dbModels import User,Movie,Genre


#TMDB - API
#https://api.themoviedb.org/3/movie/550?api_key=182afe8c78e3f9451e21950e7b29053e
#base+request+key+params
tmdbBase = "https://api.themoviedb.org/3/"
tmdbKey = "?api_key=182afe8c78e3f9451e21950e7b29053e"
tmdbBasePosterPath="https://image.tmdb.org/t/p/original"

def apiTmdbAddById(db,movieId):
	#Sastavljanje upita
	reqStart = tmdbBase + "movie/"
	reqEnd = tmdbKey
	#Get
	resp = requests.get("{0}{1}{2}{3}&append_to_response=credits".format(reqStart,str(movieId),'',reqEnd))
	if resp.ok:
		resp_json = resp.json()
		director=""
		if type(resp_json["poster_path"]) == str:
			posterPath = tmdbBasePosterPath+resp_json["poster_path"]
		else:
			posterPath = ""
		for member in resp_json["credits"]["crew"]:
			if(member["job"] == "Director"):
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


#OMDB
omdbAPI = "https://www.omdbapi.com/?apikey=65f7361a&"

def apiOmdbAddByTitle(db,movieTitle):
	omdbAPIcall = omdbAPI + "t=" + movieTitle
	resp = requests.get(omdbAPIcall)
	if resp.ok:
		resp_content = resp.content
		resp_json = json.loads(resp_content.decode("utf-8"))
		genres = resp_json["Genre"].replace(" ","")
		genres = genres.split(",")
		mov=Movie(resp_json["imdbID"],resp_json["Title"],genres,resp_json["Released"],resp_json["Plot"],resp_json["Director"],resp_json["Poster"])
		dbComms.movieCreate(db,mov)
		#Add ratings
		for rating in resp_json["Ratings"]:
			dbComms.movieAddRating(db,rating["Source"],resp_json["imdbID"],rating["Value"])
