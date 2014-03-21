import logging
from app.config import Config
from os import path
from time import gmtime, strftime

FORMAT_STRING = "%(asctime)s - %(levelname)s - %(message)s"

config = Config()
app_dir = path.dirname(path.abspath(__file__))
logs_dir = path.normpath(path.join(app_dir, "..", "logs"))
timestamp_log_name = strftime("%Y-%m-%d %H:%M:%S.log", gmtime())
timestamp_log_path = path.join(logs_dir, timestamp_log_name)

player_log_name = "player{}.log".format(config.turn)
player_log_path = path.join(logs_dir, player_log_name)

if path.exists(logs_dir):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ts = logging.FileHandler(timestamp_log_path)
    ts.setLevel(logging.DEBUG)

    gl = logging.FileHandler(player_log_path)
    gl.setLevel(logging.DEBUG)

    formatter = logging.Formatter(FORMAT_STRING)
    ts.setFormatter(formatter)
    gl.setFormatter(formatter)

    logger.addHandler(ts)
    logger.addHandler(gl)
