# Imports
from RFM69 import Radio, FREQ_433MHZ
from datetime import timedelta, datetime
import requests
import time
import dateutil.parser
from apscheduler.schedulers.background import BackgroundScheduler

from helpers import ascii_to_string, milliseconds_to_time_period, create_sensor, process_packet_control,\
    retrieve_settings, get_next_available_sensor_id, init_time_periods, process_climate_data, filter_inactive_sensors

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
            new_id = get_next_available_sensor_id(api_key, api_root)
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
                    next_send_time = milliseconds_to_time_period(datetime.now(), settings['measurement_interval'],
                                                                 int(assigned_period))
                    payload_data = 'T=T|next=' + str(next_send_time)
                    print("Sending time period")
                    print(payload_data)

                    if radio.send(sensor_id, payload_data, attempts=3, wait=400, require_ack=True):
                        print('Received ack')
                    else:
                        print('No ack')
                else:
                    print('Sensor isn\'t stored in time periods')
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
            process_climate_data(packet.received, sensor_id, control_dict, main_data, api_key, api_root)

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
    global time_periods
    data = filter_inactive_sensors(connected_sensors, time_periods, intervalMappings[settings['measurement_interval']])
    connected_sensors = data['sensors']
    time_periods = data['time_periods']


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


def load_settings():
    global settings
    settings = retrieve_settings(api_key, api_root)


def run():
    """
    Initialise program and start radio loop
    """
    load_settings()

    # Initialise sensor communication time periods
    global time_periods
    time_periods = init_time_periods(number_of_time_periods)

    # Create scheduler
    scheduler = BackgroundScheduler()

    # Create job to remove inactive sensors every 10 minutes
    inactive_job = scheduler.add_job(remove_inactive_sensors, 'interval', minutes=25)
    settings_job = scheduler.add_job(load_settings, 'interval', minutes=5)
    scheduler.start()

    if settings['measurement_interval']:
        print('Settings:')
        print(settings)
        # Start processing incoming radio packets
        run_radio()
    else:
        print('Settings not loaded')

    # Shutdown any scheduler jobs
    inactive_job.remove()
    settings_job.remove()
    scheduler.shutdown()

if __name__ == '__main__':
    # Start program
    run()
