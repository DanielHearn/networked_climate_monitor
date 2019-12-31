from marshmallow import Schema, fields, validate

## SCHEMA

class UserSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(min=0, max=120))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=40))
    settings = fields.Str(dump_only=True, required=True)


class SensorSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=0, max=40))
    sensor_id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)


class ClimateDataSchema(Schema):
    battery_voltage = fields.Float(required=True)
    date = fields.DateTime(required=True)
    climate_data = fields.List(fields.Dict(
        value=fields.Integer(required=True),
        type=fields.Str(required=True, validate=validate.Length(min=0, max=100)),
        unit=fields.Str(required=True, validate=validate.Length(min=0, max=20))
    ))