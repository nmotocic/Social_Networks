import numpy as np
import sys


def get_prediction(user_movie, user_avg, param):
	# initialize parameters I - current row, J - current column, K - similar users taken into account for prediction
	I, J, K = param
	# initialize similarity dictionary
	sims = {}
	# iterate over all columns of average user ratings
	for col_num, col in enumerate(user_avg):
		# if current column is different from given column
		if not col_num == J:
			# initialize numerator
			numer = 0
			# initialize denominators
			denom_1, denom_2 = 0, 0
			# iterate over all user average movie ratings
			for i in range(len(col)):
				# multiply user rating by average user rating for single movie
				if not col[i] == -1:
					numer += user_avg[J][i] * col[i]
					# square average user rating for movie
					denom_1 += user_avg[J][i] * user_avg[J][i]
					# square current user rating for movie
					denom_2 += col[i] * col[i]
			# calculate similarities
			sim = 0
			if not numer == 0 and not denom_1 == 0 and not denom_2 == 0:
				sim = numer / (np.sqrt(denom_1) * np.sqrt(denom_2))
			# if similarity is higher than 0 and current user rating of movie exists
			if sim >= 0 and not user_movie[I][col_num] == 'X':
				# add similarity to similiarity dictionary
				sims[col_num] = sim
	# initialize prediction rating
	rating = 0
	# initialize sum of similarities
	sum_of_sims = 0
	# for each movie rating similarity with other users in similarity dictionary
	for col_num in sims:
		# add multiplied rating of current user and similarity factor of other users
		rating += float(float(user_movie[I][col_num]) * sims[col_num])
		# add number of similarities with other users for this column (movie)
		sum_of_sims += sims[col_num]
	if not sum_of_sims == 0:
		# average the rating out by dividing with number of similarities with other users
		rating /= sum_of_sims
	return rating


def get_predictions(matrix):
	# initialize index of line (row) in matrix
	line_index = 0
	# initialize user - movie matrix
	user_movie = []
	# initialize list of average movie ratings by users
	user_avg = []
	# initialize prediction dictionary
	predictions = {}
	# iterate over input matrix
	for line in matrix:
		# first line contains number of users N and number of movies M
		if line_index == 0:
			M = int(line.split(" ")[0])
			N = int(line.split(" ")[1])
		# if line is part of user - movie matrix
		elif line_index < M + 1:
			# add all ratings divided by space as list to user - movie matrix
			user_movie.append(line.rstrip().split(" "))
		# if line is after user - movie matrix
		elif line_index == M + 1:
			# transpose user - movie matrix to movie - user matrix
			movie_user = np.transpose(user_movie)
			# iterate over movie - user matrix
			for row in movie_user:
				# change all X to 0
				row = [-1 if x == 'X' else int(x) for x in row]
				avg = 0
				# calculate average rating of all nonzero ratings
				positives = []
				for x in row:
					if x >= 0:
						positives.append(x)
				if not len(positives) == 0:
					avg = sum(positives) / len(positives)
				# subtract average rating from all nonzero ratings
				for i in range(len(row)):
					if not row[i] == -1 and not row[i] == avg:
						row[i] = float(row[i] - avg)
				user_avg.append(row)
			# read current line which is the number of prediction queries
			Q = int(line)
			# initialize counter for queries
			counter = 0
		# if line is query
		elif M + 1 < line_index < M + Q + 2:
			# get prediction of user rating for movie
			prediction = get_prediction(user_movie, user_avg, list(map(int, line.rstrip().split(" "))))
			# get movie from query
			movie = int(line.rstrip().split(" ")[1])
			# add prediction to prediction dictionary
			predictions[int(line.rstrip().split(" ")[1])] = prediction / 5
			counter += 1
		line_index += 1
	# return sorted dictionary of recommended movies by rating prediction from highest to lowest
	return dict(sorted(predictions.items(), key=lambda movie: movie[1], reverse=True))
