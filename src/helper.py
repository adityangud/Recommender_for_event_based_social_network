import os
import json

def read_json(filename):
    if not os.path.exists(filename):
        return {}

    json_file = open(filename)
    json_str = json_file.read()
    return json.loads(json_str)
