from .web_server import WebServer
from .work_queue import WorkQueue
from .request_processor import RequestProcessor
from common.logging import LogLevel
import logging
import threading
from signal import signal, SIGINT

PORT = 5000

server = None

def start():
    global server

    work_queue = WorkQueue()
    processor = RequestProcessor(work_queue)
    server = WebServer('localhost', PORT, work_queue)

    LogLevel.currentLevel = LogLevel.DEBUG

    processor.start()
    threading.Thread(target=server.start).start()

def stop(_, _2):
    server.stop()

if __name__ == '__main__':
    signal(SIGINT, stop)
    start()
