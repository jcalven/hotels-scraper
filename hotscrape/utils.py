import yaml
from configparser import ConfigParser

def load_schema(filename="db_schema.yml", path="."):
    with open(f"{path}/{filename}") as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        schema = yaml.load(file, Loader=yaml.FullLoader)
    return schema

def read_search_config(search_file):
        config = ConfigParser()
        config.read(search_file)
        config.sections()
        return [dict(config.items(s)) for s in config.sections()]