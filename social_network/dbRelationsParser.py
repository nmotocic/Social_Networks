from social_network.dbModels import *

def parseTrackRelations(relations):
	retList=[]
	trackDict={}
	artistList=[]
	for relation in relations:
		trk = relation['t']
		tId = trk.properties["id"]
		artistList.clear()
		if(tId not in trackDict):
			track=Track(tId,trk.properties["name"],None,artistList.copy())
			trackDict[tId]=track
		#Relations
		other = relation['a']
		if(relation['r1'].type == "contains"): #Other is album
			album = Album(other.properties["id"],other.properties["name"],other.properties["releaseDate"],other.properties["totalTracks"])
			trackDict[tId].album=album;
		if(relation['r1'].type == "created"): #Other is artist
			artist = Artist(other.properties["id"],other.properties["name"])
			trackDict[tId].artists.append(artist)
	#Finalize
	for track in trackDict:
		retList.append(trackDict[track])
	return retList

"""Backup
def parseTrackRelations(relations):
	retList=[]
	trackDict={}
	artistList=[]
	for relation in relations:
		trk = relation['t']
		tId = trk.properties["id"]
		artistList.clear()
		if(tId not in trackDict):
			track=Track(tId,trk.properties["name"],None,artistList.copy())
			trackDict[tId]=track
		#Relations
		if('a' in relation): #Other is album
			other = relation['a']
			album = Album(other.properties["id"],other.properties["name"],other.properties["releaseDate"],other.properties["totalTracks"])
			trackDict[tId].album=album;
		if('r' in relation): #Other is artist
			other = relation['r']
			artist = Artist(other.properties["id"],other.properties["name"])
			trackDict[tId].artists.append(artist)
	#Finalize
	for track in trackDict:
		retList.append(trackDict[track])
	return retList
"""

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
			movie=Movie(mId,mov.properties["name"],genreList.copy(),mov.properties["releaseDate"],mov.properties["overview"])
			movieDict[mId]=movie
		#Set genres
		movieDict[mId].genres.append(gen.properties["name"])
	#Finalize
	for movie in movieDict:
		retList.append(movieDict[movie])
	return retList
