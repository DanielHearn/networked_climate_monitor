def get_unit_from_type(type):
    units = {
        'Humidity': '%',
        'Temperature': 'c',
        'Pressure': 'hPa'
    }

    return units[type]