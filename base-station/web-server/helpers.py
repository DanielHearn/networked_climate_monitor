import random
import string


def get_unit_from_type(unit_type):
    """
    Converts the sensor data type into the unit of measurement for that type

    Parameters
    ----------
    type : string
        String describing the sensor data type

    Returns
    -------
    String
        Unit of measurement for that sensor data type
    """
    units = {
        'Humidity': '%',
        'Temperature': 'c',
        'Pressure': 'hPa'
    }
    return units[unit_type]


def create_settings():
    """
    Creates a default settings dictionary

    Returns
    -------
    Dictionary
        Dictionary representing all user settings
    """
    settings = {
        "temperature_unit": "c"
    }
    return settings


def generate_reset_key():
    """
    Generates a password reset token for use in the password reset page

    Returns
    -------
    String
        Password reset token
    """
    length = 20
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))
