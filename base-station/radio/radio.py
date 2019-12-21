from RFM69 import Radio, FREQ_433MHZ
import datetime
import requests
import time

node_id = 1
network_id = 100

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

    print('Packet From: Node: ' + str(sensor_id))
    print('Signal: ' + str(packet.RSSI))
    print('Date: ' + str(packet.received))
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
        if control_dict['T'] == 'C':
            print('Type: Climate Data')
            climate_api_object = {
                'date': str(packet.received),
                'battery_voltage': control_dict['V'],
                'climate_data': []
            }
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
            try:
                climate_post_url = 'http://192.168.1.180:5000/api/sensors/' + str(sensor_id) + '/climate-data'
                response = requests.post(climate_post_url, json=climate_api_object)
                print(response.json())
            except:
                print('Error sending data to API')
    else:
        print('Packet invalid')


with Radio(FREQ_433MHZ, node_id, network_id, isHighPower=True, verbose=False) as radio:
    print ("Starting loop...")
    while True:

        for packet in radio.get_packets():
            process_packet(packet)

        delay = 0.1
        time.sleep(delay)