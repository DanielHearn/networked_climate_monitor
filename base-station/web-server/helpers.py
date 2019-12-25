def get_unit_from_type(type):
    units = {
        'Humidity': '%',
        'Temperature': 'c',
        'Pressure': 'hPa'
    }

    return units[type]


def create_settings():
    settings = {
        "temperature_unit": "c"
    }
    return settings
