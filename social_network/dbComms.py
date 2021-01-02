import json
import sys
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

def userFavoritesMovie(db,email,movieId):
	if email is None or movieId is None:
		return
	if userCheck(db,email)==False or movieCheck(db,movieId) == False:
		return
	if(userCheckFavorited(db,email,movieId)):
		return
	qry = 'MATCH (u:User),(m:Movie) WHERE m.id = "{0}" AND u.email = "{1}" CREATE (u)-[r:favorited]->(m)'.format(movieId,email)
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
	if movieCheck(db,movie.id)==True:
		return
	qry = 'CREATE (n:Movie {{id: "{0}",name: "{1}", releaseDate: "{2}", overview: "{3}"}})'.format(str(movie.id),cleanString(movie.name),movie.releaseDate,cleanString(movie.overview))
	db.execute_query(qry)
	#Genre creation and linking
	for genre in movie.genres:
		#Add genres
		genreCreate(db,genre["name"])
		#Link to genre
		qry= 'MATCH (m:Movie),(g:Genre) WHERE m.id = "{0}" AND g.name = "{1}" CREATE (m)-[r:isGenre]->(g)'.format(str(movie.id),genre["name"])
		db.execute_query(qry)
	return

def movieGetAll(db):
	qry = 'MATCH (m:Movie)-[r:isGenre]->(g:Genre) RETURN m,r,g'
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)

def movieGetAllFavorited(db,email):
	qry = 'MATCH (u:User {{ email: "{0}"}})-[r2:favorited]->(m:Movie)-[r:isGenre]->(g:Genre) RETURN m,r,g'.format(email)
	relations = db.execute_and_fetch(qry)
	return parseMovieRelations(relations)

def movieGetByGenre(db,genre):
	qry = ('MATCH (:Genre {{name : "{0}"}})<-[:isGenre]-(m:Movie)-[r:isGenre]->(g:Genre) RETURN m,r,g').format(genre)
	relations = db.execute_and_fetch(qry)
	retList = parseMovieRelations(relations)
	for x in retList:
		x.genres.append(genre)
		x.genres.sort()
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

#Track controls

def trackCreateBulk(db,jsonData):
	retList=[]
	if jsonData is None:
		return
	for row in jsonData:
		#Create album
		alb = row["album"]
		album = Album(alb["id"],alb["name"],alb["release_date"],alb["total_tracks"])
		#Done album
		#Create artists
		artists = []
		for art in row["artists"]:#Create artist
			artist = Artist(art["id"],art["name"])
			artists.append(artist)
			#Done
		#Create track
		track=Track(row["id"],row["name"],album,artists)
		retList.append(track)
		trackCreate(db,track)
	return retList

def trackCheck(db,id):
	qry = 'MATCH (n:Track {{id: "{0}"}} ) RETURN n'.format(str(id))
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break;
	return ret

def trackCreate(db,track):
	if track.id is None:
		return
	if trackCheck(db,track.id)==True:
		return
	qry = 'CREATE (n:Track {{id: "{0}",name: "{1}"}})'.format(str(track.id),cleanString(track.name))
	db.execute_query(qry)
	#Artist creation and linking
	for artist in track.artists:
		#Add artist
		artistCreate(db,artist)
		#Link with artist
		qry = 'MATCH (t:Track),(a:Artist) WHERE t.id = "{0}" AND a.id = "{1}" CREATE (a)-[r:created]->(t)'.format(str(track.id),str(artist.id))
		db.execute_query(qry)
	#Album creation and linking
	albumCreate(db,track.album)
	qry = 'MATCH (t:Track),(a:Album) WHERE t.id = "{0}" AND a.id = "{1}" CREATE (a)-[r:contains]->(t)'.format(str(track.id),str(track.album.id))
	db.execute_query(qry)
	return

def trackGetAll(db):
	#qry = 'MATCH (a:Album)-[r1:contains]->(t:Track)<-[r2:created]-(r:Artist) RETURN a,r1,r2,t,r'
	qry = 'MATCH (a)-[r1:contains|created]->(t:Track) RETURN a,r1,t'
	relations = db.execute_and_fetch(qry)
	return parseTrackRelations(relations)

def trackGetByArtist(db,artist):
	qry = 'MATCH (r:Artist {{ id: "{0}" }})-[r2:created]->(t)<-[r1:contains|created]-(a) RETURN a,r1,t'.format(artist.id)
	relations = db.execute_and_fetch(qry)
	ret = parseTrackRelations(relations)
	for x in ret:
		x.artists.append(artist)
		x.artists.sort(key=nameSort)
	return ret

#Artist controls
def artistCheck(db,id):
	qry = 'MATCH (n:Artist {{id: "{0}"}} ) RETURN n'.format(id)
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break;
	return ret

def artistCreate(db,artist):
	if artist.id is None:
		return
	if artistCheck(db,artist.id)==True:
		return
	qry = 'CREATE (n:Artist {{id:"{0}" ,name: "{1}"}})'.format(artist.id,cleanString(artist.name))
	db.execute_query(qry)
	return

def artistGetAll(db):
	qry = 'MATCH (x:Artist) RETURN x'
	relations = db.execute_and_fetch(qry)
	retList=[]
	for relation in relations:
		art = relation['x']
		artist = Artist(art.properties["id"],art.properties["name"])
		retList.append(artist)
	#Finalize
	retList.sort(key=nameSort)
	return retList

def artistGetById(db,artistId):
	qry = 'MATCH (x:Artist {{id : "{0}"}}) RETURN x'.format(artistId)
	relations = db.execute_and_fetch(qry)
	for relation in relations:
		art = relation['x']
		artist = Artist(art.properties["id"],art.properties["name"])
		return artist

#Album controls

def albumCreate(db,album):
	if album.id is None:
		return
	if albumCheck(db,album.id)==True:
		return
	qry = 'CREATE (n:Album {{id: "{0}",name: "{1}",totalTracks: "{2}", releaseDate: "{3}"}})'.format(str(album.id),cleanString(album.name),str(album.totalTracks),album.releaseDate)
	db.execute_query(qry)
	return

def albumCheck(db,id):
	qry = 'MATCH (n:Album {{id: "{0}"}}) RETURN n'.format(str(id))
	result = db.execute_and_fetch(qry)
	ret = False
	for row in result:
		ret = True
		break;
	return ret

#Help functions
def cleanString(st):
	ret = st
	ret = ret.replace('"',"'")

	return ret

def nameSort(obj):
	return obj.name