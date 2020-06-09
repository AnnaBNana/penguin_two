import json
import os

with open(os.path.join(os.path.dirname(__file__), "shipping_options.json"), 'r') as json_file:
    SHIPPING_OPTIONS = json.load(json_file)
