from social_network.dbModels import *
import operator
import collections

def parseMovieRelations(relations):
	retList=[]
	movieDict={}
	genreList=[]
	for relation in relations:
		#Relations
		mov = relation['m']
		gen = relation['g']
		#Props
		mId = mov.properties["id"]
		#Set movie
		genreList.clear()
		if mId not  in movieDict:
			movie=Movie(mId,mov.properties["name"],genreList.copy(),mov.properties["releaseDate"],mov.properties["overview"],mov.properties["directorName"],mov.properties["posterPath"])
			movieDict[mId]=movie
		#Set genres
		movieDict[mId].genres.append(gen.properties["name"])
	#Finalize
	for movie in movieDict:
		retList.append(movieDict[movie])
	return retList

def parseMovieRelationSingle(relations):
	movieDict={}
	genreList=[]
	for relation in relations:
		#Relations
		mov = relation['m']
		gen = relation['g']
		#Props
		mId = mov.properties["id"]
		#Set movie
		genreList.clear()
		if mId not  in movieDict:
			movie=Movie(mId,mov.properties["name"],genreList.copy(),mov.properties["releaseDate"],mov.properties["overview"],mov.properties["directorName"],mov.properties["posterPath"])
			movieDict[mId]=movie
		#Set genres
		movieDict[mId].genres.append(gen.properties["name"])
	return movie

def parseMovieRatings(relations):
	movieDict={}
	calculatedDict = {}
	for relation in relations:
		#Relations
		mov = relation['m']
		rel = relation['r']
		#Props
		mId = mov.properties["id"]
		if mId not  in movieDict:
			movieDict[mId]=[0,0]
		if rel.properties["rating"]==1:
			movieDict[mId][0]=movieDict[mId][0]+1
		movieDict[mId][1]=movieDict[mId][1]+1
	for movie in movieDict:
		calculatedDict[movie] = movieDict[movie][0]/movieDict[movie][1]+0.05*movieDict[movie][1]
	return sorted(calculatedDict, key=calculatedDict.get, reverse=True)

def parseMovieRatingSingle(relations):
	calculatedDict = {}
	for relation in relations:
		#Relations
		rel = relation['r']
		return rel.properties["rating"]