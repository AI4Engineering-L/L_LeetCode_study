"""Real synchronization, subprocess-isolated tests, explicit liveness assumptions."""
from course_builder import add

THREAD_BASE = '''import threading
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
'''
ISOLATION = '''
import json
import subprocess
import sys

# This defines the visible APIs only; it does not launch a thread.
exec(THREAD_SOURCE, globals())

def run_isolated(extra):
    """A timeout is a failure; subprocess.run kills and reaps the child."""
    result = subprocess.run([sys.executable, '-c', THREAD_SOURCE + '\\n' + extra],
        text=True, capture_output=True, check=True, timeout=20)
    return result.stdout
'''
def thread_code(source):
    return "THREAD_SOURCE = r'''" + source + "'''\n" + ISOLATION

T164 = THREAD_BASE + '''
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
'''
add(164,
'''启动顺序不是执行顺序。即使先启动 third 线程，也必须等 second 的回调完成；这是一条执行先后关系，而不是“睡一会儿大概够了”。

first 在回调结束后设置事件 A，second 等 A 后运行并设置 B，third 等 B。事件保留已触发状态，因此先触发再等待也不会丢失通知。

测试实际启动线程，并把整组可能阻塞的线程放进独立进程。外层超时会终止并回收子进程，同时使 Notebook 测试失败；没有把超时算成成功，也不使用 daemon 线程掩盖泄漏。''',
thread_code(T164),
'''from IPython.display import Code
display(Code(THREAD_SOURCE,language='python'))
rows = json.loads(run_isolated("import json,itertools; print(json.dumps([[list(p),run_ordering_case(p)] for p in itertools.permutations(range(3))]))"))
show_table(['thread start order','actual callback order'],rows)
''',
'''print(run_isolated("""import itertools
for _ in range(10):
    for order in itertools.permutations(range(3)):
        assert run_ordering_case(order) == 'firstsecondthird'
assert threading.active_count() == 1
print('All six start orders passed; every worker joined.')
"""))
''',
'''A 只能在 first 回调之后触发，second 只能在 A 之后运行；同理 third 在 second 之后。因此由传递性保证完整顺序，各方法启动一次保证回调各一次。活性另要求所有方法都被调用、回调有限完成、线程最终获得调度。''',
'''同步状态 O(1)。等待时间由任务和调度决定，不应声称固定毫秒延迟；调度测试有限次通过不等于证明所有环境都及时响应。''')

T165 = THREAD_BASE + '''
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
'''
add(165,
'''条件变量的通知不是“轮到我”的证明。线程被唤醒后必须在同一把锁下用 while 重新检查 turn；否则错误唤醒或竞争可能破坏交替顺序。

FooBar 用状态机 0→1→0；ZeroEvenOdd 用三组许可证：初始只允许 zero，zero 根据下一数字的奇偶把唯一的工作许可转交给对应线程；数字线程打印后再把许可交回 zero。

每个打印回调都假定有限完成且不抛异常。把回调作为可失败的业务任务时，需额外设计取消与故障传播，不应悄悄把这类契约塞进教学算法。''',
thread_code(T165),
'''rows = json.loads(run_isolated("""import json
obj=ZeroEvenOdd(5);trace=[]
run_threads([lambda:obj.even(trace.append),lambda:obj.odd(trace.append),lambda:obj.zero(trace.append)])
print(json.dumps([[i,value,'zero -> number' if value==0 else 'number -> zero'] for i,value in enumerate(trace)]))
"""))
show_table(['step','printed','permission transfer'],rows)
''',
'''print(run_isolated("""import itertools
for n in [0,1,3,10]:
    for order in itertools.permutations(range(2)):
        obj=FooBar(n);out=[]
        methods=[lambda:obj.foo(lambda:out.append('foo')),lambda:obj.bar(lambda:out.append('bar'))]
        run_threads([methods[i] for i in order])
        assert ''.join(out)=='foobar'*n
    for order in itertools.permutations(range(3)):
        obj=ZeroEvenOdd(n);out=[]
        methods=[lambda:obj.zero(out.append),lambda:obj.even(out.append),lambda:obj.odd(out.append)]
        run_threads([methods[i] for i in order])
        assert out==[x for i in range(1,n+1) for x in (0,i)]
assert threading.active_count()==1
print('Alternation, counts, and worker cleanup passed.')
"""))
''',
'''FooBar 在锁内检查、打印、切换状态，整个转换是原子的。零奇偶算法每一步只开放下一类合法操作的许可，按 i 归纳得到 0,1,0,2,…,0,n。有限测试不证明调度公平；活性以相关线程最终被调度为前提。''',
'''输出 2n 个标记，算法状态 O(1)。记录测试轨迹需 O(n) 额外空间，但不是同步算法自身所需。''')

T166 = THREAD_BASE + '''
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
'''
add(166,
'''H2O 不要求三个原子的内部次序为 HHO，但每个连续三原子批次必须恰好两个 H、一个 O。信号量限制成分，屏障等待本批三次回调全部完成后才释放下一批许可证。

有界队列的关键是两个条件：满时生产者等待，空时消费者等待。检查条件、修改队列和通知都在同一互斥区；wait 会释放锁，使能够改变条件的对方有机会前进。

队列可选记录真实操作轨迹，用于显示占用与检查线性化次序；默认不记录，避免教学监测让正常队列空间随操作次数增长。''',
thread_code(T166),
'''rows = json.loads(run_isolated("""import json
q=BoundedBlockingQueue(2,record_trace=True)
def produce():
    for value in range(6):q.enqueue(value)
def consume():
    for _ in range(6):q.dequeue()
run_threads([consume,produce])
print(json.dumps(q.history))
"""))
show_table(['operation','value','queue size after operation'],rows)
''',
'''print(run_isolated("""import itertools,random
from collections import Counter
for arrival in sorted(set(itertools.permutations('HHHHOO'))):
    water=H2O();out=[];lock=threading.Lock()
    def append(atom):
        with lock:out.append(atom)
    functions=[(lambda:water.hydrogen(lambda:append('H'))) if atom=='H'
               else (lambda:water.oxygen(lambda:append('O'))) for atom in arrival]
    run_threads(functions)
    assert len(out)==6
    assert all(Counter(out[i:i+3])==Counter('HHO') for i in range(0,6,3))
for capacity in [1,2,5]:
    q=BoundedBlockingQueue(capacity,record_trace=True)
    outputs=[];out_lock=threading.Lock()
    def producer(p):
        for i in range(12):q.enqueue((p,i))
    def consumer():
        for _ in range(12):
            value=q.dequeue()
            with out_lock:outputs.append(value)
    functions=[lambda p=p:producer(p) for p in range(3)]+[consumer for _ in range(3)]
    random.Random(capacity).shuffle(functions)
    run_threads(functions)
    assert Counter(outputs)==Counter((p,i) for p in range(3) for i in range(12))
    assert q.size()==0
    assert all(0<=size<=capacity for _,_,size in q.history)
    enqueued=[value for action,value,size in q.history if action=='enqueue']
    dequeued=[value for action,value,size in q.history if action=='dequeue']
    assert enqueued==dequeued
assert threading.active_count()==1
print('Molecule batches, FIFO linearization, capacity and exact delivery passed.')
"""))
''',
'''屏障释放前已有本批全部三个回调，因此下一批不会插入本批输出中。队列在锁内 append/popleft，分别是入队与出队的线性化点；长度不变量由满/空 while 检查保持。队列完成需要生产消费数量匹配；水分子需要原子计量匹配，这些不是超时后偷偷忽略的输入。''',
'''队列单次结构操作 O(1)，默认存储 O(capacity)，诊断轨迹另占 O(操作次数)。同步等待时长依赖负载和调度；屏障/许可证状态 O(1)。''')

T167 = THREAD_BASE + '''
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
'''
add(167,
'''“没有死锁”不等于“没有饥饿”。本章采用 FIFO 请求队列，在一把条件锁内同时预留两把叉子：不允许线程拿一把叉子再等另一把，因此消除循环等待；FIFO 则阻止后来的请求无限插队。

队列单位必须是**请求票号**，不是哲学家编号。同一位哲学家可以有多个并发调用，每个调用必须拥有独立的等待、授予和释放记录。

严格 FIFO 会产生队头阻塞：即使后面某个请求能立即获得两把空闲叉子，也可能等待队头。这是可解释公平性与吞吐量的取舍。下面的检查器重放真实资源轨迹，验证独占、持有两叉再吃、准确释放以及票号顺序。''',
thread_code(T167),
'''rows = json.loads(run_isolated("""import json
obj=DiningPhilosophersFIFO()
callbacks=[lambda:None]*5
run_threads([lambda p=p:obj.wantsToEat(p,*callbacks) for p in [0,2,4,1,3]])
assert validate_fork_trace(obj.events)
print(json.dumps(obj.events))
"""))
show_table(['event','ticket','philosopher','forks'],rows)
''',
'''print(run_isolated("""from collections import Counter
for _ in range(3):
    obj=DiningPhilosophersFIFO()
    first_started=threading.Event();release_first=threading.Event();go=threading.Event()
    seen=Counter();seen_lock=threading.Lock();tickets=[]
    requests=[0,0,0,1,2,3,4,0,2,4]
    def request(i,p):
        if i:go.wait()
        def eating():
            if i==0:
                first_started.set();release_first.wait()
            with seen_lock:seen[i]+=1
        ticket=obj.wantsToEat(p,lambda:None,lambda:None,eating,lambda:None,lambda:None)
        with seen_lock:tickets.append(ticket)
    def coordinate():
        first_started.wait();go.set()
        with obj.condition:
            while obj.next_ticket != len(requests):obj.condition.wait()
        release_first.set()
    run_threads([lambda i=i,p=p:request(i,p) for i,p in enumerate(requests)]+[coordinate])
    assert validate_fork_trace(obj.events)
    assert seen==Counter({i:1 for i in range(len(requests))})
    assert len(set(tickets))==len(requests)
    bad=list(obj.events)
    bad.insert(1,('eat',0,0,None))
    try:validate_fork_trace(bad)
    except AssertionError:pass
    else:raise AssertionError('Eating without forks was accepted')
assert threading.active_count()==1
print('FIFO tickets, concurrent repeated philosophers, ownership and cleanup passed.')
"""))
''',
'''安全性：grant 在同一锁内同时检查并设置两个 owner，任何叉子不会属于两个票号。无死锁：已获准请求不再等待叉子；它有限完成后释放，队头最终可进。无饥饿需要有限回调、锁与线程弱公平调度，以及每个已排队请求之前仅有有限个请求；按票号归纳，前序请求终会退出。有限压测只检查此次运行，不代替这些活性前提。回调异常会向外传播；轨迹不完整不会被检查器视为成功。''',
'''叉子状态 O(1)，FIFO 队列 O(q)。本章为核验保存 O(r) 条事件；条件通知可能唤醒多个等待者，不声称每个请求的总调度开销为 O(1)。''')
