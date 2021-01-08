import sys
import random
from social_network import dbComms
from social_network.dbModels import Movie
from social_network import predict


def get_recommendations(db, current_user_id):
	#initialize list of recommendations
	recommendations = []
	# get user-item matrix to use in collaborative filtering
	matrix = dbComms.get_user_ratings(db, current_user_id)
	# store all movies from database in list
	movies = dbComms.get_all_movies(db)
	# call get_predictions method that will return a sorted list of movies and their predictions of likeability for the current user
	predictions = predict.get_predictions(matrix)
	# initialize list of movie predictions
	recommendations = []
	# iterate over all predictions
	for key in predictions:
		sys.stdout.flush()
		# take in account only positive predictions
		if predictions[key] >= 0.8:
			# create Movie object and set its parameters
			movie = Movie(movies[key].properties["id"], movies[key].properties["name"], [], 
			movies[key].properties["releaseDate"], movies[key].properties["overview"], 
			movies[key].properties["directorName"], movies[key].properties["posterPath"])
			# set movie recommendation percentage
			movie.percentage = str(round(predictions[key], 2) * 100) + "%"
			# add created object to list of movie predictions
			recommendations.append(movie)
	# set size of roulette (default is 8, but if less movies are recommended it is equal to predicted movie list size)
	roulette_size = 8 if len(recommendations) >= 8 else len(recommendations)
	# return moviePredictions template view with items of movie_prediction_list
	recommendations = random.sample(recommendations, roulette_size)
	return recommendations
