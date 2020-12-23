import os, sys, json, requests
from social_network.database import Memgraph, db_operations
from flask import Flask, render_template, redirect, jsonify, url_for, make_response, session, request
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook

app = Flask(__name__)
app.config["SECRET_KEY"] = "matejevtajnikljuc"

facebook_bp = make_facebook_blueprint()
app.register_blueprint(facebook_bp, url_prefix="/login")

app.config["FACEBOOK_OAUTH_CLIENT_ID"] = "141269584858"
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = "f9343613c08bce71b9540819a11478fd"
app.config["Client ID"] = "d13fd92d1fa91c135b829b792aab3816a84068ef99b73631ffc5ac9b68d915c6"
app.config["Client Secret"] = "478d1b0e4d246c979307850e5d03241ab6d3120d51a3b260dc8bc9657d4fb560"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

headers = {
    "Content-Type": "application/json",
    "trakt-api-version": "2",
    "trakt-api-key": "d13fd92d1fa91c135b829b792aab3816a84068ef99b73631ffc5ac9b68d915c6"
}

db = Memgraph()

@app.route("/clear")
def clear():
    db_operations.clear(db)
    return redirect(url_for("index"))
   
@app.route("/populate")
def populate():
    db_operations.populate(db)
    return redirect(url_for("index"))

@app.route("/")
@app.route("/index")
def index():
    if "username" not in session and facebook.authorized:
        print("-------------------------")
        resp_json = facebook.get("/me?fields=id,name,email").json()
        print("Adding " + resp_json["name"] + " to session...")
        session["username"] = resp_json["name"]
        session["id"] = resp_json["id"]
        for i in resp_json:
            print("i: " + i)
            print("resp_json[" + i + "]: " + resp_json[i])
        session["db_id"] = db_operations.add_user(db, resp_json["name"], resp_json["email"])
        print("-------------------------")
        sys.stdout.flush()
    return render_template("index.html")

@app.route("/logout")
def logout():
    print("-------------------------")
    for i in session:
        print(session[i])
    resp_json = facebook.get("/me").json()
    if "id" in resp_json:
        print(resp_json["id"])
        #facebook.delete("/" + resp_json["id"] + "/permissions")
    print("Clearing current session...")
    session.clear()
    print("-------------------------")
    sys.stdout.flush()
    return redirect(url_for("index"))

@app.route("/login")
def login():
    if not facebook.authorized:
        print("Redirecting to facebook login page...")
        sys.stdout.flush()
        return redirect(url_for("facebook.login"))
    print("You are already logged in...")
    sys.stdout.flush()
    return redirect(url_for("index"))    

@app.route("/query")
def query():
    return render_template("query.html")

@app.route("/get-graph", methods=["POST"])
def get_graph():
    db = Memgraph()
    response = make_response(
        jsonify(db_operations.get_graph(db)), 200)
    return response

@app.route("/get-users", methods=["POST"])
def get_users():
    db = Memgraph()
    response = make_response(
        jsonify(db_operations.get_users(db)), 200)
    return response

@app.route("/get-relationships", methods=["POST"])
def get_relationships():
    db = Memgraph()
    response = make_response(
        jsonify(db_operations.get_realtionships(db)), 200)
    return response
    
@app.route("/get-shows", methods=["POST"])
def get_shows():
    db = Memgraph()
    response = make_response(
        jsonify(db_operations.get_shows(db)), 200)
    return response

@app.route("/add-review", methods=["POST"])
def add_review():
    if "username" in session:
        user_id = str(session["db_id"])
        show_id = str(request.form["show_id"])
        score = str(request.form["score"])
        print("User " + session["username"] + " with id " + user_id + " is rating a show with id " + show_id + " with a score of " + score)
        sys.stdout.flush()
        db = Memgraph()
        db_operations.add_review(db, user_id, show_id, score)
    return redirect(url_for("query"))