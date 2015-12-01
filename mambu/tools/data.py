import yaml
import os


def load_yaml(filename, field=None):
    with open(etc_filepath(filename), 'r') as f:
        result = yaml.load(f)
    if field:
        result = result[field]
    return result


def etc_filepath(filename=None):
    return os.path.join(os.path.dirname(__file__), '..', 'etc', filename)
