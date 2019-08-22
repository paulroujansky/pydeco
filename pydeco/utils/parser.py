# Parser utils
import os
import yaml
from ast import literal_eval
from os.path import abspath, dirname, isfile, join, realpath

dir_path = dirname(realpath(__file__))
PROJECT_DIR = abspath(join(dir_path, '..'))


def parse_config():
    """Parse configuration file and return a dictionary."""
    with open(abspath(join(PROJECT_DIR, 'config.yml')), 'r') as file:
        config = yaml.safe_load(file)
    for k, v in config.items():
        config[k] = literal_eval(v)
    return config

CONFIG = parse_config()
