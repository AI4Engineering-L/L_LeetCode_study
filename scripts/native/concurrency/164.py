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

class Foo:
    def __init__(self):
        self.first_done = threading.Event()
        self.second_done = threading.Event()
    def first(self, printFirst):
        printFirst()
        self.first_done.set()
    def second(self, printSecond):
        self.first_done.wait()
        printSecond()
        self.second_done.set()
    def third(self, printThird):
        self.second_done.wait()
        printThird()

def run_ordering_case(start_order):
    if sorted(start_order) != [0,1,2]:
        raise ValueError('Each method must be launched exactly once')
    foo = Foo()
    out = []
    methods = [lambda: foo.first(lambda: out.append('first')),
               lambda: foo.second(lambda: out.append('second')),
               lambda: foo.third(lambda: out.append('third'))]
    run_threads([methods[i] for i in start_order])
    return ''.join(out)
