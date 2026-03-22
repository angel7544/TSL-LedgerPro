import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "database": {
            "type": "sqlite",
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "database": "ledgerpro"
        }
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
