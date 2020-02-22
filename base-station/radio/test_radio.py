import pytest
from datetime import datetime
from helpers import create_sensor, convert_type_to_string, get_unit_from_type, ascii_to_string, \
    milliseconds_to_time_period, process_packet_control, retrieve_settings, get_next_available_sensor_id, \
    init_time_periods, process_climate_data, filter_inactive_sensors
from radio import process_initialisation
import responses
from RFM69 import Radio, FREQ_433MHZ

api_root = 'http://0.0.0.0/api/'
api_key = 'xgLxTX7Nkem5qc9jllg2'


@responses.activate
def test_retrieve_settings():
    api_key = 'xgLxTX7Nkem5qc9jllg2'
    responses.add(responses.GET, api_root + 'base-station-settings',
                  json={
                      'settings': "{\"temperature_unit\":\"c\",\"measurement_interval\":\"10_min\",\"wifi\":{\"ssid\":\"test-wifi\",\"password\":\"test-password\"}}"},
                  status=200)
    assert retrieve_settings(api_key, api_root) == {
        'temperature_unit': 'c',
        'measurement_interval': '10_min',
        'wifi': {
            'ssid': 'test-wifi',
            'password': 'test-password'
        }
    }
    with pytest.raises(Exception):
        assert retrieve_settings()


@responses.activate
def test_get_next_available_sensor_id():
    responses.add(responses.GET, api_root + 'sensors/actions/next-available-sensor-id',
                  json={"status": "Next available ID found", "ID": 1}, status=200)
    assert get_next_available_sensor_id(api_key, api_root) == 1
    with pytest.raises(Exception):
        assert get_next_available_sensor_id()


@responses.activate
def test_process_climate_data():
    responses.add(responses.POST, api_root + 'sensors/1/climate-data?api_key=xgLxTX7Nkem5qc9jllg2',
                  json={"status": "Climate data successfully set"}, status=200)
    process_climate_data(datetime(2020, 1, 1), 1, {'T': 'I', 'V': '3.92'}, 'T=19.58,H=51.46,P=1023.82', api_key,
                         api_root)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://0.0.0.0/api/sensors/1/climate-data?api_key=xgLxTX7Nkem5qc9jllg2'
    assert responses.calls[0].request.body == str.encode('{"date": "2020-01-01 00:00:00", "battery_voltage": "3.92", ' \
                                                         '"climate_data": [{"type": "Temperature", "value": "19.58", ' \
                                                         '"unit": "c"}, {"type": "Humidity", "value": "51.46", "unit": "%"}, ' \
                                                         '{"type": "Pressure", "value": "1023.82", "unit": "hPa"}]}')
    assert responses.calls[0].response.json() == {"status": "Climate data successfully set"}
    with pytest.raises(Exception):
        assert process_climate_data()


def test_filter_inactive_sensors():
    now = datetime.now()
    sensors = {
        '1': {
            'id': 1,
            'last_date': datetime(2020, 1, 1)
        },
        '2': {
            'id': 2,
            'last_date': now
        }
    }
    time_periods = {
        '1': 1,
        '2': 2,
        '3': None,
        '4': None,
        '5': None
    }
    interval = 60000
    assert filter_inactive_sensors(sensors, time_periods, interval) == {
        'sensors': {
            '2': {
                'id': 2,
                'last_date': now
            }
        },
        'time_periods': {
            '1': None,
            '2': 2,
            '3': None,
            '4': None,
            '5': None
        }
    }
    with pytest.raises(Exception):
        assert filter_inactive_sensors()

def test_init_time_periods():
    assert init_time_periods(5) == {
        '1': None,
        '2': None,
        '3': None,
        '4': None,
        '5': None
    }
    with pytest.raises(Exception):
        assert init_time_periods()

def test_process_packet_control():
    assert process_packet_control('T=I,V=3.92') == {
        'T': 'I',
        'V': '3.92'
    }
    assert process_packet_control('T=T') == {
        'T': 'T'
    }
    with pytest.raises(Exception):
        assert process_packet_control(5)


def test_create_sensor():
    id = 1
    date = datetime.now()
    sensor = create_sensor(id, date)
    assert sensor['id'] == 1
    assert sensor['last_date'] == date


def test_convert_type_to_string():
    assert convert_type_to_string('H') == 'Humidity'
    assert convert_type_to_string('T') == 'Temperature'
    assert convert_type_to_string('P') == 'Pressure'
    with pytest.raises(Exception):
        assert convert_type_to_string('C')


def test_get_unit_from_type():
    assert get_unit_from_type('Humidity') == '%'
    assert get_unit_from_type('Temperature') == 'c'
    assert get_unit_from_type('Pressure') == 'hPa'
    with pytest.raises(Exception):
        assert get_unit_from_type('Wind Direction')


def test_ascii_to_string():
    assert ascii_to_string([49, 55]) == '17'
    assert ascii_to_string([72, 101, 108, 108, 111]) == 'Hello'
    with pytest.raises(Exception):
        assert ascii_to_string('Test')


def test_milliseconds_to_time_period():
    now = datetime(2020, 1, 27, 13, 0, 0, 0)
    assert milliseconds_to_time_period(now, '5_min', 1) == 300000
    assert milliseconds_to_time_period(now, '10_min', 1) == 600000
    assert milliseconds_to_time_period(now, '30_min', 1) == 1800000
    assert milliseconds_to_time_period(now, '60_min', 1) == 3600000

    now = datetime(2020, 1, 27, 13, 1, 0, 0)
    assert milliseconds_to_time_period(now, '5_min', 1) == 240000
    assert milliseconds_to_time_period(now, '10_min', 1) == 540000
    assert milliseconds_to_time_period(now, '30_min', 1) == 1740000
    assert milliseconds_to_time_period(now, '60_min', 1) == 3540000

    now = datetime(2020, 1, 27, 13, 8, 0, 0)
    assert milliseconds_to_time_period(now, '5_min', 1) == 120000
    assert milliseconds_to_time_period(now, '10_min', 1) == 120000
    assert milliseconds_to_time_period(now, '30_min', 1) == 1320000
    assert milliseconds_to_time_period(now, '60_min', 1) == 3120000

    now = datetime(2020, 1, 27, 13, 12, 0, 0)
    assert milliseconds_to_time_period(now, '5_min', 1) == 180000
    assert milliseconds_to_time_period(now, '10_min', 1) == 480000
    assert milliseconds_to_time_period(now, '30_min', 1) == 1080000
    assert milliseconds_to_time_period(now, '60_min', 1) == 2880000

    now = datetime(2020, 1, 27, 13, 25, 0, 0)
    assert milliseconds_to_time_period(now, '5_min', 1) == 300000
    assert milliseconds_to_time_period(now, '10_min', 1) == 300000
    assert milliseconds_to_time_period(now, '30_min', 1) == 300000
    assert milliseconds_to_time_period(now, '60_min', 1) == 2100000

    now = datetime(2020, 1, 27, 13, 47, 0, 0)
    assert milliseconds_to_time_period(now, '5_min', 1) == 180000
    assert milliseconds_to_time_period(now, '10_min', 1) == 180000
    assert milliseconds_to_time_period(now, '30_min', 1) == 780000
    assert milliseconds_to_time_period(now, '60_min', 1) == 780000

    now = datetime(2020, 1, 27, 23, 59, 0, 0)
    assert milliseconds_to_time_period(now, '5_min', 1) == 60000
    assert milliseconds_to_time_period(now, '10_min', 1) == 60000
    assert milliseconds_to_time_period(now, '30_min', 1) == 60000
    assert milliseconds_to_time_period(now, '60_min', 1) == 60000
