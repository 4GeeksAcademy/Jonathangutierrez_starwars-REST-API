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
from models import db, User, People, Planet
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

@app.route('/user', methods=['GET'])
def get_user():

    all_user = User.query.all()
    result = [element.serialize() for element in all_user]
    return jsonify(result), 200

@app.route('/people', methods=['GET'])
def get_all_people():

    all_people = People.query.all()
    result = [element.serialize() for element in all_people]
    return jsonify(result), 200

@app.route('/people/<int:id>', methods=['GET'])
def get_one_person(id):


    #Aquí cambia la petición y solicitamos sólo una persona por el ID que hemos definido en el Endpoint de arriba (@app.route('/people/<int:id>')
    person = People.query.get(id)
    if person:
        return jsonify(person.serialize()), 200
    else:
        return jsonify({"message": "Person not found"}), 404

@app.route('/people', methods=['POST'])
def post_people():

    # obtener los datos de la petición que están en formato JSON a un tipo de datos entendibles por pyton (a un diccionario). En principio, en esta petición, deberían enviarnos 3 campos: el nombre, la descripción del planeta y la población
    data = request.get_json()

    # creamos un nuevo objeto de tipo Planet
    
    people = People(name=data['name'], gender=data['gender'], height=data['height'], mass=data['mass'])


    # añadimos el planeta a la base de datos
    db.session.add(people)
    db.session.commit()

    response_body = {"msg": "Person inserted successfully"}
    return jsonify(response_body), 200


@app.route('/planet', methods=['GET'])
def get_planets():
    allPlanets = Planet.query.all()
    result = [element.serialize() for element in allPlanets]
    return jsonify(result), 200

@app.route('/planet/<int:id>', methods=['GET'])
def get_one_planet(id):


    #Aquí cambia la petición y solicitamos sólo una planeta por el ID que hemos definido en el Endpoint de arriba (@app.route('/planet/<int:id>')
    planet = Planet.query.get(id)
    if planet:
        return jsonify(planet.serialize()), 200
    else:
        return jsonify({"message": "Planet not found"}), 404

@app.route('/planet', methods=['POST'])
def post_planet():

    # obtener los datos de la petición que están en formato JSON a un tipo de datos entendibles por pyton (a un diccionario). En principio, en esta petición, deberían enviarnos 3 campos: el nombre, la descripción del planeta y la población
    data = request.get_json()

    # creamos un nuevo objeto de tipo Planet
    planet = Planet(name=data['name'], description=data['description'], population=data['population'])

    # añadimos el planeta a la base de datos
    db.session.add(planet)
    db.session.commit()

    response_body = {"msg": "Planet inserted successfully"}
    return jsonify(response_body), 200

  


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
