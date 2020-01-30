# Library imports
import dateutil.parser
from datetime import timedelta, datetime
from flask import Flask, render_template, jsonify, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy_serializer import SerializerMixin
from passlib.hash import bcrypt
from marshmallow import ValidationError, validate
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS

# Local imports
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

# API key for use by the radio program
api_key = 'xgLxTX7Nkem5qc9jllg2'

db = SQLAlchemy(app)
jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    """
    Creates all database tables if the database doesn't already exist
    """
    db.create_all()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    """
    Checks if a JWT token has been blacklisted within the database

    Parameters
    ----------
    decrypted_token : string
        JWT token

    Returns
    -------
    Boolean
        If the token has been blacklisted
    """
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)


@jwt.expired_token_loader
def expired_token_callback(expired_token):
    """
    Generates custom error message for expired tokens

    Parameters
    ----------
    expired_token : string
        JWT token
    """
    token_type = expired_token['type']
    return {
               'status': 'Error',
               'errors': ['The {} token has expired'.format(token_type)]
           }, 401


@jwt.revoked_token_loader
def revoked_token_loader_callback():
    """
    Generates custom error message for revoked tokens
    """
    return {
               'status': 'Error',
               'errors': ['The token is invalid as it has been revoked']
           }, 401


@jwt.unauthorized_loader
def unauthorized_loader_callback(msg):
    """
    Generates custom error message for missing authorisation headers

    Parameters
    ----------
    msg : string
        Error generated by the JWT library
    """
    return {
               'status': 'Error',
               'errors': [msg]
           }, 401


# MODELS

class UserModel(db.Model, SerializerMixin):
    """
     Model that represents a user within the database
     Attributes
     -------
     id
         ID to identify the user
     password
         Hashed string of the user's password
     email
         String of the user's email
     settings
         String representing the jsonified settings string
     reset_token
         String of the user's password reset token
     """

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    settings = db.Column(db.Text, nullable=False)
    reset_token = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        """
        Generates a string representation of the user
        Returns
        -------
        String
            String representation of the user
        """
        return '<UserModel %r>' % self.email

    def save(self):
        """
        Saves or updates an instance of user to the database
        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        """
        Finds a user based on a an input email address

        Parameters
        ----------
        email : string
            Email that the user registered with

        Returns
        -------
        Query
            User that has an email address that matches the input email
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def return_first(cls):
        """
        Returns the first user in the database

        Returns
        -------
        Query
            First user that has been stored in the database
        """
        return UserModel.query.first()

    @staticmethod
    def generate_hash(password):
        """
        Generates a hashed version of the input password

        Parameters
        ----------
        password : string
            Unhashed password

        Returns
        -------
        String
            Hashed version of the input password
        """
        return bcrypt.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        """
        Verifies that the hashed version of the input password matches the input hashed password

        Parameters
        ----------
        password : string
            Unhashed password to be hashed an compared with the hashed passwod
        hash : string
            Hashed password

        Returns
        -------
        Boolean
            Whether the hashed version of the input password matches the input hashed password
        """
        return bcrypt.verify(password, hash)


class RevokedTokenModel(db.Model):
    """
     Model that represents a revoked JWT token in the database
     Attributes
     -------
     id
         ID to identify the revoked token
     jti
         JWT token identifier
     """

    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def save(self):
        """
        Saves or updates an instance of revoked token to the database
        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        """
        Checks if a JWT token has been blacklisted within the database

        Parameters
        ----------
        jti : string
            JWT token identifier

        Returns
        -------
        Boolean
            If the token has been blacklisted
        """
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class SensorModel(db.Model, SerializerMixin):
    """
     Model that represents a sensor in the database
     Attributes
     -------
     id
         ID to identify the sensor
     user_id
         ID of the user that the sensor belongs to
     name
         Name of the sensor
     """

    __tablename__ = 'sensor'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        """
        Generates a string representation of the sensor

        Returns
        -------
        String
            String representation of the sensor
        """
        return '<SensorModel %r>' % self.name

    def save(self):
        """
        Saves or updates an instance of sensor to the database
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Deletes an instance of sensor from the database
        """
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_all(cls):
        """
        Deletes all instances of sensor from the database
        """
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Error during row deletion'}


class ClimateModel(db.Model, SerializerMixin):
    """
     Model that represents an individual climate data recording in the database
     Attributes
     -------
     id
         ID to identify the climate data recording
     sensor_id
         ID of the sensor that the climate recording belongs to
     battery_voltage
         Voltage of the sensor's battery
     date
         Date that the climate data was recorded at
     """
    __tablename__ = 'climate'

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)
    battery_voltage = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """
        Generates a string representation of the climate data

        Returns
        -------
        String
            String representation of the climate data
        """
        return '<Climate %r>' % self.id

    @hybrid_method
    def interval(self, n):
        """
        Checks if the climate data id can be reduced to an input integer

        Parameters
        ----------
        n : integer
            Integer that the id will be reduced by

        Returns
        -------
        Boolean
            If the climate data id can be reduced by n to 0
        """
        return self.id % n == 0

    @interval.expression
    def interval(cls, n):
        """
        Checks if the climate data id can be reduced to an input integer

        Parameters
        ----------
        n : integer
            Integer that the id will be reduced by

        Returns
        -------
        Boolean
            If the climate data id can be reduced by n to 0
        """
        return cls.id % n == 0

    def save(self):
        """
        Saves or updates an instance of climate data to the database
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Deletes an instance of climate data from the database
        """
        db.session.delete(self)
        db.session.commit()


class SensorDataModel(db.Model, SerializerMixin):
    """
     Model that represents an individual sensor data recording in the database
     Attributes
     -------
     id
         ID to identify the sensor data recording
     climate_id
         ID of the climate data recording that the sensor data recording belongs to
     value
         Value that the sensor recorded
     type
         Type of the data that the sensor recorded
     unit
         Unit of measurement that the sensor value was recorded with
     """
    __tablename__ = 'sensordata'

    id = db.Column(db.Integer, primary_key=True)
    climate_id = db.Column(db.Integer, db.ForeignKey('climate.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        """
        Generates a string representation of the sensor data

        Returns
        -------
        String
            String representation of the sensor data
        """
        return '<Sensor Data %r>' % self.id

    def save(self):
        """
        Saves or updates an instance of sensor data to the database
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Deletes an instance of sensor data from the database
        """
        db.session.delete(self)
        db.session.commit()


# Load schemas to evaluate the correctness of data in the API
climate_data_schema = ClimateDataSchema()
sensor_schema = SensorSchema()
user_schema = UserSchema()
change_password_schema = ChangePasswordSchema()


class UserLogin(Resource):
    def post(self):
        """
        Get access token and refresh token if a valid email and password are input into the request body
        """

        # Load request body data
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate and deserialize input
        try:
            data = user_schema.load(json_data)
        except ValidationError as err:
            return {'status': 'Error', 'errors': err.messages}, 422

        current_user = UserModel.find_by_email(data['email'])

        # Cannot login if a user hasn't been registered
        if not current_user:
            return {'status': 'Error', 'errors': [
                'User doesn\'t exist'
            ]}, 500

        # If the input password matches the stored user password
        if UserModel.verify_hash(data['password'], current_user.password):
            try:
                # Generate JWT access and refresh tokens for user authentication
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
        """
        Blacklists an access token
        """

        # Get access token from request header
        jti = get_raw_jwt()['jti']
        try:
            # Blacklist access token within database
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
        """
        Blacklists an refresh token
        """

        # Get refresh token from request header
        jti = get_raw_jwt()['jti']
        try:
            # Blacklist refresh token within database
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.save()
            return {'status': 'Refresh token has been revoked'}
        except:
            return {'status': 'Error', 'errors': [
                'Error in revoking refresh token'
            ]}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        """
        Return a new access token if a valid refresh token is received
        """

        # Identifies the user based on the refresh token
        current_user = get_jwt_identity()
        try:
            # Generate new access stoken
            access_token = create_access_token(identity=current_user)
            return {'access_token': access_token}
        except:
            return {'status': 'Error', 'errors': [
                'Error in refreshing access token'
            ]}, 500


class Users(Resource):
    def post(self):
        """
        Return a new access token if a valid refresh token is received
        """

        # Load request body data
        json_data = request.get_json()
        if not json_data:
            return {'status': 'Error', 'errors': ['No input data provided']}, 400

        # Validate and deserialize input
        try:
            data = user_schema.load(json_data)
        except ValidationError as err:
            return {'status': 'Error', 'errors': err.messages}, 422

        # Error if a user already exists
        if len(UserModel.query.all()):
            return {'status': 'Error', 'errors': ['An account already exists']}, 500

        # Generate a password reset token
        reset_token = generate_reset_key()

        # Create a user model
        new_user = UserModel(
            email=data['email'],
            password=UserModel.generate_hash(data['password']),
            settings=str(create_settings()),
            reset_token=reset_token
        )

        try:
            # Save user to database
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
        """
        Update a existing user with new data
        """

        # Load request body data
        json_data = request.get_json()
        if not json_data:
            return {'status': 'Error', 'errors': ['No input data provided']}, 400

        user = UserModel.return_first()

        # Error if a user hasn't been registered
        if not user:
            return {'status': 'Error', 'errors': ['The account has not been created']}, 500

        # Update user data if it exists in the request body
        if 'email' in json_data:
            user.email = json_data['email']
        if 'password' in json_data:
            user.password = UserModel.generate_hash(json_data['password'])
        if 'settings' in json_data:
            user.settings = json_data['settings']

        # Update user
        db.session.commit()

        return {'status': 'Account successfully updated'}, 200

    @jwt_required
    def get(self):
        """
        Get user data
        """

        user = UserModel.return_first()

        # Error if a user hasn't been registered
        if not user:
            return {'status': 'Error', 'errors': ['The account has not been created']}, 500

        # Process user data to avoid sensitive data from being retrieved
        user = user.to_dict()
        del user['password']

        return {'status': 'Account successfully retrieved', 'account': user}, 200


class ClimateData(Resource):
    def post(self, sensor_id):
        """
        Create new climate data if a valid api key is input
        """

        # Load request body data
        json_data = request.get_json()
        if not json_data:
            return {'status': 'Error', 'errors': ['No input data provided']}, 400

        input_api_key = request.args.get('api_key')

        if input_api_key == api_key:
            # Validate and deserialize request body data
            try:
                data = climate_data_schema.load(json_data)
            except ValidationError as err:
                return {'status': 'Error', 'errors': err.messages}, 422

            # Find sensor that matches the sensor id from the database
            sensor = SensorModel.query.filter_by(id=sensor_id).first()
            if sensor:
                battery_voltage = data['battery_voltage']
                date = data['date']
                sensors_data = data['climate_data']

                # Create climate data
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

                # Save climate and sensor recording data to the database
                db.session.commit()
                return {'status': 'Sensor data successfully created.'}, 200
            return {'status': 'Error', 'errors': ['Sensor doesn\'t exist']}, 500
        return {'status': 'Error', 'errors': ['Invalid API key']}, 401

    @jwt_required
    def get(self, sensor_id):
        """
        Get climate data for given sensor ID
        """

        # Get quantity and range arguments from request query string
        input_quantity = request.args.get('quantity')
        input_range_start = request.args.get('range_start')
        input_range_end = request.args.get('range_end')

        # Find sensor that matches the sensor id from the database
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            # Use a quantity to limit the number of climate objects returned
            default_quantity = 50
            quantity = default_quantity

            # Validate quantity if it has been input
            if input_quantity:
                try:
                    # Attempt to case quantity to integer
                    int_quantity = int(input_quantity)
                except:
                    return {'status': 'Error',
                            'errors': ['Quantity must be an integer']}, 422

                # Only use quantity if it is within the valid quantity range
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
                # Parse ranges into dates
                try:
                    date_start = dateutil.parser.parse(range_start)
                    date_end = dateutil.parser.parse(range_end)
                except:
                    return {'status': 'Error', 'errors': ['Invalid date range']}, 422

                # Find climate data that matches sensor id
                sensor_climate_data = ClimateModel.query.filter_by(sensor_id=sensor_id)

                climate_data_length = sensor_climate_data.count()
                days_in_range = (date_end - date_start).days
                data_interval = 1

                # Only collect climate data at an interval depending on the range length and quantity of climate data
                # stored by the sensor
                if days_in_range > 120 and climate_data_length > 2880:
                    data_interval = 20
                elif days_in_range > 60 and climate_data_length > 1440:
                    data_interval = 10
                elif days_in_range > 30 and climate_data_length > 720:
                    data_interval = 7
                elif days_in_range > 14 and climate_data_length > 360:
                    data_interval = 6
                elif days_in_range > 7 and climate_data_length > 168:
                    data_interval = 5
                elif days_in_range > 2 and climate_data_length > 48:
                    data_interval = 4
                elif days_in_range > 1 and climate_data_length > 24:
                    data_interval = 3

                # Get climate data between the two dates with descending date order
                climate_data = sensor_climate_data.order_by(ClimateModel.id.desc()).filter(
                    ClimateModel.sensor_id == sensor_id,
                    ClimateModel.interval(data_interval),
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
        """
        Deletes all climate data for the sensor id
        """

        # Check if sensor exists
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            # Get all climate data for that sensor
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
    @jwt_required
    def patch(self, sensor_id):
        """
        Update sensor for the specified sensor id
        """

        # Retrieve sensor based on sensor id
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            # Load request body data
            json_data = request.get_json()
            if not json_data:
                return {'status': 'Error', 'errors': ['No input data provided']}, 400

            # Update sensor data if it exists in the request body
            if 'name' in json_data:
                sensor.name = json_data['name']
            if 'sensor_id' in json_data:
                sensor.id = json_data['sensor_id']

            # Update sensor
            db.session.commit()
            return {'status': 'Sensor successfully updated'}, 200
        return {'status': 'Error', 'errors': ['Sensor doesn\'t exist']}, 500

    @jwt_required
    def delete(self, sensor_id):
        """
        Delete sensor for the specified sensor id
        """

        # Retrieve sensor based on sensor id
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            # Delete sensor
            sensor.delete()

            # Find all climate data for the sensor
            climate_data = ClimateModel.query.filter_by(sensor_id=sensor_id)

            # Delete all climate data
            for climate in climate_data:
                climate_dict = climate.to_dict()
                climate_id = climate_dict['id']

                # Delete all sensor data for the climate data
                sensor_data = SensorDataModel.query.filter_by(climate_id=climate_id)
                for sensor in sensor_data:
                    sensor.delete()

                # Delete climate data
                climate.delete()
            return {'status': 'Sensor successfully deleted'}, 200
        return {'status': 'Error', 'errors': ['Sensor doesn\'t exist']}, 500

    @jwt_required
    def get(self, sensor_id):
        """
        Get sensor data for the specified sensor id
        """

        # Retrieve sensor based on sensor id
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            sensor_dict = sensor.to_dict()

            # Retrieve most recent climate data for the sensor
            recent_climate_data = ClimateModel.query.order_by(ClimateModel.id.desc()).filter_by(
                sensor_id=sensor_dict['id']).first()
            if recent_climate_data:
                climate_data = recent_climate_data.to_dict()

                # Find sensor data for the most recent climate data
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
    def post(self):
        """
        Create new sensor if a valid api_key is input
        """

        input_api_key = request.args.get('api_key')

        if input_api_key == api_key:
            # Load request body data
            json_data = request.get_json(force=True)
            if not json_data:
                return {'status': 'Error', 'errors': ['No body json data provided']}, 422

            # Validate and deserialize json data for sensor
            try:
                data = sensor_schema.load(json_data)
            except ValidationError as err:
                return {'status': 'Error', 'errors': err.messages}, 422

            name = data['name']
            sensor_id = data['sensor_id']
            user_id = data['user_id']

            # Check if that sensor already exists
            if SensorModel.query.filter_by(id=sensor_id).first():
                return {'status': 'Error', 'errors': ['A sensor with that id already exists']}, 500

            try:
                # Create sensor in database
                sensor = SensorModel(name=name, id=sensor_id, user_id=user_id)
                sensor.save()
                return {'status': 'Sensor successfully created.'}
            except:
                return {'status': 'Error', 'errors': ['Error while adding sensor to database']}, 500
        else:
            return {'status': 'Error', 'errors': ['Invalid api key']}, 401

    @jwt_required
    def get(self):
        """
        Get all sensors
        """

        try:
            # Retrieve all sensors from database
            sensors_list = SensorModel.query.all()
            sensor_dict_list = []

            # Convert all sensors into dicts
            for sensor in sensors_list:
                sensor_dict = sensor.to_dict()

                # Retrieve most recent climate data for the current sensor
                recent_climate_data = ClimateModel.query.order_by(ClimateModel.id.desc()).filter_by(
                    sensor_id=sensor_dict['id']).first()
                if recent_climate_data:
                    climate_data = recent_climate_data.to_dict()

                    # Retrieve sensor data recordings for the climate data
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

    @jwt_required
    def delete(self):
        """
        Delete all sensors
        """

        try:
            SensorModel.delete_all()
            return {'status': 'Sensors successfully deleted.'}, 200
        except:
            return {'status': 'Error', 'errors': ['Error while deleting all sensors from database']}, 500


class ChangePassword(Resource):
    def post(self):
        """
        Change user password
        """

        # Load request body data
        json_data = request.get_json(force=True)
        if not json_data:
            return {'status': 'Error', 'errors': ['No body json data provided']}, 422

        # Validate and deserialize json data for sensor
        try:
            data = change_password_schema.load(json_data)
        except ValidationError as err:
            return {'status': 'Error', 'errors': err.messages}, 422

        # Retrieve first user in database
        user = UserModel.return_first()
        if not user:
            return {'status': 'Error', 'errors': ['An account doesn\'t exist']}, 500

        # Change password if the input reset token matches the stored reset token
        if user.reset_token == data['reset_token']:
            # Hash the new password
            user.password = UserModel.generate_hash(data['password'])

            # Generate new reset token
            new_reset_token = generate_reset_key()
            user.reset_token = new_reset_token

            # Update user in database
            db.session.commit()

            return {'status': 'Successfully reset password', 'new_reset_token': new_reset_token}, 200
        return {'status': 'Error', 'errors': ['Invalid password reset token']}, 401


class NextAvailableSensorID(Resource):
    def get(self):
        """
        Get the next unused sensor id
        """

        input_api_key = request.args.get('api_key')

        if input_api_key == api_key:
            # Retrieve all sensors in the database
            sensors_list = SensorModel.query.all()

            if len(sensors_list):
                sensor_dict_list = []

                # Convert all sensors into dicts
                for sensor in sensors_list:
                    sensor_dict = sensor.to_dict()
                    sensor_dict_list.append(sensor_dict)

                # Sort sensors by sensor ID
                sorted_sensor_list = sorted(sensor_dict_list, key=lambda x: x['id'])

                # If there are no missing sequential IDs in the list then list length
                next_sensor_id = len(sorted_sensor_list) + 1

                # Find first missing ID from the sensor list
                for i, sensor in enumerate(sorted_sensor_list, start=1):
                    if i != sensor['id']:
                        next_sensor_id = i
                return {'ID': next_sensor_id}, 200
            return {'ID': 1}, 200
        return {'status': 'Error', 'errors': ['Invalid API key']}, 401


# RESOURCES

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
api.add_resource(NextAvailableSensorID, '/api/sensors/actions/next-available-sensor-id')


# ROUTES

@app.route('/api', defaults={'path': ''})
@app.route('/api/<path:path>')
def api_catch_all(path):
    return {'status': 'Error', 'errors': ['Endpoint doesn\'t exist']}, 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')


# FUNCTIONS

def remove_old_climate_data():
    """
    Deletes old climate data from the database to save storage space
    """

    print('Removing climate data older than 6 months (approximated as 24 weeks)')

    # Generate data 24 weeks in the future
    old_time = datetime.now() - timedelta(weeks=24)

    sensors = SensorModel.query.all()
    for sensor in sensors:
        sensor_id = sensor.id

        # Retrieve climate data older than 24 weeks
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
    # Create scheduler instance
    scheduler = BackgroundScheduler()

    # Create job to remove old climate data every 24 hours
    remove_old_climate_data()
    old_climate_job = scheduler.add_job(remove_old_climate_data, 'interval', hours=24)
    scheduler.start()

    print('Starting server')
    # Run API on local network IP
    app.run(debug=True, host='0.0.0.0')

    # Shutdown any scheduler jobs
    old_climate_job.remove()
    scheduler.shutdown()


if __name__ == '__main__':
    init()
