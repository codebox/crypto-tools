import threading

class RequestProcessor:
    def __init__(self, queue):
        self.queue = queue

    def start(self):
        threading.Thread(target=self._work, daemon=True).start()

    def _work(self):
        while True:
            item = self.queue.get()

            if item['type'] == 'registration':
                print('reg')

            self.queue.task_done()