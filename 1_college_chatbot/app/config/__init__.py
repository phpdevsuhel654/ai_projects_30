from app.config.settings import CONFIG_MAP


def get_config(config_name):
    return CONFIG_MAP.get(config_name.lower(), CONFIG_MAP["development"])
