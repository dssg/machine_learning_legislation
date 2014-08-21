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

def get_path_to_reports():
    return os.path.join(get_data_folder(), "congress_reports")

def get_path_to_bills():
    return os.path.join(get_data_folder(), "bills")

def get_path_to_classification_data():
    return os.path.join(get_data_folder(), "classification_data")

def get_path_to_omb_data():
    return os.path.join(get_data_folder(), "OMB")

def get_path_to_plaws():
    return os.path.join(get_data_folder(), "plaws")

