import configparser
import pathlib

config_path = pathlib.Path(__file__).parent.absolute() / "app.local.conf"
config = configparser.ConfigParser()
config.read(config_path)
