

#Twitter/Facebook
class User:
	def __init__(self,username,email,avatarUrl="",creationDate=""):
		self.username = username
		self.email = email
		self.creationDate=creationDate
		if avatarUrl is None:
			self.avatarUrl = ""
		else:
			self.avatarUrl = avatarUrl
	def setName(self,username):
		self.username = username

#TMDB
class Movie:
	def __init__(self,id,name,genres,releaseDate,overview,directorName,posterPath):
		self.id = id
		self.name = name
		self.genres = genres #List
		self.releaseDate = releaseDate
		self.overview = overview
		self.directorName = directorName
		self.posterPath = posterPath


class Genre:
	def __init__(self,name):
		self.name = name

class ratingSource:
	def __init__(self,name):
		self.name = name