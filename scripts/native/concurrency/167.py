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

class DiningPhilosophersFIFO:
    def __init__(self):
        self.condition = threading.Condition()
        self.waiting = deque()
        self.next_ticket = 0
        self.owners = [None]*5
        self.events = []
    def _event(self,action,ticket,philosopher,payload=None):
        self.events.append((action,ticket,philosopher,payload))
    def wantsToEat(self,philosopher,pickLeftFork,pickRightFork,eat,putLeftFork,putRightFork):
        if philosopher not in range(5):
            raise ValueError('Philosopher must be 0..4')
        left,right = philosopher,(philosopher+1)%5
        with self.condition:
            ticket = self.next_ticket
            self.next_ticket += 1
            self.waiting.append((ticket,philosopher))
            self._event('request',ticket,philosopher)
            self.condition.notify_all()
            while self.waiting[0][0] != ticket or self.owners[left] is not None or self.owners[right] is not None:
                self.condition.wait()
            self.waiting.popleft()
            self.owners[left] = self.owners[right] = ticket
            self._event('grant',ticket,philosopher,(left,right))
            self.condition.notify_all()
        try:
            pickLeftFork()
            with self.condition:self._event('pick',ticket,philosopher,left)
            pickRightFork()
            with self.condition:self._event('pick',ticket,philosopher,right)
            eat()
            with self.condition:self._event('eat',ticket,philosopher)
            putLeftFork()
            with self.condition:self._event('put',ticket,philosopher,left)
            putRightFork()
            with self.condition:self._event('put',ticket,philosopher,right)
        finally:
            with self.condition:
                self.owners[left] = self.owners[right] = None
                self._event('release',ticket,philosopher,(left,right))
                self.condition.notify_all()
        return ticket

def validate_fork_trace(events):
    waiting = deque()
    records = {}
    owners = [None]*5
    for action,ticket,p,payload in events:
        forks = {p,(p+1)%5}
        if action=='request':
            assert ticket not in records
            records[ticket] = {'p':p,'picked':set(),'put':set(),'eaten':0,'released':False,'granted':False}
            waiting.append(ticket)
            continue
        assert ticket in records and records[ticket]['p']==p
        record = records[ticket]
        assert not record['released']
        if action=='grant':
            assert waiting and waiting.popleft()==ticket
            assert not record['granted'] and set(payload)==forks
            assert all(owners[f] is None for f in forks)
            for f in forks:owners[f]=ticket
            record['granted']=True
        elif action=='pick':
            assert record['granted'] and payload in forks and owners[payload]==ticket
            assert payload not in record['picked']
            record['picked'].add(payload)
        elif action=='eat':
            assert record['picked']==forks and not record['put'] and record['eaten']==0
            assert all(owners[f]==ticket for f in forks)
            record['eaten']=1
        elif action=='put':
            assert record['eaten']==1 and payload in forks and payload not in record['put']
            assert owners[payload]==ticket
            record['put'].add(payload)
        elif action=='release':
            assert record['put']==forks and record['eaten']==1 and set(payload)==forks
            assert all(owners[f]==ticket for f in forks)
            for f in forks:owners[f]=None
            record['released']=True
        else:
            raise AssertionError('Unknown trace event')
    assert not waiting and all(x is None for x in owners)
    assert all(r['released'] for r in records.values())
    return True
