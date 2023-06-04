import os

import yaml

settings_file_path = os.path.join("config", "settings.yml")


def read_settings() -> dict:
    with open(settings_file_path, 'r', encoding='utf-8') as config_file:
        return yaml.load(config_file, Loader=yaml.FullLoader)


def write_settings(data: dict):
    with open(settings_file_path, 'w', encoding='utf-8') as config_file:
        yaml.dump(data, config_file, default_flow_style=False)
