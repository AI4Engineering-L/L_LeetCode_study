# N167 · 死锁、饥饿与哲学家问题 —— 说人话详解

> 对应 notebook：`notebooks/20_concurrency/167_deadlocks_fairness_philosophers.ipynb`

## 一、这章要解决什么问题？（问题描述）

经典"哲学家就餐"问题（LeetCode 1226）：5 位哲学家围一桌，5 把叉子放在相邻两人之间，哲学家 i 的左右叉分别是 `i` 和 `(i+1)%5`。任意线程可以随时调用 `wantsToEat(philosopher, ...)`，方法体内按顺序执行六个回调：拿左叉、拿右叉、吃、放左叉、放右叉。你要保证：

1. **互斥（安全）**：一把叉子同一时刻最多属于一个人，谁也不能和邻居同时开吃。
2. **无死锁**：不会出现"人人心怀一把叉、个个等着另一把"的循环等待，谁也吃不上。
3. **无饥饿（公平）**：只要每个人都有限时长地吃，先来排队的请求不会被后来者无限插队。

三者是递进关系，本章标题"区分安全性、无死锁和有条件的无饥饿"说的就是：**没有死锁不等于没有饥饿**。一个反例直觉：如果只用"给叉子编号、按从小到大拿"的统一顺序，确实无死锁，但某位哲学家可能永远抢不过手快的邻居——这就是"安全且无死锁但会饿"。

举个具体数字例子：哲学家 0 和 2 不相邻（0 用叉 0、1；2 用叉 2、3），他们的请求互不冲突可以先后处理；而哲学家 4 的右叉是 `(4+1)%5=0`，和哲学家 0 的左叉是同一把叉 0，所以他俩必须错开。本章方案是"FIFO 排队 + 一把锁内同时预留两把叉"，并提供 `validate_fork_trace` 检查器重放真实轨迹来验证全部约束。

## 二、关键概念（定义）

- **循环等待（circular wait）**：每个线程都占着一把叉、等着邻居手里那把，5 个人围成一圈互相等，谁也动不了——这是死锁的经典形态。成因是"允许拿着一把叉等另一把"。
- **资源有序分配**：给资源编号，规定必须按编号从小到大申请，破坏循环等待的条件。它能保证无死锁，但**不自动保证无饥饿**（练习 1 的主题）。
- **FIFO 准入（先来先服务）**：所有就餐请求按到达顺序排成一条队列，只有队头请求有权拿叉。后来的请求就算两把叉都空闲也必须排队，从制度上杜绝插队饿人。
- **请求票号（ticket）**：每次 `wantsToEat` 调用领到的唯一号码。**队列的单位是票号而不是哲学家编号**——cell1 特意强调这一点：同一个哲学家可以并发发起多次调用，每次调用都要有独立的等待、授予和释放记录，用哲学家编号当单位会把它们搅在一起。
- **条件变量（Condition）**：一把锁加等待队列。本章所有状态（等待队列、next_ticket、owners）都在同一把锁内查看和修改，`wait()` 放锁睡觉、`notify_all()` 叫醒众人重查。
- **预留式授予（同时预留两叉）**：在同一互斥区内一次性检查并占住左右两把叉，中间没有放锁的缝隙——因此不可能出现"占住左叉等右叉"，循环等待从根上不存在。
- **队头阻塞（head-of-line blocking）**：严格 FIFO 的代价——队头请求的两把叉没空时，即使队尾某请求的两把叉都空着也得等。这是"可解释的公平性"对吞吐量的让步，是取舍而不是 bug。
- **有限持有时间**：每个人吃一口就放叉（回调有限完成）。这是无饥饿论证的前提之一：前面的请求占用的资源有限时间内必然归还。
- **轨迹检查器（validate_fork_trace）**：把运行期记录的事件流（request/grant/pick/eat/put/release）在单线程里重放一遍，逐条断言互斥、顺序、成对拿放等约束——用"事后审计"代替"相信并发跑完没炸"。

## 三、解决思路（一步步推导）

**Step 1：把"吃一口饭"建模成一条事件链。** 每个请求产生 8 个事件：`request`（领票排队）→ `grant`（同时拿到两叉的所有权）→ `pick`（左叉）→ `pick`（右叉）→ `eat` → `put`（左叉）→ `put`（右叉）→ `release`（归还所有权）。检查器就按这条链审计。

**Step 2：领票与排队。** `wantsToEat` 一进互斥区就领票：`ticket = self.next_ticket`，自增计数器，把自己 `(ticket, philosopher)` 追加到 `waiting` 队尾，然后 `notify_all`（告知可能正在吃的人"又有人排队了"，虽然他们多半不关心，通知是让等待逻辑统一）。

**Step 3：授予条件是"我是队头且两叉全空"。** 线程在 `while self.waiting[0][0] != ticket or self.owners[left] is not None or self.owners[right] is not None:` 上等待——三个条件缺一不可：不是队头就等（FIFO），左叉或右叉被占也等（互斥）。醒来后把自己弹出队头、把两把叉的 owner 都写成自己的票号，这个"检查+占用"在锁内一气呵成。

**Step 4：吃饭与释放。** 拿到授权后按回调顺序执行拿叉、吃、放叉（每个回调后补记一个事件），`finally` 里无条件归还两把叉的所有权并 `notify_all`——用 try/finally 保证即使回调抛异常也会释放叉子，不留"带着叉子逃跑"的窗口。

**Step 5：手推 cell6 的小实例。** 5 位哲学家 `[0,2,4,1,3]` 各发起一次请求（回调全是空操作），假设领票顺序恰好是启动顺序：

```
票0(p0,叉0,1) 等待时两叉全空 → 立即授予 → pick,pick,eat,put,put → release
票1(p2,叉2,3) 两叉全空 → 授予 → 吃完释放
票2(p4,叉4,0) 叉0刚被票0归还 → 空闲 → 授予 → 吃完释放
票3(p1,叉1,2) → 授予 → 释放；票4(p3,叉3,4) → 授予 → 释放
```

cell6 的表格就是这 5×8=40 条事件的实录，最后 `validate_fork_trace(obj.events)` 通过。注意票 2 依赖票 0 归还叉 0——这就是"哲学家 4 与哲学家 0 共享叉 0"的体现。

**Step 6：检查器怎么审计。** `validate_fork_trace` 维护自己的重放状态：`waiting` 队列、每票的 `records`、`owners` 数组。每读一个事件就断言它在该发生的位置发生：grant 必须弹出队头且两叉原主为 None；pick 必须先有 grant 且叉主是自己；eat 必须两叉都 pick 过、一把没 put；release 必须两叉都 put 过才归还。结尾要求队列清空、全部叉子无主、每票都 released。

## 四、代码逐段讲解

`run_threads` 与前几章相同，略。核心两个部件。

**DiningPhilosophersFIFO：**

```python
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
```

逐段看：构造函数里 `owners=[None]*5` 记录每把叉当前属于哪个票号，`events` 收集轨迹。入口先校验哲学家编号在 0..4。`left,right = philosopher,(philosopher+1)%5` 算出左右叉——`%5` 让 4 号的右叉绕回 0 号叉。第一段 `with` 是排队与授予：领票、入队、记 request、通知；那个长 `while` 就是授予谓词（队头 + 两叉空闲），不满足就 `wait()`；满足则弹队头、一口气把两把叉的 owner 写成自己（预留式授予），记 grant 再通知。中间 try 块执行六个回调，每个回调后单独拿锁补记事件——注意回调本身在锁外执行，避免拿着全局锁跑用户代码。`finally` 保证无论回调是否抛异常都归还两叉、记 release、通知下一位。返回票号方便测试对账。

**validate_fork_trace（重放检查器）：**

```python
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
```

它用独立的状态重放事件流：`waiting` 是期望的 FIFO 授予顺序，`records[ticket]` 是每票的生命周期账本，`owners` 重演叉子归属。request 时要求票号唯一并建账本；grant 时断言"弹出的队头恰好是这张票"（FIFO 的直接验证）、两叉原主为 None（互斥）然后占叉；pick 断言先授权、叉主是自己、没重复拿；eat 断言两叉齐、还没放、只吃一次；put 断言吃过且没重复放；release 断言两叉都放过后才清空归属。结尾三连断言：队列清空（每个请求都被授予）、叉子全部无主、每票都完整走完。任何一条不满足都会 AssertionError。

## 五、为什么是对的？复杂度是多少？（说人话）

**安全性（不共叉）**：grant 在同一把锁内同时检查并设置两个 owner，中间没有放锁缝隙，所以一把叉绝不可能同时属于两个票号；pick/eat 阶段叉主始终是自己。**无死锁**：被授予的请求已经握有两把叉，之后只执行有限回调、不再等待任何叉子；它吃完必释放（finally 兜底），于是队头终能推进——没有"拿着叉子等叉子"，循环等待无从谈起。**无饥饿（有条件的）**：按票号归纳——0 号票前面没人，只要叉子空出就能走；假设 k 号票之前的都走完了，轮到 k 号当队头，在叉子有限归还的前提下它也被授予。这个论证依赖 cell4 列出的前提：回调有限完成、锁与线程的弱公平调度、每个请求前只有有限个先到者。有限次压测只能检查"这一次跑没出错"，代替不了这些活性前提。**异常路径**：回调抛异常会向外传播（guarded 收集后统一抛出），轨迹不完整的运行不会被检查器判为成功。

**复杂度**：叉子归属是长度 5 的数组，O(1)；FIFO 队列存 q 个排队请求，O(q)；为了核验保存 r 条事件，O(r)。`notify_all` 可能一次唤醒多个等待者，所以本章不声称"每个请求的调度开销 O(1)"——公平与简单是用唤醒风暴换的。

## 六、测试用例在测什么

cell8 在子进程里跑了 3 轮，每轮的构造很讲究：

- `requests=[0,0,0,1,2,3,4,0,2,4]`——哲学家 0 出现 4 次（并发重复请求，验证"票号而非哲学家编号"这条契约），其余各 1 到 2 次。0 号请求（i==0）在 eat 回调里设 `first_started` 并卡在 `release_first.wait()`——人为制造"队头抱着叉子慢慢吃"。
- `coordinate` 协调线程等队头开吃后放行其他请求（`go.set()`），再等 `next_ticket` 涨到 10（全部领完票）才让队头放叉——保证测试窗口内确实形成了一条有 10 张票的完整队列。
- 断言一：`validate_fork_trace(obj.events)` 通过——互斥、FIFO、成对拿放全部审计过关。
- 断言二：`seen==Counter({i:1 for i in range(10)})`——10 个请求每个都吃到了一次（无饥饿的直接证据）。
- 断言三：`len(set(tickets))==10`——票号全不重复。
- **负向测试**：把事件流复制一份，在第 1 位插入一条伪造的 `('eat',0,0,None)`（让 0 号票没拿叉就吃），断言检查器**必须拒绝**它。这一条防的是"检查器是个只会点头的摆设"。
- 收尾 `threading.active_count()==1`：全部线程回收，没人卡在 `condition.wait()`。

## 七、练习思路提示

**练习 1（统一加锁顺序 vs FIFO 准入）**：提示：写一个对照版——每人拿叉必须"先拿编号小的那把"（哲学家 4 因此要先拿叉 0 再拿叉 4）。分析两层：无死锁上，两者都成立（破坏循环等待 vs 不允许持叉等待）；无饥饿上，FIFO 有制度保证，而"从小到大"版本里，若 0 号和 1 号哲学家高频抢叉 1，0 号可能反复失败——构造一个"1 号总在 0 号之前抢到叉 1"的调度叙事即可说明饥饿是可能的，不必真的复现。可以拿"叉 0 空闲但被队头阻塞"的例子同时讲 FIFO 的队头阻塞代价，说明两种方案各让渡了什么。

**练习 2（为活性明确调度假设）**：提示：把"无饥饿"的论证前提一条条写出来：每个 eat/put 回调有限完成（否则 finally 永不到达）；Python 的锁唤醒是弱公平的（睡着的线程最终会被唤醒，但不保证先到先得）；排队请求之前的先到者是有限个。然后对每条前提各构造一个反例世界：如果有人的 eat 回调死循环，后面全部饿死；如果调度器永远不唤醒某个线程，它也饿死。结论是"无饥饿是条件成立下的定理，不是无条件的保证"，能把这些边界说清楚就算达标。

## 八、对应 LeetCode 题目

- **1226. The Dining Philosophers（canonical）**：本章的原题——5 哲学家 5 叉子，练的是无死锁结构（本章用"一把锁内同时预留两叉"）与公平准入（FIFO 票号）的完整设计。
- **1195. Fizz Buzz Multithreaded（extension）**：也是多线程按规则轮流打印（3/5/15 的倍数），练的是和本章同源的"轮到谁"状态管理，可视为 N165 交替打印到本章准入控制之间的过渡题。
