import dateutil.parser
from datetime import timedelta, datetime
from flask import Flask, render_template, jsonify, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from passlib.hash import bcrypt
from marshmallow import ValidationError, validate
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS

from helpers import get_unit_from_type, create_settings, generate_reset_key
from schema import UserSchema, SensorSchema, ClimateDataSchema, ChangePasswordSchema

# Load Flask
app = Flask(__name__)
api = Api(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

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
    return {
        'status': 'Error',
        'errors': ['The {} token has expired'.format(token_type)]
    }, 401


# Specify custom error message for revoked tokens
@jwt.revoked_token_loader
def revoked_token_loader_callback():
    return {
        'status': 'Error',
        'errors': ['The token is invalid as it has been revoked']
    }, 401


# Specify custom error message for missing authorisation headers
@jwt.unauthorized_loader
def unauthorized_loader_callback(msg):
    return {
        'status': 'Error',
        'errors': [msg]
    }, 401


# MODELS

class UserModel(db.Model, SerializerMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    settings = db.Column(db.Text, nullable=False)
    reset_token = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return '<UserModel %r>' % self.email

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def return_first(cls):
        return UserModel.query.first()

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


climate_data_schema = ClimateDataSchema()
sensor_schema = SensorSchema()
user_schema = UserSchema()
change_password_schema = ChangePasswordSchema()


class UserLogin(Resource):
    # Get access token and refresh token if a valid email and password are received
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate and deserialize input
        try:
            data = user_schema.load(json_data)
        except ValidationError as err:
            return {'status': 'Error', 'errors': err.messages}, 422

        current_user = UserModel.find_by_email(data['email'])

        if not current_user:
            return {'status': 'Error', 'errors': [
                'User doesn\'t exist'
            ]}, 500

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
            revoked_token.save()
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
            revoked_token.save()
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
            return {'status': 'Error', 'errors': ['No input data provided']}, 400

        # Validate and deserialize input
        try:
            data = user_schema.load(json_data)
        except ValidationError as err:
            return {'status': 'Error', 'errors': err.messages}, 422

        if len(UserModel.query.all()):
            return {'status': 'Error', 'errors': ['An account already exists']}, 500

        reset_token = generate_reset_key()

        new_user = UserModel(
            email=data['email'],
            password=UserModel.generate_hash(data['password']),
            settings=str(create_settings()),
            reset_token=reset_token
        )

        try:
            new_user.save()
            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            return {
                       'status': 'Account was successfully created',
                       'access_token': access_token,
                       'refresh_token': refresh_token,
                       'reset_key': reset_token
                   }, 200
        except:
            return {'status': 'Error', 'errors': ['Account creation failed']}, 500

    @jwt_required
    def patch(self):
        user = UserModel.return_first()
        if not user:
            return {'status': 'Error', 'errors': ['The account has not been created']}, 500

        json_data = request.get_json()
        if 'email' in json_data:
            user.email = json_data['email']
        if 'password' in json_data:
            user.password = UserModel.generate_hash(json_data['password'])
        if 'settings' in json_data:
            user.settings = json_data['settings']

        db.session.commit()

        return {'status': 'Account successfully updated'}, 200

    @jwt_required
    def get(self):
        user = UserModel.return_first()
        if not user:
            return {'status': 'Error', 'errors': ['The account has not been created']}, 500
        return {'status': 'Account successfully retrieved', 'account': user.to_dict()}, 200


class ClimateData(Resource):
    # Create new climate data if a valid api key is input
    def post(self, sensor_id):
        json_data = request.get_json()
        input_api_key = request.args.get('api_key')

        if not json_data:
            return {'status': 'Error', 'errors': ['No input data provided']}, 400

        # Validate and deserialize input
        try:
            data = climate_data_schema.load(json_data)
        except ValidationError as err:
            return {'status': 'Error', 'errors': err.messages}, 422

        if input_api_key == api_key:

            # Find sensor
            sensor = SensorModel.query.filter_by(id=sensor_id).first()
            if sensor:
                battery_voltage = data['battery_voltage']
                date = data['date']
                sensors_data = data['climate_data']

                climate_data = ClimateModel(sensor_id=sensor_id, battery_voltage=battery_voltage, date=date)
                climate_data.save()

                climate_id = climate_data.to_dict()['id']

                # Create sensor data for each type of sensor
                for sensor_data in sensors_data:
                    value = sensor_data['value']
                    data_type = sensor_data['type']

                    unit = get_unit_from_type(data_type)

                    sensor_obj = SensorDataModel(climate_id=climate_id, value=value, type=data_type, unit=unit)
                    db.session.add(sensor_obj)

                db.session.commit()
                return {'status': 'Sensor data successfully created.'}, 200
            return {'status': 'Error', 'errors': ['Sensor doesn\'t exist']}, 500
        return {'status': 'Error', 'errors': ['Invalid API key']}, 401

    @jwt_required
    def get(self, sensor_id):
        input_quantity = request.args.get('quantity')
        input_range_start = request.args.get('range_start')
        input_range_end = request.args.get('range_end')

        # Check if sensor exists
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            # Use a quantity to limit the number of climate objects returned
            default_quantity = 50
            quantity = default_quantity

            # Validate quantity if input
            if input_quantity:
                try:
                    int_quantity = int(input_quantity)
                except:
                    return {'status': 'Error',
                            'errors': ['Quantity must be an integer']}, 422
                if int_quantity > default_quantity or int_quantity < 0:
                    return {'status': 'Error',
                            'errors': ['Quantity must be below or equal to 50 and greater than 0']}, 422
                else:
                    quantity = int_quantity

            range_start = input_range_start
            range_end = input_range_end

            # Check if range is valid
            if (range_start and range_end is None) or (range_start is None and range_end):
                return {'status': 'Error', 'errors': ['Invalid date range']}, 422
            elif (range_start and range_end) and (range_start < range_end):
                try:
                    date_start = dateutil.parser.parse(range_start)
                    date_end = dateutil.parser.parse(range_end)
                except:
                    return {'status': 'Error', 'errors': ['Invalid date range']}, 422

                # Get climate data between the two dates with descending date order
                climate_data = ClimateModel.query.order_by(ClimateModel.id.desc()).filter(
                    ClimateModel.sensor_id == sensor_id,
                    ClimateModel.date <= date_end,

                    ClimateModel.date >= date_start)
            else:
                # Get the most recent climate data limited by the specified quantity
                climate_data = ClimateModel.query.order_by(ClimateModel.id.desc()).filter_by(sensor_id=sensor_id).limit(
                    quantity)

            # Retrieve sensor data for each climate data
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

            return {'status': 'Climate data succesfully retrieved', 'climate_data': climate_dict_list}, 200
        return {'status': 'Error', 'errors': ['Sensor doesn\'t exist']}, 500

    @jwt_required
    def delete(self, sensor_id):
        # Check if sensor exists
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            climate_data = ClimateModel.query.filter_by(sensor_id=sensor_id)

            # Delete all climate data
            for climate in climate_data:
                climate_dict = climate.to_dict()
                climate_id = climate_dict['id']

                # Delete all sensor data for the climate data
                sensor_data = SensorDataModel.query.filter_by(climate_id=climate_id)
                for sensor in sensor_data:
                    sensor.delete()
                climate.delete()

            return {'status': ['Sensor climate data successfully deleted']}, 200
        return {'status': 'Error', 'errors': ['Sensor doesn\'t exist']}, 500


class Sensor(Resource):
    # Update sensor for the specified sensor id
    @jwt_required
    def patch(self, sensor_id):
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            json_data = request.get_json()
            if 'name' in json_data:
                sensor.name = json_data['name']
            if 'sensor_id' in json_data:
                sensor.id = json_data['sensor_id']

            db.session.commit()
            return {'status': 'Sensor successfully updated'}, 200
        return {'status': 'Error', 'errors': ['Sensor doesn\'t exist']}, 500

    # Delete sensor for the specified sensor id
    @jwt_required
    def delete(self, sensor_id):
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            sensor.delete()
            climate_data = ClimateModel.query.filter_by(sensor_id=sensor_id)

            # Delete all climate data
            for climate in climate_data:
                climate_dict = climate.to_dict()
                climate_id = climate_dict['id']

                # Delete all sensor data for the climate data
                sensor_data = SensorDataModel.query.filter_by(climate_id=climate_id)
                for sensor in sensor_data:
                    sensor.delete()
                climate.delete()
            return {'status': 'Sensor successfully deleted'}, 200
        return {'status': 'Error', 'errors': ['Sensor doesn\'t exist']}, 500

    # Get sensor data for the specified sensor id
    @jwt_required
    def get(self, sensor_id):
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            sensor_dict = sensor.to_dict()
            recent_climate_data = ClimateModel.query.order_by(ClimateModel.id.desc()).filter_by(
                sensor_id=sensor_dict['id']).first()
            if recent_climate_data:
                climate_data = recent_climate_data.to_dict()
                sensor_data_list = SensorDataModel.query.filter_by(climate_id=recent_climate_data.id)
                if sensor_data_list:
                    sensor_data_dict_list = []
                    for sensor_data in sensor_data_list:
                        sensor_data_dict_list.append(sensor_data.to_dict())
                    climate_data['climate_data'] = sensor_data_dict_list
                sensor_dict['recent_climate_data'] = climate_data
            return {'status': 'Sensor successfully retrieved', 'sensor': sensor_dict}, 200
        return {'status': 'Error', 'errors': ['Sensor doesn\'t exist']}, 500


class Sensors(Resource):
    # Create new sensor if a valid api_key is input
    def post(self):
        json_data = request.get_json(force=True)
        input_api_key = request.args.get('api_key')

        if not json_data:
            return {'status': 'Error', 'errors': ['No body json data provided']}, 422

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
                sensor.save()
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
                sensor_dict = sensor.to_dict()

                recent_climate_data = ClimateModel.query.order_by(ClimateModel.id.desc()).filter_by(sensor_id=sensor_dict['id']).first()
                if recent_climate_data:
                    climate_data = recent_climate_data.to_dict()
                    sensor_data_list = SensorDataModel.query.filter_by(climate_id=recent_climate_data.id)
                    if sensor_data_list:
                        sensor_data_dict_list = []
                        for sensor_data in sensor_data_list:
                            sensor_data_dict_list.append(sensor_data.to_dict())
                        climate_data['climate_data'] = sensor_data_dict_list
                    sensor_dict['recent_climate_data'] = climate_data
                sensor_dict_list.append(sensor_dict)
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


class ChangePassword(Resource):
    def post(self):
        json_data = request.get_json(force=True)

        if not json_data:
            return {'status': 'Error', 'errors': ['No body json data provided']}, 422

        # Validate and deserialize json data for sensor
        try:
            data = change_password_schema.load(json_data)
        except ValidationError as err:
            return {'status': 'Error', 'errors': err.messages}, 422

        user = UserModel.return_first()
        if not user:
            return {'status': 'Error', 'errors': ['An account doesn\'t exist']}, 500

        if user.reset_token == data['reset_token']:
            user.password = UserModel.generate_hash(data['password'])
            new_reset_token = generate_reset_key()
            user.reset_token = new_reset_token

            db.session.commit()

            return {'status': 'Successfully reset password', 'new_reset_token': new_reset_token}, 200
        return {'status': 'Error', 'errors': ['Invalid password reset token']}, 401


## RESOURCES

# Account Resources
api.add_resource(UserLogin, '/api/login')
api.add_resource(UserLogoutAccess, '/api/logout/access')
api.add_resource(UserLogoutRefresh, '/api/logout/refresh')
api.add_resource(TokenRefresh, '/api/token/refresh')
api.add_resource(Users, '/api/account')
api.add_resource(ChangePassword, '/api/accounts/actions/change-password')

# Sensor Resources
api.add_resource(Sensor, '/api/sensors/<int:sensor_id>')
api.add_resource(Sensors, '/api/sensors')
api.add_resource(ClimateData, '/api/sensors/<int:sensor_id>/climate-data')


## ROUTES

@app.route('/api', defaults={'path': ''})
@app.route('/api/<path:path>')
def api_catch_all(path):
    return {'status': 'Error', 'errors': ['Endpoint doesn\'t exist']}, 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')


## FUNCTIONS

# Deletes old climate data from the database to save storage space
def remove_old_climate_data():
    print('Removing climate data older than 6 months')
    now = datetime.now()
    old_time = now - timedelta(weeks=24)

    sensors = SensorModel.query.all()
    for sensor in sensors:
        sensor_id = sensor.id
        climate_data = ClimateModel.query.filter(ClimateModel.sensor_id == sensor_id,
                                                    ClimateModel.date <= old_time)
        # Delete all climate data
        for climate in climate_data:
            print('Deleting old climate data at: ' + str(climate.date))
            climate_dict = climate.to_dict()
            climate_id = climate_dict['id']

            # Delete all sensor data for the climate data
            sensor_data = SensorDataModel.query.filter_by(climate_id=climate_id)
            for sensor_d in sensor_data:
                sensor_d.delete()
            climate.delete()


def init():
    scheduler = BackgroundScheduler()


    # Create job to remove old climate data every 24 hours
    old_climate_job = scheduler.add_job(remove_old_climate_data, 'interval', hours=24)
    scheduler.start()

    print('Starting server')
    app.run(debug=True, host='0.0.0.0')

    # Shutdown any scheduler jobs
    old_climate_job.remove()
    scheduler.shutdown()


if __name__ == '__main__':
    init()
