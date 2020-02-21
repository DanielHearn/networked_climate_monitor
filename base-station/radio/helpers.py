from datetime import timedelta, datetime


def create_sensor(id, last_date):
    """
    Creates a dictionary to represent a sensor within the system

    Parameters
    ----------
    id : Integer
        Sensor ID assigned by the base station
    last_date : datetime
        The date that the sensor last communicated with the base station

    Returns
    -------
    Dictionary
        Dictionary representing the sensor within the system
    """
    sensor = {
        "id": id,
        "last_date": last_date
    }
    return sensor


def convert_type_to_string(type_char):
    """
    Converts sensor type character to the equivalent string

    Parameters
    ----------
    type_char : string
        Single character string that represents the sensor data type

    Returns
    -------
    String
        String describing the sensor data type
    """
    types = {
        'H': 'Humidity',
        'T': 'Temperature',
        'P': 'Pressure'
    }

    return types[type_char]


def get_unit_from_type(type):
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

    return units[type]


def ascii_to_string(ascii_list):
    """
    Converts an ascii string to the equivalent unicode string

    Parameters
    ----------
    ascii_list : list
        List of ascii characters

    Returns
    -------
    String
        String of unicode characters that has been assembled from the ascii characters
    """
    converted_string = ''

    for x in ascii_list:
        converted_string += chr(x)

    return converted_string


def milliseconds_to_time_period(now, interval, time_period):
    """
    Calculate next time period for the node to start sending data at

    Parameters
    ----------
    now : datetime
        Date for the current time that the next time period will be calculated from
    interval : string
        String representing the interval length e.g. '30_min'
    time_period : integer
        Integer representing the time period for the sensor

    Returns
    -------
    integer
        Milliseconds until the next climate data sending date based on the time period
    """
    adjusted_time_period = time_period - 1

    if interval == '5_min':
        start_time = now + timedelta(minutes=5)
        minutes = str(start_time.minute)
        print(minutes)
        if len(minutes) == 1:
            if int(minutes[0]) < 5:
                minutes = 0
            else:
                minutes = 5
        else:
            if int(minutes[1]) < 5:
                minutes = minutes[0] + str(0)
            else:
                minutes = minutes[0] + str(5)
        print(minutes)
        start_time = start_time.replace(minute=int(minutes), second=0, microsecond=0)
        start_time = start_time + timedelta(seconds=20 * adjusted_time_period)
    elif interval == '10_min':
        start_time = now + timedelta(minutes=10)
        minutes = str(start_time.minute)
        print(minutes)
        if len(minutes) == 1:
            minutes = 0
        else:
            minutes = minutes[0] + '0'
        print(minutes)
        start_time = start_time.replace(minute=int(minutes), second=0, microsecond=0)
        start_time = start_time + timedelta(seconds=30 * adjusted_time_period)
    elif interval == '30_min':
        start_time = now + timedelta(minutes=30)
        minutes = str(start_time.minute)
        print(minutes)
        if len(minutes) == 1:
            minutes = 0
        else:
            if int(minutes) < 30:
                minutes = 0
            else:
                minutes = 30
        print(minutes)
        start_time = start_time.replace(minute=int(minutes), second=0, microsecond=0)
        start_time = start_time + timedelta(seconds=30 * adjusted_time_period)
    elif interval == '60_min':
        start_time = now + timedelta(minutes=60)
        minutes = 0
        start_time = start_time.replace(minute=int(minutes), second=0, microsecond=0)
        start_time = start_time + timedelta(minutes=1 * adjusted_time_period)

    # Calculate milliseconds to the start of the time period
    milliseconds_till_start = int((start_time - now).total_seconds() * 1000)

    print('Next time period: ' + str(start_time))
    return milliseconds_till_start
