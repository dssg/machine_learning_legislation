import ConfigParser

config = ConfigParser.ConfigParser()
config.read("../../../earmarks.cfg")

def get_connection_string():
    return config.get("keys", "conn")

def get_data_folder():
    return config.get("keys","data")
