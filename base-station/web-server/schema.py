from marshmallow import Schema, fields, validate


## SCHEMA

class UserSchema(Schema):
    """
    Schema representing a user
    """
    email = fields.Email(required=True, validate=validate.Length(min=0, max=120))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=40))
    settings = fields.Str(dump_only=True, required=True)


class UserPatchSchema(Schema):
    """
    Schema representing a user
    """
    email = fields.Email(required=False, validate=validate.Length(min=0, max=120))
    password = fields.Str(required=False, validate=validate.Length(min=8, max=40))
    settings = fields.Str(required=False)


class SensorSchema(Schema):
    """
    Schema representing a sensor
    """
    name = fields.Str(required=True, validate=validate.Length(min=0, max=40))
    sensor_id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)


class SensorPatchSchema(Schema):
    """
    Schema representing a user
    """
    name = fields.Str(required=False, validate=validate.Length(min=0, max=40))
    sensor_id = fields.Integer(required=False)
    user_id = fields.Integer(required=False)


class SensorDataSchema(Schema):
    """
    Schema representing the data of an individual sensor reading
    """
    value = fields.Float(required=True)
    type = fields.Str(required=True, validate=validate.Length(min=0, max=100))
    unit = fields.Str(required=True, validate=validate.Length(min=0, max=20))


class ClimateDataSchema(Schema):
    """
    Schema representing the data of an individual climate data reading
    """
    battery_voltage = fields.Float(required=True)
    date = fields.DateTime(required=True)
    climate_data = fields.List(fields.Nested(SensorDataSchema), required=True)


class ChangePasswordSchema(Schema):
    """
    Schema representing the post data of the change password endpoint
    """
    reset_token = fields.Str(required=True, validate=validate.Length(equal=20))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=40))
