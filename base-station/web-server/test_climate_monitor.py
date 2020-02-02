import pytest
import json
from datetime import datetime

from run import app, create_tables, drop_tables, UserModel, SensorModel, RevokedTokenModel, ClimateModel, \
    SensorDataModel
from helpers import create_settings

api_key = 'xgLxTX7Nkem5qc9jllg2'


@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            drop_tables()
            create_tables()
        yield client


def test_nonexistant_endpoint(client):
    rv = client.get('/api/endpoint')
    assert rv.status_code == 500
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    endpoint_error = {
        "errors": ["Endpoint doesn\'t exist"],
        "status": "Error"
    }
    assert json_data == endpoint_error


def test_serve_static(client):
    '''
    Test html page at root
    '''
    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.content_type == 'text/html; charset=utf-8'
    data = rv.data.decode("utf-8")

    assert '<!DOCTYPE html><html lang=en>' in data
    assert '</html>' in data


@pytest.fixture(scope='module')
def new_user():
    password = UserModel.generate_hash('password')
    settings = str(create_settings())
    user = UserModel(
        email='email@email.com',
        password=password,
        settings=settings,
        reset_token='ABCDEFGHIKLMNOPQRSTV'
    )
    return user


def test_new_user(new_user):
    '''
    Create
    '''
    assert new_user.email == 'email@email.com'
    assert UserModel.verify_hash('password', new_user.password)
    assert new_user.settings == str(create_settings())
    assert new_user.reset_token == 'ABCDEFGHIKLMNOPQRSTV'

    '''
    Save
    '''
    assert len(UserModel.query.all()) == 0
    new_user.save()
    assert len(UserModel.query.all()) == 1
    saved_user = UserModel.query.first()
    assert saved_user.email == 'email@email.com'
    assert UserModel.verify_hash('password', saved_user.password)
    assert saved_user.settings == str(create_settings())
    assert saved_user.reset_token == 'ABCDEFGHIKLMNOPQRSTV'

    '''
    return_first
    '''
    assert UserModel.query.count() == 1
    saved_user = UserModel.return_first()
    assert saved_user.email == 'email@email.com'
    assert UserModel.verify_hash('password', saved_user.password)
    assert saved_user.settings == str(create_settings())
    assert saved_user.reset_token == 'ABCDEFGHIKLMNOPQRSTV'

    '''
    find_by_email
    '''
    assert UserModel.query.count() == 1
    saved_user = UserModel.find_by_email('email@email.com')
    assert saved_user.email == 'email@email.com'
    assert UserModel.verify_hash('password', saved_user.password)
    assert saved_user.settings == str(create_settings())
    assert saved_user.reset_token == 'ABCDEFGHIKLMNOPQRSTV'

    '''
    verify_hash
    '''
    assert UserModel.query.count() == 1
    assert UserModel.verify_hash('password', saved_user.password)

    '''
    Delete
    '''
    assert UserModel.query.count() == 1
    saved_user = UserModel.query.first()
    saved_user.delete()
    assert UserModel.query.count() == 0


@pytest.fixture(scope='module')
def new_sensor():
    sensor = SensorModel(name='Sensor 1', id=1, user_id=1)
    return sensor


def test_new_sensor(new_sensor):
    '''
    Create
    '''
    assert new_sensor.name == 'Sensor 1'
    assert new_sensor.id == 1
    assert new_sensor.user_id == 1

    '''
    Save
    '''
    assert SensorModel.query.count() == 0
    new_sensor.save()
    assert SensorModel.query.count() == 1

    '''
    Delete
    '''
    assert SensorModel.query.count() == 1
    new_sensor.delete()
    assert SensorModel.query.count() == 0

    '''
    delete_all
    '''
    sensor_1 = SensorModel(name='Sensor 1', id=1, user_id=1)
    sensor_1.save()
    sensor_2 = SensorModel(name='Sensor 2', id=2, user_id=1)
    sensor_2.save()
    sensor_3 = SensorModel(name='Sensor 3', id=3, user_id=1)
    sensor_3.save()
    assert SensorModel.query.count() == 3
    SensorModel.delete_all()
    assert SensorModel.query.count() == 0


@pytest.fixture(scope='module')
def new_revoked_token():
    revoked_token = RevokedTokenModel(jti='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9'
                                          '.eyJpYXQiOjE1Nzg0MTY0MTYsIm5iZiI6MTU3ODQxNjQxNiwianRpIjoiNzIxM2JkMWYtNmJkZi00YzVmLTg1OWQtMDkxM2VkYmUwOGI4IiwiZXhwIjoxNjA5OTUyNDE2LCJpZGVudGl0eSI6ImVtYWlsQGVtYWlsLmNvbSIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.exOM3mytXaqeBvqfu3QFPH9yCLdw11gjONolLQGTq4w')
    return revoked_token


def test_new_revoked_token(new_revoked_token):
    '''
    Create
    '''
    assert new_revoked_token.jti == 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Nzg0MTY0MTYsIm5iZiI6MTU3ODQxNjQxNiwianRpIjoiNzIxM2JkMWYtNmJkZi00YzVmLTg1OWQtMDkxM2VkYmUwOGI4IiwiZXhwIjoxNjA5OTUyNDE2LCJpZGVudGl0eSI6ImVtYWlsQGVtYWlsLmNvbSIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.exOM3mytXaqeBvqfu3QFPH9yCLdw11gjONolLQGTq4w'

    '''
    Save
    '''
    assert RevokedTokenModel.query.count() == 0
    new_revoked_token.save()
    assert RevokedTokenModel.query.count() == 1

    '''
    Delete
    '''
    assert RevokedTokenModel.query.count() == 1
    new_revoked_token.delete()
    assert RevokedTokenModel.query.count() == 0

    '''
    is_jti_blacklisted
    '''
    assert RevokedTokenModel.is_jti_blacklisted(new_revoked_token.jti) == False
    assert RevokedTokenModel.query.count() == 0
    revoked_token = RevokedTokenModel(jti='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9'
                                          '.eyJpYXQiOjE1Nzg0MTY0MTYsIm5iZiI6MTU3ODQxNjQxNiwianRpIjoiNzIxM2JkMWYtNmJkZi00YzVmLTg1OWQtMDkxM2VkYmUwOGI4IiwiZXhwIjoxNjA5OTUyNDE2LCJpZGVudGl0eSI6ImVtYWlsQGVtYWlsLmNvbSIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.exOM3mytXaqeBvqfu3QFPH9yCLdw11gjONolLQGTq4w')
    return revoked_token
    revoked_token.save()
    assert RevokedTokenModel.is_jti_blacklisted(revoked_token.jti) == True
    assert RevokedTokenModel.query.count() == 1


@pytest.fixture(scope='module')
def new_climate_data():
    sensor = ClimateModel(sensor_id=1, battery_voltage=4.22, date=datetime(2020, 1, 31, 16, 30, 33, 619535))
    return sensor


def test_new_climate_data(new_climate_data):
    '''
    Create
    '''
    assert new_climate_data.sensor_id == 1
    assert new_climate_data.battery_voltage == 4.22
    assert new_climate_data.date == datetime(2020, 1, 31, 16, 30, 33, 619535)

    '''
    Save
    '''
    assert ClimateModel.query.count() == 0
    new_climate_data.save()
    assert ClimateModel.query.count() == 1

    '''
    Delete
    '''
    assert ClimateModel.query.count() == 1
    new_climate_data.delete()
    assert ClimateModel.query.count() == 0

    '''
    interval
    '''
    climate_1 = ClimateModel(sensor_id=1, battery_voltage=4.22, date=datetime(2020, 1, 31, 16, 30, 33, 619535))
    climate_1.save()
    assert climate_1.interval(1) is True
    assert climate_1.interval(2) is False
    assert climate_1.interval(5) is False

    climate_2 = ClimateModel(sensor_id=2, battery_voltage=4.22, date=datetime(2020, 1, 31, 16, 30, 33, 619535))
    climate_2.save()
    assert climate_2.interval(1) is True
    assert climate_2.interval(2) is True
    assert climate_2.interval(5) is False


@pytest.fixture(scope='module')
def new_sensor_data():
    sensor = SensorDataModel(climate_id=1, value=23.45, type='Temperature', unit='c')
    return sensor


def test_new_sensor_data(new_sensor_data):
    '''
    Create
    '''
    assert new_sensor_data.climate_id == 1
    assert new_sensor_data.value == 23.45
    assert new_sensor_data.type == 'Temperature'
    assert new_sensor_data.unit == 'c'

    '''
    Save
    '''
    assert SensorDataModel.query.count() == 0
    new_sensor_data.save()
    assert SensorDataModel.query.count() == 1

    '''
    Delete
    '''
    assert SensorDataModel.query.count() == 1
    new_sensor_data.delete()
    assert SensorDataModel.query.count() == 0

    '''
    delete_all
    '''


def test_register_endpoint(client):
    '''
    No JSON data error
    '''
    rv = client.post('/api/account', json={})
    assert rv.status_code == 400
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['No input data provided']
    assert len(UserModel.query.all()) == 0

    '''
    Missing email
    '''
    email = "email@email.com"

    rv = client.post('/api/account', json={
        'email': email
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {
        "password": [
            "Missing data for required field."
        ]
    }
    assert len(UserModel.query.all()) == 0

    '''
    Missing password
    '''
    email = "email@email.com"

    rv = client.post('/api/account', json={
        'email': email
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {
        "password": [
            "Missing data for required field."
        ]
    }
    assert len(UserModel.query.all()) == 0

    '''
    Email isn’t a string
    '''
    email = 5
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"email": [
        "Not a valid email address."
    ]}
    assert len(UserModel.query.all()) == 0

    '''
    Password isn’t a string
    '''
    email = "email@email.com"
    password = 5

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"password": [
        "Not a valid string."
    ]}
    assert len(UserModel.query.all()) == 0

    '''
    Password isn’t between 8 to 40 characters long
    '''
    email = "email@email.com"
    password = "12345"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"password": [
        "Length must be between 8 and 40."
    ]}
    assert len(UserModel.query.all()) == 0

    '''
    Success
    '''
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Account was successfully created'
    assert type(json_data['access_token']) is str
    assert type(json_data['refresh_token']) is str
    assert type(json_data['reset_token']) is str

    db_user = UserModel.query.first()
    assert len(UserModel.query.all()) == 1
    assert db_user.email == 'email@email.com'
    assert db_user.verify_hash('password', db_user.password)
    assert db_user.settings == str(create_settings())
    assert type(db_user.reset_token) is str


def test_login_endpoint(client):
    '''
    No JSON data error
    '''
    rv = client.post('/api/login', json={
    })
    assert rv.status_code == 400
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['No input data provided']
    assert len(UserModel.query.all()) == 0

    '''
    Missing email
    '''
    password = "password"

    rv = client.post('/api/login', json={
        'password': password
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {
        "email": [
            "Missing data for required field."
        ]
    }
    assert len(UserModel.query.all()) == 0

    '''
    Missing password
    '''
    email = "email@email.com"

    rv = client.post('/api/login', json={
        'email': email
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {
        "password": [
            "Missing data for required field."
        ]
    }
    assert len(UserModel.query.all()) == 0

    '''
    Email isn’t a string
    '''
    email = 5
    password = "password"

    rv = client.post('/api/login', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"email": [
        "Not a valid email address."
    ]}
    assert len(UserModel.query.all()) == 0

    '''
    Password isn’t a string
    '''
    email = "email@email.com"
    password = 5

    rv = client.post('/api/login', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"password": [
        "Not a valid string."
    ]}
    assert len(UserModel.query.all()) == 0

    '''
    User doesn't exist
    '''
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/login', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 500
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ["User doesn't exist"]
    assert len(UserModel.query.all()) == 0

    '''
    Incorrect email or password
    '''
    password = UserModel.generate_hash('password')
    settings = str(create_settings())
    user = UserModel(
        email='email@email.com',
        password=password,
        settings=settings,
        reset_token='ABCDEFGHIKLMNOPQRSTV'
    )
    user.save()

    email = "email@email.com"
    password = "differentpassword"

    rv = client.post('/api/login', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ["Email or password is incorrect"]

    '''
    Success
    '''
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/login', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Successful login'
    assert type(json_data['access_token']) is str
    assert type(json_data['refresh_token']) is str


def test_logout_access_endpoint(client):
    '''
    Missing auth
    '''
    rv = client.post('/api/logout/access')
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Missing Authorization Header']

    '''
    Success
    '''
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()
    access_token = json_data['access_token']

    rv = client.post('/api/logout/access', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Access token has been revoked'

    '''
    Token has already been revoked
    '''
    rv = client.post('/api/logout/access', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The token is invalid as it has been revoked']


def test_logout_refresh_endpoint(client):
    '''
    Missing auth
    '''
    rv = client.post('/api/logout/refresh')
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Missing Authorization Header']

    '''
    Success
    '''
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()
    access_token = json_data['refresh_token']

    rv = client.post('/api/logout/refresh', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Refresh token has been revoked'

    '''
    Token has already been revoked
    '''
    rv = client.post('/api/logout/refresh', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The token is invalid as it has been revoked']


def test_token_refresh_endpoint(client):
    '''
    Missing auth
    '''
    rv = client.post('/api/token/refresh')
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Missing Authorization Header']

    '''
    Success
    '''
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()
    refresh_token = json_data['refresh_token']

    rv = client.post('/api/token/refresh', headers={'Authorization': 'Bearer ' + refresh_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Successful refresh'
    assert type(json_data['access_token']) is str


def test_get_account_endpoint(client):
    '''
    Missing auth
    '''
    rv = client.get('/api/account')
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Missing Authorization Header']

    '''
    Success
    '''
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()
    access_token = json_data['access_token']

    rv = client.get('/api/account', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Account successfully retrieved'
    assert type(json_data['account']) is dict
    assert json_data['account']['id'] == 1
    assert json_data['account']['email'] == 'email@email.com'
    assert json_data['account']['settings'] == "{'temperature_unit': 'c'}"
    assert type(json_data['account']['reset_token']) is str

    '''
    User doesn't exist
    '''
    UserModel.query.first().delete()

    rv = client.get('/api/account', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 500
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The account has not been created']

    '''
    Invalid token
    '''
    rv = client.post('/api/logout/access', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'

    rv = client.get('/api/account', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The token is invalid as it has been revoked']


def test_patch_account_endpoint(client):
    # Create account
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()
    access_token = json_data['access_token']

    '''
    Missing auth
    '''
    rv = client.patch('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Missing Authorization Header']

    '''
    No JSON data error
    '''
    rv = client.patch('/api/account', json={
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 400
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['No input data provided']

    '''
    Email isn’t a string
    '''
    email = 5

    rv = client.patch('/api/account', json={
        'email': email,
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"email": [
        "Not a valid email address."
    ]}

    '''
    Password isn’t a string
    '''
    password = False

    rv = client.patch('/api/account', json={
        'password': password
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"password": [
        "Not a valid string."
    ]}

    '''
    Password isn’t between 8 to 40 characters long
    '''
    email = "email@email.com"
    password = "12345"

    rv = client.patch('/api/account', json={
        'email': email,
        'password': password
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"password": [
        "Length must be between 8 and 40."
    ]}

    '''
    Settings isn’t a string
    '''
    settings = 5

    rv = client.patch('/api/account', json={
        'settings': settings
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"settings": [
        "Not a valid string."
    ]}

    '''
    Success
    '''
    email = "newemail@email.com"
    password = "newpassword"
    settings = create_settings()
    settings['test'] = False

    rv = client.patch('/api/account', json={
        'email': email,
        'password': password,
        'settings': str(settings),
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Account successfully updated'

    db_user = UserModel.query.first()
    assert len(UserModel.query.all()) == 1
    assert db_user.email == 'newemail@email.com'
    assert db_user.verify_hash('newpassword', db_user.password)
    assert db_user.settings == str(settings)
    assert type(db_user.reset_token) is str

    '''
    User doesn't exist
    '''
    UserModel.query.first().delete()

    rv = client.patch('/api/account', json={
        'email': email,
        'password': password
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 500
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The account has not been created']

    '''
    Invalid token
    '''
    rv = client.post('/api/logout/access', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'

    rv = client.patch('/api/account', json={
        'email': email,
        'password': password
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The token is invalid as it has been revoked']


def test_change_password_endpoint(client):
    password = 'password'
    settings = str(create_settings())
    reset_token = 'ABCDEFGHIKLMNOPQRSTV'

    '''
    User doesn't exist
    '''
    rv = client.post('/api/accounts/actions/change-password', json={
        'password': password,
        'reset_token': reset_token
    })
    assert rv.status_code == 500
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The account has not been created']

    # Create account
    user = UserModel(
        email='email@email.com',
        password=password,
        settings=settings,
        reset_token=reset_token
    )
    user.save()

    '''
    No JSON data error
    '''
    rv = client.post('/api/accounts/actions/change-password', json={
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['No input data provided']

    '''
    Missing password
    '''
    rv = client.post('/api/accounts/actions/change-password', json={
        'reset_token': reset_token
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"password": [
        "Missing data for required field."
    ]}

    '''
    Missing reset_token
    '''
    rv = client.post('/api/accounts/actions/change-password', json={
        'password': password
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"reset_token": [
        "Missing data for required field."
    ]}

    '''
    Wrong reset_token length
    '''
    rv = client.post('/api/accounts/actions/change-password', json={
        'password': password,
        'reset_token': 'ABCDEFG'
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"reset_token": [
        "Length must be 20."
    ]}

    '''
    Invalid reset_token
    '''
    rv = client.post('/api/accounts/actions/change-password', json={
        'password': password,
        'reset_token': '1BCDEFGHIKLMNOPQRSTV'
    })
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == [
        "Invalid password reset token"
    ]

    '''
    Password isn’t a string
    '''
    password = False

    rv = client.post('/api/accounts/actions/change-password', json={
        'password': password,
        'reset_token': reset_token
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"password": [
        "Not a valid string."
    ]}

    '''
    Password isn’t between 8 to 40 characters long
    '''
    password = "12345"

    rv = client.post('/api/accounts/actions/change-password', json={
        'password': password,
        'reset_token': reset_token
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"password": [
        "Length must be between 8 and 40."
    ]}

    '''
    Success
    '''
    password = "newpassword"

    rv = client.post('/api/accounts/actions/change-password', json={
        'password': password,
        'reset_token': reset_token
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Successfully reset password'

    db_user = UserModel.query.first()
    assert len(UserModel.query.all()) == 1
    assert db_user.verify_hash('newpassword', db_user.password)
    assert type(json_data['new_reset_token']) is str
    assert len(json_data['new_reset_token']) is 20


def test_post_sensors_endpoint(client):
    name = 'sensor_1'
    user_id = 1
    sensor_id = 1

    '''
    No JSON data error
    '''
    rv = client.post('/api/sensors?api_key=' + api_key, json={})
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['No input data provided']
    assert len(SensorModel.query.all()) == 0

    '''
    Missing api_key
    '''
    rv = client.post('/api/sensors', json={
        "sensor_id": sensor_id,
        "user_id": user_id,
        "name": name
    })
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Invalid api key']
    assert len(SensorModel.query.all()) == 0

    '''
    Invalid api_key
    '''
    rv = client.post('/api/sensors?api_key=invalid_key', json={
        "sensor_id": sensor_id,
        "user_id": user_id,
        "name": name
    })
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Invalid api key']
    assert len(SensorModel.query.all()) == 0

    '''
    Missing name
    '''
    rv = client.post('/api/sensors?api_key=' + api_key, json={
        "sensor_id": sensor_id,
        "user_id": user_id,
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"name": [
        "Missing data for required field."
    ]}
    assert len(SensorModel.query.all()) == 0

    '''
    Name isn't string
    '''
    rv = client.post('/api/sensors?api_key=' + api_key, json={
        "sensor_id": sensor_id,
        "user_id": user_id,
        "name": 5
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"name": [
        "Not a valid string."
    ]}
    assert len(SensorModel.query.all()) == 0

    '''
    Name is too long
    '''
    rv = client.post('/api/sensors?api_key=' + api_key, json={
        "sensor_id": sensor_id,
        "user_id": user_id,
        "name": "DTERDIRDNGFIDUFDNGFLDOIJRTYNDFJKLGLDFIUGERNJLTRUTGV"
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"name": [
        "Length must be between 0 and 40."
    ]}
    assert len(SensorModel.query.all()) == 0

    '''
    Missing sensor_id
    '''
    rv = client.post('/api/sensors?api_key=' + api_key, json={
        "user_id": user_id,
        "name": name
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"sensor_id": [
        "Missing data for required field."
    ]}
    assert len(SensorModel.query.all()) == 0

    '''
    sensor_id isn't string
    '''
    rv = client.post('/api/sensors?api_key=' + api_key, json={
        "sensor_id": "invalid",
        "user_id": user_id,
        "name": name
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"sensor_id": [
        "Not a valid integer."
    ]}
    assert len(SensorModel.query.all()) == 0

    '''
    Missing user_id
    '''
    rv = client.post('/api/sensors?api_key=' + api_key, json={
        "sensor_id": sensor_id,
        "name": name
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"user_id": [
        "Missing data for required field."
    ]}
    assert len(SensorModel.query.all()) == 0

    '''
    user_id isn't string
    '''
    rv = client.post('/api/sensors?api_key=' + api_key, json={
        "sensor_id": sensor_id,
        "user_id": "invalid",
        "name": name
    })
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"user_id": [
        "Not a valid integer."
    ]}
    assert len(SensorModel.query.all()) == 0

    '''
    Success
    '''
    rv = client.post('/api/sensors?api_key=' + api_key, json={
        "sensor_id": sensor_id,
        "user_id": user_id,
        "name": name
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Sensor successfully created.'
    assert len(SensorModel.query.all()) == 1
    new_sensor = SensorModel.query.filter_by(id=sensor_id).first()
    assert new_sensor.name == name
    assert new_sensor.id == sensor_id
    assert new_sensor.user_id == user_id

    '''
    Duplicate ID
    '''
    rv = client.post('/api/sensors?api_key=' + api_key, json={
        "sensor_id": sensor_id,
        "user_id": user_id,
        "name": name
    })
    assert rv.status_code == 500
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['A sensor with that id already exists']
    assert len(SensorModel.query.all()) == 1
    new_sensor = SensorModel.query.filter_by(id=sensor_id).first()
    assert new_sensor.name == name
    assert new_sensor.id == sensor_id
    assert new_sensor.user_id == user_id


def test_get_sensors_endpoint(client):
    # Create account
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()
    access_token = json_data['access_token']

    '''
    Missing auth
    '''
    rv = client.get('/api/sensors')
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Missing Authorization Header']

    '''
    No sensors
    '''
    rv = client.get('/api/sensors', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Sensors successfully retrieved'
    assert json_data['sensors'] == []
    assert len(SensorModel.query.all()) == 0

    '''
    Success no climate data
    '''
    sensor_1 = SensorModel(name='Sensor 1', id=1, user_id=1)
    sensor_2 = SensorModel(name='Sensor 2', id=2, user_id=1)
    sensor_1.save()
    sensor_2.save()

    rv = client.get('/api/sensors', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Sensors successfully retrieved'
    assert json_data['sensors'] == [{'id': 1, 'user_id': 1, 'name': 'Sensor 1'},
                                    {'id': 2, 'user_id': 1, 'name': 'Sensor 2'}]
    assert len(SensorModel.query.all()) == 2

    '''
    Success no climate data
    '''
    climate_data_1 = ClimateModel(sensor_id=1, battery_voltage=4.22, date=datetime(2020, 1, 31, 16, 30, 33, 619535))
    sensor_data_1 = SensorDataModel(climate_id=1, value=23.45, type='Temperature', unit='c')
    climate_data_1.save()
    sensor_data_1.save()

    climate_data_2 = ClimateModel(sensor_id=2, battery_voltage=4.16, date=datetime(2020, 1, 31, 16, 30, 35, 619535))
    sensor_data_2 = SensorDataModel(climate_id=2, value=21.52, type='Humidity', unit='%')
    climate_data_2.save()
    sensor_data_2.save()

    rv = client.get('/api/sensors', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Sensors successfully retrieved'
    assert json_data['sensors'] == [
        {
            'name': 'Sensor 1',
            'id': 1, 'user_id': 1,
            'recent_climate_data': {
                'sensor_id': 1,
                'date': '2020-01-31 16:30',
                'battery_voltage': 4.22,
                'id': 1,
                'climate_data': [
                    {'climate_id': 1, 'value': 23.45, 'id': 1, 'type': 'Temperature', 'unit': 'c'}
                ]
            }
        },
        {'name': 'Sensor 2',
         'id': 2,
         'user_id': 1,
         'recent_climate_data': {
             'sensor_id': 2,
             'date': '2020-01-31 16:30',
             'battery_voltage': 4.16,
             'id': 2,
             'climate_data': [
                 {'climate_id': 2, 'value': 21.52, 'id': 2, 'type': 'Humidity', 'unit': '%'}
             ]
         }
         }
    ]
    assert len(SensorModel.query.all()) == 2

    '''
    Invalid token
    '''
    rv = client.post('/api/logout/access', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'

    rv = client.get('/api/sensors', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The token is invalid as it has been revoked']


def test_delete_sensors_endpoint(client):
    # Create account
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()
    access_token = json_data['access_token']

    '''
    Missing auth
    '''
    rv = client.delete('/api/sensors')
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Missing Authorization Header']

    '''
    No sensors
    '''
    rv = client.delete('/api/sensors', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Sensors successfully deleted'
    assert len(SensorModel.query.all()) == 0

    '''
    Success
    '''
    sensor_1 = SensorModel(name='Sensor 1', id=1, user_id=1)
    sensor_2 = SensorModel(name='Sensor 2', id=2, user_id=1)
    sensor_1.save()
    sensor_2.save()
    assert len(SensorModel.query.all()) == 2

    rv = client.delete('/api/sensors', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Sensors successfully deleted'
    assert len(SensorModel.query.all()) == 0


def test_next_available_id_endpoint(client):
    '''
    Missing api_key
    '''
    rv = client.get('/api/sensors/actions/next-available-sensor-id')
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Invalid API key']

    '''
    Invalid api_key
    '''
    rv = client.get('/api/sensors/actions/next-available-sensor-id?api_key=invalid_key')
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Invalid API key']

    '''
    Success no sensors
    '''
    rv = client.get('/api/sensors/actions/next-available-sensor-id?api_key=' + api_key)
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Next available ID found'
    assert json_data['ID'] == 1

    '''
    Success multiple sensors
    '''
    sensor_1 = SensorModel(name='Sensor 1', id=1, user_id=1)
    sensor_2 = SensorModel(name='Sensor 2', id=2, user_id=1)
    sensor_1.save()
    sensor_2.save()
    assert len(SensorModel.query.all()) == 2

    rv = client.get('/api/sensors/actions/next-available-sensor-id?api_key=' + api_key)
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Next available ID found'
    assert json_data['ID'] == 3


def test_get_sensor_endpoint(client):
    # Create account
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()
    access_token = json_data['access_token']

    '''
    Sensor doesn't exist
    '''
    rv = client.get('/api/sensors/1', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 500
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert len(SensorModel.query.all()) == 0
    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Sensor doesn\'t exist']

    '''
    Missing auth
    '''
    sensor_1 = SensorModel(name='Sensor 1', id=1, user_id=1)
    climate_data_1 = ClimateModel(sensor_id=1, battery_voltage=4.22, date=datetime(2020, 1, 31, 16, 30, 33, 619535))
    sensor_data_1 = SensorDataModel(climate_id=1, value=23.45, type='Temperature', unit='c')
    sensor_1.save()
    climate_data_1.save()
    sensor_data_1.save()

    rv = client.get('/api/sensors/1')
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Missing Authorization Header']

    '''
    Success
    '''
    rv = client.get('/api/sensors/1', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert len(SensorModel.query.all()) == 1
    assert json_data['status'] == 'Sensor successfully retrieved'
    assert json_data['sensor'] == {
        'name': 'Sensor 1',
        'id': 1, 'user_id': 1,
        'recent_climate_data': {
            'sensor_id': 1,
            'date': '2020-01-31 16:30',
            'battery_voltage': 4.22,
            'id': 1,
            'climate_data': [
                {'climate_id': 1, 'value': 23.45, 'id': 1, 'type': 'Temperature', 'unit': 'c'}
            ]
        }
    }


def test_delete_sensor_endpoint(client):
    # Create account
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()
    access_token = json_data['access_token']

    '''
    Sensor doesn't exist
    '''
    rv = client.delete('/api/sensors/1', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 500
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert len(SensorModel.query.all()) == 0
    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Sensor doesn\'t exist']

    '''
    Missing auth
    '''
    sensor_1 = SensorModel(name='Sensor 1', id=1, user_id=1)
    climate_data_1 = ClimateModel(sensor_id=1, battery_voltage=4.22, date=datetime(2020, 1, 31, 16, 30, 33, 619535))
    sensor_data_1 = SensorDataModel(climate_id=1, value=23.45, type='Temperature', unit='c')
    sensor_1.save()
    climate_data_1.save()
    sensor_data_1.save()

    rv = client.delete('/api/sensors/1')
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Missing Authorization Header']

    '''
    Success
    '''
    assert len(SensorModel.query.all()) == 1

    rv = client.delete('/api/sensors/1', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert len(SensorModel.query.all()) == 0
    assert len(ClimateModel.query.all()) == 0
    assert len(SensorDataModel.query.all()) == 0
    assert json_data['status'] == 'Sensor successfully deleted'

    '''
    Invalid token
    '''
    rv = client.post('/api/logout/access', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'

    rv = client.delete('/api/sensors/1', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The token is invalid as it has been revoked']


def test_patch_sensor_endpoint(client):
    # Create account
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/account', json={
        'email': email,
        'password': password
    })
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()
    access_token = json_data['access_token']

    '''
    Sensor doesn't exist
    '''
    rv = client.patch('/api/sensors/1', json={
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 500
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert len(SensorModel.query.all()) == 0
    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Sensor doesn\'t exist']

    '''
    No JSON data error
    '''
    sensor_1 = SensorModel(name='Sensor 1', id=1, user_id=1)
    sensor_1.save()

    rv = client.patch('/api/sensors/1', json={
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 400
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['No input data provided']
    assert len(SensorModel.query.all()) == 1

    '''
    Missing auth
    '''
    rv = client.patch('/api/sensors/1', json={
        'name': 'Greenhouse sensor',
        'sensor_id': 5
    })
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['Missing Authorization Header']
    assert len(SensorModel.query.all()) == 1

    '''
    Name isn’t a string
    '''
    rv = client.patch('/api/sensors/1', json={
        'name': 5,
        'sensor_id': 5
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"name": [
        "Not a valid string."
    ]}
    assert len(SensorModel.query.all()) == 1

    '''
    sensor_id isn’t a integer
    '''
    rv = client.patch('/api/sensors/1', json={
        'name': 'Greenhouse sensor',
        'sensor_id': False
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"sensor_id": [
        "Not a valid integer."
    ]}
    assert len(SensorModel.query.all()) == 1

    '''
    Name is too long
    '''
    rv = client.patch('/api/sensors/1', json={
        "sensor_id": 5,
        "name": "DTERDIRDNGFIDUFDNGFLDOIJRTYNDFJKLGLDFIUGERNJLTRUTGV"
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 422
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"name": [
        "Length must be between 0 and 40."
    ]}
    assert len(SensorModel.query.all()) == 1

    '''
    Success
    '''
    rv = client.patch('/api/sensors/1', json={
        'name': 'Greenhouse sensor',
        'sensor_id': 5
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Sensor successfully updated'
    assert len(SensorModel.query.all()) == 1
    updated_sensor = SensorModel.query.first()
    assert updated_sensor.name == 'Greenhouse sensor'
    assert updated_sensor.id == 5
    assert updated_sensor.user_id == 1

    '''
    Invalid token
    '''
    rv = client.post('/api/logout/access', headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 200
    assert rv.content_type == 'application/json'

    rv = client.patch('/api/sensors/1', json={
        "sensor_id": 5,
        "name": "Greenhouse sensor"
    }, headers={'Authorization': 'Bearer ' + access_token})
    assert rv.status_code == 401
    assert rv.content_type == 'application/json'
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The token is invalid as it has been revoked']
