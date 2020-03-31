from run import app, init, db, SensorModel, ClimateModel, SensorDataModel
from datetime import datetime

def create_test_data():
    print('Creating test data')
    sensor_1 = SensorModel(name='Sensor 1', id=1, user_id=1)
    sensor_1.save()
    sensor_2 = SensorModel(name='Sensor 2', id=2, user_id=1)
    sensor_2.save()
    sensor_3 = SensorModel(name='Sensor 3', id=3, user_id=1)
    sensor_3.save()
    climate_data_list = [
        {
            'id': 1, 'sensor_id': 1, 'battery_voltage': 4.22, 'date': datetime(2019, 11, 10, 16, 30, 33, 619535),
            'climate_data': [{'id': 1, 'climate_id': 1, 'value': 23.45, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 2, 'sensor_id': 1, 'battery_voltage': 4.21, 'date': datetime(2019, 11, 20, 16, 30, 33, 619535),
            'climate_data': [{'id': 2, 'climate_id': 2, 'value': 23.44, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 3, 'sensor_id': 1, 'battery_voltage': 4.2, 'date': datetime(2019, 12, 10, 16, 30, 33, 619535),
            'climate_data': [{'id': 3, 'climate_id': 3, 'value': 23.43, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 4, 'sensor_id': 1, 'battery_voltage': 4.19, 'date': datetime(2019, 12, 20, 16, 30, 33, 619535),
            'climate_data': [{'id': 4, 'climate_id': 4, 'value': 23.42, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 5, 'sensor_id': 1, 'battery_voltage': 4.18, 'date': datetime(2020, 1, 1, 16, 30, 33, 619535),
            'climate_data': [{'id': 5, 'climate_id': 5, 'value': 23.41, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 6, 'sensor_id': 1, 'battery_voltage': 4.17, 'date': datetime(2020, 1, 2, 16, 30, 33, 619535),
            'climate_data': [{'id': 6, 'climate_id': 6, 'value': 23.40, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 7, 'sensor_id': 1, 'battery_voltage': 4.16, 'date': datetime(2020, 1, 3, 16, 30, 33, 619535),
            'climate_data': [{'id': 7, 'climate_id': 7, 'value': 23.39, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 8, 'sensor_id': 1, 'battery_voltage': 4.15, 'date': datetime(2020, 1, 4, 16, 30, 33, 619535),
            'climate_data': [{'id': 8, 'climate_id': 8, 'value': 23.38, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 9, 'sensor_id': 1, 'battery_voltage': 4.14, 'date': datetime(2020, 1, 5, 16, 30, 33, 619535),
            'climate_data': [{'id': 9, 'climate_id': 9, 'value': 23.37, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 10, 'sensor_id': 1, 'battery_voltage': 4.13, 'date': datetime(2020, 1, 6, 16, 30, 33, 619535),
            'climate_data': [{'id': 10, 'climate_id': 10, 'value': 23.36, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 11, 'sensor_id': 1, 'battery_voltage': 4.12, 'date': datetime(2020, 1, 7, 16, 30, 33, 619535),
            'climate_data': [{'id': 11, 'climate_id': 11, 'value': 23.35, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 12, 'sensor_id': 1, 'battery_voltage': 4.11, 'date': datetime(2020, 1, 8, 16, 30, 33, 619535),
            'climate_data': [{'id': 12, 'climate_id': 12, 'value': 23.34, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 13, 'sensor_id': 1, 'battery_voltage': 4.1, 'date': datetime(2020, 1, 8, 16, 30, 33, 619535),
            'climate_data': [{'id': 13, 'climate_id': 13, 'value': 23.33, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 14, 'sensor_id': 1, 'battery_voltage': 4.09, 'date': datetime(2020, 1, 9, 16, 30, 33, 619535),
            'climate_data': [{'id': 14, 'climate_id': 14, 'value': 23.32, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 15, 'sensor_id': 1, 'battery_voltage': 4.08, 'date': datetime(2020, 1, 10, 16, 30, 33, 619535),
            'climate_data': [{'id': 15, 'climate_id': 15, 'value': 23.31, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 16, 'sensor_id': 1, 'battery_voltage': 4.07, 'date': datetime(2020, 1, 11, 16, 30, 33, 619535),
            'climate_data': [{'id': 16, 'climate_id': 16, 'value': 23.30, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 17, 'sensor_id': 1, 'battery_voltage': 4.06, 'date': datetime(2020, 1, 12, 16, 30, 33, 619535),
            'climate_data': [{'id': 17, 'climate_id': 17, 'value': 23.29, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 18, 'sensor_id': 1, 'battery_voltage': 4.05, 'date': datetime(2020, 1, 13, 16, 30, 33, 619535),
            'climate_data': [{'id': 18, 'climate_id': 18, 'value': 23.28, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 19, 'sensor_id': 1, 'battery_voltage': 4.04, 'date': datetime(2020, 1, 14, 16, 30, 33, 619535),
            'climate_data': [{'id': 19, 'climate_id': 19, 'value': 23.27, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 20, 'sensor_id': 1, 'battery_voltage': 4.03, 'date': datetime(2020, 1, 15, 16, 30, 33, 619535),
            'climate_data': [{'id': 20, 'climate_id': 20, 'value': 23.26, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 21, 'sensor_id': 1, 'battery_voltage': 4.02, 'date': datetime(2020, 1, 16, 16, 30, 33, 619535),
            'climate_data': [{'id': 21, 'climate_id': 21, 'value': 23.25, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 22, 'sensor_id': 1, 'battery_voltage': 4.01, 'date': datetime(2020, 1, 17, 16, 30, 33, 619535),
            'climate_data': [{'id': 23, 'climate_id': 22, 'value': 23.24, 'type': 'Temperature', 'unit': 'c'}]
        },
        {
            'id': 23, 'sensor_id': 1, 'battery_voltage': 4.01, 'date': datetime.now(),
            'climate_data': [{'id': 22, 'climate_id': 23, 'value': 23.24, 'type': 'Temperature', 'unit': 'c'}]

        },
    ]
    for climate_data in climate_data_list:
        ClimateModel(sensor_id=climate_data['sensor_id'], battery_voltage=climate_data['battery_voltage'],
                     date=climate_data['date']).save()
        sensor_data_list = climate_data['climate_data']
        for sensor_data in sensor_data_list:
            SensorDataModel(climate_id=sensor_data['climate_id'], value=sensor_data['value'], type=sensor_data['type'],
                            unit=sensor_data['unit']).save()

@app.route('/api/delete-all')
def api_delete_all():
    db.drop_all()
    db.create_all()
    create_test_data()
    return {'status': 'Successfully deleted all database data'}, 200

if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['TEST_SERVER'] = True

    #meta = db.metadata
    #for table in reversed(meta.sorted_tables):
    ##    print('Clear table %s' % table)
    #    db.session.execute(table.delete())
    #db.session.commit()
    db.drop_all()
    db.create_all()

    create_test_data()

    init()
