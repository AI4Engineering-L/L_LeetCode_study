# N151 · 多结构组合与时间序服务 —— 说人话详解

> 对应 notebook：`notebooks/18_design/151_composite_service_design.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章把两道经典设计题放在一起讲，因为它们共用同一个思想：**从 API 倒推存储结构——先看清楚调用方要什么查询，再决定数据怎么摆。**

**问题一（TimeMap，时间键值存储）**：还是 `set`/`get`，但 `set(key, value, timestamp)` 要求同一个 key 的 timestamp 严格递增，而 `get(key, timestamp)` 要返回"时间戳不大于查询时刻的最后一次写入的值"。举例：`set('x','old',3)`、`set('x','new',7)` 之后，`get('x',5)` 应该返回 `'old'`——因为 5 这个时刻，7 那次写入还没发生，离 5 最近的过往写入是时刻 3 的 `'old'`。

**问题二（Twitter，消息流服务）**：要支持 `postTweet`（发推）、`follow`/`unfollow`（关注/取关）、`getNewsFeed`（拿"我关注的所有人加我自己"最近发的最多 10 条推文，新的在前）。举例：用户 1 发了推文 101，用户 2 发了推文 201，用户 1 关注了用户 2，那么 `getNewsFeed(1)` = `[201, 101]`（201 更晚所以排前面）；用户 1 取关用户 2 之后，`getNewsFeed(1)` = `[101]`——只剩自己的推。

两个问题的共同点：数据都带着时间，且都**只追加、不回头改**；区别在 TimeMap 查"单个 key 的过去"，Twitter 查"多个来源拼起来的最新 10 条"。存储结构必须为查询服务，这就是本章的主线。

## 二、关键概念（定义）

- **追加日志（append-only log）**：只往列表尾部追加记录、从中间不改不删的存储方式。TimeMap 里每个 key 一本日志（时间戳, 值），Twitter 里每个用户一本日志（时间, 推文id）。日志天然按时间有序，这是后面二分和归并的前提。
- **时间前驱查询**：问"时刻 t 时的值"，等价于在日志里找"时间戳 ≤ t 的最后一条记录"。和上一章 SnapshotArray 的 `get` 是同一个招式。
- **二分查找（`bisect_right`）**：日志按时间戳有序，所以找前驱不用从头扫，`bisect_right(日志, t) - 1` 一步定位最后一条不晚于 t 的记录。
- **一致性约束（时间戳严格递增）**：TimeMap 的 `set` 强制同一 key 的时间戳必须严格大于上一条，否则抛 `ValueError`。这个约束是二分正确性的保险：它排除了并列时间戳造成的歧义（同一个时刻写两个值，查哪个？）。
- **K 路归并（K-way merge）**：把 K 个各自有序的序列合并成一个有序序列。诀窍是用一个小顶堆装着"每个序列还没被取走的最新元素"，每次弹出全局最新的那个，再从它所属的序列补上下一个。消息流正是这个场景：每个关注对象的日志各自有序，合并它们的前 10 条即可。
- **堆（`heapq`）与负数技巧**：Python 的 `heapq` 只有小顶堆（堆顶最小）。想要"最新优先"（最大优先），就把时间取负塞进堆——最新的时间取负后最小，自然浮到堆顶。
- **全局时钟（`self.clock`）**：Twitter 用一个自己维护的整数计数器当时间戳，每发一条推加一。它单调递增且永不并列，不依赖系统时钟的精度，也不怕两条推"同一毫秒"分不出先后。
- **关注关系图（following）**：`用户 → 他关注的人的集合`。它和消息日志是**两套独立存储**：取关只是从集合里删掉一个人，那个人历史发的推一条都不删。

## 三、解决思路（一步步推导）

### 3.1 TimeMap

- **Step 1**：查询是"按 key 查历史"，所以外层用字典 `history: key → [(timestamp, value), ...]`，每个 key 一本追加日志。
- **Step 2**：`set` 时把 `(timestamp, value)` 追加到对应日志；追加前检查时间戳比上一条大，不满足就报错——宁可拒绝脏数据，也不让二分将来出歧义。
- **Step 3**：`get` 时二分找时间前驱；日志为空（key 没见过）或查询时刻早于所有记录时，返回空字符串 `''`（题目约定的"查无此事"答案）。

**手算演示**（cell6 的小实例，两次写入后查五个时刻）：

| 查询时间 | 返回值 | 为什么 |
|---|---|---|
| 0 | `''` | 日志是 `[(3,'old'),(7,'new')]`，没有任何记录的时间 ≤ 0 |
| 3 | `'old'` | 恰好命中时刻 3 的记录 |
| 5 | `'old'` | 5 在 3 和 7 之间，最后一条 ≤ 5 的是 (3,'old') |
| 7 | `'new'` | 恰好命中时刻 7 |
| 20 | `'new'` | 7 之后没再写过，值一直是 'new' |

### 3.2 Twitter

- **Step 1**：`getNewsFeed` 是唯一复杂的查询，它决定存储：推文按作者分堆存放（`posts: 用户 → [(时间, 推文id), ...]`），每个作者的日志按全局 clock 递增天然有序；关注关系单独放（`following: 用户 → set`）。
- **Step 2**：取关**不**删历史推文——消息日志和关注关系解耦，取关只改集合。这样"取关后再关注回来"消息流立刻恢复完整，也省掉删消息的成本。
- **Step 3**：`getNewsFeed` 别把所有人推文拼起来全量排序（每次都 O(全部推文数 log 全部推文数)，太浪费）；改用 K 路归并：可见用户 = 关注集合 ∪ {自己}，每个用户的日志**倒着数**就是从新到旧。
- **Step 4**：初始化时每个来源只把"最新一条"（日志末项）装进堆；每弹一条（当前全局最新），就从同一来源补上它的前一条（下标减一），直到取满 10 条或堆空。
- **Step 5**：防卫细节：不允许自己关注自己（`follow` 里 `followerId!=followeeId` 才记录）——自己永远在可见集合里，重复关注会让同一条推在流里出现两次。

**手算演示**（cell6 的小实例）：`postTweet(1,101)` 后 clock=1，用户 1 日志 `[(1,101)]`；`postTweet(2,201)` 后 clock=2，用户 2 日志 `[(2,201)]`；`follow(1,2)` 后用户 1 的可见集合 = `{1, 2}`。`getNewsFeed(1)` 开堆：装入 `(-1, 用户1, 0, 101)` 和 `(-2, 用户2, 0, 201)`。弹出最小的 `-2` → 输出 201（用户 2 日志已到头，没有前一条可补）；再弹出 `-1` → 输出 101。结果 `[201, 101]`。`unfollow(1,2)` 后可见集合只剩 `{1}`，同样的流程输出 `[101]`。这正是 cell6 表格里的两行状态。

## 四、代码逐段讲解

### 4.1 TimeMap

```python
from bisect import bisect_right
from heapq import heapify,heappop,heappush

class TimeMap:
    def __init__(self): self.history={}
    def set(self,key,value,timestamp):
        history=self.history.setdefault(key,[])
        if history and timestamp<=history[-1][0]: raise ValueError('timestamps per key must strictly increase')
        history.append((timestamp,value))
    def get(self,key,timestamp):
        history=self.history.get(key,[]); index=bisect_right(history,timestamp,key=lambda item:item[0])-1
        return history[index][1] if index>=0 else ''
```

- `set`：`setdefault(key,[])` 一句完成"没有日志就建一本空的，然后取出来"。紧接着的检查是紧凑的条件句：`history` 非空且新时间戳不大于最后一条的时间戳（`timestamp<=history[-1][0]`）就抛 `ValueError`——把"时间戳必须严格递增"这条契约挡在门口，这是 fail fast 的态度。通过检查才 `append`。
- `get`：`self.history.get(key,[])` 用 `get` 而不是方括号，key 不存在时拿到空列表而不是抛 KeyError——空列表会让二分结果 `index=-1`，正好走 `''` 分支。主体一行：`bisect_right(history,timestamp,key=lambda item:item[0])-1` 在日志里定位"时间戳 ≤ 查询时刻"的最后一条（`key` 参数让二分只比较元组第一项；需要 Python 3.10+）。最后 `history[index][1] if index>=0 else ''` 是条件表达式：找得到就返回那条的值，找不到（查询早于全部记录）返回空串。

### 4.2 Twitter

```python
class Twitter:
    def __init__(self): self.clock=0; self.posts={}; self.following={}
    def postTweet(self,userId,tweetId):
        self.clock+=1; self.posts.setdefault(userId,[]).append((self.clock,tweetId))
    def follow(self,followerId,followeeId):
        if followerId!=followeeId: self.following.setdefault(followerId,set()).add(followeeId)
    def unfollow(self,followerId,followeeId):
        self.following.get(followerId,set()).discard(followeeId)
    def getNewsFeed(self,userId):
        users=self.following.get(userId,set())|{userId}; heap=[]
        for user in users:
            posts=self.posts.get(user,[])
            if posts:
                time,tweet=posts[-1]; heap.append((-time,user,len(posts)-1,tweet))
        heapify(heap); answer=[]
        while heap and len(answer)<10:
            negative,user,index,tweet=heappop(heap); answer.append(tweet)
            if index:
                time,tweet=self.posts[user][index-1]; heappush(heap,(-time,user,index-1,tweet))
        return answer
```

- `__init__`：三个状态——全局时钟从 0 起步、每用户推文日志、每用户关注集合。
- `postTweet`：时钟先加一（所以第一条推的时间是 1），然后把 `(clock, tweetId)` 追加进作者日志。用自增整数而不说真实时间，保证任意两条推的时间绝不并列。
- `follow`：单行条件挡掉"自己关注自己"；其余情况把关注对象加进集合。集合自动去重，重复关注无副作用。
- `unfollow`：`get(followerId,set())` 保证"从没关注过任何人"也不报错，`discard` 保证"取关一个没关注过的人"静默无事（`remove` 会抛 KeyError，`discard` 不会）。这就是"取关不删推文、不删日志"的体现——只动集合。
- `getNewsFeed` 是重头戏，分三段读：
  - 第一段（算可见集合、建初始堆）：`following.get(userId,set())|{userId}` 用集合并运算把"我关注的人"并上"我自己"；遍历每个可见用户，若他有推文，就把他**最新一条**装进候选堆，四元组是 `(-时间, 用户, 该条在日志里的下标, 推文id)`。存负时间是因为 `heapq` 是小顶堆，负号把"最新"变成"最小"，堆顶就是全局最新。存下标是为了弹出后能定位"同一用户的下一条（更旧一条，下标减一）"。`heapify` 把这个列表原地整理成堆，O(F) 一次完成。
  - 第二段（循环取数）：条件 `heap and len(answer)<10`——堆空（可见推文全取完）或拿满 10 条就停。每轮 `heappop` 弹出当前全局最新的一条，把推文 id 放进答案；`if index:` 检查这条在作者日志里还有没有更早的前一条（下标 0 就是最早一条），有就把 `(前一条, 下标-1)` 补进堆。
  - 第三段：返回答案列表（从新到旧）。

## 五、为什么是对的？复杂度是多少？（说人话）

**TimeMap 为什么对？** 每本日志按时间严格递增（`set` 门口的检查保证），日志里相邻两条记录之间值保持不变，所以"时刻 t 的值"就是"最后一条时间戳 ≤ t 的记录的值"，二分找的正是它。查询时刻早于全部记录时二分给出 `index=-1`，代码返回 `''`，这是唯一需要特判的边界。

拿手算表再验证一遍二分边界也值得：日志 `[(3,'old'),(7,'new')]` 查时刻 5，`bisect_right` 按 3<5、7>5 定位出"插在 (3,'old') 后面"的位置 1，减 1 得 0，取到 'old'；查时刻 0 时所有记录都晚于 0，定位 0，减 1 得 -1，走 `''` 分支。两个方向都严丝合缝。

**Twitter 的归并为什么对？** 想象每个可见用户面前摆着自己"从新到旧"的推文队列。堆里随时放着**每个队列的队首**，所以堆顶必然是所有可见推文里最新的一条（队首是各自队列最大的，堆顶是队首们最小的负数 = 最大的时间）。弹出它、答案收下，再把该队列的下一张牌顶上来——任何时刻堆里都是"每个来源还没交付的最新一条"，第 k 次弹出的就是全局第 k 新。所以答案严格按时间从新到旧，且不多不少（取满 10 或取光为止）。全局 clock 单调且不并列，两条推绝不会比不出先后，也不需要任何平局裁决。

**复杂度是多少？** 配数字说：

- TimeMap：`set` 是字典查找加列表追加，均摊 O(1)；`get` 是二分，O(log 该 key 的记录数)——比如某个 key 写过 1000 次，一次查询约 10 步。反过来如果 `get` 用从后往前线性扫描，最坏要扫完 1000 条，二分的优势随记录数增长越来越明显。
- Twitter：`postTweet`/`follow`/`unfollow` 都是 O(1)。`getNewsFeed` 设 F = 自己加关注的人数（比如关注了 200 人，F=201）：建初始堆遍历 201 个用户 O(F)，之后最多弹 10 轮、每轮一次堆操作 O(log F)≈8 步，总共 O(F + 10·log F)。对比全量拼接排序：假如这些用户累计发过 100 万条推，每次刷新都要百万级排序；归并方案每次刷新只碰至多 201 + 10×8 这点工作量。
- 空间：推文日志 O(消息数)、关注集合 O(关注边数)，加起来 O(消息数 + 关注边数)。

**前提与边界（cell4 特意声明）**：这套实现假设接口按顺序调用、单机单线程；不含分布式时钟、并发一致性这类生产级话题。取关不删历史是刻意的设计决定：日志只增不减，才保得住"重新关注后历史可见"。

## 六、测试用例在测什么

cell8 分两段：

**TimeMap 段**：`set('foo','bar',1)`、`set('foo','bar2',4)` 之后四条断言——

- `get('foo',0)==''`：边界值——查询时刻早于任何写入，必须返回空串。
- `get('foo',3)=='bar'`：正常值——查两次写入之间的时刻，命中前一条（1 时刻的 'bar'）。
- `get('foo',4)=='bar2'`：特殊值——查询时刻恰好等于某条写入的时间戳，应返回该条本身（≤ 包含等于）。
- `get('missing',9)==''`：边界值——查一个从未 set 过的 key，不许抛异常，返回空串。

**Twitter 段（600 轮随机对拍）**：7 个用户、600 轮，每轮随机做四件事之一。朴素模型是：`posts` 列表按序记下全部推文（推文 id 用自增 counter，兼当时间），`following` 字典记关注。前三类操作（发推/关注/取关）同时更新实现与模型；第四类操作随机挑个用户调 `getNewsFeed`，并用 `[tweet for time,author,tweet in reversed(posts) if author in allowed][:10]` 算出期望值——这句话就是"全量扫描暴力解"：把所有推文倒序（reversed，因为 counter 递增所以列表反着就是新到旧）、只留可见作者的、截前 10 条。断言实现与暴力结果完全一致。注意模型里 `if user!=other` 与实现的"不许自关"规则对齐。

**收尾段（自关注边界）**：对每个用户显式地 `follow(user,user)` 再 `unfollow(user,user)`，然后断言消息流与不搞这套动作时一致——专测"自己关注自己被忽略""取关自己也是无害空操作"这两条边界，防止消息流里同一条自己的推出现两次。

## 七、练习思路提示

- **练习 1（解释全量扫描慢模型的正确性与局限）**：提示——测试里的 `expected=[...reversed(posts)...][:10]` 就是那个慢模型。说正确性很容易：它模拟了题目定义的字面意思（取全部可见推文、按时间倒序、取前 10），没有跳过任何数据。说局限要拿数字：用户发了 100 万条推时，每次刷新它都要扫 100 万条，而堆归并只碰 F 个来源和 10 次弹出；再想一步"只取 10 条却要遍历全部"正是浪费所在。验证方法：用随机对拍比较两种实现输出是否逐条相等（测试已经示范了这个套路）。边界：可见推文不足 10 条、一个关注的人都没有、取关后立刻查。
- **练习 2（限定题目要求而不扩展分布式系统）**：提示——把题目契约的假设一条条写下来：单机内存、接口按顺序调用、不追问"取关后历史推文算不算"、推文 id 与用户 id 都是整数。然后讨论"如果哪条假设不成立会怎样"：比如两台机器各持有一个 clock 就会出现并列时间，`timestamp<=history[-1][0]` 的检查会误伤合法写入；又比如要支持"取关即从历史流里抹除"，追加日志就不够用。结论落在"设计题先圈定契约，再选结构"这个方法论上，不要真的去实现分布式时钟。

另外建议把"哪些行为故意不做"也写进练习报告：本章实现没有删推文接口、没有分页、没有缓存——每一条"不做"都对应一条题目没提的假设，圈出边界和写出功能一样是设计能力的一部分。

## 八、对应 LeetCode 题目

- **981. Time Based Key-Value Store**：对应 `TimeMap`——练"每 key 一本有序日志 + set 时强制时间戳递增 + get 二分找时间前驱"。
- **355. Design Twitter**：对应 `Twitter`——练"多结构分工（推文日志、关注集合、全局时钟）+ K 路堆归并只取前 10 条 + 取关不删历史"这整套组合设计。
