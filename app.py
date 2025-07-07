#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
CORS(app)  # Allow all origins for testing

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MYSQL_HOST'] = 'gateway01.eu-central-1.prod.aws.tidbcloud.com'
app.config['MYSQL_PORT'] = 4000
app.config['MYSQL_USER'] = '2wzHdmFpocYGaEr.root'
app.config['MYSQL_PASSWORD'] = 'INb2B81TQp1BgyY5'
app.config['MYSQL_DB'] = 'test'  # Default DB
app.json.compact = False

migrate = Migrate(app, db)
mysql = MySQL(app)

db.init_app(app)

@app.route('/')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT 1")  # Test query
    result = cursor.fetchone()
    return f"TiDB Connected! Query result: {result}"


@app.route('/heroes', methods=['GET'])
def heroes():
    heroes=[hero.to_dict() for hero in Hero.query.all()]

    response=make_response(
        heroes,
        200
    )

    return response


@app.route('/heroes/<int:id>', methods=['GET'])
def hero_by_id(id):
    hero = Hero.query.get(id)
    if hero is None:
        return {"error": "Hero not found"}, 404
    hero_dict = hero.to_dict()
    return hero_dict, 200


@app.route('/powers', methods=['GET'])
def powers():
    powers=[power.to_dict() for power in Power.query.all()]

    response=make_response(
        powers,
        200
    )

    return response


@app.route('/powers/<int:id>', methods=['GET'])
def power_by_id(id):
    power = Power.query.get(id)
    if power is None:
        return {"error": "Power not found"}, 404
    power_dict = power.to_dict()
    return power_dict, 200


@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({'error':'Power not found'}), 404
    
    data = request.get_json()

    if 'name' in data:
        power.name = data['name']
    
    if 'description' in data:
        if len(data['description']) < 20:
            return jsonify(errors="Description must be at least 20 characters"), 400
        power.description = data['description']

    db.session.commit()
    return jsonify(power.to_dict()), 200



@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    
    strength = data.get('strength')
    hero_id = data.get('hero_id')
    power_id = data.get('power_id')

    
    if strength not in ['Weak', 'Average', 'Strong']:
        return jsonify({"errors": ["Invalid strength value"]}), 400

    
    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)

    if not hero or not power:
        return jsonify({"errors": ["Hero or Power not found"]}), 404

    
    hero_power = HeroPower(
        strength=strength,
        power_id=power_id,
        hero_id=hero_id
    )

    db.session.add(hero_power)
    db.session.commit()

    
    response_data = {
        "id": hero_power.id,
        "hero_id": hero.id,
        "power_id": power.id,
        "strength": hero_power.strength,
        "hero": {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        },
        "power": {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
    }

    return jsonify(response_data), 201






@app.route('/hero_powers/<int:id>', methods=['DELETE'])
def delete_hero_power(id):
    hero_power = HeroPower.query.get(id)
    if hero_power is None:
        return jsonify({"error": "Hero Power not found"}), 404
    db.session.delete(hero_power)
    db.session.commit()
    return jsonify({"message": "Hero Power deleted successfully"}), 200



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
