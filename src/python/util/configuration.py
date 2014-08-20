import os
import ConfigParser

config = ConfigParser.ConfigParser()
absolute_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(absolute_path, "../../../conf/earmarks.cfg")
print absolute_path, __file__
print config_path
config.read(config_path)

def get_connection_string():
    return config.get("keys", "conn")

def get_data_folder():
    return config.get("keys","data")
