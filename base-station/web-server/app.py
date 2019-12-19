from flask import Flask, render_template, redirect, jsonify, request
from tinydb import TinyDB, Query, where

db = TinyDB('db.json')
app = Flask(__name__)

salt = 'f10026b636'

def init_database():
    print('Initialising database')
    db.purge_tables()
    db.purge()

    account_table = db.table('account')
    account_table.insert({'user': {
        'email': '',
        'password': ''
    }})

    sensors_table = db.table('sensors')

    settings_table = db.table('settings')
    settings_table.insert({'settings': {
        'preferred_temperature_unit': 'c'
    }})

    print('Initialising complete')
    print(db.all())


def create_sensor(identifier, name, climate_data):
    if climate_data is None:
        climate_data = []
    if name is None:
        name = 'Sensor'
    sensor = {
        'identifier': identifier,
        'name': name,
        'climate_data': climate_data
    }
    return sensor


def create_climate_data(time_date, battery_voltage, sensor_data):
    if sensor_data is None:
        sensor_data = []
    climate_data = {
        'time_date': time_date,
        'battery_voltage': battery_voltage,
        'sensor_data': sensor_data
    }
    return climate_data


def create_sensor_data(type, value, unit):
    sensor_data = {
        'type': type,
        'value': value,
        'unit': unit
    }
    return sensor_data


@app.route('/api/account', methods=["GET", "POST"])
def account():
    account_table = db.table('account')
    account_data = account_table.get(where('user').exists())
    if request.method == "POST":
        body = request.json
        account_table.update({'user': {'email': body['email'], 'password': body['password']}}, where('user').exists())
        return jsonify({'status': 'success'})
    return jsonify(account_data)


@app.route('/api/sensors', methods=["GET", "POST", 'DELETE'])
def sensors():
    sensors_table = db.table('sensors')
    if request.method == "POST":
        body = request.json

        if sensors_table.search(where('identifier') == body['identifier']):
            return jsonify({'status': 'Error', 'Errors': ['Sensor already exists.']})

        new_sensor = create_sensor(
            body['identifier'],
            body['name'],
            body['climate_data']
        )
        sensors_table.insert(new_sensor)
        return jsonify({'status': 'Sensor successfully created.'})
    if request.method == "DELETE":
        sensors_table.remove(where('identifier').exists())
        return jsonify({'status': 'Sensors successfully deleted.'})
    sensors_data = sensors_table.search(where('identifier').exists())
    return jsonify(sensors_data)


@app.route('/api/delete-all', methods=["GET"])
def delete_all():
    init_database()
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
    if not (db.tables()):
        init_database()
    else:
        print('Existing database found')
    app.run(debug=True, host='192.168.1.180')
