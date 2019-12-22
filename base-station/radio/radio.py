from RFM69 import Radio, FREQ_433MHZ
import datetime
import requests
import time

node_id = 1
network_id = 100
connected_sensors = {}
api_root = 'http://192.168.1.180:5000/api/sensors/'


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


def process_packet(packet):
    print('-----------------------')
    packet_data = ascii_to_string(packet.data)
    sensor_id = packet.sender
    packet_date = str(packet.received)

    print('Packet From: Node: ' + str(sensor_id))
    print('Signal: ' + str(packet.RSSI))
    print('Date: ' + packet_date)
    print('Data: ' + packet_data)

    data_parts = packet_data.split('|')

    if len(data_parts) == 2:
        control = data_parts[0]
        main_data = data_parts[1].split('_')[0]

        # Process control
        control_data = control.split(',')
        control_dict = {}
        for control_part in control_data:
            control_parts = control_part.split('=')
            if len(control_parts) == 2:
                control_dict[control_parts[0]] = control_parts[1]

        # Process main packet data
        packet_type = control_dict['T']
        if packet_type == 'C':
            print('Type: Climate Data')

            # Update date of last node communication
            if connected_sensors[sensor_id]:
                connected_sensors[sensor_id].last_date = packet_date
            else:
                print('Sensor isn\'t stored in connected_sensors')

            # Create object for API usage
            climate_api_object = {
                'date': str(packet.received),
                'battery_voltage': control_dict['V'],
                'climate_data': []
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
            sensor = create_sensor(sensor_id, packet_date, start_time, interval_period)
            connected_sensors[sensor_id] = sensor

            # Send back time period
    else:
        print('Packet invalid')


with Radio(FREQ_433MHZ, node_id, network_id, isHighPower=True, verbose=False) as radio:
    print("Starting loop...")
    while True:

        # Process packets at each interval
        for packet in radio.get_packets():
            process_packet(packet)

        # Periodically process packets
        delay = 0.1
        time.sleep(delay)
