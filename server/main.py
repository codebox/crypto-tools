from .web_server import WebServer
from .work_queue import WorkQueue
from .request_processor import RequestProcessor
from common.logging import log, LogLevel
import logging
import threading
import urllib
from signal import signal, SIGINT

PORT = 5000

server = None

def start():
    work_queue = WorkQueue()
    processor = RequestProcessor(work_queue)

    server = WebServer('localhost', PORT, work_queue)

    LogLevel.currentLevel = LogLevel.DEBUG

    flask_log = logging.getLogger('werkzeug')
    flask_log.setLevel(logging.ERROR)

    processor.start()
    threading.Thread(target=server.start, daemon=False).start()


def stop(_, _2):
    server.stop()

if __name__ == '__main__':
    signal(SIGINT, stop)
    start()
