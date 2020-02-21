import pytest
from datetime import timedelta, datetime
from helpers import create_sensor, convert_type_to_string, get_unit_from_type, ascii_to_string, \
    milliseconds_to_time_period


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
