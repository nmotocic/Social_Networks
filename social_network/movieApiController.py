import requests
import json


#TMDB - API
#https://api.themoviedb.org/3/movie/550?api_key=182afe8c78e3f9451e21950e7b29053e
#base+request+key+params
tmdbBase = "https://api.themoviedb.org/3/"
tmdbKey = "?api_key=182afe8c78e3f9451e21950e7b29053e"
tmdbBasePosterPath="https://image.tmdb.org/t/p/original"



#OMDB
omdbAPI = "https://www.omdbapi.com/?apikey=65f7361a&"

def getOmdbByName(movieName):
	omdbAPIcall = omdbAPI + "t=" + movieTitle
	resp = requests.get(omdbAPIcall)
	if resp.ok:
		resp_content = resp.content
		resp_json = json.loads(resp_content.decode("utf-8"))
		#return resp_json
		genres = resp_json["Genre"].replace(" ","")
		genres = genres.split(",")
		mov=Movie(resp_json["imdbID"],resp_json["Title"],genres,resp_json["Released"],resp_json["Plot"],resp_json["Director"],resp_json["Poster"])
		return mov
	else:
		return None
