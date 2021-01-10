import sys
import random
from social_network import dbComms
from social_network.dbModels import Movie
from social_network import predict

def get_recommendations(db, current_user_id, startingPerc=0.8, stepSize=0.1, minPerc=0.2, roulleteSize=8, sampleSize=16):
	#initialize list of recommendations
	recommendations = []
	# get user-item matrix to use in collaborative filtering
	matrix = dbComms.get_user_ratings(db, current_user_id)
	# store all movies from database in list
	movies = dbComms.get_all_movies(db)
	# end if there are not enough movies
	if(len(movies)<10):
		return recommendations
	# call get_predictions method that will return a sorted list of movies and their predictions of likeability for the current user
	predictions = predict.get_predictions(matrix)
	# initialize list of movie predictions
	recommendations = []
	# iterate over all predictions
	steps=0
	lowerLimit = startingPerc
	upperLimit = 1
	while (len(recommendations)<sampleSize and lowerLimit>=minPerc):
		for key in predictions:
			# take in account only positive predictions
			if (predictions[key] > lowerLimit and predictions[key]<=upperLimit):
				# create Movie object and set its parameters
				movie = Movie(movies[key].properties["id"], movies[key].properties["name"], [], 
				movies[key].properties["releaseDate"], movies[key].properties["overview"], 
				movies[key].properties["directorName"], movies[key].properties["posterPath"])
				# set movie recommendation percentage
				movie.percentage = str(round(predictions[key], 2) * 100) + "%"
				# add created object to list of movie predictions
				recommendations.append(movie)
		steps+=1
		upperLimit = lowerLimit
		lowerLimit = lowerLimit-stepSize
	# set size of roulette (default is 8, but if less movies are recommended it is equal to predicted movie list size)
	roulette_size = roulleteSize if len(recommendations) >= 8 else len(recommendations)
	# return moviePredictions template view with items of movie_prediction_list
	recommendations = random.sample(recommendations, roulette_size)
	return recommendations
