from RFM69 import Radio, FREQ_433MHZ
import datetime
import requests
import time
import threading
import dateutil.parser
from apscheduler.schedulers.background import BackgroundScheduler

node_id = 1
network_id = 100
connected_sensors = {}
api_root = 'http://192.168.1.180:5000/api/sensors/'
api_key = 'xgLxTX7Nkem5qc9jllg2'


def create_sensor(id, last_date, start_time, interval_time):
    sensor = {
        "id": id,
        "last_date": last_date,
        "start_time": start_time,
        "interval_time": interval_time
    }
    return sensor


def ascii_to_string(ascii_array):
    converted_string = ''

    for x in ascii_array:
        converted_string += chr(x)

    return converted_string


def convert_type_to_string(type_char):
    types = {
        'H': 'Humidity',
        'T': 'Temperature',
        'P': 'Pressure'
    }

    return types[type_char]


def process_packet_control(control):
    control_dict = {}
    control_data = control.split(',')
    for control_part in control_data:
        control_parts = control_part.split('=')
        if len(control_parts) == 2:
            control_dict[control_parts[0]] = control_parts[1]
    return control_dict


def process_packet(packet, radio):
    print('-----------------------')
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

            if len(connected_sensors):
                if id_str in connected_sensors:
                    connected_sensors[id_str]['last_date'] = packet_datetime
                else:
                    print('Sensor isn\'t stored in connected_sensors')
                    sensor = create_sensor(id_str, packet_datetime, 0, 500)
                    connected_sensors[id_str] = sensor
            else:
                sensor = create_sensor(id_str, packet_datetime, 0, 500)
                connected_sensors[id_str] = sensor

            # Create object for API usage
            climate_api_object = {
                'date': str(packet.received),
                'battery_voltage': control_dict['V'],
                'climate_data': [],
                'api_key': api_key
            }

            # Process climate data
            climate_data_parts = main_data.split(',')
            for climate_part in climate_data_parts:
                climate_parts = climate_part.split('=')
                if len(climate_parts) == 2:
                    type = convert_type_to_string(climate_parts[0])
                    value = climate_parts[1]
                    climate_data_dict = {
                        'type': type,
                        'value': value
                    }
                    climate_api_object['climate_data'].append(climate_data_dict)

            print(climate_api_object)

            # Send climate data to API
            try:
                climate_post_url = api_root + str(sensor_id) + '/climate-data'
                response = requests.post(climate_post_url, json=climate_api_object)
                print(response.json())
            except:
                print('Error sending data to API')
        elif packet_type == 'I':
            print('Type: Node Initialisation')
            # Calculate time period
            start_time = 100
            interval_period = 500

            # Create sensor object to track connected sensors
            sensor = create_sensor(sensor_id, packet_datetime, start_time, interval_period)
            connected_sensors[sensor_id] = sensor

            payload_data = 'T=T|initial=' + start_time + ',interval=' + interval_period
            print('Assigned start_time: ' + start_time + ', interval: ' + interval_period)

            # Send back time period
            radio.send(sensor_id, payload_data)
    else:
        print('Packet invalid')


def remove_inactive_sensors():
    print('Removing inactive sensors')
    global connected_sensors
    connected_sensors = filter_inactive_sensors(connected_sensors)


def filter_inactive_sensors(sensors):
    now = datetime.datetime.now()
    inactive_time = now - datetime.timedelta(minutes=10)
    temp_sensors = {}

    # Filter only active sensors
    for sensor_id in connected_sensors:
        sensor = connected_sensors[sensor_id]

        # Keep sensors that have communicated in the last 10 minutes
        if sensor['last_date'] > inactive_time:
            temp_sensors[sensor_id] = sensor
        else:
            print('Removed sensor with id: ' + sensor_id)
    return temp_sensors


def run():
    scheduler = BackgroundScheduler()

    # Create job to remove inactive sensors every 10 minutes
    inactive_job = scheduler.add_job(remove_inactive_sensors, 'interval', minutes=10)
    scheduler.start()

    # Initialise the radio and start processing packets
    with Radio(FREQ_433MHZ, node_id, network_id, isHighPower=True, verbose=False) as radio:
        print("Starting loop...")
        while True:

            # Process packets at each interval
            for packet in radio.get_packets():
                process_packet(packet, radio)

            # Periodically process packets
            delay = 0.1
            time.sleep(delay)

    # Shutdown any scheduler jobs
    inactive_job.remove()
    scheduler.shutdown()


run()
