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
