import os
import json
import requests
from flask import Flask, render_template, redirect, url_for, session
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from social_network.database.memgraph import Memgraph
from social_network import db_operations
from flask_scss import Scss

app = Flask(__name__)
app.debug = True
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

Scss(app, static_dir='static', asset_dir='assets')

app.config['FACEBOOK_OAUTH_CLIENT_ID'] = ''
app.config['FACEBOOK_OAUTH_CLIENT_SECRET'] = ''
facebook_bp = make_facebook_blueprint(rerequest_declined_permissions=True)
facebook_bp.rerequest_declined_permissions = True
app.register_blueprint(facebook_bp, url_prefix="/login")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

omdbAPI = "https://www.omdbapi.com/?apikey=65f7361a&"

openLibraryAPI = "http://openlibrary.org/"
openLibraryCoverAPI = "http://covers.openlibrary.org/"

db = Memgraph()

@app.route('/')
@app.route('/index')
def index():
   user_data_json = None
   movie_data_json = None
   book_data_json = None
   if 'userid' in session:
      user_id = session['userid']
      user_node = db_operations.get_user_by_fb_id(db, user_id)
      if user_node:
         user_data_json = json.loads(user_node)
         movie_node = db_operations.get_movie_user_searched(db, user_id)
         if movie_node:
            movie_data_json = json.loads(movie_node)
            novel_node = db_operations.get_book_based_on_movie(db, movie_data_json["imdbid"])
            if novel_node:
               book_data_json = json.loads(novel_node)
   return render_template("index.html", user_data=user_data_json, movie_data=movie_data_json, book_data=book_data_json)

@app.route('/find')
def movie():
    return render_template("findMovies.html")

@app.route('/movie')
def find():
    return render_template("movieDisplay.html")

@app.route('/discover')
def discover():
    return render_template("movieDiscover.html")

@app.route('/fb_login')
def fb_login():
   if not facebook.authorized:
      return redirect(url_for("facebook.login"))
   resp = facebook.get("/me?fields=id,name,email,picture,birthday")
   if resp.ok and resp.text:
      resp_json = resp.json()
      return resp_json
      user_id = resp_json["id"]
      user_name = resp_json["name"]
      user_mail = resp_json["email"]
      user_picture = resp_json["picture"]["data"]["url"]
      user_node = db_operations.get_user_by_fb_id(db, user_id)
      if user_node is None:
         db_operations.add_user(db, user_id, user_name, user_mail, user_picture)
      session['userid'] = user_id
      return redirect(url_for("index"))
   else:
      return "<h1>Request failed</h1>"

@app.route('/movie_api/<movie_title>')
def movie_api(movie_title):
   omdbAPIcall = omdbAPI + "t=" + movie_title
   resp = requests.get(omdbAPIcall)
   if resp.ok:
      resp_content = resp.content
      resp_json = json.loads(resp_content.decode("utf-8"))
      movie_id = resp_json["imdbID"]
      movie_title = resp_json["Title"]
      movie_year = resp_json["Year"]
      movie_director = resp_json["Director"]
      movie_poster = resp_json["Poster"]
      movie_node = db_operations.get_movie_by_imdb_id(db, movie_id)
      if movie_node is None:
         db_operations.add_movie(db, movie_id, movie_title, movie_year, movie_director, movie_poster)
         if 'userid' in session:
            db_operations.connect_user_to_movie(db, session['userid'], movie_id)
      return redirect(url_for("index"))
   else:
      return "<h1>Request failed</h1>"

@app.route('/book_api/<book_title>')
def book_api(book_title):
   openLibraryListAPIcall = openLibraryAPI + "search.json?title=" + book_title
   resp_list = requests.get(openLibraryListAPIcall)
   if resp_list.ok:
      resp_list_content = resp_list.content
      resp_list_content_json = json.loads(resp_list_content)
      book_isbn_array = resp_list_content_json["docs"][0]["isbn"]
      book_isbn = book_isbn_array[0]
      for isbn in book_isbn_array:
         try:
            openLibraryBookAPIcall = openLibraryAPI + "api/books?bibkeys=ISBN:" + isbn + "&jscmd=details&format=json"
            resp_book = requests.get(openLibraryBookAPIcall)
            if resp_book.ok:
               resp_book_content = resp_book.content
               resp_book_content_json = json.loads(resp_book_content)
               book_title = resp_book_content_json["ISBN:" + isbn]["details"]["title"]
               book_author = resp_book_content_json["ISBN:" + isbn]["details"]["authors"][0]["name"]
               book_isbn = isbn
               break
            else:
               return "<h1>Request failed</h1>"
         except:
            continue
      openLibraryCoverAPIcall = openLibraryCoverAPI + "b/isbn/" + book_isbn + ".jpg"
      resp_cover = requests.get(openLibraryCoverAPIcall)
      if resp_cover.ok:
         book_cover = openLibraryCoverAPIcall
      else:
         return "<h1>Request failed</h1>"
      book_node = db_operations.get_book_by_isbn(db, book_isbn)
      if book_node is None:
         db_operations.add_book(db, book_isbn, book_title, book_author, book_cover)
         if 'userid' in session:
            db_operations.connect_searched_movie_to_book(db, session['userid'], book_isbn)
      return redirect(url_for("index"))
   else:
      return "<h1>Request failed</h1>"