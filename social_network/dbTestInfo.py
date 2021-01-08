from social_network.dbModels import *
from social_network import dbComms
from social_network import movieApiController
import random

minUserId = 1
maxUserId = 30


def addTestUsers(db):
	dbComms.userCreate(db, "Alice", "alice@fakemail.com")
	dbComms.userCreate(db, "Bob", "bob@fakemail.com")
	dbComms.userCreate(db, "George", "george@fakemail.com")
	dbComms.userCreate(db, "Shrek", "shrek@fakemail.com")
	for i in range(minUserId, maxUserId):
		dbComms.userCreate(
			db, "FakeUser" + str(i), "fakeuser{0}@fakemail.com".format(str(i))
		)


def addTmdbMovies(db):
	for i in range(550, 650):
		movieApiController.apiTmdbAddById(db, i)


def addOmdbMovies(db):
	movieList = [
		"Shrek",
		"Spider Man",
		"Mister Bean",
		"Avatar",
		"Forrest Gump",
		"Alice in Wonderland",
		"Chernobyl",
	]
	for movie in movieList:
		movieApiController.apiOmdbAddByTitle(db, movie)


def addTestLikes(db):
	# Alice likes
	# Men in black,Jaws 2, Secret beyond the door
	user = "alice@fakemail.com"
	likes = ["tt0119654", "tt0077766", "tt0040766"]
	dislikes = []
	favorites = ["tt0087332"]  # Ghost busters
	for movie in likes:
		dbComms.userRateMovie(db, user, movie, 1)
	for movie in dislikes:
		dbComms.userRateMovie(db, user, movie, 0)
	for movie in favorites:
		dbComms.userFavoritesMovie(db, user, movie)
	# Bob likes
	# Men in black,Jaws 2,Die Hard, Independance Day
	user = "bob@fakemail.com"
	likes = ["tt0119654", "tt0077766", "tt0095016", "tt0116629"]
	favorites = ["tt0137523"]  # Fight club
	dislikes = []
	for movie in likes:
		dbComms.userRateMovie(db, user, movie, 1)
	for movie in dislikes:
		dbComms.userRateMovie(db, user, movie, 0)
	for movie in favorites:
		dbComms.userFavoritesMovie(db, user, movie)
	# George likes
	# 2 Fast 2 Furious,Jaws 2,Die Hard, Chernobyl, Shrek
	user = "george@fakemail.com"
	likes = ["tt0322259", "tt0077766", "tt0095016", "tt7366338", "tt0126029"]
	favorites = ["tt0137523"]  # Fight club
	dislikes = []
	# Shrek likes
	# Shrek,Shrek, FFVII, Monster Inc
	user = "shrek@fakemail.com"
	likes = ["tt0126029"]
	favorites = ["tt0126029"]  # Shrek
	dislikes = ["tt0077766"]  # Jaws 2
	for movie in likes:
		dbComms.userRateMovie(db, user, movie, 1)
	for movie in dislikes:
		dbComms.userRateMovie(db, user, movie, 0)
	for movie in favorites:
		dbComms.userFavoritesMovie(db, user, movie)


def addRandomVotes(db, limit=40, page=0):
	movieList = dbComms.movieGetAll(db, limit=limit, page=page)
	for movie in movieList:
		for i in range(minUserId, maxUserId):
			rand = random.randrange(0, 11, 1)
			if rand >= 10:
				dbComms.userRateMovie(
					db, "fakeuser{0}@fakemail.com".format(str(i)), movie.id, 1
				)
				dbComms.userFavoritesMovie(
					db, "fakeuser{0}@fakemail.com".format(str(i)), movie.id
				)
			elif rand >= 8:
				dbComms.userRateMovie(
					db, "fakeuser{0}@fakemail.com".format(str(i)), movie.id, 1
				)
			elif rand == 0:
				dbComms.userRateMovie(
					db, "fakeuser{0}@fakemail.com".format(str(i)), movie.id, 0
				)

def add_alice_likes(db):
	user = "alice@fakemail.com"
	likes = ["tt0119654", "tt0077766"]
	dislikes = []
	favorites = ["tt0087332"]  # Ghost busters
	for movie in likes:
		dbComms.userRateMovie(db, user, movie, 1)
	for movie in dislikes:
		dbComms.userRateMovie(db, user, movie, 0)
	for movie in favorites:
		dbComms.userFavoritesMovie(db, user, movie)
