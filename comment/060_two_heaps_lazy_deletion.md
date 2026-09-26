# N060 · 双堆中位数与延迟删除 —— 说人话详解

> 对应 notebook：`notebooks/08_heaps/060_two_heaps_lazy_deletion.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决两个层层递进的问题：

1. **数据流中位数**：数一个一个来，每来一个，你都要能立刻说出"目前所有数的中位数"。排序当然行，但每来一个数就重排一次太亏，我们要一个"来一个数只花对数时间"的结构。
2. **滑动窗口中位数**：给你一个数组和窗口长度 k，窗口从左滑到右，每一步报出"窗口里这 k 个数的中位数"。难就难在窗口每滑一步，不仅要"进一个数"，还要"删一个数"——而堆偏偏不擅长删中间的元素。

具体到数字的小例子：

- 数据流版：依次 addNum 1、2、3，中位数依次是 1、1.5、2。奇数个取正中间那个；偶数个取中间两个的平均。
- 滑窗版：`nums=[1,2,3,4]`，k=3。第一个窗口 [1,2,3] 中位数是 2；窗口右滑变成 [2,3,4]（1 离开、4 进入），中位数是 3。我们的结构必须支持"删掉 1"这件事。

问题的核心矛盾：中位数需要把数据分成"较小一半"和"较大一半"两堆，这用两个堆就能做；但删除一个不在堆顶的元素，堆做不到——本章的答案是"先记账、不真删，等它浮到堆顶再顺手扔掉"，也就是标题里的"延迟删除"。

## 二、关键概念（定义）

- **双堆中位数结构**：小的一半放进"最大堆"（`low`，存负数模拟），大的一半放进"最小堆"（`high`，存原数）。这样 `low` 的堆顶是较小一半的最大值，`high` 的堆顶是较大一半的最小值，中位数只能从这两个"边界"读出来：元素奇数个时就是 `low` 堆顶，偶数个时是两个堆顶的平均。
- **平衡（两半的大小关系）**：不变量是 `low` 的有效元素个数要么等于 `high`，要么正好多一个（约定奇数时多出来的那个放 `low`）。每次增删后检查一次、不平衡就搬一个元素过桥，这个动作叫 balance。
- **逻辑大小 vs 物理大小**：物理大小是 `len(heap)`——堆里真实躺着的元素个数；逻辑大小是"还有效的元素个数"（`nl`、`nh` 两个计数器）。因为延迟删除会让堆里暂时混着已经作废的元素，所以任何"两半谁多谁少"的判断都必须看逻辑大小，绝不能拿 `len()` 充数。
- **延迟删除（lazy deletion）**：要删的元素 x 不去堆里翻找（那是 O(n) 的），只在 `delayed` 字典里记一笔"x 该删一个"。等某次清理时它正好出现在堆顶，才真正弹出销账。
- **延迟计数字典（`delayed`）**：`collections.Counter`，键是被删的值，值是"这个值还欠着几次删除"。值可以大于 1——比如窗口里有两个相同的 5 先后离开，就欠两笔。
- **prune（清理过期堆顶）**：访问或移动堆顶之前的例行检查——只要堆顶的值在 `delayed` 里有欠账，就弹出它、欠账减一，直到堆顶是无债一身轻的"活人"。
- **过期元素**：已经逻辑删除、但身体还躺在堆里的元素。它们不影响中位数（读中位数前会先 prune），只占内存。

## 三、解决思路（一步步推导）

Step 1：先用"数据流中位数"热身。每个新数 x 无脑先丢进 `low`，再把 `low` 的堆顶（较小一半当前的最大值）转交给 `high`，最后如果 `high` 人数超过 `low`，把 `high` 堆顶搬回 `low`。三步走完，"两半都不越界 + 奇数时 low 多一个"自动保持。

Step 2：滑动窗口 = 每次"进一个 + 删一个"。进入用 Step 1 的逻辑（但要判断新数该进哪半：不大于 `low` 堆顶就进 `low`，否则进 `high`）；删除用延迟记账：`delayed[x] += 1`，对应半区的逻辑大小减一，若 x 恰好就是该半区堆顶则立刻 prune。

Step 3：每次增删之后调 balance，用逻辑大小判断谁多谁少、搬边界元素过桥；搬完必须再 prune 一次"腾出来的新堆顶"——它可能也是欠账的。

Step 4：读中位数前依赖"堆顶已被清理"这个前提（balance 和 remove 里的 prune 保证了这一点）。

手算演示一（数据流版，notebook 小实例原数据）：依次 addNum `[1,2,3,9,0,5]`：

| 新值 | 较小一半 low | 较大一半 high | 中位数 |
| --- | --- | --- | --- |
| 1 | {1} | {} | 1 |
| 2 | {1} | {2} | 1.5 |
| 3 | {1,2} | {3} | 2 |
| 9 | {1,2} | {3,9} | 2.5 |
| 0 | {0,1,2} | {3,9} | 2 |
| 5 | {0,1,2} | {3,5,9} | 2.5 |

以"新值 0"这一行验证 Step 1 的三步：0 先进 low；low 堆顶 2 转给 high（high 变 {2,3,9}）；high 有 3 个、low 只剩 2 个，超了，把 high 堆顶 2 搬回 low——净效果等价于"0 进了 low、其余不动"，且两半恢复 {0,1,2} | {3,9}。这张表与 notebook 小实例生成的表格一致。

手算演示二（滑窗版，展示延迟删除的精髓）：`nums=[1,2,3,4]`，k=3。第一个窗口建好后 `low={1,2}`、`high={3}`，中位数 2。窗口右滑：加入 4（4 大于 low 堆顶 2，进 high），删除 1——1 在 low 的堆底吗？不，low 物理数组是 [-2,-1]（存负数），1 就是堆顶……那就换一个更能说明问题的看法：假设被删的 1 此刻不在堆顶，我们只记账 `delayed[1]+=1`、`nl-=1`，堆身体不动；balance 发现 `nl=1 < nh=2`，把 3 从 high 搬到 low 并顺手 prune——如果堆顶恰好是欠账的 1，此刻才真正把它弹出。最终 `low={2,3}`、`high={4}`，中位数 3，与窗口 [2,3,4] 的期望一致。

## 四、代码逐段讲解

### 1. `MedianFinder`：数据流中位数（无删除版）

```python
import heapq
from collections import Counter

class MedianFinder:
    def __init__(self): self.low=[]; self.high=[]
    def addNum(self,x):
        heapq.heappush(self.low,-x)
        heapq.heappush(self.high,-heapq.heappop(self.low))
        if len(self.high)>len(self.low): heapq.heappush(self.low,-heapq.heappop(self.high))
    def findMedian(self):
        if not self.low: raise ValueError('no observations')
        return -self.low[0] if len(self.low)>len(self.high) else (-self.low[0]+self.high[0])/2
```

- `low` 存负数（Python 只有最小堆，取负就成了最大堆），`high` 存原数。
- `addNum` 就是 Step 1 的三步：x 取负压入 low；把 low 堆顶（负数）弹出、再取负还原、压入 high——这一步保证"凡是进 high 的数都不小于留在 low 里的最大值"；最后若 high 人多，把 high 堆顶搬回 low。三步下来无需任何 if 判断新数该去哪半，非常省心。
- `findMedian` 开头 `if not self.low: raise ValueError` 挡"一个数都没来就问中位数"。之后是三元表达式：low 人多（奇数个）中位数就是 -low[0]（取负还原）；两半人齐（偶数个）取两堆顶平均，注意 Python 3 的 `/` 自然产生 1.5 这样的浮点。

### 2. `_WindowMedian`：带延迟删除的滑窗内核

```python
class _WindowMedian:
    def __init__(self):
        self.low=[]; self.high=[]; self.delayed=Counter(); self.nl=self.nh=0
```

比 MedianFinder 多了两样东西：欠账本 `delayed` 和两个逻辑计数器 `nl`、`nh`。

```python
    def prune(self,heap,sign):
        while heap and self.delayed[sign*heap[0]]:
            x=sign*heapq.heappop(heap); self.delayed[x]-=1
            if not self.delayed[x]: del self.delayed[x]
```

- `sign` 是换算符号：low 存的是负数，真实值是 `-heap[0]`，所以传 `sign=-1`；high 存原数，传 `sign=1`。`sign*heap[0]` 一律换算回真实值去查欠账本。
- 只要堆顶在欠账本里有账（`Counter` 查不存在的键返回 0，正好当"没账"用），就弹出它、账减一；账清零就把键从字典删掉，防止字典越长越大。
- 循环条件里 `heap and ...` 双保险：堆空了当然停。

```python
    def balance(self):
        if self.nl>self.nh+1:
            heapq.heappush(self.high,-heapq.heappop(self.low)); self.nl-=1; self.nh+=1
            self.prune(self.low,-1)
        elif self.nl<self.nh:
            heapq.heappush(self.low,-heapq.heappop(self.high)); self.nl+=1; self.nh-=1
            self.prune(self.high,1)
```

- 判断全部使用逻辑大小：`nl > nh+1` 说明 low 超编，把 low 堆顶（负数弹出再取负）送去 high；`nl < nh` 说明 high 超编，反向搬一个。
- 搬完立刻 prune 对面的堆——因为搬走堆顶后露出来的新堆顶可能就是欠账元素，不清理的话后续判断会被尸体污染。

```python
    def add(self,x):
        if not self.low or x<=-self.low[0]: heapq.heappush(self.low,-x); self.nl+=1
        else: heapq.heappush(self.high,x); self.nh+=1
        self.balance()
    def remove(self,x):
        self.delayed[x]+=1
        if x<=-self.low[0]:
            self.nl-=1
            if x==-self.low[0]: self.prune(self.low,-1)
        else:
            self.nh-=1
            if self.high and x==self.high[0]: self.prune(self.high,1)
        self.balance()
```

- `add` 与 MedianFinder 不同：这里显式判断去哪半（`x<=-low[0]` 进 low，否则进 high），因为滑窗里我们要精确控制并随时 remove，不能再靠"三步搬运"间接到达。`not self.low` 照顾第一个元素。
- `remove` 第一句只记账不翻堆，O(1)；然后判断 x 属于哪半（用同样的分界规则）、给对应逻辑大小减一；如果 x 恰好就是那半的堆顶，立刻 prune 把尸体清走（`self.high and ...` 防止 high 为空时读 `heap[0]` 报错）。最后 balance。
- 为什么 x 不在堆顶时不用清？因为尸体躺在堆中间不影响逻辑大小，也不影响中位数读取——读之前堆顶一定已被清理干净（balance/add/remove 都保证了这一点）。

```python
    def median(self):
        return -self.low[0] if self.nl>self.nh else (-self.low[0]+self.high[0])/2
```

与 `findMedian` 同构，唯一区别是用逻辑大小 `nl/nh` 做奇偶判断。

### 3. `sliding_window_median`：装填第一个窗口再一步一滑

```python
def sliding_window_median(nums,k):
    if not 1<=k<=len(nums): raise ValueError('invalid window size')
    state=_WindowMedian(); out=[]
    for x in nums[:k]: state.add(x)
    out.append(state.median())
    for i in range(k,len(nums)):
        state.add(nums[i]); state.remove(nums[i-k]); out.append(state.median())
    return out
```

- 第一行守卫：k 至少 1、至多数组长度，否则窗口没有意义。
- `nums[:k]` 先建满第一个窗口并记录中位数；之后每轮"进入 `nums[i]`、离开 `nums[i-k]`"——离开的正是窗口左端滑出的那个元素。先 add 后 remove 的顺序让两步共用同一次 balance。

## 五、为什么是对的？复杂度是多少？（说人话）

为什么两个堆顶就能给出中位数？因为我们维护了三条性质：其一，low 里的每个有效元素都不大于 high 里的每个有效元素（进入时就按分界走，搬桥的 balance 也不会破坏）；其二，low 的有效个数要么等于 high 要么多一个；其三，读数之前堆顶一定没有欠账元素（prune 兜底）。于是全体有效元素从小到大排开后，正中间的位置必然落在两个堆顶上：奇数个时是 low 堆顶，偶数个时是两堆顶的平均。

为什么逻辑大小必须先减、不能等物理弹出再减？举例：删除一个埋在堆中间的 5，如果我们等它被弹出才记账，那么在它被弹出之前的所有 balance 判断都会以为"5 还活着"，把两半的大小关系算错，中位数随之出错。先减逻辑大小等于立刻承认"5 已经不在窗口里"，尸体什么时候抬走只是内存问题。

复杂度：数据流版每次 addNum 三次堆操作，O(log n) 时间、累计 O(n) 空间。n=10⁵ 个数时每次插入约 17 次比较，非常轻。滑窗版每个元素至多进堆一次、出堆一次（加上偶尔的搬运），每次 O(log n)，总时间 O(n log n)；n=10⁵ 时约几百万次堆操作，一两秒内跑完。要特别诚实地说空间：尸体是慢慢清理的，极端情况下物理堆可能攒下 O(n) 个元素（notebook 明确声明这一点），所以本实现空间是 O(n) 而不是想当然的 O(k)；想要严格 O(k)，得定期推倒重建两个堆。

## 六、测试用例在测什么

```python
m=MedianFinder(); m.addNum(1); m.addNum(2); assert m.findMedian()==1.5
m.addNum(3); assert m.findMedian()==2
```
基础用例：前两个数验证偶数个取平均（1 和 2 的中位数 1.5，同时测出实现返回的是浮点而不是整数 1）；第三个数进入后验证奇数个取正中（2）。

```python
rng=Random(60)
for n in range(1,35):
    for a in [[3]*n,list(range(n)),list(range(n,0,-1)),[rng.randrange(-3,4) for _ in range(n)]]:
        for k in range(1,n+1): assert sliding_window_median(a,k)==[median(a[i:i+k]) for i in range(n-k+1)]
```
大规模对照测试，右侧用标准库 `statistics.median` 对每个真实窗口切片现算，是最可信的参照。四种数组形状各有用意：`[3]*n` 全相同值——专门折磨"连续相等值的过期元素"（欠账本里同一个键欠多笔账）；`list(range(n))` 升序与 `list(range(n,0,-1))` 降序——单调输入让删除永远发生在堆的一端；随机数组（值域只有 -3..3，重复率极高）——混合考验。n 从 1 到 34、k 从 1 到 n 全遍历，n=1、k=1（窗口就是整个数组）这类边界都在内。

## 七、练习思路提示

- 练习 1（解释物理堆长不等于有效大小）：构造一个能"留住尸体"的例子，比如 `[3]*n` 开头的数组，删除 3 时堆里还躺着好几个 3。提示：写一个调试函数在每步打印 `len(low)`、`nl`、`len(high)`、`nh` 和 `delayed`，观察 `len(low)` 与 `nl` 何时分叉、何时又合拢（prune 之后）；再回答"如果 balance 误用 len 会出什么错"，拿一个具体窗口手推一遍错误答案。
- 练习 2（处理连续相等值的过期元素）：场景是堆顶值 x 欠着多笔账。提示：`prune` 的 while 循环正是为此设计的——它会把所有欠账的同值堆顶连续弹出；你可以设计输入让同一个值先离开两次再被访问，画一张"欠账本余额"变化表验证账目收支平衡（delayed[x] 加几笔减几笔，最终归零删除键）。

## 八、对应 LeetCode 题目

- **295. Find Median from Data Stream（数据流的中位数）**：`MedianFinder` 的原题，练的是"最大堆装小半 + 最小堆装大半 + 平衡搬运"这套双堆骨架。
- **480. Sliding Window Median（滑动窗口中位数）**：`sliding_window_median` 的原题，在 295 的骨架上加"延迟删除 + 逻辑大小 + prune"，练的是双堆的删除难题。
