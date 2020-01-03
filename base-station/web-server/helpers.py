import random
import string


def get_unit_from_type(unit_type):
    units = {
        'Humidity': '%',
        'Temperature': 'c',
        'Pressure': 'hPa'
    }
    return units[unit_type]


def create_settings():
    settings = {
        "temperature_unit": "c"
    }
    return settings


def generate_reset_key():
    length = 20
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))
