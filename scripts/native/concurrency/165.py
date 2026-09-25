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

class FooBar:
    def __init__(self,n):
        if n < 0:
            raise ValueError('n must be nonnegative')
        self.n = n
        self.turn = 0
        self.condition = threading.Condition()
    def foo(self, printFoo):
        self._repeat(0,printFoo)
    def bar(self, printBar):
        self._repeat(1,printBar)
    def _repeat(self, turn, callback):
        for _ in range(self.n):
            with self.condition:
                while self.turn != turn:
                    self.condition.wait()
                callback()
                self.turn = 1-turn
                self.condition.notify_all()

class ZeroEvenOdd:
    def __init__(self,n):
        if n < 0:
            raise ValueError('n must be nonnegative')
        self.n = n
        self.zero_gate = threading.Semaphore(1)
        self.odd_gate = threading.Semaphore(0)
        self.even_gate = threading.Semaphore(0)
    def zero(self, printNumber):
        for value in range(1,self.n+1):
            self.zero_gate.acquire()
            printNumber(0)
            (self.odd_gate if value%2 else self.even_gate).release()
    def odd(self, printNumber):
        for value in range(1,self.n+1,2):
            self.odd_gate.acquire()
            printNumber(value)
            self.zero_gate.release()
    def even(self, printNumber):
        for value in range(2,self.n+1,2):
            self.even_gate.acquire()
            printNumber(value)
            self.zero_gate.release()
