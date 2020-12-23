import json, requests, sys

headers = {
	"Content-Type": "application/json",
	"trakt-api-version": "2",
	"trakt-api-key": "d13fd92d1fa91c135b829b792aab3816a84068ef99b73631ffc5ac9b68d915c6",
}

def clear(db):
	clear_users(db)
	clear_shows(db)
	clear_reviews(db)

def clear_users(db):
	command = "MATCH (node:User) DETACH DELETE node"
	db.execute_query(command)

def clear_shows(db):
	command = "MATCH (node:Show) DETACH DELETE node"
	db.execute_query(command)

def clear_reviews(db):
	command = "MATCH (node:Show) DETACH DELETE node"
	db.execute_query(command)

def populate(db):
	clear_shows(db)
	clear_reviews(db)
	r = requests.get(url="http://api.tvmaze.com/shows")
	data = r.content
	json_data = json.loads(data)
	count = 0
	for i in range(50):
		if i < len(json_data):
			name = json_data[i]["name"].replace('"', "")
			name = name.replace("'", "")
			db.execute_query("CREATE (n:Show { id:" + str(count) + ", name:'" + name + "'});")
			count += 1
	r = requests.get(
		url="https://private-anon-c710405608-trakt.apiary-proxy.com/shows/trending",
		headers=headers,
	)
	data = r.content
	json_data = json.loads(data)
	for i in range(50):
		if i < len(json_data):
			name = json_data[i]["show"]["title"].replace('"', "")
			name = name.replace("'", "")
			db.execute_query("CREATE (n:Show { id:" + str(count) + ", name:'" + name + "'});")
			count += 1

def add_user(db, name, email):
	count = 0
	result = db.execute_and_fetch("MATCH (n:User) WHERE n.name = '" + name + "' RETURN n")
	users = sum(1 for _ in result)
	if users == 0:
		for i in db.execute_and_fetch("MATCH (n:User) RETURN n"):
			count += 1
		db.execute_query("CREATE (n:User { id:" + str(count) + ", name: '" + name + "', email: '" + email + "'});")
		#db.execute_query("MATCH (a:User),(b:Show) WHERE a.id = " + str(count) + " AND b.id = 0 CREATE (a)-[r:Review]->(b);")
	return count

def get_graph(db):
	command = "MATCH (n1:User)-[e:Review]-(n2:Show) RETURN n1,n2,e;"
	relationships = db.execute_and_fetch(command)

	link_objects = []
	node_objects = []
	added_nodes = []
	for relationship in relationships:
		e = relationship["e"]
		data = {"source": e.nodes[0], "target": e.nodes[1]}
		link_objects.append(data)

		n1 = relationship["n1"]
		if not (n1.id in added_nodes):
			data = {"id": n1.id, "name": n1.properties["name"]}
			node_objects.append(data)
			added_nodes.append(n1.id)

		n2 = relationship["n2"]
		if not (n2.id in added_nodes):
			data = {"id": n2.id, "name": n2.properties["name"]}
			node_objects.append(data)
			added_nodes.append(n2.id)
	data = {"links": link_objects, "nodes": node_objects}

	return json.dumps(data)


def get_users(db):
	command = "MATCH (n:User) RETURN n;"
	users = db.execute_and_fetch(command)
	user_objects = []
	for user in users:
		u = user["n"]
		data = {"id": u.properties["id"], "name": u.properties["name"], "email": u.properties["email"]}
		user_objects.append(data)

	return json.dumps(user_objects)

def get_shows(db):
	command = "MATCH (n:Show) RETURN n;"
	shows = db.execute_and_fetch(command)

	show_objects = []
	for show in shows:
		s = show["n"]
		data = {"id": s.properties["id"], "name": s.properties["name"]}
		show_objects.append(data)

	return json.dumps(show_objects)


def get_realtionships(db):
	command = "MATCH (n1:User)-[r:Review]-(n2) RETURN n1,n2,r;"
	relationships = db.execute_and_fetch(command)

	relationship_objects = []
	for relationship in relationships:
		n1 = relationship["n1"]
		n2 = relationship["n2"]
		review = relationship["r"]

		data = {"User": n1.properties["name"], "Show": n2.properties["name"], "Score": review.properties["score"]}
		relationship_objects.append(data)

	return json.dumps(relationship_objects)

def add_review(db, user_id, show_id, score):
	results = db.execute_and_fetch("MATCH (a:User{id:" + user_id + "})-[:Review]->(b:Show{id:" + show_id + "}) RETURN a, b;")
	print("-----------------------")
	reviews = sum(1 for _ in results)
	if reviews == 0:
		command = "MATCH (a:User{id:" + user_id + "}),(b:Show{id:" + show_id + "}) CREATE (a)-[r:Review{score:" + score + "}]->(b);"
	else:
		command = "MATCH (a:User{id:" + user_id + "})-[r:Review]->(b:Show{id:" + show_id + "}) SET r.score=" + score + ";"
	#command = "MATCH (a:User{id:" + user_id + "}),(b:Show{id:" + show_id +"}) CREATE (a)-[:Review{score:" + str(score) + "}]->(b);"
	db.execute_query(command)