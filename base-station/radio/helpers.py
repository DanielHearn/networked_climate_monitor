from datetime import timedelta, datetime
import requests
import json


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
        start_time = start_time.replace(minute=int(minutes), second=0, microsecond=0)
        start_time = start_time + timedelta(seconds=20 * adjusted_time_period)
    elif interval == '10_min':
        start_time = now + timedelta(minutes=10)
        minutes = str(start_time.minute)
        if len(minutes) == 1:
            minutes = 0
        else:
            minutes = minutes[0] + '0'
        start_time = start_time.replace(minute=int(minutes), second=0, microsecond=0)
        start_time = start_time + timedelta(seconds=30 * adjusted_time_period)
    elif interval == '30_min':
        start_time = now + timedelta(minutes=30)
        minutes = str(start_time.minute)
        if len(minutes) == 1:
            minutes = 0
        else:
            if int(minutes) < 30:
                minutes = 0
            else:
                minutes = 30
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


# Process packet control data
def process_packet_control(control):
    """
    Process packet control string into a dictionary

    Parameters
    ----------
    control : string
        String of the control data from a radio packet

    Returns
    -------
    dictionary
        Dictionary of the control data from a radio packet
    """
    control_dict = {}
    control_data = control.split(',')

    # Create a new key value pair for control data
    for control_part in control_data:
        control_parts = control_part.split('=')
        if len(control_parts) == 2:
            control_dict[control_parts[0]] = control_parts[1]
    return control_dict


def retrieve_settings(api_key, api_root):
    '''
    Retrieves new settings from API and triggers node reinitialisation if new settings are found
    -------

    '''
    params = {
        'api_key': api_key
    }
    try:
        settings_get_url = api_root + 'base-station-settings'
        response = requests.get(settings_get_url, params=params)
        response_data = response.json()
        if 'settings' in response_data:
            raw_settings = response_data['settings'].replace('\'', '"')
            new_settings = json.loads(raw_settings)
            return new_settings
        else:
            print('Bad response for settings retrieval')
            return None
    except:
        print('Bad response for settings retrieval')
        return None


def get_next_available_sensor_id(api_key, api_root):
    """
    Return the next unused sensor ID

    Returns
    -------
    integer
        Next unused sensor ID
    """

    params = {
        'api_key': api_key
    }

    # Retrieve sensor ID from API
    sensor_next_id_url = api_root + 'sensors/actions/next-available-sensor-id'
    response = requests.get(sensor_next_id_url, params=params)
    response_data = response.json()
    if response_data['ID']:
        return response_data['ID']
    else:
        print('Couldn\'t retrieve next sensor ID')
        return None


def init_time_periods(number_of_time_periods):
    """
    Initialise the time periods
    """
    time_periods = {}
    for i in range(0, number_of_time_periods):
        time_periods[str(i + 1)] = None
    return time_periods


def process_climate_data(packet_date, sensor_id, control_dict, main_data, api_key, api_root):
    """
    Process a climate data packet

    Parameters
    ----------
    packet_date : datetime
        Packet datetime
    sensor_id : integer
        Sensor ID assigned by the base station
    control_dict : dictionary
        Dictionary of the control data from a radio packet
    main_data : string
        String of the main data from a radio packet
    """

    # Create object for API usage
    climate_api_object = {
        'date': str(packet_date),
        'battery_voltage': control_dict['V'],
        'climate_data': []
    }
    params = {
        'api_key': api_key
    }

    # Process climate data
    climate_data_parts = main_data.split(',')
    for climate_part in climate_data_parts:
        climate_parts = climate_part.split('=')

        # Generate climate data dictionary from key value pair in packet
        if len(climate_parts) == 2:
            sensor_type = convert_type_to_string(climate_parts[0])
            unit = get_unit_from_type(sensor_type)
            value = climate_parts[1]

            climate_data_dict = {
                'type': sensor_type,
                'value': value,
                'unit': unit
            }
            climate_api_object['climate_data'].append(climate_data_dict)

    print(climate_api_object)

    # Send climate data to API
    try:
        climate_post_url = api_root + 'sensors/' + str(sensor_id) + '/climate-data'
        response = requests.post(climate_post_url, json=climate_api_object, params=params)
        print(response.json())
    except:
        print('Error sending data to API')


def filter_inactive_sensors(sensors, time_periods, interval):
    """
    Removes sensors that have not send data in the last 10 minutes

    Parameters
    ----------
    sensors : dictionary
        Dictionary containing all of the sensors currently connected to the base station

    Returns
    -------
    dictionary
        Dictionary containing active sensors that have communicated in the last 10 minutes
    """

    # Calculate date based on the current interval period
    inactive_time = datetime.now() - timedelta(milliseconds=interval * 2)

    temp_sensors = {}
    temp_time_periods = time_periods

    # Filter only active sensors
    for sensor_id in sensors:
        sensor = sensors[sensor_id]

        # Keep sensors that have communicated in the last measurement period
        if sensor['last_date'] > inactive_time:
            temp_sensors[sensor_id] = sensor
        else:
            print('Removed sensor with id: ' + sensor_id)
            # Remove sensor from assigned time period
            temp_time_periods[str(sensor_id)] = None

    return {'sensors': temp_sensors, 'time_periods': temp_time_periods}
