# Imports
from RFM69 import Radio, FREQ_433MHZ
from datetime import timedelta, datetime
import requests
import time
import dateutil.parser
from apscheduler.schedulers.background import BackgroundScheduler

# Config variables
node_id = 1
network_id = 100
api_root = 'http://192.168.1.180:5000/api/'
api_key = 'xgLxTX7Nkem5qc9jllg2'
encrypt_key = 'pnOvzy105sF5g8Ot'
number_of_time_periods = 10
node_interval = 600000

# State variables
connected_sensors = {}
time_periods = {}


# Creates a sensor object
def create_sensor(id, last_date, start_time, interval_time):
    sensor = {
        "id": id,
        "last_date": last_date,
        "start_time": start_time,
        "interval_time": interval_time
    }
    return sensor


# Converts an ascii string to the equivalent unicode string
def ascii_to_string(ascii_array):
    converted_string = ''

    for x in ascii_array:
        converted_string += chr(x)

    return converted_string


# Converts sensor type character to the equivalent string
def convert_type_to_string(type_char):
    types = {
        'H': 'Humidity',
        'T': 'Temperature',
        'P': 'Pressure'
    }

    return types[type_char]


# Process packet control data
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
                connected_sensors[id_str]['last_date'] = packet_datetime

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
                        sensor_type = convert_type_to_string(climate_parts[0])
                        value = climate_parts[1]
                        climate_data_dict = {
                            'type': sensor_type,
                            'value': value
                        }
                        climate_api_object['climate_data'].append(climate_data_dict)

                print(climate_api_object)

                # Send climate data to API
                try:
                    climate_post_url = api_root + 'sensors/' + str(sensor_id) + '/climate-data'
                    response = requests.post(climate_post_url, json=climate_api_object)
                    print(response.json())
                except:
                    print('Error sending data to API')
            else:
                print('Sensor isn\'t stored in connected_sensors')

                # Request initialisation
                payload_data = 'T=RI|'
                radio.send(sensor_id, payload_data)
                print("Sent re-initialisation request")
        elif packet_type == 'I':
            print('Type: Node Initialisation')

            # Calculate time period
            assigned_period = None
            global time_periods

            for period in time_periods:
                sensor = time_periods[period]
                if sensor == sensor_id:
                    assigned_period = period
                    break
                elif sensor is None:
                    assigned_period = period
                    break

            if assigned_period is None:
                print('No available intervals')
                return None
            else:
                # Assign time period
                time_periods.update({str(assigned_period): sensor_id})

            # Calculate next time period for the node to start sending data at
            now = datetime.now()
            start_time = now + timedelta(minutes=10)
            start_time -= timedelta(seconds=start_time.second)  - timedelta(microseconds=start_time.microsecond)
            minutes = str(start_time.minute)
            if len(minutes) == 1:
                minutes = '0' + minutes
            period = int(minutes[0] + str(int(assigned_period) - 1))
            start_time = start_time.replace(minute=period)

            print('Assigned sensor with period: ' + assigned_period)
            print('Sensor will start sending at: ' + str(start_time))

            # Calculate milliseconds to the start of the time period
            milliseconds_till_start = int((start_time - now).total_seconds() * 1000)

            start_time = milliseconds_till_start
            interval_period = node_interval

            # Create sensor object to track connected sensors
            id_str = str(sensor_id)
            sensor = create_sensor(id_str, packet_datetime, start_time, interval_period)
            connected_sensors[id_str] = sensor

            payload_data = 'T=T|initial=' + str(start_time) + ',interval=' + str(interval_period)
            print('Assigned start_time: ' + str(start_time) + ', interval: ' + str(interval_period))

            # Send back time period
            radio.send(sensor_id, payload_data)

            # Assemble sensor object
            sensor_name = 'Sensor ' + str(sensor_id)
            sensor_api_object = {
                'name': sensor_name,
                'user_id': 1,
                'sensor_id': sensor_id,
                'api_key': api_key
            }

            # Attempt to create sensor
            # Will fail if the sensor already exists
            try:
                sensor_post_url = api_root + 'sensors'
                response = requests.post(sensor_post_url, json=sensor_api_object)
                print(response.json())
            except:
                print('Error sending data to API')
    else:
        print('Packet invalid')


# Removes inactive sensors
def remove_inactive_sensors():
    print('Removing inactive sensors')
    global connected_sensors
    connected_sensors = filter_inactive_sensors(connected_sensors)


# Removes sensors that have not send data in the last 10 minutes
def filter_inactive_sensors(sensors):
    now = datetime.now()
    inactive_time = now - timedelta(minutes=10)
    temp_sensors = {}

    # Filter only active sensors
    for sensor_id in sensors:
        sensor = connected_sensors[sensor_id]

        # Keep sensors that have communicated in the last 10 minutes
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


# Initialise the time periods
def init_time_periods():
    for i in range(1, number_of_time_periods):
        time_periods[str(i)] = None


# Initialise radio and process radio packets
def run_radio():
    # Initialise the radio and start processing packets
    with Radio(FREQ_433MHZ, node_id, network_id, isHighPower=True, verbose=False, encryptionKey=encrypt_key) as radio:
        print("Starting radio loop")
        while True:

            # Process packets at each interval
            for packet in radio.get_packets():
                process_packet(packet, radio)

            # Periodically process packets
            delay = 0.05
            time.sleep(delay)


# Initialise program and start radio loop
def run():
    init_time_periods()

    scheduler = BackgroundScheduler()

    # Create job to remove inactive sensors every 10 minutes
    inactive_job = scheduler.add_job(remove_inactive_sensors, 'interval', minutes=10)
    scheduler.start()

    run_radio()

    # Shutdown any scheduler jobs
    inactive_job.remove()
    scheduler.shutdown()


# Start program
run()
