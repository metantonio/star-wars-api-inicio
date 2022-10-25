from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False) 
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    description = db.Column(db.String(120), unique=False, nullable=False)
    #conectando la tabla user con las tablas pivote de planets, vehicles y people 
    user_favorite = db.relationship("Favorite_People", backref="user")
    user_favorite_planet = db.relationship("Favorite_Planets", backref="user")
    user_favorite_vehicles = db.relationship("Favorite_Vehicles", backref="user")


    #de manera automática, el nombre de la tabla es el nombre de la clase en minúscula
    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "descripcion": self.description
        }


# Tabla Characters
class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    height = db.Column(db.Float)
    mass = db.Column(db.Float)
    hair_color  = db.Column(db.String(250))
    skin_color  = db.Column(db.String(250))
    eye_color  = db.Column(db.String(250))
    birth_year = db.Column(db.Integer)
    gender = db.Column(db.String(250))
    homeworld = db.Column(db.String(250))
    people_favorite = db.relationship("Favorite_People", backref="people")

#Characters serialize
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "homeworld": self.homeworld
        }

# Tabla Pivote: Characters/ Favorites
class Favorite_People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #con el nombre de la tabla user y atributo id
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    #Esta es una tabla pivote para relacionar User y Characters, relación muchos a muchos

    def serialize(self):
        return {
            "id": self.id,
            "user_email": User.query.get(self.user_id).serialize()['email'],
            "character_name": People.query.get(self.people_id).serialize()['name']          
        }


# Tabla Planets
class Planets (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    diameter = db.Column(db.Float)
    rotation_Period = db.Column(db.Float)
    orbital_Period = db.Column(db.Float)
    gravity = db.Column(db.String(100))
    population = db.Column(db.Integer)
    climate = db.Column(db.String(100))
    terrain = db.Column(db.String(100))
    surface_Water = db.Column(db.Integer)
    planets_favorite = db.relationship("Favorite_Planets", backref="planets")

    #Planets serialize
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "rotation_Period": self.rotation_Period,
            "orbital_Period": self.orbital_Period,
            "gravity": self.gravity,
            "population": self.population,
            "climate": self.climate,
            "terrain": self.terrain,
            "surface_Water": self.surface_Water
        }

# Tabla Pivote: Planets/ Favorites    
#Esta es una tabla pivote para relacionar User y Planets, relación muchos a muchos
class Favorite_Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #con el nombre de la tabla user y atributo id
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))

    #serialize
    def serialize(self):
        return {
            "id": self.id,
            "user_email": User.query.get(self.user_id).serialize()['email'],
            "planet_name": Planets.query.get(self.planet_id).serialize()['name'],
        }

class Vehicles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(250))
    vehicle_class = db.Column(db.String(250))
    manufacturer = db.Column(db.String(250))
    cost_in_credits = db.Column(db.Integer)
    length = db.Column(db.Float)
    crew = db.Column(db.Integer)
    passengers = db.Column(db.Integer)
    max_atmosphering_speed = db.Column(db.Float)
    cargo_capacity = db.Column(db.Float)
    consumables = db.Column(db.String(250))
    vehicles_favorite = db.relationship("Favorite_Vehicles", backref="vehicles")

    #serialize
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "vehicle_class": self.vehicle_class,
            "manufacturer": self.manufacturer,
            "cost_in_credits": self.cost_in_credits,
            "length": self.length,
            "crew": self.crew,
            "passengers": self.passengers,
            "max_atmosphering_speed": self.max_atmosphering_speed,
            "cargo_capacity": self.cargo_capacity,
            "consumables": self.consumables
        }

# Tabla Pivote: Vehicles/ Favorites
class Favorite_Vehicles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #con el nombre de la tabla user y atributo id
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    #Esta es una tabla pivote para relacionar User y Vehicles, relación muchos a muchos

    def serialize(self):
        return {
            "id": self.id,
            "user_email": User.query.get(self.user_id).serialize()['email'],
            "vehicle_name": Vehicles.query.get(self.vehicles_id).serialize()['name']       
        }