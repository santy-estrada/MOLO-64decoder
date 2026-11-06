import base64
from dataclasses import dataclass
from datetime import datetime, timezone

# Protocol Buffer imports and initialization from sensor_pb2.py
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0csensor.proto\"<\n\nSensorData\x12\n\n\x02UI\x18\x01 \x02(\t\x12\x0c\n\x04time\x18\x02 \x02(\x05\x12\x14\n\x0cmeasurements\x18\x03 \x03(\x02'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'sensor_pb2', globals())
_SENSORDATA = DESCRIPTOR.message_types_by_name['SensorData']
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _SENSORDATA._serialized_start=16
    _SENSORDATA._serialized_end=76

# Decoding logic from decoder.py[cite: 1]
NB_MEASUREMENTS = 6

def int_to_iso8601(value: int) -> str:
    """Convert a Unix timestamp in seconds to an ISO 8601 UTC string."""
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()

def conversion_volt(value):
    """
    Convert raw value to voltage
    Current encoding requires sender to convert to 0-4095 range
    """
    if not value:
        return float('nan')
    return (value / 4095.0) * 3.3 # V_ref = 3.3V

@dataclass
class Sensor:
    UI: str
    time: str
    a0: float
    a1: float
    a2: float
    a3: float
    a4: float
    a5: float

def decode_proto_data(data_b64: str) -> Sensor | None:
    """
    Decodes a base64 payload containing a Protobuf SensorData message.
    Returns a Sensor object (with NaN if some values are missing).
    """
    try:
        data_bytes = base64.b64decode(data_b64)
        
        # SensorData is made available globally by the _builder above
        msg = globals()["SensorData"]()
        msg.ParseFromString(data_bytes)
        
        measurements = list(msg.measurements)
        while len(measurements) < NB_MEASUREMENTS:
            measurements.append(float('nan'))
        
        return Sensor(
            UI = msg.UI,
            time = int_to_iso8601(msg.time),
            a0=conversion_volt(measurements[0]),
            a1=conversion_volt(measurements[1]),
            a2=conversion_volt(measurements[2]),
            a3=conversion_volt(measurements[3]),
            a4=conversion_volt(measurements[4]),
            a5=conversion_volt(measurements[5])
        )
    except Exception as e:
        print("Error in Protobuf decoding:", e)
        return None

if __name__ == "__main__":
    # Replace this placeholder with the base64 string to decode.
    encoded_string = "ChBhODYxMGEzNDMzNGQ3MTBkEIee49YGGhgAQNVEACAtRQCQFkUAgBRFADAVRQAAFUU="
    decoded_result = decode_proto_data(encoded_string)
    print(decoded_result)