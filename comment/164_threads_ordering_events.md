# N164 · 线程、互斥与顺序同步 —— 说人话详解

> 对应 notebook：`notebooks/20_concurrency/164_threads_ordering_events.ipynb`

## 一、这章要解决什么问题？（问题描述）

LeetCode 1114「Print in Order」的场景是：有一个类暴露 `first`、`second`、`third` 三个方法，三个线程会各自调用其中一个，但**调用（启动）顺序完全随机**。你要保证三个回调的实际执行顺序永远是"先 first、再 second、后 third"，输出恒为 `firstsecondthird`。

举个例子：操作系统可能先调度了执行 `third` 的线程，接着是 `second` 的线程，最后才是 `first` 的线程。如果什么都不做，输出可能是 `thirdsecondfirst`，彻底乱套。我们要的是一种**同步关系**：不管谁先被启动，`second` 必须等 `first` 的回调真正跑完才能开始，`third` 必须等 `second` 跑完才能开始。

一个直观但错误的做法是"睡一会儿"——比如 `third` 里 `time.sleep(0.01)` 赌 `first` 已经跑完。这在慢机器、高负载下随时翻车。正确做法是用线程间通信原语表达"等这件事做完"，而不是"等这么多毫秒"。cell1 里那句话就是这个意思：这是一条执行先后关系，不是"睡一会儿大概够了"。

## 二、关键概念（定义）

- **线程（threading.Thread）**：程序里一条独立执行的指令流。同一个进程里的多个线程共享内存，所以它们能看见同一份变量，也正因为如此才会互相踩踏。
- **共享状态**：多个线程都能读写的变量。本章的 `out` 列表被三个线程同时 append，就是共享状态。
- **竞态（race condition）**：结果取决于线程被调度执行的先后次序。无同步版本输出乱序，就是竞态的直接表现。
- **锁（threading.Lock）**：最基础的互斥工具，同一时刻只允许一个线程持有。本章的 `run_threads` 用 `error_lock` 保护 `errors` 列表，避免多个线程同时 append 出问题。
- **事件（threading.Event）**：一个带内部布尔标志的线程间信号。`set()` 把标志置为真并唤醒所有等待者；`wait()` 在标志为假时阻塞、为真时立即通过。关键性质：**标志有记忆**（latch，门闩语义）——先 `set()` 后 `wait()` 也不会丢失通知，`wait()` 直接放行。这和"一次性的响铃"不同。
- **happens-before（先行发生）**：如果操作 A 完成是操作 B 开始的前提，那 A 一定先于 B 发生。我们用两个 Event 构造出 `first回调 → second回调 → third回调` 的链条。
- **GIL（全局解释器锁）非同步契约**：CPython 的 GIL 保证同一时刻只有一个线程执行字节码，但这不保证线程之间的先后顺序，也不能替代锁和事件——"不会数据撕裂"不等于"顺序正确"。
- **join 与线程泄漏**：`thread.join()` 等一个线程彻底结束。测试最后 `assert threading.active_count()==1`（只剩主线程），就是在检查没有线程泄漏地挂着。
- **隔离进程测试**：把可能卡死的整组线程放进子进程里跑，外层设 20 秒超时；超时就杀掉子进程并让测试失败——超时不算成功，也不用 daemon 线程掩盖卡死。

## 三、解决思路（一步步推导）

**Step 1：把"顺序"翻译成两个"事件"。** 我们需要两个带记忆的信号：`first_done`（first 的回调完成了）和 `second_done`（second 的回调完成了）。三个方法的逻辑就是：

- `first`：直接执行回调，然后 `first_done.set()`。
- `second`：先 `first_done.wait()`，再执行回调，然后 `second_done.set()`。
- `third`：先 `second_done.wait()`，再执行回调。

**Step 2：手推一个"最坏启动顺序"。** 假设线程启动顺序是 `[third, second, first]`（cell6 表格里 6 种排列之一）：

```
时刻    third 线程             second 线程           first 线程
T1     second_done.wait() → 阻塞（标志为假）
T2                            first_done.wait() → 阻塞
T3                                                  printFirst() 执行，输出 'first'
T4                                                  first_done.set() → 标志置真
T5                            被唤醒，wait() 返回
T6                            printSecond() 输出 'second'
T7                            second_done.set()
T8     被唤醒，wait() 返回
T9     printThird() 输出 'third'
最终输出：firstsecondthird
```

**Step 3：事件先触发后等待也不怕。** 如果调度反过来、`first` 线程最先跑完并 `set()` 了，之后 `second` 才走到 `wait()`——因为标志已经是真，`wait()` 立即通过，通知不会丢。这就是选 Event 而不是"发一次性信号"的原因。

**Step 4：正确性传递。** `second` 的回调只在 `first_done` 为真之后运行，而 `first_done` 为真只在 `first` 回调之后；同理 `third` 在 `second` 之后。两级等待串起来，按传递性得到完整顺序——这和 cell4 的论证一致。

**Step 5：测试基建。** `run_threads` 为每个函数开一个线程，用 `guarded` 包一层捕获异常（异常经 `error_lock` 保护后收集，任一线程炸了最后统一 raise）；全部 `join` 之后断言没有线程还活着。`run_ordering_case(start_order)` 校验启动排列合法（0、1、2 各出现一次），按给定顺序把三个方法丢进 `run_threads`，返回拼接后的输出。cell6 的表格把 6 种排列全跑了一遍，输出清一色 `firstsecondthird`；cell8 再把这套东西循环 10 轮防"运气好"。

## 四、代码逐段讲解

cell3 是一段 Python 源码（`THREAD_SOURCE` 字符串），由 `run_isolated` 放进子进程执行；notebook 内核里也 `exec` 了一份供直接调用。

**run_threads（测试基建）：**

```python
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
```

`guarded` 把每个函数包起来抓 `BaseException`（连 `KeyboardInterrupt` 这类都抓），抓到后用 `error_lock` 互斥地放进 `errors`——不加锁的话"三个线程同时 append"本身就是一个竞态。先全部 `start()` 再逐个 `join()`，保证三个线程确实并发启动。如果有任何异常，把第一个重新抛出让测试失败；最后那句 assert 是"所有线程都 join 干净"的兜底检查。docstring 提醒调用者：可能阻塞的用例要放到隔离进程里跑。

**Foo（本章核心，就 15 行）：**

```python
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
```

`__init__` 建两个 Event，初始都是假。`first` 不等任何人：执行回调后 `set()`，向 `second` 发出"我完成了"。`second` 的三行是"等→做→发信号"：先 `wait()` 阻塞到 `first_done` 为真，执行回调，再 `set()` 放行 `third`。`third` 只等不发。注意每个方法都假定"每个方法只被调用一次"，这正是题面给的运行条件。

**run_ordering_case：**

```python
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
```

第一行是边界防御：启动排列必须是 0、1、2 的某个排列，否则直接 ValueError。`out` 是共享输出缓冲，三个回调分别往里 append 各自的名字。`methods[i]` 把"方法下标"映射到对应的调用函数，按 `start_order` 重排后交给 `run_threads`。最后把列表拼成字符串返回，方便断言比较。

## 五、为什么是对的？复杂度是多少？（说人话）

**正确性：** 关键事实有三个。第一，`first_done` 只在 `first` 的回调执行完之后才可能为真（`set()` 写在回调后面）；第二，`second` 的回调只在 `first_done` 为真之后才运行（`wait()` 写在回调前面）；两者合起来就是"second 回调必然晚于 first 回调"。third 与 second 之间是同样的关系，串起来按传递性得到完整顺序。第三，因为每个方法只被调用一次，三个回调各执行一次，输出长度也对。活性（最终都能跑完）还需要附加前提：三个方法都被调用、回调有限完成、线程最终获得调度——如果有人永远不调 `first`，`second` 就会永远等下去，这不是算法 bug 而是输入没满足。

**复杂度：** 同步状态只有两个 Event，O(1) 空间。等待时长由任务本身和操作系统调度决定，任何"固定多少毫秒"的说法都不成立。另外 cell4 特意提醒：调度相关的测试跑有限次通过，不等于证明了所有环境下都及时响应——所以测试循环了 10 轮只是增加信心，不是证明。

## 六、测试用例在测什么

cell8 的测试代码在子进程里执行：

```python
for _ in range(10):
    for order in itertools.permutations(range(3)):
        assert run_ordering_case(order) == 'firstsecondthird'
assert threading.active_count() == 1
```

- `itertools.permutations(range(3))` 枚举 6 种启动排列（cell6 的表格就是它的输出，每行是"启动顺序 → 实际输出"）：这是穷举边界，说明无论谁先启动结果都一样。
- 外层 `for _ in range(10)`：重复 10 轮，覆盖不同的线程调度运气——单次通过可能只是碰巧。
- 断言值 `'firstsecondthird'`：回调顺序恰好是先 first 后 second 再 third，一个字符都不能错位。
- `threading.active_count()==1`：所有工作线程都被 join 回收，没有泄漏线程（若 second/third 卡死在 wait，join 就不会返回，子进程会超时被杀，测试失败而不是"侥幸通过"）。
- 从测试基建看，`run_threads` 里任何一个线程抛异常都会导致 `raise errors[0]`，加上子进程 20 秒超时兜底——"卡死"和"异常"都算失败，绝不算成功。

## 七、练习思路提示

**练习 1（枚举三线程启动排列）：** 提示：排列就是 `itertools.permutations` 给出的 6 种。对每种排列画一条和第三节那样的线程时间线，标出谁在 `wait()` 里阻塞、哪个 `set()` 唤醒了谁。手算完可以用 `run_ordering_case` 逐个验证，预测和结果应当完全一致。边界别忘了"排列不合法要报错"（比如 `[0,0,1]`）。

**练习 2（构造无同步版本的交错）：** 提示：把 `Foo` 里的两个 Event 拿掉、回调直接执行，就是无同步版。你要做的是**构造**一种可能的交错并论证它输出错误，而不是赌跑一万次必然出错——比如给出"third 线程先被调度完整执行"的时刻表，推出输出 `third...`。可以借助"主线程先 start 哪个、操作系统先跑哪个"的组合来描述，不必真的让错误随机复现。

## 八、对应 LeetCode 题目

- **1114. Print in Order（canonical）**：就是本章的原题——三个方法、三个线程、任意启动顺序，用两个 Event（或两个 Semaphore、一个 Condition）构造 happens-before 链，保证输出恒为 `firstsecondthird`。
