from datetime import datetime
from enum import IntEnum


class LogLevel(IntEnum):
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4

LogLevel.currentLevel = LogLevel.INFO

log_messages = []


def log(level, msg):
    log_messages.append((level, msg))
    if level >= LogLevel.currentLevel:
        ts = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        print('[{}] {} {}'.format(ts, level.name, msg))


def get_log_messages():
    return log_messages


def clear_log_messages():
    log_messages = []
