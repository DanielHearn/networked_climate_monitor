import dateutil.parser
from datetime import timedelta
from flask import Flask, render_template, jsonify, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from passlib.hash import bcrypt
from marshmallow import ValidationError, validate
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from helpers import get_unit_from_type, create_settings
from schema import UserSchema, SensorSchema, ClimateDataSchema

# Load Flask
app = Flask(__name__)
api = Api(app)

# Initialise configuration variables
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a060dc4d401ffdb1b91bf5db8430f88d'
app.config['JWT_SECRET_KEY'] = '13071ce246c22add4f57eeb916f4d46d'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

api_key = 'xgLxTX7Nkem5qc9jllg2'

db = SQLAlchemy(app)
jwt = JWTManager(app)


# Create the database if it doesn't already exist
@app.before_first_request
def create_tables():
    db.create_all()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)


# Specify custom error message for expired tokens
@jwt.expired_token_loader
def expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 'Error',
        'errors': ['The {} token has expired'.format(token_type)]
    }), 401


# Specify custom error message for revoked tokens
@jwt.revoked_token_loader
def revoked_token_loader_callback():
    return jsonify({
        'status': 'Error',
        'errors': ['The token is invalid as it has been revoked']
    }), 401


# Specify custom error message for missing authorisation headers
@jwt.unauthorized_loader
def unauthorized_loader_callback(msg):
    return jsonify({
        'status': 'Error',
        'errors': [msg]
    }), 401


# MODELS

class UserModel(db.Model, SerializerMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    settings = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<UserModel %r>' % self.email

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def return_all(cls):
        return {'users': list(map(lambda x: x.to_dict(), UserModel.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Error during row deletion'}

    @staticmethod
    def generate_hash(password):
        return bcrypt.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return bcrypt.verify(password, hash)


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class SensorModel(db.Model, SerializerMixin):
    __tablename__ = 'sensor'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return '<SensorModel %r>' % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Error during row deletion'}


class ClimateModel(db.Model, SerializerMixin):
    __tablename__ = 'climate'

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)
    battery_voltage = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Climate %r>' % self.id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Error during row deletion'}


class SensorDataModel(db.Model, SerializerMixin):
    __tablename__ = 'sensordata'

    id = db.Column(db.Integer, primary_key=True)
    climate_id = db.Column(db.Integer, db.ForeignKey('climate.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Sensor Data %r>' % self.id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Error during row deletion'}


climate_data_schema = ClimateDataSchema()
sensor_schema = SensorSchema()
user_schema = UserSchema()


class UserLogin(Resource):
    # Get access token and refresh token if a valid email and password are received
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, 400

        # Validate and deserialize input
        try:
            data = user_schema.load(json_data)
        except ValidationError as err:
            return err.messages, 422

        current_user = UserModel.find_by_email(data['email'])

        if not current_user:
            return {'message': 'UserModel {} doesn\'t exist'.format(data['email'])}

        if UserModel.verify_hash(data['password'], current_user.password):
            try:
                expires = timedelta(days=365)
                access_token = create_access_token(identity=data['email'], expires_delta=expires)
                refresh_token = create_refresh_token(identity=data['email'])
                return {
                    'status': 'Successful login',
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            except:
                return {'status': 'Error', 'errors': [
                    'Error in generating tokens'
                ]}, 500
        else:
            return {'status': 'Error', 'errors': [
                'Email or password is incorrect'
            ]}, 401


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.save_to_db()
            return {'status': 'Access token has been revoked'}
        except:
            return {'status': 'Error', 'errors': [
                'Error in revoking access token'
            ]}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.save_to_db()
            return {'status': 'Refresh token has been revoked'}
        except:
            return {'status': 'Error', 'errors': [
                'Error in revoking refresh token'
            ]}, 500


class TokenRefresh(Resource):
    # Return a new access token if a valid refresh token is received
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        try:
            access_token = create_access_token(identity=current_user)
            return {'access_token': access_token}
        except:
            return {'status': 'Error', 'errors': [
                'Error in refreshing access token'
            ]}, 500


class Users(Resource):
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, 400

        # Validate and deserialize input
        try:
            data = user_schema.load(json_data)
        except ValidationError as err:
            return err.messages, 422

        if len(UserModel.query.all()):
            return {'message': 'An account already exists'}

        new_user = UserModel(
            email=data['email'],
            password=UserModel.generate_hash(data['password']),
            settings=str(create_settings())
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            return {
                       'status': 'UserModel {} was successfully created'.format(data['email']),
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200
        except:
            return {'status': 'Error', 'errors': ['Account creation failed']}, 500

    @jwt_required
    def get_all(self):
        return UserModel.return_all()

    @jwt_required
    def delete_all(self):
        return UserModel.delete_all()


class ClimateData(Resource):
    # Create new climate data if a valid api key is input
    def post(self, sensor_id):
        json_data = request.get_json(force=True)
        input_api_key = request.args.get('api_key')

        if not json_data:
            return {"message": "No input data provided"}, 400

        # Validate and deserialize input
        try:
            data = climate_data_schema.load(json_data)
        except ValidationError as err:
            return err.messages, 422

        if input_api_key == api_key:

            sensor = SensorModel.query.filter_by(id=sensor_id).first()
            if sensor:
                if data['battery_voltage'] and data['date'] and data['climate_data']:
                    battery_voltage = data['battery_voltage']
                    date = dateutil.parser.parse(data['date'])
                    sensors_data = data['climate_data']
                    print(sensors_data)

                    climate_data = ClimateModel(sensor_id=sensor_id, battery_voltage=battery_voltage, date=date)
                    climate_data.save_to_db()

                    climate_id = climate_data.to_dict()['id']

                    for sensor_data in sensors_data:
                        value = sensor_data['value']
                        data_type = sensor_data['type']

                        unit = get_unit_from_type(data_type)

                        sensor_obj = SensorDataModel(climate_id=climate_id, value=value, type=data_type, unit=unit)
                        db.session.add(sensor_obj)

                    db.session.commit()
                    return {'status': 'Sensor data successfully created.'}, 200
            return {'status': 'Sensor doesn\'t exist'}, 500
        return {'status': 'Invalid API key'}, 500

    @jwt_required
    def get(self, sensor_id):
        input_quantity = request.args.get('quantity')
        input_range_start = request.args.get('range_start')
        input_range_end = request.args.get('range_end')

        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            quantity = 20
            input_quantity = input_quantity
            if input_quantity:
                quantity = input_quantity

            range_start = input_range_start
            range_end = input_range_end
            if (range_start and range_end is None) or (range_start is None and range_end):
                return jsonify({'status': 'Invalid date range'})
            elif range_start and range_end:
                date_start = dateutil.parser.parse(range_start)
                date_end = dateutil.parser.parse(range_end)

                # Get climate data between the two dates
                climate_data = ClimateModel.query.order_by(ClimateModel.id.desc()).filter(
                    ClimateModel.sensor_id == sensor_id,
                    ClimateModel.date <= date_end,

                    ClimateModel.date >= date_start)
            else:
                # Get the most recent climate data limited by the specified quantity
                climate_data = ClimateModel.query.order_by(ClimateModel.id.desc()).filter_by(sensor_id=sensor_id).limit(
                    quantity)

            climate_dict_list = []
            for climate in climate_data:
                climate_dict = climate.to_dict()
                climate_id = climate_dict['id']
                sensor_data = SensorDataModel.query.filter_by(climate_id=climate_id)
                sensor_dict_list = []
                for sensor in sensor_data:
                    sensor_dict = sensor.to_dict()
                    sensor_dict_list.append(sensor_dict)
                climate_dict['climate_data'] = sensor_dict_list
                climate_dict_list.append(climate_dict)

            return {'climate_data': climate_dict_list}, 200
        return {'status': 'Sensor doesn\'t exist'}, 500

    @jwt_required
    def delete(self, sensor_id):
        return jsonify({'status': 'Sensor climate data successfully deleted.'})


class Sensor(Resource):
    @jwt_required
    def delete(self, sensor_id):
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            sensor.save_to_db()
            return {'status': 'Sensor successfully deleted.'}, 200
        return {'status': 'Sensor doesn\'t exist'}, 500

    @jwt_required
    def get(self, sensor_id):
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            return jsonify(sensor.to_dict())
        return {'status': 'Sensor doesn\'t exist'}, 500


class Sensors(Resource):
    # Create new sensor if a valid api_key is input
    def post(self):
        json_data = request.get_json(force=True)
        input_api_key = request.args.get('api_key')

        if not json_data:
            return {'status': 'Error', 'errors': "No body json data provided"}, 422

        # Validate and deserialize json data for sensor
        try:
            data = sensor_schema.load(json_data)
        except ValidationError as err:
            return {'status': 'Error', 'errors': err.messages}, 422

        if input_api_key == api_key:
            name = data['name']
            sensor_id = data['sensor_id']
            user_id = data['user_id']

            # Check if that sensor already exists
            if SensorModel.query.filter_by(id=sensor_id).first():
                return {'status': 'Error', 'errors': ['A sensor with that id already exists']}, 500

            try:
                sensor = SensorModel(name=name, id=sensor_id, user_id=user_id)
                sensor.save_to_db()
                return {'status': 'Sensor successfully created.'}
            except:
                return {'status': 'Error', 'errors': ['Error while adding sensor to database']}, 500
        else:
            return {'status': 'Error', 'errors': ['Invalid api key']}, 401

    # Get all sensors in an array
    @jwt_required
    def get(self):
        try:
            sensors_list = SensorModel.query.all()
            sensor_dict_list = []

            # Convert all sensors into dicts
            for sensor in sensors_list:
                sensor_dict_list.append(sensor.to_dict())
            return {'status': 'Sensors successfully retrieved', 'sensors': sensor_dict_list}, 200
        except:
            return {'status': 'Error', 'errors': ['Error while retrieving sensors from database']}, 500

    # Delete all sensors
    @jwt_required
    def delete(self):
        try:
            SensorModel.delete_all()
            return {'status': 'Sensors successfully deleted.'}, 200
        except:
            return {'status': 'Error', 'errors': ['Error while deleting all sensors from database']}, 500


## RESOURCES

# Account Resources
api.add_resource(UserLogin, '/api/login')
api.add_resource(UserLogoutAccess, '/api/logout/access')
api.add_resource(UserLogoutRefresh, '/api/logout/refresh')
api.add_resource(TokenRefresh, '/api/token/refresh')
api.add_resource(Users, '/api/account')

# Sensor Resources
api.add_resource(Sensor, '/api/sensors/<int:sensor_id>')
api.add_resource(Sensors, '/api/sensors')
api.add_resource(ClimateData, '/api/sensors/<int:sensor_id>/climate-data')


## ROUTES

@app.route('/api', defaults={'path': ''})
@app.route('/api/<path:path>')
def api_catch_all(path):
    return jsonify({'status': 'error', 'errors': ['Endpoint doesn\'t exist']}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")


if __name__ == '__main__':
    print('Starting server')
    app.run(debug=True, host='192.168.1.156')
