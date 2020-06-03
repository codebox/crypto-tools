from enum import Enum
from queue import Queue
from common.logging import log, LogLevel


class WorkQueue:
    def __init__(self):
        self.queue = Queue()
        self.request_statuses = {}

    def add(self, item):
        request_id = item['requestId']
        self.request_statuses[request_id] = RequestStatus.PENDING
        self.queue.put(item, block=False)

    def process_next(self, handler):
        item = self.queue.get()
        request_id = item['requestId']
        try:
            handler(item)
            self.request_statuses[request_id] = RequestStatus.SUCCESS
            self.queue.task_done()

        except Exception as ex :
            log(LogLevel.ERROR, str(ex))
            self.request_statuses[request_id] = RequestStatus.FAILURE
            print('======',self.request_statuses)

    def query(self, id):
        return self.request_statuses.get(id, RequestStatus.UNKNOWN)


class RequestStatus(Enum):
    UNKNOWN = 0
    PENDING = 1
    SUCCESS = 2
    FAILURE = 3
