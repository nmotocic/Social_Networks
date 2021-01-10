from social_network.dbModels import *
from social_network import dbComms
from social_network import movieApiController
import random
import math
import time
#Random users
minUserId=1
maxUserId=30
#Preff users
minActionUserId = 1
maxActionUserId = 30
minDramaUserId = 1
maxDramaUserId = 15
minThrillerUserId = 1
maxThrillerUserId = 12

def addTestUsers(db):
	dbComms.userCreate(db,"Alice","alice@fakemail.com")
	dbComms.userCreate(db,"Bob","bob@fakemail.com")
	dbComms.userCreate(db,"George","george@fakemail.com")
	dbComms.userCreate(db,"Shrek","shrek@fakemail.com")
	for i in range (minUserId,maxUserId):
		dbComms.userCreate(db,"FakeUser"+str(i),"fakeuser{0}@fakemail.com".format(str(i)))

def addPrefUsers(db):
	#Action
	for i in range (minActionUserId,maxActionUserId):
		dbComms.userCreate(db,"ActionUser"+str(i),"actionuser{0}@fakemail.com".format(str(i)))
	#Drama
	for i in range (minDramaUserId,maxDramaUserId):
		dbComms.userCreate(db,"DramaUser"+str(i),"dramauser{0}@fakemail.com".format(str(i)))
	#Thriller
	for i in range (minThrillerUserId,maxThrillerUserId):
		dbComms.userCreate(db,"ThrillerUser"+str(i),"thrilleruser{0}@fakemail.com".format(str(i)))

def addTmdbMovies(db):
	for i in range(550,1110):
		movieApiController.apiTmdbAddById(db,i)

def addOmdbMovies(db):
	movieList = ["Shrek","Spider Man","Avatar","Forrest Gump","Alice in Wonderland","Chernobyl"]
	for movie in movieList:
		movieApiController.apiOmdbAddByTitle(db,movie)
def addTestLikes(db):
	#Alice likes
	#Men in black,Jaws 2, Secret beyond the door
	user = "alice@fakemail.com"
	likes = ["tt0119654","tt0077766","tt0040766"]
	dislikes = []
	favorites = ["tt0087332"] # Ghost busters
	for movie in likes:
		dbComms.userRateMovie(db,user,movie,1)
	for movie in dislikes:
		dbComms.userRateMovie(db,user,movie,0)
	for movie in favorites:
		dbComms.userFavoritesMovie(db,user,movie)
	#Bob likes
	#Men in black,Jaws 2,Die Hard, Independance Day
	user = "bob@fakemail.com"
	likes = ["tt0119654","tt0077766","tt0095016","tt0116629"]
	favorites = ["tt0137523"] # Fight club
	dislikes = []
	for movie in likes:
		dbComms.userRateMovie(db,user,movie,1)
	for movie in dislikes:
		dbComms.userRateMovie(db,user,movie,0)
	for movie in favorites:
		dbComms.userFavoritesMovie(db,user,movie)
	#George likes
	#2 Fast 2 Furious,Jaws 2,Die Hard, Chernobyl, Shrek
	user = "george@fakemail.com"
	likes = ["tt0322259","tt0077766","tt0095016","tt7366338","tt0126029"]
	favorites = ["tt0137523"] # Fight club
	dislikes = []
	#Shrek likes
	#Shrek,Shrek, FFVII, Monster Inc
	user = "shrek@fakemail.com"
	likes = ["tt0126029","tt0126029","tt0385700","tt0198781"]
	favorites = ["tt0126029"] # Shrek
	dislikes = ["tt0077766"] # Jaws 2
	for movie in likes:
		dbComms.userRateMovie(db,user,movie,1)
	for movie in dislikes:
		dbComms.userRateMovie(db,user,movie,0)
	for movie in favorites:
		dbComms.userFavoritesMovie(db,user,movie)

def addRandomVotes(db,limit=300,page=0):
	#Today votes
	movieList = dbComms.movieGetAll(db,limit=limit,page=page)
	for movie in movieList:
		for i in range(minUserId,round(maxUserId/3)):
			rand = random.randrange(0,11,1)
			if (rand >= 10):
				dbComms.userRateMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,1)
				dbComms.userFavoritesMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id)
			elif (rand >= 8):
				dbComms.userRateMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,1)
			elif (rand == 2):
				dbComms.userRateMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,0)
	#Last week votes (0-604800 timestamp)
	timestampOverride = time.time()-400000
	movieList = dbComms.movieGetAll(db,limit=limit,page=page)
	for movie in movieList:
		for i in range(round(maxUserId/3),round(2*maxUserId/3)):
			rand = random.randrange(0,11,1)
			if (rand >= 10):
				dbComms.userRateMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,1,timestampOverride=timestampOverride)
				dbComms.userFavoritesMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,timestampOverride=timestampOverride)
			elif (rand >= 6):
				dbComms.userRateMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,1,timestampOverride=timestampOverride)
			elif (rand <= 2):
				dbComms.userRateMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,0,timestampOverride=timestampOverride)
	#Last month votes (604800-2629743 timestamp)
	timestampOverride = time.time()-2400000
	movieList = dbComms.movieGetAll(db,limit,page=page)
	for movie in movieList:
		for i in range(round(2*maxUserId/3),maxUserId):
			rand = random.randrange(0,11,1)
			if (rand >= 10):
				dbComms.userRateMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,1,timestampOverride=timestampOverride)
				dbComms.userFavoritesMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,timestampOverride=timestampOverride)
			elif (rand >= 4):
				dbComms.userRateMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,1,timestampOverride=timestampOverride)
			elif (rand <= 3):
				dbComms.userRateMovie(db,"fakeuser{0}@fakemail.com".format(str(i)),movie.id,0,timestampOverride=timestampOverride)

def addAllPrefVotes(db):
	addPrefVotes(db,"Drama",minDramaUserId,maxDramaUserId)
	addPrefVotes(db,"Action",minActionUserId,maxActionUserId)
	addPrefVotes(db,"Thriller",minThrillerUserId,maxThrillerUserId)

def addPrefVotes(db,userType,lowerLimit,upperLimit,limit=300,page=0):
	#Today votes
	movieList = dbComms.movieGetAll(db,limit=limit,page=page)
	pref = userType
	mail = userType.lower()
	for movie in movieList:
		for i in range(lowerLimit,round(upperLimit/3)):
			rand = random.randrange(0,11,1)
			if userType in movie.genres:
				rand+=8
			if (rand >= 13):
				dbComms.userRateMovie(db,"{0}user{1}@fakemail.com".format(mail,str(i)),movie.id,1)
				dbComms.userFavoritesMovie(db,"fakeuser{1}@fakemail.com".format(mail,str(i)),movie.id)
			elif (rand >= 9):
				dbComms.userRateMovie(db,"{0}user{1}@fakemail.com".format(mail,str(i)),movie.id,1)
			elif (rand == 4):
				dbComms.userRateMovie(db,"{0}user{1}@fakemail.com".format(mail,str(i)),movie.id,0)
	#Last month votes (604800-2629743 timestamp)
	timestampOverride = time.time()-2400000
	movieList = dbComms.movieGetAll(db,limit,page=page+2)
	for movie in movieList:
		for i in range(minUserId,maxUserId):
			rand = random.randrange(0,11,1)
			if userType in movie.genres:
				rand+=8
			if (rand >= 13):
				dbComms.userRateMovie(db,"{0}user{1}@fakemail.com".format(mail,str(i)),movie.id,1,timestampOverride=timestampOverride)
				dbComms.userFavoritesMovie(db,"fakeuser{1}@fakemail.com".format(mail,str(i)),movie.id,timestampOverride=timestampOverride)
			elif (rand >= 8):
				dbComms.userRateMovie(db,"{0}user{1}@fakemail.com".format(mail,str(i)),movie.id,1,timestampOverride=timestampOverride)
			elif (rand == 0):
				dbComms.userRateMovie(db,"{0}user{1}@fakemail.com".format(mail,str(i)),movie.id,0,timestampOverride=timestampOverride)

