import json
import sys
import time
import math
from social_network.dbModels import *
from social_network.dbRelationsParser import *

#User controls
def userCheck(db,email):
	qry = 'MATCH (n:User {{email: "{0}"}}) RETURN n'.format(email)
	#return qry
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break;
	return ret

def userCreate(db,username,email):
	if email is None:
		return
	if(userCheck(db,email)==True):
		return
	qry = 'CREATE (n:User {{name: "{0}", email: "{1}"}})'.format(cleanString(username),cleanString(email))
	db.execute_query(qry)

def userGetByEmail(db,email):
	if email is None:
		return
	qry = 'MATCH (n:User {{email:"{0}"}}) RETURN n'.format(cleanString(email))
	relations = db.execute_and_fetch(qry)
	for relation in relations:
		user = relation['n']
		usr = User(user.properties["name"],user.properties["email"])
	return usr

def userChangeName(db,email,newName):
	if email is None:
		return
	qry = 'MATCH (u:User {{email:"{0}"}}) SET u.name = "{1}"'.format(email,cleanString(newName))
	db.execute_query(qry)
	return cleanString(newName)

#Favorites
def userFavoritesMovie(db,email,movieId,timestampOverride=0):
	if email is None or movieId is None:
		return
	if userCheck(db,email)==False or movieCheck(db,movieId) == False:
		return
	if(userCheckFavorited(db,email,movieId)):
		return
	if timestampOverride != 0:
		timestamp=timestampOverride
	else:
		timestamp=math.floor(time.time())
	qry = 'MATCH (u:User),(m:Movie) WHERE m.id = "{0}" AND u.email = "{1}" CREATE (u)-[r:favorited {{timestamp : {2}}}]->(m)'.format(movieId,email,timestamp)
	db.execute_query(qry)
	return

def userUnFavoritesMovie(db,email,movieId):
	if email is None or movieId is None:
		return
	if userCheck(db,email)==False or movieCheck(db,movieId) == False:
		return
	if(not userCheckFavorited(db,email,movieId)):
		return
	qry = 'MATCH ( u:User {{ email:"{0}"}} )-[r:favorited]->( m:Movie {{ id: "{1}" }} ) DELETE r'.format(email,movieId)
	db.execute_query(qry)
	return

def userCheckFavorited(db,email,movieId):
	qry = 'MATCH (u:User {{ email : "{0}" }})-[r:favorited]->(m:Movie {{ id : "{1}" }}) RETURN r'.format(email,movieId)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break;
	return ret

def movieGetAllFavorited(db,email):
	qry = 'MATCH (u:User {{ email: "{0}"}})-[r2:favorited]->(m:Movie)-[r:isGenre]->(g:Genre) RETURN m,r,g'.format(email)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)

def movieGetFavoritedLimited(db,email,lastSeconds=8):
	timeLimit = math.floor(time.time())-lastSeconds
	qry = 'MATCH (u:User {{ email: "{0}"}})-[r2:favorited]->(m:Movie)-[r:isGenre]->(g:Genre) WHERE r2.timestamp >= {1} RETURN m,r,g'.format(email,timeLimit)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)

#User rating 0 negative, 1 positive
def userRateMovie(db,email,movieId,rating,timestampOverride=0):
	if rating != 0 and rating != 1:
		return
	if email is None or movieId is None:
		return
	if userCheck(db,email)==False or movieCheck(db,movieId) == False:
		return
	if timestampOverride != 0:
		timestamp=timestampOverride
	else:
		timestamp=math.floor(time.time())
	if userCheckRating(db,email,movieId):
		qry = 'MATCH (u:User {{ email : "{1}" }})-[r:rated]->(m:Movie {{ id : "{0}" }}) SET r.timestamp = {2}, r.rating = {3}'.format(movieId,email,timestamp,rating)
	else:
		qry = 'MATCH (u:User),(m:Movie) WHERE m.id = "{0}" AND u.email = "{1}" CREATE (u)-[r:rated {{ timestamp : {2}, rating : {3} }}]->(m)'.format(movieId,email,timestamp,rating)
	db.execute_query(qry)
	return

def userUnRateMovie(db,email,movieId):
	if email is None or movieId is None:
		return
	if userCheck(db,email)==False or movieCheck(db,movieId) == False:
		return
	if(not userCheckFavorited(db,email,movieId)):
		return
	qry = 'MATCH ( u:User {{ email:"{0}"}} )-[r:rated]->( m:Movie {{ id: "{1}" }} ) DELETE r'.format(email,movieId)
	db.execute_query(qry)
	return

def userCheckRating(db,email,movieId):
	qry = 'MATCH (u:User {{ email : "{0}" }})-[:rated]->(m:Movie {{ id : "{1}" }}) RETURN u'.format(email,movieId)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break;
	return ret


#If lastSeconds 0 get all, otherwise get movies rated within "lastSeconds"
def userGetPositiveRatedMovies(db,email,lastSeconds=0):
	if(lastSeconds!=0):
		timeLimit = math.floor(time.time())-lastSeconds
	else:
		timeLimit = 0
	qry = 'MATCH (u:User {{ email: "{0}"}})-[r2:rated]->(m:Movie)-[r:isGenre]->(g:Genre) WHERE r2.timestamp >= {1} AND r2.rating = 1 RETURN m,r,g'.format(email,timeLimit)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)

def userGetNegativeRatedMoviesLimited(db,email,lastSeconds=0):
	if(lastSeconds!=0):
		timeLimit = math.floor(time.time())-lastSeconds
	else:
		timeLimit = 0
	qry = 'MATCH (u:User {{ email: "{0}"}})-[r2:rated]->(m:Movie)-[r:isGenre]->(g:Genre) WHERE r2.timestamp >= {1} AND r2.rating = 0 RETURN m,r,g'.format(email,timeLimit)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)

#Get movies rated withing lastSeconds seconds, list size is limited by limit
def movieGetRecentlyRated(db,lastSeconds=0,limit=10):
	if(lastSeconds!=0):
		timeLimit = math.floor(time.time())-lastSeconds
	else:
		timeLimit = 0
	qry = 'MATCH (u:User)-[r:rated]->(m:Movie) WHERE r.timestamp >= {0} RETURN m,r'.format(timeLimit)
	relations = db.execute_and_fetch(qry)
	sortedList = parseMovieRatings(relations)
	retList = []
	i = 0
	for mov in sortedList:
		retList.append(movieGetById(db,mov))
		i = i+1
		if(i>=10):
			break
	return retList

#Movie controls
def movieCheck(db,id):
	qry = 'MATCH (n:Movie {{id: "{0}"}}) RETURN n'.format(str(id))
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break;
	return ret

def movieCreate(db,movie):
	if movie.id is None:
		return
	if type(movie.directorName) != str:
		movie.directorName = "Unkown"
	if movieCheck(db,movie.id)==True:
		return
	qry = 'CREATE (n:Movie {{id: "{0}",name: "{1}", releaseDate: "{2}", overview: "{3}", directorName: "{4}", posterPath: "{5}"}})'.format(str(movie.id),cleanString(movie.name),movie.releaseDate,cleanString(movie.overview),cleanString(movie.directorName),cleanString(movie.posterPath))
	db.execute_query(qry)
	#Genre creation and linking
	for genre in movie.genres:
		#Add genres
		genreCreate(db,genre)
		#Link to genre
		qry= 'MATCH (m:Movie),(g:Genre) WHERE m.id = "{0}" AND g.name = "{1}" CREATE (m)-[r:isGenre]->(g)'.format(str(movie.id),genre)
		db.execute_query(qry)
	return

def movieGetAll(db,limit=10,page=0):
	#If limit is 0 get all
	if(limit<=0):
		qry = 'MATCH (m:Movie)-[r:isGenre]->(g:Genre) RETURN m,r,g'
	else:
		qry = 'MATCH (m:Movie) WITH DISTINCT m SKIP {0} LIMIT {1} MATCH (m:Movie)-[r:isGenre]->(g:Genre) RETURN m,r,g'.format(page*limit,limit)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)


def movieGetByGenre(db,genre,limit=10,page=0):
	if(limit<=0):
		qry = ('MATCH (:Genre {{name : "{0}"}})<-[:isGenre]-(m:Movie) WITH DISTINCT m MATCH (m)-[r:isGenre]->(g:Genre) RETURN m,r,g').format(genre)
	else:
		qry = ('MATCH (:Genre {{name : "{0}"}})<-[:isGenre]-(m:Movie) WITH DISTINCT m SKIP {1} LIMIT {2} MATCH (m)-[r:isGenre]->(g:Genre) RETURN m,r,g').format(genre,page*limit,limit)
	relations = db.execute_and_fetch(qry)
	retList = parseMovieRelations(relations)
	return retList

def movieGetById(db,movieId):
	qry = ('MATCH (m:Movie {{id : "{0}"}})-[r:isGenre]->(g:Genre) RETURN m,r,g').format(movieId)
	relations = db.execute_and_fetch(qry)
	retList = parseMovieRelationSingle(relations)
	return retList

#Genre controls
def genreCheck(db,name):
	qry = 'MATCH (n:Genre {{name: "{0}"}} ) RETURN n'.format(name)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break;
	return ret

def genreCreate(db,name):
	if name is None:
		return
	if genreCheck(db,name)==True:
		return
	qry = 'CREATE (n:Genre {{name: "{0}"}})'.format(cleanString(name))
	db.execute_query(qry)
	return

def genreGetAll(db):
	qry = 'MATCH (g:Genre) RETURN g'
	relations = db.execute_and_fetch(qry)
	retList=[]
	for relation in relations:
		gen = relation['g']
		genre = Genre(gen.properties["name"])
		retList.append(genre)
	#Finalize
	retList.sort(key=nameSort)
	return retList
#Rating source
def ratingSourceCreate(db,sourceName):
	if sourceName is None:
		return
	qry = 'CREATE (n:RatingSource {{name: "{0}"}})'.format(cleanString(sourceName))
	db.execute_query(qry)
	return

def ratingSourceCheck(db,sourceName):
	qry = 'MATCH (n:RatingSource {{name: "{0}"}} ) RETURN n'.format(sourceName)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break;
	return ret

def ratingExists(db,sourceName,movieId):
	qry = 'MATCH (s:RatingSource {{name: "{0}"}})-[r:Rated]->(m:Movie {{id: "{1}"}}) RETURN s,r,m'.format(sourceName,movieId)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break;
	return ret

def movieAddRating(db,sourceName,movieId,rating):
	if sourceName is None or movieId is None or rating is None:
		return
	#Source exist?
	if not ratingSourceCheck(db,sourceName):
		ratingSourceCreate(db,sourceName)
	#Rating exist?
	if ratingExists(db,sourceName,movieId):
		qry = 'MATCH (s:RatingSource {{name: "{0}"}})-[r:Rated]->(m:Movie {{id: "{1}"}}) SET r.score= "{2}"'.format(sourceName,movieId,rating)
	else:
		qry = 'MATCH (s:RatingSource),(m:Movie) WHERE m.id = "{0}" AND s.name = "{1}" CREATE (s)-[r:Rated {{score: "{2}"}}]->(m)'.format(movieId,sourceName,rating)
	db.execute_query(qry)
	return

def movieGetRating(db,movieId):
	if movieId is None:
		return
	qry = 'MATCH (s:RatingSource)-[r]->(m:Movie {{ id: "{0}" }}) RETURN s,r'.format(movieId)
	relations = db.execute_and_fetch(qry)
	retDict={}
	for relation in relations:
		retDict[relation["s"].properties["name"]] = relation['r'].properties["score"]
	return retDict

#Help functions
def cleanString(st):
	ret = st
	ret = ret.replace('"',"'")
	return ret


def nameSort(obj):
	return obj.name