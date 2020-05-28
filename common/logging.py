from datetime import datetime
from enum import IntEnum


class LogLevel(IntEnum):
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4

LogLevel.currentLevel = LogLevel.INFO

def log(level, msg):
    if level >= LogLevel.currentLevel:
        ts = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        print('[{}] {} {}'.format(ts, level.name, msg))
