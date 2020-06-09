import yaml
from configparser import ConfigParser

def load_schema(file_path):
    with open(f"{file_path}") as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        schema = yaml.load(file, Loader=yaml.FullLoader)
    return schema

def read_search_config(search_file):
    config = ConfigParser()
    config.read(search_file)
    config.sections()
    return [dict(config.items(s)) for s in config.sections()]