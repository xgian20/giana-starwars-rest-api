"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Person, Planet, Users, FavoritePeople, FavoritePlanets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# routes below are for people starwars

@app.route('/people', methods=['GET'])
def get_people():
    response_body = Person.query.all()
    response_body = list(map(lambda x: x.serialize(), response_body))
    return jsonify(response_body), 200

@app.route('/people/<int:person_id>', methods=['GET'])
def get_one_person(person_id):

    single_person = Person.query.get(person_id)

    if single_person is None:
        raise APIException(f'Person ID {person_id} is not found.', status_code=404)

    single_person = Person.query.get(person_id)
    return jsonify(single_person.serialize()), 200

# routes below are for planets starwars

@app.route('/planets', methods=['GET'])
def get_planets():
    response_body = Planet.query.all()
    response_body = list(map(lambda x: x.serialize(), response_body))
    return jsonify(response_body), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):

    single_planet = Planet.query.get(planet_id)

    if single_planet is None:
        raise APIException(f'Planet ID {planet_id} is not found.', status_code=404)

    single_planet = Planet.query.get(planet_id)
    return jsonify(single_planet.serialize()), 200

# users and favorites

@app.route('/users', methods=['GET'])
def get_all_users():
    users = Users.query.all()
    serialized_users = []
    for user in users:
        serialized_users.append(user.serialize())
    return jsonify({"msg": "List of users: ", "users": serialized_users}), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    user = Users.query.filter_by(id = user_id).first()
    if user is None: 
        return jsonify({"msg": "Here is your user", "user": user.serialize()}), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_one_user_favorites(user_id):
    user = Users.query.filter_by(id = user_id).first()
    if user is None: 
        return jsonify({"msg": "User not found"}), 404
    favorite_planets = FavoritePlanets.query.filter_by(user_id_favorites = user_id)
    favorite_people = FavoritePeople.query.filter_by(user_id_favorites = user_id)
    serialized_planets = []
    serialized_people = []
    for favorite_planet in favorite_planets:
        serialized_planets.append(favorite_planet.serialize())
    for favorite_people in favorite_people:
        serialized_people.append(favorite_people.serialize())
    return jsonify({"msg": f"Here is the list of User {user_id}'s favorite planets & people", "planets": serialized_planets, "people": serialized_people})

@app.route('/users/<int:user_id>/favorites/people/<int:person_id>', methods=['POST'])
def add_one_person_to_favorites(user_id,person_id):
    user = Users.query.filter_by(id = user_id).first()
    if user is None: 
        return jsonify({"msg": "user not found"}), 404 
    
    person = Person.query.filter_by(id = person_id).first()
    if person is None: 
        return jsonify({"msg": "person not found"}), 404 
    
    check_favorite = FavoritePeople.query.filter_by(favorite_person_id = person_id).first()
    if check_favorite :
        return jsonify({"msg": "This person is already on your Favorite's list"}), 409
    
    favorite_person = FavoritePeople(user_id_favorites = user_id, favorite_person_id = person_id)
    db.session.add(favorite_person) 
    db.session.commit()
    db.session.refresh(favorite_person)
    return jsonify({"msg": "Your favorite person has been added!"}), 201

@app.route('/users/<int:user_id>/favorites/people/<int:person_id>', methods=['DELETE'])
def delete_one_person_from_favorites(user_id, person_id):
    user = Users.query.filter_by(id = user_id).first()
    if user is None: 
        return jsonify({"msg": "user not found"}), 404 
    
    person = Person.query.filter_by(id = person_id).first()
    if person is None: 
        return jsonify({"msg": "person not found"}), 404 
    
    favorite_person = FavoritePeople.query.filter_by(user_id_favorites = user_id, favorite_person_id = person_id).first()
    if favorite_person is None :
        return jsonify({"msg": "This person is not in your favorites"}), 404
    
    db.session.delete(favorite_person) 
    db.session.commit()
    return jsonify({"msg": "This person has been removed from your favorites"}), 200 

@app.route('/users/<int:user_id>/favorites/planets/<int:planet_id>', methods=['DELETE'])
def delete_one_planet_from_favorites(user_id, planet_id):
    user = Users.query.filter_by(id = user_id).first()
    if user is None: 
        return jsonify({"msg": "user not found"}), 404 
    
    planet = Planet.query.filter_by(id = planet_id).first()
    if planet is None: 
        return jsonify({"msg": "planet not found"}), 404 
    
    favorite_planet = FavoritePlanets.query.filter_by(user_id_favorites = user_id, favorite_planet_id = planet_id).first()
    if favorite_planet is None :
        return jsonify({"msg": "This planet is not in your favorites"}), 404
    
    db.session.delete(favorite_planet) 
    db.session.commit()
    return jsonify({"msg": "This planet has been removed from your favorites"}), 200




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
