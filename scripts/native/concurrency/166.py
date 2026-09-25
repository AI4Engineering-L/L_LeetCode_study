import threading
from collections import deque

def run_threads(functions):
    """Caller must run potentially blocking cases inside the isolated process."""
    errors = []
    error_lock = threading.Lock()
    def guarded(fn):
        try:
            fn()
        except BaseException as error:
            with error_lock:
                errors.append(error)
    threads = [threading.Thread(target=guarded, args=(fn,)) for fn in functions]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if errors:
        raise errors[0]
    assert not any(thread.is_alive() for thread in threads)

class H2O:
    def __init__(self):
        self.hydrogen_slots = threading.Semaphore(2)
        self.oxygen_slots = threading.Semaphore(1)
        self.molecule_done = threading.Barrier(3)
    def hydrogen(self, releaseHydrogen):
        self.hydrogen_slots.acquire()
        releaseHydrogen()
        self.molecule_done.wait()
        self.hydrogen_slots.release()
    def oxygen(self, releaseOxygen):
        self.oxygen_slots.acquire()
        releaseOxygen()
        self.molecule_done.wait()
        self.oxygen_slots.release()

class BoundedBlockingQueue:
    def __init__(self,capacity,record_trace=False):
        if capacity <= 0:
            raise ValueError('Capacity must be positive')
        self.capacity = capacity
        self.items = deque()
        self.condition = threading.Condition()
        self.history = [] if record_trace else None
    def _record(self,action,value):
        if self.history is not None:
            self.history.append((action,value,len(self.items)))
    def enqueue(self,element):
        with self.condition:
            while len(self.items) == self.capacity:
                self.condition.wait()
            self.items.append(element)
            self._record('enqueue',element)
            self.condition.notify_all()
    def dequeue(self):
        with self.condition:
            while not self.items:
                self.condition.wait()
            element = self.items.popleft()
            self._record('dequeue',element)
            self.condition.notify_all()
            return element
    def size(self):
        with self.condition:
            return len(self.items)
