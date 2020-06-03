import yaml

def load_schema(filename="db_schema.yml", path="."):
    with open(f"{path}/{filename}") as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        schema = yaml.load(file, Loader=yaml.FullLoader)
    return schema