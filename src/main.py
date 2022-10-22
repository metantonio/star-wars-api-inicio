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
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
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
def handle_hello():
    users = User.query.all()
    #print(users)
    users = list(map( lambda user: user.serialize(), users)) #(user)=>user.serialize()
    #print(users)
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }   
    return jsonify(users), 200

@app.route('/user', methods=['POST'])
def create_new_user():
    body = request.get_json()
    #print(body['username']) 
    descripcion=""

    if body is None or "email" not in body:
        raise APIException("Body está vacío o email no viene en el body, es inválido" , status_code=400)
    if body['email'] is None or body['email']=="":
        raise APIException("email es inválido" , status_code=400)
    if body['password'] is None or body['password']=="":
        raise APIException("password es inválido" , status_code=400)
    if body['description'] is None or body['description']=="":
        descripcion="no hay descripción"
    else:
        descripcion=body['description']

    new_user = User(email=body['email'], password=body['password'], is_active=True, description=descripcion)
    users = User.query.all()
    users = list(map( lambda user: user.serialize(), users))

    for i in range(len(users)):
        if(users[i]['email']==new_user.serialize()['email']):
            raise APIException("El usuario ya existe" , status_code=400)
            
    print(new_user)
    #print(new_user.serialize())
    db.session.add(new_user) 
    db.session.commit()
    
    return jsonify({"mensaje": "Usuario creado exitósamente"}), 201

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    if user_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    user = User.query.get(user_id)
    if user == None:
        raise APIException("El usuario no existe", status_code=400)  
    #print(user.serialize())
    return jsonify(user.serialize()), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
    if user_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    user = User.query.get(user_id)
    if user == None:
        raise APIException("El usuario no existe", status_code=400)  
    #print(user.serialize())
    db.session.delete(user)
    db.session.commit()
    return jsonify("usuario eliminado exitósamente"), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
