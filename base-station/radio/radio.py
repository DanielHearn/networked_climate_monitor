# Imports
from RFM69 import Radio, FREQ_433MHZ
from datetime import timedelta, datetime
import requests
import time
import dateutil.parser
from apscheduler.schedulers.background import BackgroundScheduler
import json

from helpers import ascii_to_string, milliseconds_to_time_period, create_sensor, convert_type_to_string, get_unit_from_type

# Config variables
base_station_id = 255
network_id = 100
api_root = 'http://0.0.0.0/api/'
api_key = 'xgLxTX7Nkem5qc9jllg2'
encrypt_key = 'pnOvzy105sF5g8Ot'
number_of_time_periods = 10

# State variables
connected_sensors = {}
time_periods = {}
settings = {}

intervalMappings = {
    '5_min': 300000,
    '10_min': 600000,
    '30_min': 1800000,
    '60_min': 3600000
}

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


def process_climate_data(packet_data, sensor_id, control_dict, main_data):
    """
    Process a climate data packet

    Parameters
    ----------
    packet_data : string
        String of the radio packet data
    sensor_id : integer
        Sensor ID assigned by the base station
    control_dict : dictionary
        Dictionary of the control data from a radio packet
    main_data : string
        String of the main data from a radio packet
    """

    # Create object for API usage
    climate_api_object = {
        'date': str(packet_data),
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


def get_next_available_sensor_id():
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


def process_initialisation(radio, sensor_id, packet_datetime):
    """
    Calculate next time period for the node to start sending data at

    Parameters
    ----------
    radio : radio
        Radio instance
    sensor_id : integer
        Sensor ID assigned by the base station
    packet_datetime : datetime
        Datetime that the packet was received
    """

    print('Type: Node Initialisation')
    new_id = sensor_id

    # Allocate sensor ID for new sensor
    if sensor_id == 254:
        print('Allocating ID for new sensor')
        try:
            new_id = get_next_available_sensor_id()
        except:
            print('Error while retrieving next available sensor ID')
            return None

    # Calculate time period
    assigned_period = None
    global time_periods

    # Assign a time period if a time period is available or has already been assigned to the sensor ID
    for period in time_periods:
        sensor = time_periods[period]
        if sensor == new_id:
            assigned_period = period
            break
        elif sensor is None:
            assigned_period = period
            break

    if assigned_period is None:
        # No time period available so cancel processing packet
        print('No available intervals')
        return None
    else:
        # Assign time period
        time_periods.update({str(assigned_period): new_id})

    print('Assigned sensor with period: ' + assigned_period)
    print('Using measurement interval: ' + settings['measurement_interval'])
    start_time = milliseconds_to_time_period(datetime.now(), settings['measurement_interval'], int(assigned_period))

    # Create sensor object to track connected sensors
    id_str = str(new_id)
    sensor = create_sensor(id_str, packet_datetime)
    connected_sensors[id_str] = sensor

    payload_data = 'T=I|id=' + str(new_id) + ',next=' + str(start_time)
    print(payload_data)

    # Send back time period
    radio.send(sensor_id, payload_data)

    # Assemble sensor object
    sensor_name = 'Sensor ' + str(new_id)
    sensor_api_object = {
        'name': sensor_name,
        'user_id': 1,
        'sensor_id': new_id
    }
    params = {
        'api_key': api_key
    }

    # Attempt to create sensor
    # Will fail if the sensor already exists
    try:
        sensor_post_url = api_root + 'sensors'
        response = requests.post(sensor_post_url, json=sensor_api_object, params=params)
        print(response.json())
    except:
        print('Error sending data to API')


def process_packet(packet, radio):
    """
    Process a radio packet

    Parameters
    ----------
    packet : dictionary
        Radio packet
    radio : radio
        Radio instance
    """

    print('-----------------------')

    # Get packet data
    packet_data = ascii_to_string(packet.data)
    sensor_id = packet.sender
    packet_date = str(packet.received)
    packet_datetime = dateutil.parser.parse(packet_date)

    # Display packet data
    print('Packet From: Node: ' + str(sensor_id))
    print('Signal: ' + str(packet.RSSI))
    print('Date: ' + packet_date)
    print('Data: ' + packet_data)

    data_parts = packet_data.split('|')

    # Process packet data if it is in the required format
    if len(data_parts) == 2:
        control = data_parts[0]
        main_data = data_parts[1].split('_')[0]

        # Process control
        control_dict = process_packet_control(control)

        # Process main packet data
        packet_type = control_dict['T']
        if packet_type == 'C':
            print('Type: Climate Data')

            # Update date of last node communication
            id_str = str(sensor_id)
            if id_str in connected_sensors:
                # Update last communication date for the sensor
                connected_sensors[id_str]['last_date'] = packet_datetime

                assigned_period = None
                global time_periods

                # Find which time period has been assigned to the sensor
                for period in time_periods:
                    sensor = time_periods[period]
                    if sensor == sensor_id:
                        assigned_period = period
                        break

                # If sensor has an assigned time period then send the next time period
                if assigned_period:
                    print('Sensor has time period: ' + assigned_period)
                    next_send_time = milliseconds_to_time_period(datetime.now(), settings['measurement_interval'], int(assigned_period))
                    payload_data = 'T=T|next=' + str(next_send_time)
                    print("Sending time period")
                    print(payload_data)

                    if radio.send(sensor_id, payload_data, attempts=3, wait=400, require_ack=True):
                        print('Received ack')
                    else:
                        print('No ack')
                else:
                    print('Sensor isn\'t stored in time periods')

                # Send climate data to API
                process_climate_data(packet.received, sensor_id, control_dict, main_data)
            else:
                print('Sensor isn\'t stored in connected_sensors')

                # Request re-initialisation from sensor node
                payload_data = 'T=RI|'
                print("Sending re-initialisation request")
                if radio.send(sensor_id, payload_data, attempts=3, wait=400, require_ack=True):
                    print('Received ack')
                else:
                    print('No ack')

                # Send climate data to API
                process_climate_data(packet.received, sensor_id, control_dict, main_data)

        elif packet_type == 'I':
            process_initialisation(radio, sensor_id, packet_datetime)
    else:
        # Packet doesn't match any expected packet type so it cannot be processed
        print('Packet invalid')


def remove_inactive_sensors():
    """
    Removes inactive sensors
    """

    print('Removing inactive sensors')
    global connected_sensors
    connected_sensors = filter_inactive_sensors(connected_sensors)


def filter_inactive_sensors(sensors):
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
    inactive_time = datetime.now() - timedelta(milliseconds=intervalMappings[settings['measurement_interval']]*2)

    temp_sensors = {}

    # Filter only active sensors
    for sensor_id in sensors:
        sensor = connected_sensors[sensor_id]

        # Keep sensors that have communicated in the last measurement period
        if sensor['last_date'] > inactive_time:
            temp_sensors[sensor_id] = sensor
        else:
            print('Removed sensor with id: ' + sensor_id)

            # Remove sensor from assigned time period
            for period in time_periods:
                period_sensor = time_periods[period]
                if period_sensor == sensor_id:
                    time_periods.update({str(period): None})

    return temp_sensors


def init_time_periods():
    """
    Initialise the time periods
    """
    for i in range(1, number_of_time_periods):
        time_periods[str(i)] = None


def run_radio():
    """
    Initialise radio and process radio packets
    """

    # Initialise the radio and start processing packets
    with Radio(FREQ_433MHZ, base_station_id, network_id, isHighPower=True, verbose=False,
               encryptionKey=encrypt_key) as radio:
        print("Starting radio loop")
        while True:

            # Process packets at each interval
            for packet in radio.get_packets():
                process_packet(packet, radio)

            # Periodically process packets
            delay = 0.05
            time.sleep(delay)


def retrieve_settings():
    '''
    Retrieves new settings from API and triggers node reinitialisation if new settings are found
    -------

    '''
    global settings
    global connected_sensors

    params = {
        'api_key': api_key
    }
    settings_get_url = api_root + 'base-station-settings'
    response = requests.get(settings_get_url, params=params)
    response_data = response.json()
    raw_settings = response_data['settings'].replace('\'', '"')
    new_settings = json.loads(raw_settings)
    settings = new_settings


def run():
    """
    Initialise program and start radio loop
    """
    retrieve_settings()

    # Initialise sensor communication time periods
    init_time_periods()

    # Create scheduler
    scheduler = BackgroundScheduler()

    # Create job to remove inactive sensors every 10 minutes
    inactive_job = scheduler.add_job(remove_inactive_sensors, 'interval', minutes=25)
    settings_job = scheduler.add_job(retrieve_settings, 'interval', minutes=5)
    scheduler.start()

    if settings['measurement_interval']:
        # Start processing incoming radio packets
        run_radio()
    else:
        print('Settings not loaded')

    # Shutdown any scheduler jobs
    inactive_job.remove()
    settings_job.remove()
    scheduler.shutdown()


# Start program
run()
