

#Twitter
class User:
	def __init__(self,username,email):
		self.username = username
		self.email = email
	def setName(self,username):
		self.username = username

#TMDB
class Movie:
	def __init__(self,id,name,genres,releaseDate,overview):
		self.id = id
		self.name = name
		self.genres = genres #List
		self.releaseDate = releaseDate
		self.overview = overview


class Genre:
	def __init__(self,name):
		self.name = name

#Spotify
class Track:
	def __init__(self,id,name,album,artists):
		self.id = id
		self.name = name
		self.album = album #Album object
		self.artists = artists #List

class Album:
	def __init__(self,id,name,releaseDate,totalTracks):
		self.id = id
		self.name = name
		self.releaseDate = releaseDate
		self.totalTracks = totalTracks

class Artist:
	def __init__(self,id,name):
		self.id = id
		self.name = name

