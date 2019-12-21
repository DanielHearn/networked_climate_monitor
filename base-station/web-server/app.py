from flask import Flask, render_template, redirect, jsonify, request
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
import dateutil.parser

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)
salt = 'f10026b636'

def get_unit_from_type(type):
    units = {
        'Humidity': '%',
        'Temperature': 'c',
        'Pressure': 'hPa'
    }

    return units[type]


class User(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

class Sensor(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return '<Sensor %r>' % self.name

class Climate(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)
    battery_voltage = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Climate %r>' % self.id

class SensorData(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    climate_id = db.Column(db.Integer, db.ForeignKey('climate.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Sensor Data %r>' % self.id

@app.route('/api/account', methods=["GET", "POST"])
def account_view():
    if request.method == "POST":
        body = request.json
        if body['email'] and body['password']:
            email = body['email']
            password = body['password']
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()

            return jsonify({'status': 'success'})
        return jsonify({'status': 'Invalid body data.'})
    users = User.query.all()
    if len(users):
        user = users[0]
        print(user)
        return jsonify(user.to_dict())


@app.route('/api/sensors/<int:sensor_id>/climate-data', methods=["POST", "GET", 'DELETE'])
def sensor_climate_view(sensor_id=None):
    sensor = Sensor.query.filter_by(id=sensor_id).first()
    if sensor:
        if request.method == "POST":
            body = request.json
            if body['battery_voltage'] and body['date'] and body['climate_data']:
                battery_voltage = body['battery_voltage']
                date = dateutil.parser.parse(body['date'])
                sensor_data = body['climate_data']

                climate_data = Climate(sensor_id=sensor_id, battery_voltage=battery_voltage, date=date)
                db.session.add(climate_data)
                db.session.commit()
                print(climate_data)
                climate_id = climate_data.to_dict()['id']
                print(climate_id)

                for sensor in sensor_data:
                    value = sensor['value']
                    data_type = sensor['type']

                    unit = get_unit_from_type(data_type)

                    sensor_obj = SensorData(climate_id=climate_id, value=value, type=data_type, unit=unit)
                    db.session.add(sensor_obj)

                db.session.commit()
                return jsonify({'status': 'Sensor data successfully created.'})
            return jsonify({'status': 'Invalid body data.'})
        if request.method == "DELETE":
            return jsonify({'status': 'Sensor climate data successfully deleted.'})
        #climate_data = Climate.query.filter_by(sensor_id=sensor_id)
        climate_data = Climate.query.all()
        climate_dict_list = []
        for climate in climate_data:
            climate_dict = climate.to_dict()
            climate_id = climate_dict['id']
            sensor_data = SensorData.query.filter_by(climate_id=climate_id)
            print(sensor_data)
            sensor_dict_list = []
            for sensor in sensor_data:
                sensor_dict = sensor.to_dict()
                sensor_dict_list.append(sensor_dict)
            climate_dict['climate_data'] = sensor_dict_list

            climate_dict_list.append(climate_dict)
        return jsonify(climate_dict_list)
    return jsonify({'status': 'Sensor doesn\'t exist'})


@app.route('/api/sensors/<int:sensor_id>', methods=["GET", 'DELETE'])
def sensor_view(sensor_id=None):
    sensor = Sensor.query.filter_by(id=sensor_id).first()
    if sensor:
        if request.method == "DELETE":
            db.session.delete(sensor)
            db.session.commit()
            return jsonify({'status': 'Sensor successfully deleted.'})
        return jsonify(sensor.to_dict())
    return jsonify({'status': 'Sensor doesn\'t exist'})


@app.route('/api/sensors', methods=["GET", "POST", 'DELETE'])
def sensors_view():
    if request.method == "POST":
        body = request.json
        if body['name'] and body['sensor_id'] and body['user_id']:
            name = body['name']
            sensor_id = body['sensor_id']
            user_id = body['user_id']

            sensor = Sensor(name=name, id=sensor_id, user_id=user_id)
            db.session.add(sensor)
            db.session.commit()
            return jsonify({'status': 'Sensor successfully created.'})
        return jsonify({'status': 'Invalid body data.'})
    if request.method == "DELETE":
        sensors = Sensor.query.delete()
        db.session.commit()
        return jsonify({'status': 'Sensors successfully deleted.'})
    sensors_list = Sensor.query.all()
    if len(sensors_list):
        sensor_dict_list = []
        for sensor in sensors_list:
            sensor_dict_list.append(sensor.to_dict())
        return jsonify(sensor_dict_list)
    return jsonify([])


@app.route('/api/delete-all', methods=["GET"])
def delete_all():
    return jsonify({'status': 'success'})


@app.route('/api', defaults={'path': ''})
@app.route('/api/<path:path>')
def api_catch_all(path):
    return jsonify({'status': 'error', 'errors': ['Endpoint doesn\'t exist']})


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")


if __name__ == '__main__':
    print('Starting server')
    db.create_all()
    app.run(debug=True, host='192.168.1.156')
