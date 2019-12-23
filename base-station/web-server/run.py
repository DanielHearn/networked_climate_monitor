import dateutil.parser
from flask import Flask, render_template, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from passlib.hash import bcrypt
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from helpers import get_unit_from_type

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a060dc4d401ffdb1b91bf5db8430f88d'
app.config['JWT_SECRET_KEY'] = '13071ce246c22add4f57eeb916f4d46d'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

db = SQLAlchemy(app)
jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    db.create_all()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)


class UserModel(db.Model, SerializerMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<UserModel %r>' % self.email

    def save_to_db(self):
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
            return {'message': 'Something went wrong'}

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

    def add(self):
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


class ClimateModel(db.Model, SerializerMixin):
    __tablename__ = 'climate'

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)
    battery_voltage = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Climate %r>' % self.id


class SensorDataModel(db.Model, SerializerMixin):
    __tablename__ = 'sensordata'

    id = db.Column(db.Integer, primary_key=True)
    climate_id = db.Column(db.Integer, db.ForeignKey('climate.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Sensor Data %r>' % self.id


account_parser = reqparse.RequestParser()
account_parser.add_argument('email', help='This field cannot be blank', required=True)
account_parser.add_argument('password', help='This field cannot be blank', required=True)


class UserRegistration(Resource):
    def post(self):
        data = account_parser.parse_args()

        if len(UserModel.query.all()):
            return {'message': 'An account already exists'}

        new_user = UserModel(
            email=data['email'],
            password=UserModel.generate_hash(data['password'])
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            return {
                'message': 'UserModel {} was created'.format(data['email']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = account_parser.parse_args()
        current_user = UserModel.find_by_email(data['email'])

        if not current_user:
            return {'message': 'UserModel {} doesn\'t exist'.format(data['email'])}

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            return {
                'message': 'Logged in as {}'.format(current_user.email),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    @jwt_required
    def get(self):
        return UserModel.return_all()

    @jwt_required
    def delete(self):
        return UserModel.delete_all()


climate_data_post_parser = reqparse.RequestParser()
climate_data_post_parser.add_argument('battery_voltage', help='This field cannot be blank', required=True)
climate_data_post_parser.add_argument('date', help='This field cannot be blank', required=True)
climate_data_post_parser.add_argument('climate_data', help='This field cannot be blank', required=True, type=list, location='json')

climate_data_get_parser = reqparse.RequestParser()
climate_data_get_parser.add_argument('quantity', help='This field cannot be blank', required=False)
climate_data_get_parser.add_argument('range_start', help='This field cannot be blank', required=False)
climate_data_get_parser.add_argument('range_end', help='This field cannot be blank', required=False)


class ClimateData(Resource):
    @jwt_required
    def post(self, sensor_id):
        request.get_json(force=True)
        data = climate_data_post_parser.parse_args()
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            if data['battery_voltage'] and data['date'] and data['climate_data']:
                battery_voltage = data['battery_voltage']
                date = dateutil.parser.parse(data['date'])
                sensors_data = data['climate_data']
                print(sensors_data)

                climate_data = ClimateModel(sensor_id=sensor_id, battery_voltage=battery_voltage, date=date)
                db.session.add(climate_data)
                db.session.commit()

                climate_id = climate_data.to_dict()['id']

                for sensor_data in sensors_data:
                    value = sensor_data['value']
                    data_type = sensor_data['type']

                    unit = get_unit_from_type(data_type)

                    sensor_obj = SensorDataModel(climate_id=climate_id, value=value, type=data_type, unit=unit)
                    db.session.add(sensor_obj)

                db.session.commit()
                return jsonify({'status': 'Sensor data successfully created.'})
        return jsonify({'status': 'Sensor doesn\'t exist'})

    @jwt_required
    def get(self, sensor_id):
        data = climate_data_get_parser.parse_args()
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            quantity = 20
            input_quantity = data['quantity']
            if input_quantity:
                quantity = input_quantity

            range_start = data['range_start']
            range_end = data['range_end']
            if (range_start and range_end is None) or (range_start is None and range_end):
                return jsonify({'status': 'Invalid date range'})
            elif range_start and range_end:

                date_start = dateutil.parser.parse(range_start)
                date_end = dateutil.parser.parse(range_end)
                print(date_start)
                print(date_end)
                climate_data = ClimateModel.query.order_by(ClimateModel.id.desc()).filter(
                    ClimateModel.sensor_id == sensor_id,
                    ClimateModel.date <= date_end,

                    ClimateModel.date >= date_start)
            else:
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
            return jsonify(climate_dict_list)
        return jsonify({'status': 'Sensor doesn\'t exist'})

    @jwt_required
    def delete(self, sensor_id):
        return jsonify({'status': 'Sensor climate data successfully deleted.'})


class Sensor(Resource):
    @jwt_required
    def delete(self, sensor_id):
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            db.session.delete(sensor)
            db.session.commit()
            return jsonify({'status': 'Sensor successfully deleted.'})
        return jsonify({'status': 'Sensor doesn\'t exist'})

    @jwt_required
    def get(self, sensor_id):
        sensor = SensorModel.query.filter_by(id=sensor_id).first()
        if sensor:
            return jsonify(sensor.to_dict())
        return jsonify({'status': 'Sensor doesn\'t exist'})


sensor_parser = reqparse.RequestParser()
sensor_parser.add_argument('name', help='This field cannot be blank', required=False)
sensor_parser.add_argument('sensor_id', help='This field cannot be blank', required=False)
sensor_parser.add_argument('user_id', help='This field cannot be blank', required=False)


class Sensors(Resource):
    @jwt_required
    def post(self):
        data = sensor_parser.parse_args()
        if data['name'] and data['sensor_id'] and data['user_id']:
            name = data['name']
            sensor_id = data['sensor_id']
            user_id = data['user_id']

            sensor = SensorModel(name=name, id=sensor_id, user_id=user_id)
            db.session.add(sensor)
            db.session.commit()
            return jsonify({'status': 'Sensor successfully created.'})
        return jsonify({'status': 'Invalid body data.'})

    @jwt_required
    def get(self):
        sensors_list = SensorModel.query.all()
        sensor_dict_list = []
        for sensor in sensors_list:
            sensor_dict_list.append(sensor.to_dict())
        return jsonify(sensor_dict_list)

    @jwt_required
    def delete(self):
        sensors = SensorModel.query.delete()
        db.session.commit()
        return jsonify({'status': 'Sensors successfully deleted.'})


# Account Resources
api.add_resource(UserRegistration, '/api/register')
api.add_resource(UserLogin, '/api/login')
api.add_resource(UserLogoutAccess, '/api/logout/access')
api.add_resource(UserLogoutRefresh, '/api/logout/refresh')
api.add_resource(TokenRefresh, '/api/token/refresh')
api.add_resource(AllUsers, '/api/account')

# Sensor Resources
api.add_resource(Sensor, '/api/sensors/<int:sensor_id>')
api.add_resource(Sensors, '/api/sensors')
api.add_resource(ClimateData, '/api/sensors/<int:sensor_id>/climate-data')


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
    app.run(debug=True, host='192.168.1.156')
