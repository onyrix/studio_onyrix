import time

class Scheduler:
    def __init__(self):
        self.queue = []

    def add_event(self, event, delay):
        self.queue.append((time.time() + delay, event))

    def run(self):
        while True:
            now = time.time()
            for e in self.queue:
                if e[0] <= now:
                    self.queue.remove(e)
                    e[1]()