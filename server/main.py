from .web_server import WebServer
from .work_queue import WorkQueue
from .request_processor import RequestProcessor
from common.logging import LogLevel
import logging
import threading
import socket
import time
from signal import signal, SIGINT

HOST = '127.0.0.1'
PORT = 5000

class ServerManager:
    def __init__(self):
        self.server = None

    def start(self):
        work_queue = WorkQueue()
        processor = RequestProcessor(work_queue)
        self.server = WebServer(HOST, PORT, work_queue)

        LogLevel.currentLevel = LogLevel.DEBUG

        processor.start()
        threading.Thread(target=self.server.start).start()
        self._wait_for_port_state(True)

    def stop(self):
        if self.server:
            self.server.stop()
            self.server = None
            self._wait_for_port_state(False)

    def _wait_for_port_state(self, is_open):
        while is_open != self._is_port_open():
            time.sleep(1)

    def _is_port_open(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        is_open = sock.connect_ex((HOST, PORT)) == 0
        sock.close()
        return is_open

server_manager = ServerManager()

def handle_ctrl_c(sig, frame):
    server_manager.stop()

if __name__ == '__main__':
    signal(SIGINT, handle_ctrl_c)
    server_manager.start()
