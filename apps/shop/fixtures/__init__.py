import json

with open('shipping_options.json') as json_file:
    SHIPPING_OPTIONS = json.load(json_file)
