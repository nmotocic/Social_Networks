import json
import sys
import time
import math
import copy
import numpy as np
from datetime import datetime
from social_network.dbModels import *
from social_network.dbRelationsParser import *


stockAvatarUrl="https://image.shutterstock.com/image-vector/male-avatar-profile-picture-vector-600w-221431012.jpg"
stockPosterUrl="https://underscoremusic.co.uk/site/wp-content/uploads/2014/05/no-poster.jpg"
# User controls
def userCheck(db, email):
	qry = 'MATCH (n:User {{email: "{0}"}}) RETURN n'.format(email)
	# return qry
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break
	return ret


def userCreate(db, username, email, avatarUrl=stockAvatarUrl):
	if email is None:
		return
	if userCheck(db, email) == True:
		return
	if avatarUrl is None:
		avatarUrl = stockAvatarUrl
	qry = 'CREATE (n:User {{name: "{0}", email: "{1}", avatarUrl: "{2}", creationDate: "{3}"}})'.format(
		cleanString(username), email, cleanString(avatarUrl),datetime.today().strftime('%Y-%m-%d'))
	db.execute_query(qry)


def userGetByEmail(db, email):
	if email is None:
		return
	qry = 'MATCH (n:User {{email:"{0}"}}) RETURN n'.format(email)
	relations = db.execute_and_fetch(qry)
	usr = None
	for relation in relations:
		user = relation["n"]
		usr = User(user.properties["name"], user.properties["email"], user.properties["avatarUrl"], user.properties["creationDate"])
	return usr


def get_user_id_by_email(db, email):
	if email is None:
		return
	qry = 'MATCH (n:User {{email:"{0}"}}) RETURN n'.format(cleanString(email))
	relations = db.execute_and_fetch(qry)
	for relation in relations:
		user_id = relation["n"].id
	return user_id


def userChangeName(db, email, newName):
	if email is None:
		return
	qry = 'MATCH (u:User {{email:"{0}"}}) SET u.name = "{1}"'.format(
		email, cleanString(newName)
	)
	db.execute_query(qry)
	return cleanString(newName)


# Favorites
def userFavoritesMovie(db, email, movieId, timestampOverride=0):
	if email is None or movieId is None:
		return
	if userCheck(db, email) == False or movieCheck(db, movieId) == False:
		return
	if userCheckFavorited(db, email, movieId):
		return
	if timestampOverride != 0:
		timestamp = timestampOverride
	else:
		timestamp = math.floor(time.time())
	qry = 'MATCH (u:User),(m:Movie) WHERE m.id = "{0}" AND u.email = "{1}" CREATE (u)-[r:favorited {{timestamp : {2}}}]->(m)'.format(
		movieId, email, timestamp
	)
	db.execute_query(qry)
	return


def userUnFavoritesMovie(db, email, movieId):
	if email is None or movieId is None:
		return
	if userCheck(db, email) == False or movieCheck(db, movieId) == False:
		return
	if not userCheckFavorited(db, email, movieId):
		return
	qry = 'MATCH ( u:User {{ email:"{0}"}} )-[r:favorited]->( m:Movie {{ id: "{1}" }} ) DELETE r'.format(
		email, movieId
	)
	db.execute_query(qry)
	return


def userCheckFavorited(db, email, movieId):
	qry = 'MATCH (u:User {{ email : "{0}" }})-[r:favorited]->(m:Movie {{ id : "{1}" }}) RETURN r'.format(
		email, movieId
	)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break
	return ret


def userGetAllFavorited(db, email):
	qry = 'MATCH (u:User {{ email: "{0}"}})-[r2:favorited]->(m:Movie)-[r:isGenre]->(g:Genre) RETURN m,r,g'.format(
		email
	)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)


def movieGetFavoritedLimited(db, email, lastSeconds=8):
	timeLimit = math.floor(time.time()) - lastSeconds
	qry = 'MATCH (u:User {{ email: "{0}"}})-[r2:favorited]->(m:Movie)-[r:isGenre]->(g:Genre) WHERE r2.timestamp >= {1} RETURN m,r,g'.format(
		email, timeLimit
	)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)


# User rating 0 negative, 1 positive
def userRateMovie(db, email, movieId, rating, timestampOverride=0):
	if rating != 0 and rating != 1:
		return
	if email is None or movieId is None:
		return
	if userCheck(db, email) == False or movieCheck(db, movieId) == False:
		return
	if timestampOverride != 0:
		timestamp = timestampOverride
	else:
		timestamp = math.floor(time.time())
	if userCheckRating(db, email, movieId):
		qry = 'MATCH (u:User {{ email : "{1}" }})-[r:rated]->(m:Movie {{ id : "{0}" }}) SET r.timestamp = {2}, r.rating = {3}'.format(
			movieId, email, timestamp, rating
		)
	else:
		qry = 'MATCH (u:User),(m:Movie) WHERE m.id = "{0}" AND u.email = "{1}" CREATE (u)-[r:rated {{ timestamp : {2}, rating : {3} }}]->(m)'.format(
			movieId, email, timestamp, rating
		)
	db.execute_query(qry)
	return


def userUnRateMovie(db, email, movieId):
	if email is None or movieId is None:
		return
	if userCheck(db, email) == False or movieCheck(db, movieId) == False:
		return
	qry = 'MATCH ( u:User {{ email:"{0}"}} )-[r:rated]->( m:Movie {{ id: "{1}" }} ) DELETE r'.format(
		email, movieId
	)
	db.execute_query(qry)
	return


def userCheckRating(db, email, movieId):
	qry = 'MATCH (u:User {{ email : "{0}" }})-[:rated]->(m:Movie {{ id : "{1}" }}) RETURN u'.format(
		email, movieId
	)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break
	return ret

def userGetRating(db, email ,movieId):
	qry = 'MATCH (u:User {{ email : "{0}" }})-[r:rated]->(m:Movie {{ id : "{1}" }}) RETURN r'.format(
		email, movieId
	)
	result = db.execute_and_fetch(qry)
	for relation in result:
		return parseMovieRatingSingle(relation)
	return None

# If lastSeconds 0 get all, otherwise get movies rated within "lastSeconds"
def userGetPositiveRatedMovies(db, email, lastSeconds=0):
	if lastSeconds != 0:
		timeLimit = math.floor(time.time()) - lastSeconds
	else:
		timeLimit = 0
	qry = 'MATCH (u:User {{ email: "{0}"}})-[r2:rated]->(m:Movie)-[r:isGenre]->(g:Genre) WHERE r2.timestamp >= {1} AND r2.rating = 1 RETURN m,r,g'.format(
		email, timeLimit
	)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)


def userGetNegativeRatedMovies(db, email, lastSeconds=0):
	if lastSeconds != 0:
		timeLimit = math.floor(time.time()) - lastSeconds
	else:
		timeLimit = 0
	qry = 'MATCH (u:User {{ email: "{0}"}})-[r2:rated]->(m:Movie)-[r:isGenre]->(g:Genre) WHERE r2.timestamp >= {1} AND r2.rating = 0 RETURN m,r,g'.format(
		email, timeLimit
	)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)


def movieGetRecentlyRated(db,limit=20, lastSeconds=0):
	if lastSeconds != 0:
		timeLimit = math.floor(time.time()) - lastSeconds
	else:
		timeLimit = 0
	qry = "MATCH (u:User)-[r:rated]->(m:Movie) WHERE r.timestamp >= {0} RETURN m,r".format(
		timeLimit
	)
	relations = db.execute_and_fetch(qry)
	sortedList = parseMovieRatings(relations)
	retList = []
	for mov in sortedList:
		retList.append(movieGetById(db, mov))
		if(len(retList)>=limit):
			break
	return retList

def movieGetUserRatings(db, movieId, lastSeconds=0):
	if movieId is None:
		return
	if lastSeconds != 0:
		timeLimit = math.floor(time.time()) - lastSeconds
	else:
		timeLimit = 0
	qry = 'MATCH (u:User)-[r:rated]->(m:Movie {{ id: "{0}" }}) WHERE r.timestamp>={1} RETURN u,r,m'.format(
		movieId,timeLimit
	)
	relations = db.execute_and_fetch(qry)
	retDict = {"positive":0,"negative":0}
	for relation in relations:
		rating = parseMovieRatingSingle(relation)
		if rating==1:
			retDict["positive"]+=1
		elif rating == 0:
			retDict["negative"]+=1
	if(retDict["negative"]==0 and retDict["positive"]>0):
		retDict["score"]="100%"
	elif retDict["negative"]==0 and retDict["positive"]==0:
		retDict["score"]="No user ratings"
	else:
		retDict["score"] = str(round((retDict["positive"]/(retDict["negative"]+retDict["positive"])*100)))+"%"
	return retDict

# Movie controls
def movieCheck(db, id):
	qry = 'MATCH (n:Movie {{id: "{0}"}}) RETURN n'.format(str(id))
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break
	return ret


def movieCreate(db, movie):
	if movie.id is None:
		return
	if type(movie.directorName) != str:
		movie.directorName = "Unkown"
	if movieCheck(db, movie.id) == True:
		return
	if movie.posterPath is None or movie.posterPath == "":
		movie.posterPath = stockPosterUrl
	qry = 'CREATE (n:Movie {{id: "{0}",name: "{1}", releaseDate: "{2}", overview: "{3}", directorName: "{4}", posterPath: "{5}"}})'.format(
		str(movie.id),
		cleanString(movie.name),
		movie.releaseDate,
		cleanString(movie.overview),
		cleanString(movie.directorName),
		cleanString(movie.posterPath),
	)
	db.execute_query(qry)
	# Genre creation and linking
	for genre in movie.genres:
		# Add genres
		genreCreate(db, genre)
		# Link to genre
		qry = 'MATCH (m:Movie),(g:Genre) WHERE m.id = "{0}" AND g.name = "{1}" CREATE (m)-[r:isGenre]->(g)'.format(
			str(movie.id), genre
		)
		db.execute_query(qry)
	return


def movieGetAll(db, limit=10, page=0):
	# If limit is 0 get all
	if limit <= 0:
		qry = "MATCH (m:Movie)-[r:isGenre]->(g:Genre) RETURN m,r,g"
	else:
		qry = "MATCH (m:Movie) WITH DISTINCT m SKIP {0} LIMIT {1} MATCH (m:Movie)-[r:isGenre]->(g:Genre) RETURN m,r,g".format(
			page * limit, limit
		)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)


def movieGetByGenre(db, genre, limit=10, page=0):
	if limit <= 0:
		qry = (
			'MATCH (:Genre {{name : "{0}"}})<-[:isGenre]-(m:Movie) WITH DISTINCT m MATCH (m)-[r:isGenre]->(g:Genre) RETURN m,r,g'
		).format(genre)
	else:
		qry = (
			'MATCH (q:Genre)<-[:isGenre]-(m:Movie) WHERE toLower(q.name)="{0}" WITH DISTINCT m SKIP {1} LIMIT {2} MATCH (m)-[r:isGenre]->(g:Genre) RETURN m,r,g'
		).format(genre.lower(), page * limit, limit)
	relations = db.execute_and_fetch(qry)
	retList = parseMovieRelations(relations)
	return retList


def movieGetById(db, movieId):
	qry = ('MATCH (m:Movie {{id : "{0}"}})-[r:isGenre]->(g:Genre) RETURN m,r,g').format(
		movieId
	)
	relations = db.execute_and_fetch(qry)
	retList = parseMovieRelationSingle(relations)
	return retList


# Genre controls
def genreCheck(db, name):
	qry = 'MATCH (n:Genre {{name: "{0}"}} ) RETURN n'.format(name)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break
	return ret


def genreCreate(db, name):
	if name is None:
		return
	if genreCheck(db, name) == True:
		return
	qry = 'CREATE (n:Genre {{name: "{0}"}})'.format(cleanString(name))
	db.execute_query(qry)
	return


def genreGetAll(db):
	qry = "MATCH (g:Genre) RETURN g"
	relations = db.execute_and_fetch(qry)
	retList = []
	for relation in relations:
		gen = relation["g"]
		genre = Genre(gen.properties["name"])
		retList.append(genre)
	# Finalize
	retList.sort(key=nameSort)
	return retList


# Rating source
def ratingSourceCreate(db, sourceName):
	if sourceName is None:
		return
	qry = 'CREATE (n:RatingSource {{name: "{0}"}})'.format(cleanString(sourceName))
	db.execute_query(qry)
	return


def ratingSourceCheck(db, sourceName):
	qry = 'MATCH (n:RatingSource {{name: "{0}"}} ) RETURN n'.format(sourceName)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break
	return ret


def ratingExists(db, sourceName, movieId):
	qry = 'MATCH (s:RatingSource {{name: "{0}"}})-[r:Rated]->(m:Movie {{id: "{1}"}}) RETURN s,r,m'.format(
		sourceName, movieId
	)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break
	return ret


def movieAddRating(db, sourceName, movieId, rating):
	if sourceName is None or movieId is None or rating is None:
		return
	# Source exist?
	if not ratingSourceCheck(db, sourceName):
		ratingSourceCreate(db, sourceName)
	# Rating exist?
	if ratingExists(db, sourceName, movieId):
		qry = 'MATCH (s:RatingSource {{name: "{0}"}})-[r:Rated]->(m:Movie {{id: "{1}"}}) SET r.score= "{2}"'.format(
			sourceName, movieId, rating
		)
	else:
		qry = 'MATCH (s:RatingSource),(m:Movie) WHERE m.id = "{0}" AND s.name = "{1}" CREATE (s)-[r:Rated {{score: "{2}"}}]->(m)'.format(
			movieId, sourceName, rating
		)
	db.execute_query(qry)
	return


def movieGetRating(db, movieId):
	if movieId is None:
		return
	qry = 'MATCH (s:RatingSource)-[r]->(m:Movie {{ id: "{0}" }}) RETURN s,r'.format(
		movieId
	)
	relations = db.execute_and_fetch(qry)
	retDict = {}
	for relation in relations:
		retDict[relation["s"].properties["name"]] = relation["r"].properties["score"]
	return retDict


def get_user_ratings(db, current_user_id):
	# initialize dictionary of ratings, keys are (user_id, movie_id) tuples and values are either 1 for like or 0 for dislike
	ratings = {}
	# set query that will fetch all rating relations between users and movies
	qry = "MATCH (u:User)-[r:rated]->(m:Movie) RETURN u,r,m"
	qry_favs = "MATCH (u:User)-[f:favorited]->(m:Movie) RETURN u,f,m"
	favorites = db.execute_and_fetch(qry_favs)
	favs = {}
	for favorite in favorites:
		user = favorite["u"]
		movie = favorite["m"]
		favs[(user.id, movie.id)] = 1
	# execute query and fetch results
	relations = db.execute_and_fetch(qry)
	# get all user ids in list
	user_ids = get_all_user_ids(db)
	# get all movie ids in list
	movie_ids = get_all_movie_ids(db)
	# iterate over all ratings
	for relation in relations:
		user = relation["u"]
		movie = relation["m"]
		rating = relation["r"].properties["rating"]
		# if rating is 0 that means the user dislikes the movie
		rating *= 3
		rating += 1
		if (user.id, movie.id) in favs:
			rating += 1
		
		ratings[(user.id, movie.id)] = rating
	# initialize matrix and set its first row to the number of users and number of movies
	matrix = [str(len(user_ids)) + " " + str(len(movie_ids))]
	# initialize list of queries
	queries = []
	# iterate over all user ids
	for user_id in user_ids:
		# initialize row of matrix which will be a string of ratings seperated by spaces
		line = ""
		# iterate over all movies
		for movie_id in movie_ids:
			# if tuple is in ratings that means the user rated the movie
			if (user_id, movie_id) in ratings:
				# rating is added to the line
				line += str(ratings[(user_id, movie_id)]) + " "
			else: # if tuple is not a key in ratings dictionary that means the user has not rated the movie yet
				# if the id is the same as the current logged in users id
				if user_id == current_user_id:
					# add query to the list of predictions that are needed to recommend the movie to the user
					queries.append(
						str(user_ids.index(user_id)) + " " + str(movie_ids.index(movie_id)) + " " + str(len(user_ids))
					)
					# add no rating sign "X" to the line
				line += "X "
		# add line (row) to the matrix
		matrix.append(line)
	# now add the number of predictions needed to make
	matrix.append(str(len(queries)))
	# iterate over all needed predictions
	for query in queries:
		# add prediction query to returning matrix
		matrix.append(query)
	#return filled matrix
	return matrix


def get_all_user_ids(db):
	# initialize list of user ids
	user_ids = []
	# set query that will fetch all nodes of type User
	qry = "MATCH (u:User) RETURN u"
	# execute query and return results
	results = db.execute_and_fetch(qry)
	# iterate over results
	for result in results:
		# get id of the user node from result
		user_id = result["u"].id
		# if user id is not already in the id list 
		if user_id not in user_ids:
			# add user id to id list
			user_ids.append(user_id)
	# return filled list of user ids
	return user_ids

def get_all_movie_ids(db):
	# initialize list of movie ids
	movie_ids = []
	# set query that will fetch all nodes of type Movie
	qry = "MATCH (m:Movie) RETURN m"
	# execute query and return results
	results = db.execute_and_fetch(qry)
	# iterate over results
	for result in results:
		# get id of the movie node from result
		movie_id = result["m"].id
		# if movie id is not already in the id list 
		if movie_id not in movie_ids:
			# add movie id to id list
			movie_ids.append(movie_id)
	# return filled list of movie ids
	return movie_ids

	
def get_all_movies(db):
	# initialize list of movies
	movies = []
	# set query to fetch all nodes of type Movie
	qry = "MATCH (m:Movie) RETURN m"
	# execute query and return results
	results = db.execute_and_fetch(qry)
	# iterate over results
	for result in results:
		# get movie node from result
		movie = result["m"]
		# if movie is not already in the list 
		if movie not in movies:
			# add movie to list
			movies.append(movie)
	# return filled list of movies
	return movies

# Help functions
def cleanString(st):
	ret = st
	ret = ret.replace('"', "'")
	return ret


def nameSort(obj):
	return obj.name
