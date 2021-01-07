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
def find():
    return render_template("findMovies.html")


# Route for getting to the movie page
@app.route('/movie/<imdb_id>')
def movie(imdb_id):
    omdbAPIcall = omdbAPI + "i=" + imdb_id
    resp = requests.get(omdbAPIcall)
    if resp.ok:
        resp_content = resp.content
        resp_json = json.loads(resp_content.decode("utf-8"))
        return render_template("movieDisplay.html", movie_data_json=resp_json)
    else:
        return "<h1>Request failed</h1>"
    

@app.route('/discover')
def discover():
    return render_template("movieDiscover.html")

@app.route('/profile')
def profile():
    return render_template("userProfile.html")

@app.route('/liked')
def liked():
    return render_template("likedList.html")

@app.route('/dislike')
def dislike():
    return render_template("dislikedList.html")

@app.route('/bookmarked')
def booked():
    return render_template("bookmarkedList.html")

@app.route('/login')
def login():
    return render_template("login.html")

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
