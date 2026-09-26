# N166 · 屏障、生产消费与有界队列 —— 说人话详解

> 对应 notebook：`notebooks/20_concurrency/166_barriers_bounded_queues.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决两个"多线程协作"的经典问题：

1. **H2O 分子组装（LeetCode 1117）**：多个线程调用 `hydrogen`（打出一个 H）或 `oxygen`（打出一个 O）。要求输出流里，**每连续三个字符必须恰好构成一个"水分子批次"：两个 H 加一个 O**。例如线程到达顺序是 `H O H H O H`，合法输出可以是 `HHOHHO`、`HOHHHO`、`OHHHHO`……批内三个字符的内部顺序随意，但批与批不能串线——不允许出现 `HHHHOO`（四个 H 挤在一起）这种把两个批次的原子混在一起的结果。
2. **有界阻塞队列（LeetCode 1188）**：实现一个容量固定的线程安全队列 `BoundedBlockingQueue`。容量 2 的队列：生产者往里放 6 个元素、消费者取 6 个元素，队列满了生产者必须睡等，队列空了消费者必须睡等，且任何时刻队列长度不能超过 2。

给个具体数字感受一下第二个问题：容量 2，生产者连放 0、1 之后队列长度是 2；这时生产者想放 2 就必须阻塞，直到消费者取走一个（长度变 1）才能放进去。cell6 的表格记录的就是这样一条"操作—值—操作后队列长度"的轨迹，其中长度列始终夹在 0 和 2 之间。

两个问题共同的骨架是：**用同步原语维护"容量约束"和"批次完整性"这两个不变量**。

## 二、关键概念（定义）

- **屏障（Barrier）**：`threading.Barrier(k)` 是一个集合点——前 k-1 个到达的线程都阻塞，第 k 个一到，全体同时放行。本章 `Barrier(3)` 用来凑齐"2 个 H + 1 个 O"成一个分子：三个回调都完成了，下一批才能开始。
- **信号量（Semaphore）当成分额**：`Semaphore(2)` 和 `Semaphore(1)` 分别是"H 名额 2 个、O 名额 1 个"，从源头保证每个批次成分正确。信号量在这里做的是**容量约束**：拿不到名额的线程睡觉，而不是空转。
- **生产者/消费者模型**：一类线程往缓冲区放数据，另一类线程取数据。协调规则只有两条：满时生产者等，空时消费者等。
- **条件变量（Condition）与两个谓词**：`with condition:` 进互斥区；不满才能 enqueue（谓词 `len != capacity`），不空才能 dequeue（谓词 `items 非空`）。`wait()` 释放锁并睡觉，这正是关键——锁松开手，才有机会让"能改变条件的另一方"进来动队列。
- **not_empty / not_full 两个条件共享一把锁**：Python 标准库的 `queue.Queue` 内部就是这么命名的两个等待队列。本章实现里生产者和消费者其实共用同一个 Condition 的等待池，`notify_all` 一叫醒，两边各自重查自己的谓词，效果等价。
- **容量不变量**：`0 <= len(items) <= capacity` 在任何观测时刻都成立。它靠"检查条件、修改队列、通知"全部发生在同一互斥区来保证。
- **线性化点（linearization point）**：一个操作"对外看来生效"的瞬间。本章 enqueue 的 `append`、dequeue 的 `popleft` 都在锁内执行，所以锁内的那一次 append/popleft 就是各自的线性化点；轨迹表里 enqueued 序列和 dequeued 序列完全相同（FIFO），正说明这些点排成了一个一致的全局顺序。
- **轨迹记录（record_trace）**：队列可选地把每次操作记成 `(动作, 值, 操作后长度)`，用来事后检查容量与顺序。默认关闭，因为记录会让空间随操作次数线性增长（cell1 特意说明这是"教学监测"的代价，不是队列本身的代价）。

## 三、解决思路（一步步推导）

**Step 1：H2O 拆成两件事——控成分、控批次。** 成分用两个信号量控制：`hydrogen_slots=Semaphore(2)`、`oxygen_slots=Semaphore(1)`，凑够"最多 2H+1O"才有资格打印；批次用 `Barrier(3)` 控制：三个幸运儿都打印完自己的字符后，在屏障处集合，全部到齐才一起放行，放行后才把名额还回去。

**Step 2：手推一个 H2O 时间线。** 假设线程到达顺序是 H、H、O、H、O：

```
H1 拿 H 名额(剩1) → 打印 H → 到屏障等待
H2 拿 H 名额(剩0) → 打印 H → 到屏障等待
O1 拿 O 名额(剩0) → 打印 O → 屏障凑齐3人，第1批 = "HHO" 完成，全体放行
   三人各自 release 名额 → H 名额回到 2、O 名额回到 1
H3 拿 H 名额 → 打印 H → 屏障等待
O2 拿 O 名额 → 打印 O → 屏障等待
H1(或任一 H 线程再来一次)… 直到第2批凑齐 2H+1O
```

要点：第 2 批的打印不可能插进第 1 批的三个字符中间，因为名额还没还回去，第 4 个线程根本进不来；而屏障又保证"本批三个人全打完"是放行前提。

**Step 3：有界队列的两个 while。** enqueue 里 `while len==capacity: wait()`；dequeue 里 `while not items: wait()`。醒来后条件未必还成立（别人可能抢先一步），所以用 while 重查——和 N165 的道理相同。

**Step 4：手推 cell6 的小实例轨迹。** 容量 2，生产者放 0..5，消费者取 6 次。一次典型的运行（两次运行的操作先后可能略不同，但每行的长度值都合法）：

| 操作 | 值 | 操作后队列长度 |
|---|---|---|
| enqueue | 0 | 1 |
| enqueue | 1 | 2（满了） |
| dequeue | 0 | 1 |
| enqueue | 2 | 2 |
| dequeue | 1 | 1 |
| enqueue | 3 | 2 |
| dequeue | 2 | 1 |
| enqueue | 4 | 2 |
| dequeue | 3 | 1 |
| enqueue | 5 | 2 |
| dequeue | 4 | 1 |
| dequeue | 5 | 0 |

生产者在长度为 2 的时刻想继续放就被 `wait()` 挡住，直到消费者取走一个并 `notify_all`。长度列全程在 0..2，出队序列 0,1,2,3,4,5 严格 FIFO。这就是 cell6 表格的三列数据。

**Step 5：为什么 wait 必须放锁。** 假如 wait 不释放锁：生产者满队时抱着锁睡觉，消费者永远拿不到锁、永远取不走元素、永远无法把队列变"不满"——直接死锁。`wait()` 的"原子放锁+睡眠"正是为了打开这个死结。

## 四、代码逐段讲解

cell3 的 `run_threads` 与前两章相同（错误收集、join、隔离进程），略过。核心是两个类。

**H2O：**

```python
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
```

构造函数建三个同步对象：H 名额 2、O 名额 1、3 人屏障。`hydrogen` 四步：`acquire` 抢 H 名额（抢不到睡觉，这一步同时限制了本批 H 最多 2 个）；执行回调打印 H；`molecule_done.wait()` 在屏障等本批另外两位；到齐放行后 `release` 把名额还给下一批。`oxygen` 结构完全对称，只是名额是 1 个。名额在屏障之后才归还，是"批次不串线"的关键：第 4 个原子在第一批三位齐走之前拿不到任何名额。

**BoundedBlockingQueue：**

```python
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
```

构造函数先防御非法容量（0 或负数直接 ValueError），`deque` 当底层容器（两头都 O(1)），一个 Condition，`history` 默认 None、开了才记录。`_record` 把 `(动作, 值, 此刻长度)` 追加进 history——注意它只能在锁内被调用，读到的 `len(self.items)` 才是操作生效后的真实值。`enqueue` 全程持锁：满则 `wait()`（睡着时放锁，消费者有机会进来取）；不满则 `append`、记轨迹、`notify_all` 叫醒可能空等的消费者。`dequeue` 镜像对称：空则等，非空则 `popleft`（FIFO 的线性化点）、记轨迹、通知。`size` 也要拿锁读——不拿锁读长度可能读到半新不旧的值。

## 五、为什么是对的？复杂度是多少？（说人话）

**H2O 的正确性：** 名额（2H+1O）保证任何时刻"已拿名额未归还"的原子集合成分合法；屏障保证本批三个回调全部完成后才放行归还，所以下一批的打印不可能插进本批输出中间——每个连续三字符窗口恰好是一个批次的 2H+1O。**队列的正确性：** append/popleft 都在锁内完成，各自的执行瞬间就是线性化点，所有线程看到的操作顺序是这些点拼成的一条全序；"满不 enqueue、空不 dequeue"由两个 while 谓词保持，因此容量不变量 `0<=len<=capacity` 恒成立。**完成的前提：** cell4 特意指出，队列跑完需要生产数量和消费数量匹配（放 12 取 12 才能收场），H2O 需要 H、O 调用次数成 2:1——这些是输入契约，超时后不能偷偷忽略。

**复杂度：** 队列单次 enqueue/dequeue 都是 O(1)（deque 两端操作常数时间）；默认空间 O(capacity)（元素最多塞满一圈），开了轨迹记录则额外 O(操作次数)。H2O 的屏障与名额状态 O(1)。等待时长取决于负载与调度，无法也不该承诺固定毫秒数。

## 六、测试用例在测什么

cell8 在子进程里分两大块：

- **H2O 块**：`sorted(set(itertools.permutations('HHHHOO')))` 枚举 4 个 H、2 个 O 线程的全部 720 种排列去重后的到达顺序（这是穷举边界——任何启动运气都覆盖）。对每种排列断言两件事：`len(out)==6`（没人丢）；`all(Counter(out[i:i+3])==Counter('HHO') for i in range(0,6,3))`——把输出按 3 个一组切块，每块的多重集合必须等于 {H,H,O}。用 Counter 而不是字符串相等，正体现"批内顺序随意、成分必须恰好"的语义。注意 `append` 回调里用了 `with lock`，因为 6 个线程同时 append 共享列表也要互斥。
- **队列块**：`for capacity in [1,2,5]` 覆盖容量边界（容量 1 时几乎每次操作都要等）。每个容量下：3 个生产者各放 12 个（带编号 `(p,i)`）、3 个消费者各取 12 个，把 6 个线程的顺序用固定种子的 `random.Random(capacity).shuffle` 打乱再启动。断言四件事：`Counter(outputs)==Counter(全部36个值)`——一个不多一个不少，精确送达；`q.size()==0`——收尾干净；`all(0<=size<=capacity for _,_,size in q.history)`——轨迹里每次操作后的长度都没有越界（容量不变量的直接检查）；`enqueued==dequeued`——按轨迹顺序，被放入的序列和被取出的序列完全相同，即 FIFO 且无丢失无重复。
- **收尾**：`assert threading.active_count()==1` 检查全部线程被 join 回收，没有谁卡在 `wait()` 上。

## 七、练习思路提示

**练习 1（可选输出顺序 vs 每批 2H1O 组成约束）**：提示：把"要求"拆成两层——强约束是每个长度为 3 的窗口成分必须是 {H,H,O}，弱约束是批内三个字符谁先谁后都行。你可以先列举 n=1 个分子的全部合法输出（HHO、HOH、OHH 共 3 种），再构造一个非法输出（比如 HHHO…）并说明它违反了哪一条。手算表可以照第二节的 H2O 时间线画，验证时用测试里 `Counter(out[i:i+3])` 的切块法检查即可。

**练习 2（说明多个条件共享同一锁）**：提示：想象标准库 `queue.Queue` 里有 not_empty 和 not_full 两个"候客室"，但整个队列只有一把锁。思考三个问题：为什么两个谓词不能各配一把锁？（两把锁下"检查-修改-通知"就无法互斥，容量会破。）如果生产者和消费者都 `notify_all`，会不会叫错人？（会叫醒不该动的人，但 while 重查保证他们接着睡。）`notify_all` 换成 `notify`（只叫一个）安全吗？（在本实现里恰好可以，但要论证叫醒的一定在等同一条件才稳妥，`notify_all` 是不依赖运气的写法。）用容量 1 的小例子手推一次"满队时三个生产者排队"的唤醒链。

## 八、对应 LeetCode 题目

- **1117. Building H2O（canonical）**：练的是"信号量控成分 + Barrier 控批次"的组合拳，本章 `H2O` 类就是它的直接解。
- **1188. Design Bounded Blocking Queue（extension）**：练的是条件变量的满/空双谓词与容量不变量，本章 `BoundedBlockingQueue` 是教学加强版（多了轨迹记录和 size）。
