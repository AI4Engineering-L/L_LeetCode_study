# N165 · 信号量、条件变量与交替执行 —— 说人话详解

> 对应 notebook：`notebooks/20_concurrency/165_semaphores_conditions_alternation.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决两个"多线程轮流打印"的经典问题（LeetCode 1115、1116）：

1. **FooBar 交替**：两个线程分别调用 `foo` 和 `bar` 各 n 次。输入 n=2，最终输出必须是 `foobarfoobar`——foo 打印一次、bar 打印一次，严格交替 n 轮。难点是两个线程的启动顺序随机、速度也不同，你要维护"现在轮到谁"的状态。
2. **ZeroEvenOdd 打零打奇偶**：三个线程分别调 `zero`、`even`、`odd`。输入 n=5，输出必须是 `0102030405`：先打 0，再打 1（奇数），再打 0，再打 2（偶数）……即"零线程在数字 1 到 n 之前各打一个 0，奇数线程打 1、3、5，偶数线程打 2、4"，顺序完全定死。

给个具体感受：FooBar n=1 时，如果 bar 线程先启动，它必须安静等待，直到 foo 打印完才能动手；ZeroEvenOdd n=2 时，odd 线程持有"打印 1"的任务，它必须等 zero 打完第一个 0 才能打印。本质上，两题都是把"轮到谁"编码成同步原语的状态，让不轮到的线程原地睡眠。

## 二、关键概念（定义）

- **信号量（Semaphore）**：一个带计数器的锁。`acquire()` 时计数器大于 0 就减 1 通过，等于 0 就阻塞；`release()` 把计数器加 1 并唤醒等待者。初值为 k 表示一开始允许 k 个线程同时进入。本章用它当"许可证"：`Semaphore(1)` 是一张许可证，`Semaphore(0)` 是零张——谁想进谁先得拿到别人让出来的那张。
- **条件变量（Condition）**：一把锁加一个等待队列的组合。`with condition:` 进入互斥区；`wait()` 会**原子地**释放锁并睡眠，被唤醒后重新抢锁再返回；`notify_all()` 唤醒所有等待者。它适合"等待某个谓词成立"的场景。
- **等待谓词（predicate）与 while 重查**：线程被唤醒并不代表"条件满足了"——可能被错误唤醒，也可能醒来时别的线程抢先改了状态。所以醒来后必须在**同一把锁下**用 `while` 重新检查条件，不满足就继续 `wait()`。用 `if` 只查一次就是这一章最经典的坑。
- **notify_all vs notify**：`notify_all` 唤醒所有等待线程让它们各自重查谓词。本章用 `notify_all` 是安全写法；只用 `notify` 有"叫醒的人不是该动的人"的风险。
- **零奇偶状态机（FooBar 的 turn）**：`turn` 只取 0 或 1，表示轮到 foo 还是 bar；每次打印后 `turn = 1-turn` 切换。状态转移 0→1→0→…。
- **许可证接力（ZeroEvenOdd）**：三张许可证 `zero_gate=1`、`odd_gate=0`、`even_gate=0`，同一时刻总数为 1，像接力棒一样在三个线程之间传递，保证任意时刻只有一个线程有资格打印。
- **忙等（busy waiting）反例**：不睡觉、用 `while turn != mine: pass` 空转烧 CPU 等轮到自己。功能上"可能"对，但浪费 CPU 且依赖 GIL 之外的公平性，是被否定的写法。
- **活性与回调契约**：正确性之外还要"最终能推进"。本章前提是每个打印回调有限完成且不抛异常；如果把回调当可失败的业务任务，就得另行设计取消与错误传播（cell1 明确不把这个塞进教学算法）。

## 三、解决思路（一步步推导）

**Step 1：FooBar 用"turn 状态机 + 条件变量"。** 想轮询就查 `turn`，但查完不满足要睡觉，所以把"查 turn、打印、翻 turn"整体放进 `with self.condition:` 互斥区，不满足就 `wait()`。

**Step 2：手推 FooBar n=2 的一轮。** 初始 `turn=0`，foo 和 bar 两个线程都进入了 `_repeat`：

```
1. foo 线程拿到锁：turn==0 == 自己的编号 → 打印 'foo'，turn 翻成 1，notify_all，释放锁
2. bar 线程（可能早就在 wait 中）被唤醒，重新拿锁：turn==1 == 自己 → 打印 'bar'，turn 翻回 0
3. 两线程进入第 2 轮循环，重复上述过程
输出：foobarfoobar
```

如果 bar 先到呢？它拿锁一查 `turn==0 != 1`，进 `wait()` 睡觉并放掉锁——foo 顺势进来打印。谁先到都不影响结果。

**Step 3：ZeroEvenOdd 用"许可证接力"。** 三张许可证，初始只有 zero 手里有一张。zero 打印 0 之后，看下一个要打的数字 `value` 的奇偶，把许可证交给 odd 或 even；数字线程打印完再把许可证还给 zero。手推 n=5 的完整过程（cell6 的表格就是它）：

| 步 | 持证者 | 打印 | 许可证流向 |
|---|---|---|---|
| 0 | zero | 0 | 下一个数是 1（奇）→ 交给 odd |
| 1 | odd | 1 | 还给 zero |
| 2 | zero | 0 | 下一个数是 2（偶）→ 交给 even |
| 3 | even | 2 | 还给 zero |
| 4 | zero | 0 | 下一个数 3 → odd |
| 5 | odd | 3 | 还给 zero |
| 6 | zero | 0 | 下一个数 4 → even |
| 7 | even | 4 | 还给 zero |
| 8 | zero | 0 | 下一个数 5 → odd |
| 9 | odd | 5 | 还给 zero |

输出 `0102030405`，和 cell6 表格的 step/printed/permission transfer 三列一一对应。

**Step 4：为什么 while 不能换成 if。** 条件变量的通用契约是：`wait()` 返回只代表"你被唤醒过"，不代表"条件已经成立"。本章用 `notify_all`，它会把等待池里的线程统统叫醒排队抢锁；第一个抢到锁的线程打印并把 turn 翻过去，后面抢到锁的线程醒来时条件已经不成立了——如果它用的是 `if`，检查在入睡之前只做过一次，它会把"被叫醒"误当成"轮到我"，照打不误，交替被破坏。`while` 保证每次醒来都重新对表，不满足就接着睡。要说明的是：在本章"foo、bar 各只有一个线程"的具体配置里，`if` 版往往也能碰巧跑对（每轮循环都会重新进入互斥区再查一次），这正是危险所在——它依赖当前线程数恰好为一，一旦同一个方法被多个线程调用、或换成允许虚假唤醒的平台，`if` 就静默出错。所以纪律是统一的：等待谓词一律用 while 重查。

**Step 5：忙等反例为什么被否定。** 有人会写 `while turn != mine: pass`——不睡觉、原地空转等轮到自己。它有三个问题：烧 CPU（等待期间占着核做无用功）；在 GIL 下还会拖慢真正该干活的线程；并且"最终轮到我"依赖调度器公平这种没有承诺的假设。条件变量的 `wait()` 和信号量的 `acquire()` 都是"睡觉等"，不消耗 CPU，这就是本章两种实现共同的选择。

## 四、代码逐段讲解

cell3 的 Python 源码里，`run_threads` 与 N164 完全相同（错误收集 + join + 隔离进程），不再重复。核心是两个类。

**FooBar（条件变量 + turn 状态机）：**

```python
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
```

构造函数先做边界防御（n 为负直接报错），然后是状态：`turn` 当前轮到谁（0 是 foo、1 是 bar），一个 Condition。`foo` 和 `bar` 都委托给 `_repeat`，只是带的编号不同——这消除了两份重复代码。`_repeat` 循环 n 次，每次：拿锁；`while self.turn != turn` 不轮到就 `wait()`（睡觉时放锁，被唤醒后重新拿锁、重新检查）；轮到了就执行回调；`self.turn = 1-turn` 切换轮次；`notify_all()` 叫醒对方。检查、打印、切换三件事在同一个互斥区里，整个状态转移是原子的——别人不可能在"打印完但还没翻 turn"的缝隙里插进来。

**ZeroEvenOdd（三个信号量接力）：**

```python
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
```

三个信号量就是三道闸门，初始只有 `zero_gate` 开着（计数 1）。`zero` 要为 1..n 每个数字前打一个 0：先 `acquire` 拿到许可证，打印 0，然后 `(self.odd_gate if value%2 else self.even_gate).release()` 这一行是精髓——下一个数字是奇数就把许可证交给 odd，是偶数就交给 even（`value%2` 为真即奇数）。`odd` 负责打印 1、3、5…（`range(1,n+1,2)` 步长 2），`even` 打印 2、4…（从 2 起步），两者打印完都 `self.zero_gate.release()` 把接力棒还给 zero。没有任何共享的可变变量，"顺序"完全由许可证的发放次序编码。

## 五、为什么是对的？复杂度是多少？（说人话）

**正确性（FooBar）**：互斥区内完成"查 turn → 打印 → 翻 turn"，这个转移是原子的，不可能出现两个线程同时认为轮到自己；每次打印必然把 turn 切到对方，所以输出严格按 foo、bar 交替 n 轮。**正确性（ZeroEvenOdd）**：任意时刻三张许可证的总数是 1（zero 的 acquire 与 odd/even 的 release 配对），所以同时至多一个线程能打印；zero 按数字奇偶发放下一张许可证，按 i 归纳就得到 `0,1,0,2,…,0,n` 这个唯一序列。**while 的作用**：即便被错误唤醒或被抢先，醒来重查一遍谓词就不会误打。

**活性**：上述论证有前提——相关线程最终能被调度、回调有限完成。有限次测试通过并不能证明调度永远公平（cell4 原话），所以测试跑了多种排列只是增加置信度。

**复杂度**：输出 2n 个标记（FooBar）或 2n 个数字（ZeroEvenOdd），同步算法自身状态 O(1)（FooBar 是一个 turn，ZeroEvenOdd 是三个计数器）。测试里为了断言而记录输出轨迹需要 O(n) 空间，但那是测试的钱，不是算法的钱。

## 六、测试用例在测什么

cell8 在子进程里做了三层穷举：

- **FooBar 部分**：`for n in [0,1,3,10]` 覆盖 n 的边界（0 次循环是空输出）和常规值；`for order in itertools.permutations(range(2))` 让 foo/bar 两个线程的启动顺序两种都跑一遍；断言 `''.join(out)=='foobar'*n`——期望值就是 n 份 `foobar` 连写，字符位置完全定死。
- **ZeroEvenOdd 部分**：同样 4 个 n 值、三个线程的 6 种启动排列；断言 `out==[x for i in range(1,n+1) for x in (0,i)]`——这个推导式展开就是 `[0,1,0,2,...,0,n]`，即"每个数字 i 前面配一个 0"。注意 lambda 里用的 `out.append` 直接把整数 append 进去，所以期望列表是整数而非字符串。
- **收尾**：`assert threading.active_count()==1` 检查所有工作线程都被 join 回收、没有线程卡死在 `acquire` 或 `wait` 上（卡死的话 run_threads 的 join 永不返回，子进程会超时被杀）。
- 从 `run_threads` 的角度看，任何线程抛出的异常（包括回调异常）都会被收集并在最后重抛，测试失败而非静默通过。

## 七、练习思路提示

**练习 1（分别用信号量和 Condition 实现交替）**：提示：本章的 FooBar 用的是 Condition，ZeroEvenOdd 用的是 Semaphore，你其实已经见过两种风格了。试着把 FooBar 改成两把信号量（`foo_gate=Semaphore(1)`、`bar_gate=Semaphore(0)`，打印后 release 对方），再把 ZeroEvenOdd 改成一个 Condition + 一个 turn ∈ {zero, odd, even} 的状态机。写完对比：信号量版没有显式共享变量但"顺序"藏在 release 的次序里；Condition 版有显式状态但要小心 notify 与 while 的配合。手算示例可以直接抄第三节的两张表。

**练习 2（解释等待谓词为何用 while）**：提示：从两个角度各给一个理由。角度一（竞争）：`notify_all` 会叫醒多个等待者，它们抢锁排队，第一个改完状态后，后进的那个拿到的已经是"新世界"，必须重查；角度二（语义）：`wait()` 的返回只代表"被唤醒过"，从不代表"条件成立"，这是条件变量的通用契约，Python 文档也这么写。可以做一个反例实验：把 `while` 换成 `if`，构造 foo 被连续唤醒两次的场景（或者直接跑大量随机启动排列），观察输出如何被破坏。

**一个常见疑问：notify_all 为什么不换成 notify？** `notify` 只随机叫醒一个等待者，在"等待者等的谓词各不相同"的场景里，它可能叫醒一个条件仍不成立的人，而真正该动的人还在睡——这叫丢失唤醒。`notify_all` 叫醒所有人、让 while 重查各自把关，多付出几次"醒了又睡"的代价，换来不依赖运气的正确性。本章两道题里等待者最多两三个，这点开销可以忽略。

最后提醒一句：如果你要在自己的机器上复跑这些例子，记得 notebook 是把整组线程放进带超时的子进程里执行的——万一你的改写让某个线程永远等不到许可证，子进程会超时被杀，测试报失败，这是设计好的保护而不是环境问题。

## 八、对应 LeetCode 题目

- **1115. Print FooBar Alternately（canonical）**：练的是条件变量（或信号量）维护"轮到谁"的状态机，本章 `FooBar` 就是它的直接解。
- **1116. Print Zero Even Odd（canonical）**：练的是多许可接力——用三个信号量把"0 在每个数字前"的固定顺序编码成许可证发放次序，本章 `ZeroEvenOdd` 是它的直接解。
