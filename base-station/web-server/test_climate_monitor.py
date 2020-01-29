import os
import tempfile

import pytest

from run import app, create_tables


@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
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
