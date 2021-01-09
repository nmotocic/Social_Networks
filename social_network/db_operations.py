from pathlib import Path
import json

def clear(db):
    command = "MATCH (node) DETACH DELETE node"
    db.execute_query(command)

def connect_user_to_movie(db, user_id, movie_id):
    command = "MATCH (n:User),(m:Movie) WHERE n.fbid='" + user_id + "' AND m.imdbid='" + movie_id + "' CREATE (n)-[x:Searched]->(m)"
    db.execute_query(command)

def connect_searched_movie_to_book(db, user_id, book_isbn):
    command = "MATCH (n:User {fbid:'" + user_id + "'})-[x:Searched]->(m:Movie),(b:Book {isbn:'" + book_isbn + "'}) CREATE (m)-[y:BasedOn]->(b)"
    db.execute_query(command)

def add_user(db, user_id, user_name, user_mail, user_picture):
    fb_query = "CREATE (n:User {fbid:'" + user_id + "', name:'" + user_name + "', email:'" + user_mail + "', picture:'" + user_picture + "'})"
    db.execute_query(fb_query)

def add_movie(db, movie_id, movie_title, movie_year, movie_director, movie_poster):
    movie_query = "CREATE (m:Movie {imdbid:'" + movie_id + "', title:'" + movie_title + "', year:'" + movie_year + "', director:'" + movie_director + "', poster:'" + movie_poster + "'})"
    db.execute_query(movie_query)

def add_book(db, book_isbn, book_title, book_author, book_cover):
    book_query = "CREATE (o:Book {isbn:'" + book_isbn + "', title:'" + book_title + "', author:'" + book_author + "', cover:'" + book_cover + "'})"
    db.execute_query(book_query)

def get_book_based_on_movie(db, movie_id):
    command = "MATCH (m:Movie {imdbid:'" + movie_id + "'})-[:BasedOn]->(b:Book) RETURN b"
    books = db.execute_and_fetch(command)

    if books:
        for book in books:
            u = book['b']
            data = {"isbn": u.properties["isbn"], "title": u.properties["title"], "author": u.properties["author"], "cover": u.properties["cover"]}
            return json.dumps(data)
    else:
        return None

def get_movie_user_searched(db, user_id):
    command = "MATCH (n:User {fbid:'" + user_id + "'})-[:Searched]->(m:Movie) RETURN m"
    movies = db.execute_and_fetch(command)

    if movies:
        for movie in movies:
            u = movie['m']
            data = {"imdbid": u.properties["imdbid"], "title": u.properties["title"], "year": u.properties["year"], "director": u.properties["director"], "poster": u.properties["poster"]}
            return json.dumps(data)
    else:
        return None

def get_user_by_fb_id(db, user_id):
    command = "MATCH (n:User) WHERE n.fbid='" + user_id + "' RETURN n"
    users = db.execute_and_fetch(command)

    if users:
        for user in users:
            u = user['n']
            data = {"fbid": u.properties['fbid'], "name": u.properties["name"], "email": u.properties["email"], "picture": u.properties["picture"]}
            return json.dumps(data)
    else:
        return None

def get_user_by_fb_username(db, fb_username):
    command = "MATCH (n:User) WHERE n.name='" + fb_username + "' RETURN n"
    users = db.execute_and_fetch(command)

    if users:
        for user in users:
            u = user['n']
            data = {"fbid": u.properties['fbid'], "name": u.properties["name"], "email": u.properties["email"], "picture": u.properties["picture"]}
            return json.dumps(data)
    else:
        return None

def get_movie_by_imdb_id(db, imdb_id):
    command = "MATCH (m:Movie) WHERE m.imdbid='" + imdb_id + "' RETURN m"
    movies = db.execute_and_fetch(command)

    if movies:
        for movie in movies:
            u = movie['m']
            data = {"imdbid": u.properties["imdbid"], "title": u.properties["title"], "year": u.properties["year"], "director": u.properties["director"], "poster": u.properties["poster"]}
            return json.dumps(data)
    else:
        return None

def get_book_by_isbn(db, isbn):
    command = "MATCH (o:Book) WHERE o.isbn='" + isbn + "' RETURN o"
    books = db.execute_and_fetch(command)

    if books:
        for book in books:
            u = book['o']
            data = {"isbn": u.properties["isbn"], "title": u.properties["title"], "author": u.properties["author"], "cover": u.properties["cover"]}
            return json.dumps(data)
    else:
        return None

def get_first_user(db):
    command = "MATCH (n:User) RETURN n"
    users = db.execute_and_fetch(command)

    for user in users:
        u = user['n']
        data = {"fbid": u.properties['fbid'], "name": u.properties["name"], "email": u.properties["email"], "picture": u.properties["picture"]}
        return json.dumps(data)

