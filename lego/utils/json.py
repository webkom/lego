import json
from datetime import date, datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def serialize(obj):
    """Serialize an object to JSON format"""

    return json.dumps(obj, default=json_serial)
