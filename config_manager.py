import json
import os
import sys

def get_config_path():
    """Returns absolute path to persistent config.json."""
    if getattr(sys, 'frozen', False):
        # In PyInstaller frozen bundle, store config.json next to executable
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, 'config.json')
    else:
        # Development mode
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# Defined for backward compatibility
CONFIG_FILE = get_config_path()

def load_config():
    config_file = get_config_path()
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {config_file}: {e}")

    # Fallback for frozen executable: read bundled config from sys._MEIPASS if persistent config not yet created
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', '')
        bundled = os.path.join(meipass, 'config.json')
        if os.path.exists(bundled):
            try:
                with open(bundled, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                save_config(data)
                return data
            except Exception as e:
                print(f"Error reading bundled config: {e}")

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
    config_file = get_config_path()
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

