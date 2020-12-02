from flask import Flask, redirect, url_for, render_template
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from social_network.database import Memgraph, connection 
from social_network import db_operations
from typing import Any
import json
from pathlib import Path
import mgclient
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = "totallysecretkey"

twitter_blueprint = make_twitter_blueprint(api_key='4iWV26Hm4pMdkZ2N0J5M70IPf',
                                           api_secret='HTPujWBqB1qpfEmOUzbeS3G3jG83bg9QJ48kZlryiEpoFvkJLE')

app.register_blueprint(twitter_blueprint, url_prefix='/login')

DEEZER_APP_ID = "446062"
DEEZER_SECRET_KEY = "077494748568d9e43bc157dcd3d3b36b"
DEEZER_REDIRECT_URI = "http://127.0.0.1:5000/deezer"

_here = Path(__file__)
data_path = _here.parent.joinpath("social_network/snapshots/lastfm_data.csv")

@app.route('/twitter')
def twitter_login():
   if not twitter.authorized:
      return redirect(url_for('twitter.login'))
   account_info = twitter.get('account/settings.json')
   
   if account_info.ok:
     #account_info_json = account_info.json()

      account = twitter.get('account/verify_credentials.json',params={'include_email':'true'})
      account_json = account.json()
      return '<h1>Your Twitter name is @{}'.format(account_json['screen_name'])
   
   return '<h1> Request failed!</h1>'

@app.route('/')
def index() -> Any:
   if not twitter.authorized:
      return redirect(url_for('twitter.login'))
   account = twitter.get('account/verify_credentials.json', params={'include_email':'true'})
   account_json = account.json()
   print(account_json)

   url = (f'https://connect.deezer.com/oauth/auth.php?app_id={DEEZER_APP_ID}'
         f'&redirect_uri={DEEZER_REDIRECT_URI}&perms=basic_access,email')
      
   db = Memgraph()
   db_operations.clear(db)

   db_operations.generate_user(db, account_json)
   
   songs = db_operations.generate_songs(data_path)
   artists = db_operations.generate_artists(data_path)
   tags = db_operations.generate_tags(data_path)


   db_operations.populate_database(db, songs, artists, tags)
   db_operations.generate_connections(db, data_path)
   
   return render_template("index.html", name = account_json["name"], data=account_json)

@app.route('/deezer', methods=['GET'])
def deezer_login():
    # retrieve the authorization code given in the url
    code = request.args.get('code')

    # request the access token
    url = (f'https://connect.deezer.com/oauth/access_token.php?app_id={DEEZER_APP_ID}'
           f'&secret={DEEZER_APP_SECRET}&code={code}&output=json')
    response = requests.get(url)
    
    # If it's not a good code we will get this error
    if response.text == 'wrong code':
        return 'wrong code'
    
    # We have our access token
    response = response.json()
    return response['access_token']

@app.route('/play', methods=['GET'])
def play():
   url = (f'https://www.deezer.com/plugins/player?'
           f'app_id={DEEZER_APP_ID}'
           f'&format=classic'
           f'&autoplay=true'
           f'&playlist=true'
           f'&width=700&height=400&color=ff0000'
           f'&layout=dark'
           f'&size=medium'
           f'&type=playlist'
           f'&id=8431002822'
           f'&popup=true'
           f'&repeat='
           f'0&current_song_index=0'
           f'&current_song_time=2'
           f'&playing=true')

   return redirect(url)


if __name__ == 'main' :
   app.run(debug = True)