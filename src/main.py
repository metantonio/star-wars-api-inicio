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
from models import db, User, People, Favorite_People, Planets, Favorite_Planets, Vehicles, Favorite_Vehicles, TokenBlockedList
from datetime import date, time, datetime, timezone
#from models import Person

#importar jwt-flask-extended
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

#importar Bcrypt para encriptar
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")  # Change this!
jwt = JWTManager(app)

# Setup de Bcrypt
bcrypt = Bcrypt(app)

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
    print(body['username']) 
    descripcion=""
    try:
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

        password = bcrypt.generate_password_hash(body['password'],10).decode("utf-8")

        new_user = User(email=body['email'], password=password, is_active=True, description=descripcion)
        users = User.query.all()
        users = list(map( lambda user: user.serialize(), users))

        for i in range(len(users)):
            if(users[i]['email']==new_user.serialize()['email']):
                raise APIException("El usuario ya existe" , status_code=400)
                
        print(new_user)
        #print(new_user.serialize())
        db.session.add(new_user) 
        db.session.commit()
        return jsonify({"mensaje": "Usuario creado exitosamente"}), 201

    except Exception as err:
        db.session.rollback()
        print(err)
        return jsonify({"mensaje": "error al registrar usuario"}), 500
    
    
   

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
    return jsonify("usuario eliminado exitosamente"), 200

#Función get para llamar a todos los personajes de la base de datos
@app.route('/people', methods=['GET'])
def get_people():
    peoples = People.query.all()
    #print(users)
    peoples = list(map( lambda people: people.serialize(), peoples)) 
    #print(users)  
    return jsonify(peoples), 200

#Función get para llamar personajes individualmente de la base de datos
@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    if people_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    person = People.query.get(people_id)
    if person == None:
        raise APIException("El usuario no existe", status_code=400)  
    return jsonify(person.serialize()), 200

#Función get para llamar a todos los planetas de la base de datos
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    planets = list(map( lambda planet: planet.serialize(), planets))  
    return jsonify(planets), 200

#Función get para llamar planetas individualmente de la base de datos
@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    if planet_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    planet = Planets.query.get(planet_id)
    if planet == None:
        raise APIException("El planeta no existe", status_code=400)  
    return jsonify(planet.serialize()), 200

#Función get para llamar a todos los vehículos de la base de datos
@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicles.query.all()
    vehicles = list(map( lambda vehicle: vehicle.serialize(), vehicles))  
    return jsonify(vehicles), 200

#Función get para llamar vehículos individualmente de la base de datos
@app.route('/vehicle/<int:vehicle_id>', methods=['GET'])
def get_vehicle_by_id(vehicle_id):
    if vehicle_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    vehicle = Vehicles.query.get(vehicle_id)
    if vehicle == None:
        raise APIException("El vehículo no existe", status_code=400)  
    return jsonify(vehicle.serialize()), 200

#Función get para llamar a la lista de personajes favoritos del usuario
@app.route('/user/favorites', methods=['GET'])
def get_favorites():
    favorite_peoples = Favorite_People.query.all()
    favorite_peoples = list(map( lambda favorite_people: favorite_people.serialize(), favorite_peoples))
    favorite_planets = Favorite_Planets.query.all()
    favorite_planets = list(map( lambda favorite_planet: favorite_planet.serialize(), favorite_planets))
    favorite_vehicles = Favorite_Planets.query.all()
    favorite_vehicles = list(map( lambda favorite_vehicle: favorite_vehicle.serialize(), favorite_vehicles))
    favorites_list =  favorite_peoples + favorite_planets + favorite_vehicles
    print(favorites_list)
    return jsonify(favorites_list), 200

#Funciones para agregar items a cada tabla (personajes, planetas, vehículos)

#Función post para agregar personajes individuales a la base de datos
@app.route('/people', methods=['POST'])
def create_new_person():
    body = request.get_json()
    #validaciones
    if body is None:
        raise APIException("Body está vacío" , status_code=400)
    if body['name'] is None or body['name']=="":
        raise APIException("name es inválido" , status_code=400)

    new_character = People(name=body['name'], height=body['height'], mass=body['mass'], hair_color=body['hair_color'], skin_color=body['skin_color'], eye_color=body['eye_color'], birth_year=body['birth_year'], gender=body['gender'], homeworld=body['homeworld'])
    characters = People.query.all()
    characters = list(map( lambda character: character.serialize(), characters))

    # for i in range(len(characters)):
    #     if(characters[i]['name']==new_character.serialize()['name']):
    #         raise APIException("El personaje ya existe" , status_code=400)
            
    print(new_character)
    #print(new_user.serialize())
    db.session.add(new_character) 
    db.session.commit()
    
    return jsonify({"mensaje": "Personaje creado exitosamente"}), 201

#Función post para agregar planetas individuales a la base de datos
@app.route('/planet', methods=['POST'])
def create_new_planet():
    body = request.get_json()
    #validaciones
    if body is None:
        raise APIException("Body está vacío" , status_code=400)
    if body['name'] is None or body['name']=="":
        raise APIException("name es inválido" , status_code=400)

    new_planets = Planets(name=body['name'], diameter=body['diameter'], rotation_Period=body['rotation_Period'], orbital_Period=body['orbital_Period'], gravity=body['gravity'], population=body['population'], climate=body['climate'], terrain=body['terrain'], surface_Water=body['surface_Water'])
    planets = Planets.query.all()
    planets = list(map( lambda planet: planet.serialize(), planets))

    for i in range(len(planets)):
        if(planets[i]['name']==new_planets.serialize()['name']):
            raise APIException("El planeta ya existe" , status_code=400)
            
    print(new_planets)
    #print(new_user.serialize())
    db.session.add(new_planets) 
    db.session.commit()
    
    return jsonify({"mensaje": "Planeta creado exitosamente"}), 201

#Función post para agregar vehículos individuales a la base de datos
@app.route('/vehicle', methods=['POST'])
def create_new_vehicle():
    body = request.get_json()
    #validaciones
    if body is None:
        raise APIException("Body está vacío" , status_code=400)
    if body['name'] is None or body['name']=="":
        raise APIException("name es inválido" , status_code=400)

    new_vehicles = Vehicles(name=body['name'], model=body['model'], vehicle_class=body['vehicle_class'], manufacturer=body['manufacturer'], cost_in_credits=body['cost_in_credits'], length=body['length'], crew=body['crew'], passengers=body['passengers'], max_atmosphering_speed=body['max_atmosphering_speed'], cargo_capacity=body['cargo_capacity'], consumables=body['consumables'])
    vehicles = Vehicles.query.all()
    vehicles = list(map( lambda vehicle: vehicle.serialize(), vehicles))

    for i in range(len(vehicles)):
        if(vehicles[i]['name']==new_vehicles.serialize()['name']):
            raise APIException("El vehículo ya existe" , status_code=400)
            
    print(new_vehicles)
    db.session.add(new_vehicles) 
    db.session.commit()
    
    return jsonify({"mensaje": "Vehículo creado exitosamente"}), 201

#Funciones para eliminar items de cada tabla (personajes, planetas, vehículos)

#Funcion delete para eliminar personajes individuales a la base de datos
@app.route('/people/<int:item_id>', methods=['DELETE'])
def delete_character_by_id(item_id):
    if item_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    character = People.query.get(item_id)
    if character == None:
        raise APIException("El personaje no existe", status_code=400)  
    db.session.delete(character)
    db.session.commit()
    return jsonify("personaje eliminado exitosamente"), 200

#Funcion delete para eliminar planetas individuales a la base de datos
@app.route('/planet/<int:item_id>', methods=['DELETE'])
def delete_planet_by_id(item_id):
    if item_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    planet = Planets.query.get(item_id)
    if planet == None:
        raise APIException("El planeta no existe", status_code=400)  
    db.session.delete(planet)
    db.session.commit()
    return jsonify("planeta eliminado exitosamente"), 200

#Funcion delete para eliminar vehículos individuales a la base de datos
@app.route('/vehicle/<int:item_id>', methods=['DELETE'])
def delete_vehicle_by_id(item_id):
    if item_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    vehicle = Vehicles.query.get(item_id)
    if vehicle == None:
        raise APIException("El vehículo no existe", status_code=400)  
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify("vehículo eliminado exitosamente"), 200


#Funciones para eliminar items de la lista de favoritos

#Funcion delete para eliminar items de la lista de personajes favoritos
@app.route('/favorites/people/<int:item_id>', methods=['DELETE'])
def delete_favorite_character_by_id(item_id):
    if item_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    item = People.query.get(item_id)
    if item == None:
        raise APIException("El personaje no existe", status_code=400)  
    db.session.delete(item)
    db.session.commit()
    return jsonify("Personaje eliminado exitosamente"), 200

#Funcion delete para eliminar items de la lista de planetas favoritos
@app.route('/favorites/planet/<int:item_id>', methods=['DELETE'])
def delete_favorite_planet_by_id(item_id):
    if item_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    item = Planets.query.get(item_id)
    if item == None:
        raise APIException("El planeta no existe", status_code=400)  
    db.session.delete(item)
    db.session.commit()
    return jsonify("Planeta eliminado exitosamente"), 200

#Funcion delete para eliminar items de la lista de planetas favoritos
@app.route('/favorites/vehicle/<int:item_id>', methods=['DELETE'])
def delete_favorite_vehicle_by_id(item_id):
    if item_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    item = Vehicles.query.get(item_id)
    if item == None:
        raise APIException("El vehículo no existe", status_code=400)  
    db.session.delete(item)
    db.session.commit()
    return jsonify("Vehículo eliminado exitosamente"), 200


#Función get para actualizar personajes individualmente de la base de datos
@app.route('/people/<int:people_id>', methods=['PUT'])
def put_people_by_id(people_id):
    if people_id==0:
        raise APIException("Id no puede ser igual a 0", status_code=400)  
    person = People.query.get(people_id)#buscar por ID es la manera mas eficiente de realizar busquedas en las bases de datos
    if person == None:
        raise APIException("El usuario no existe", status_code=400) 
    body = request.get_json()
    #validaciones
    if body is None:
        raise APIException("Body está vacío" , status_code=400)
    #validamos si viene el campo name en el body o no (despues de hacer el request.get_json())
    if not body['name'] is None:
        person.name = body['name']
    db.session.commit()     
    return jsonify(person.serialize()), 200


@app.route('/people/busqueda', methods=['POST'])
def busqueda_people():
    body = request.get_json()
    #validaciones
    if body is None:
        raise APIException("Body está vacío" , status_code=400)
    if not body['name'] is None:    
        found = People.query.filter(People.name==body['name']).all() #va a encontrar todas las coincidencias        
        found = list(map( lambda item: item.serialize(), found))
        print(found)
    if found == None:
        raise APIException("El personaje no existe", status_code=400)  
    return jsonify(found), 200


@app.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    email = body['email']
    password = body['password']

    user = User.query.filter_by(email=email).first()

    if user is None:
        raise APIException("usuario no existe", status_code=401)
    
    #validamos el password si el usuario existe y si coincide con el de la BD
    if not bcrypt.check_password_hash(user.password, password):
        raise APIException("usuario o password no coinciden", status_code=401)

    access_token = create_access_token(identity= user.id)
    return jsonify({"token": access_token})
    
@app.route('/helloprotected', methods=['get']) #endpoint
@jwt_required() #decorador que protege al endpoint
def hello_protected(): #definición de la función
    #claims = get_jwt()
    print("id del usuario:", get_jwt_identity()) #imprimiendo la identidad del usuario que es el id
    user = User.query.get(get_jwt_identity()) #búsqueda del id del usuario en la BD

    #get_jwt() regresa un diccionario, y una propiedad importante es jti
    jti=get_jwt()["jti"] 

    tokenBlocked = TokenBlockedList.query.filter_by(token=jti).first()
    #cuando hay coincidencia tokenBloked es instancia de la clase TokenBlockedList
    #cuando No hay coincidencia tokenBlocked = None

    if isinstance(tokenBlocked, TokenBlockedList):
        return jsonify(msg="Acceso Denegado")

    response_body={
        "message":"token válido",
        "user_id": user.id, #get_jwt_identity(),
        "user_email": user.email,
        "description": user.description
    }

    return jsonify(response_body), 200

@app.route('/logout', methods=['get']) #endpoint
@jwt_required()
def logout():
    print(get_jwt())
    jti=get_jwt()["jti"]
    now = datetime.now(timezone.utc)

    tokenBlocked = TokenBlockedList(token=jti, created_at=now)
    db.session.add(tokenBlocked)
    db.session.commit()

    return jsonify({"message":"token bloqueado"})

@app.route('/suspendido/<int:user_id>', methods=['PUT']) #endpoint
@jwt_required()
def user_suspended(user_id):
    if get_jwt_identity() != 1:
        return jsonify({"message":"Operación no permitida"}), 403
        
    user = User.query.get(user_id)
   
    #validamos si viene el campo name en el body o no (despues de hacer el request.get_json())
    if user.is_active:
        user.is_active = False
        db.session.commit()   
        return jsonify({"message":"Usuario suspendido"}), 203
    else:
        user.is_active = True
        db.session.commit()   
        return jsonify({"message":"Usuario reactivado"}), 203

   


# esta linea SIEMPRE DEBE QUEDAR AL FINAL   
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


