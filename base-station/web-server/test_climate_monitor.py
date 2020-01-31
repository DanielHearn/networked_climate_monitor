import pytest

from datetime import datetime

from run import app, create_tables, drop_tables, UserModel, SensorModel, RevokedTokenModel, ClimateModel, \
    SensorDataModel
from helpers import create_settings


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
    json_data = rv.get_json()

    endpoint_error = {
        "errors": ["Endpoint doesn\'t exist"],
        "status": "Error"
    }
    assert json_data == endpoint_error


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
    assert new_user.email == 'email@email.com'
    assert UserModel.verify_hash('password', new_user.password)
    assert new_user.settings == str(create_settings())
    assert new_user.reset_token == 'ABCDEFGHIKLMNOPQRSTV'


@pytest.fixture(scope='module')
def new_sensor():
    sensor = SensorModel(name='Sensor 1', id=1, user_id=1)
    return sensor


def test_new_sensor(new_sensor):
    assert new_sensor.name == 'Sensor 1'
    assert new_sensor.id == 1
    assert new_sensor.user_id == 1


@pytest.fixture(scope='module')
def new_revoked_token():
    revoked_token = RevokedTokenModel(jti='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9'
                                          '.eyJpYXQiOjE1Nzg0MTY0MTYsIm5iZiI6MTU3ODQxNjQxNiwianRpIjoiNzIxM2JkMWYtNmJkZi00YzVmLTg1OWQtMDkxM2VkYmUwOGI4IiwiZXhwIjoxNjA5OTUyNDE2LCJpZGVudGl0eSI6ImVtYWlsQGVtYWlsLmNvbSIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.exOM3mytXaqeBvqfu3QFPH9yCLdw11gjONolLQGTq4w')
    return revoked_token


def test_new_revoked_token(new_revoked_token):
    assert new_revoked_token.jti == 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Nzg0MTY0MTYsIm5iZiI6MTU3ODQxNjQxNiwianRpIjoiNzIxM2JkMWYtNmJkZi00YzVmLTg1OWQtMDkxM2VkYmUwOGI4IiwiZXhwIjoxNjA5OTUyNDE2LCJpZGVudGl0eSI6ImVtYWlsQGVtYWlsLmNvbSIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.exOM3mytXaqeBvqfu3QFPH9yCLdw11gjONolLQGTq4w'


@pytest.fixture(scope='module')
def new_climate_data():
    sensor = ClimateModel(sensor_id=1, battery_voltage=4.22, date=datetime(2020, 1, 31, 16, 30, 33, 619535))
    return sensor


def test_new_climate_data(new_climate_data):
    assert new_climate_data.sensor_id == 1
    assert new_climate_data.battery_voltage == 4.22
    assert new_climate_data.date == datetime(2020, 1, 31, 16, 30, 33, 619535)


@pytest.fixture(scope='module')
def new_sensor_data():
    sensor = SensorDataModel(climate_id=1, value=23.45, type='Temperature', unit='c')
    return sensor


def test_new_sensor_data(new_sensor_data):
    assert new_sensor_data.climate_id == 1
    assert new_sensor_data.value == 23.45
    assert new_sensor_data.type == 'Temperature'
    assert new_sensor_data.unit == 'c'


def test_register_endpoint(client):
    '''
    No JSON data error
    '''
    rv = client.post('/api/account', json={
    })
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
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == {"password": [
        "Not a valid string."
    ]}
    assert len(UserModel.query.all()) == 0

    '''
    Use doesn't exist
    '''
    email = "email@email.com"
    password = "password"

    rv = client.post('/api/login', json={
        'email': email,
        'password': password
    })
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
    json_data = rv.get_json()

    assert json_data['status'] == 'Successful login'
    assert type(json_data['access_token']) is str
    assert type(json_data['refresh_token']) is str


def test_logout_access_endpoint(client):
    '''
    Missing auth
    '''
    rv = client.post('/api/logout/access')
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
    json_data = rv.get_json()
    access_token = json_data['access_token']

    rv = client.post('/api/logout/access', headers={'Authorization': 'Bearer ' + access_token})
    json_data = rv.get_json()

    assert json_data['status'] == 'Access token has been revoked'

    '''
    Token has already been revoked
    '''
    rv = client.post('/api/logout/access', headers={'Authorization': 'Bearer ' + access_token})
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The token is invalid as it has been revoked']


def test_logout_refresh_endpoint(client):
    '''
    Missing auth
    '''
    rv = client.post('/api/logout/refresh')
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
    json_data = rv.get_json()
    access_token = json_data['refresh_token']

    rv = client.post('/api/logout/refresh', headers={'Authorization': 'Bearer ' + access_token})
    json_data = rv.get_json()

    assert json_data['status'] == 'Refresh token has been revoked'

    '''
    Token has already been revoked
    '''
    rv = client.post('/api/logout/refresh', headers={'Authorization': 'Bearer ' + access_token})
    json_data = rv.get_json()

    assert json_data['status'] == 'Error'
    assert json_data['errors'] == ['The token is invalid as it has been revoked']


def test_token_refresh_endpoint(client):
    '''
    Missing auth
    '''
    rv = client.post('/api/token/refresh')
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
    json_data = rv.get_json()
    refresh_token = json_data['refresh_token']

    rv = client.post('/api/token/refresh', headers={'Authorization': 'Bearer ' + refresh_token})
    json_data = rv.get_json()

    assert json_data['status'] == 'Successful refresh'
    assert type(json_data['access_token']) is str
