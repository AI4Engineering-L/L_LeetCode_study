# N147 · LRU与LFU缓存设计 —— 说人话详解

> 对应 notebook：`notebooks/18_design/147_lru_lfu_caches.ipynb`

## 一、这章要解决什么问题？（问题描述）

缓存是一种"容量有限、只装最常用数据的快速仓库"。它只支持两个接口：`get(key)` 查数据（没有返回 −1），`put(key, value)` 存数据。难题在**满了怎么办**——必须按某种"谁最没用"的规则踢掉一个：

- **LRU（Least Recently Used，最久未使用）**：谁最长时间没被碰过就踢谁。
- **LFU（Least Frequently Used，最不经常使用）**：谁被碰的次数最少就踢谁；次数并列时，再按"谁更久没被碰"（桶内 LRU）分高下。

而且 LeetCode 146/460 这类题要求 get 和 put 都是 **O(1)**，这就逼出了本章的结构设计：哈希表管"按 key 找到节点"，双向链表管"O(1) 移动和删除"。cell1 还特别点了三条语义规则：更新已有 key 也算一次访问；两套结构不能各存一份互相矛盾的状态；容量为 0 时 put 什么都不存。

具体到数字的例子（就是 cell6 那段）：容量 2 的 LRU，依次执行 put(1,1)、put(2,2)、get(1)、put(3,3)、get(2)。

- put(1,1)、put(2,2) 后，链表从旧到新是 [1, 2]。
- get(1) 返回 1，且把 1 标记为"刚用过"，顺序变 [2, 1]。
- put(3,3) 时满了，踢最久未用的 2，顺序变 [1, 3]。
- get(2) 返回 **−1**（2 已被踢）。

## 二、关键概念（定义）

- **哈希表 + 双向链表（组合结构）**：哈希表能做到"给 key 一跳找到节点"，但没法表达顺序；双向链表能表达顺序、能 O(1) 摘节点，但按 key 找节点要 O(n)。两个合体、各司其职，才是 O(1) 缓存。关键是**只存一份状态**：哈希表里放的是节点的引用，节点里才是数据——不是两套独立账本。
- **双向链表节点（_CacheNode）**：带 key、value、frequency、前驱 prev、后继 next 五个字段。key 存在节点里是为了淘汰时能反查"从哈希表里删哪一条"。
- **哨兵（sentinel）**：链表头尾各放一个不装数据的假节点（head、tail）。有了它们，"空链表""删最后一个节点""尾部插入"这些操作全都不用判空、不用特判，代码干净且不会断链。
- **访问顺序链（LRU 链）**：约定链表**尾部是"最新"**（MRU）、头部是"最旧"（LRU）。每次访问就把节点摘下来重新接到尾部；于是头部永远是淘汰候选人。
- **频次桶（frequency buckets）**：LFU 用一个字典 buckets：频率 f → 一条双向链表，装"恰好被访问过 f 次"的所有 key。同频的节点在桶内再按 LRU 排（新访问的接桶尾），并列规则就藏在桶的顺序里。
- **最小频次（minimum）**：记当前所有活节点的最小频率。淘汰时直接去 buckets[minimum] 的桶头拿人，免去"扫全表找最小"的 O(n)。维护它是 LFU 实现里最精巧的部分：什么时候 +1、什么时候重置成 1，都有讲究。
- **摊还分析（amortized）**：单次操作平均 O(1) 的论证方式（先修章节 N014 讲过）。本章所有链表操作都是真 O(1)，连摊还都不用。
- **慢速参照（slow reference）**：测试里用"简单但慢"的数据结构（OrderedDict、带时间戳的字典）当标准答案，随机操作流对拍——设计题验证的标准姿势，练习 2 会让你自己写一遍。

## 三、解决思路（一步步推导）

**Step 1：先造轮子——带哨兵的双向链表。** `_NodeList` 的 append 永远接在 tail 前（最新端），remove 摘任意节点只需改 4 根指针，pop_left 从 head 后摘最旧的。手画一遍：哨兵 H↔T 中插入节点 x：H.next=x, x.prev=H, x.next=T, T.prev=x；之后任何增删都只是在这条"双向火车"上改接两节车厢。

**Step 2：LRU 的每一步都归结为两个动作。** get 命中 = "摘下 + 接尾"（touch）；put 新键 = "满了先踢头 + 新节点接尾"；put 旧键 = "改 value + touch"。cell6 的 5 步操作演示（第三节开头已逐条列出），链表演化 [1] → [1,2] → [2,1] → 踢 2 后 [1,3] → get(2)=−1。

**Step 3：LFU 的访问 = 换桶。** 节点从频次 f 的桶摘出，频次 +1，接进 f+1 的桶（桶不存在就现建）。手算一遍（容量 2）：put(1,1) 后桶{1:[1]}；put(2,2) 后桶{1:[1,2]}；get(1) 把 1 挪走，桶{1:[2], 2:[1]}；再 get(1)，桶{1:[2], 3:[1]}。此时 put(3,3) 撞上限：最小频次是 1，去 1 号桶踢最旧的——正是 2。3 以频次 1 入桶，且 minimum 重置为 1。

**Step 4：minimum 的两条维护规则。** （a）touch 时若旧桶被搬空：刚搬走的那个节点就在 f+1 桶里，所以新的最小频次必是 f+1，直接 `minimum += 1`——不用找。（b）put 新键：新节点频次是 1，任何缓存的最小频次不可能大于 1（只要它非空），直接重置 `minimum = 1`。淘汰时踢空 minimum 桶不用特殊处理：紧接着的新节点马上会把 minimum 拉回 1。

**Step 5：容量为 0 的契约。** `if not self.capacity: return`——put 直接丢弃，不存任何节点。这条边界 cell1 点名、测试里 capacity=0 那一轮专门覆盖。

## 四、代码逐段讲解

### 底层一：`_CacheNode` —— 节点

```python
class _CacheNode:
    def __init__(self,key=None,value=None): self.key=key; self.value=value; self.frequency=1; self.prev=self.next=None
```

新节点频次默认 1（LFU 语义：进来就算被访问一次）。哨兵节点用默认参数 key=None 造，天然区分于真节点。prev/next 之后由链表接线。

### 底层二：`_NodeList` —— 哨兵双向链表

```python
    def __init__(self):
        self.head=_CacheNode(); self.tail=_CacheNode(); self.head.next=self.tail; self.tail.prev=self.head; self.size=0
```

两个哨兵互相手拉手构成空链；size 让"桶是否空"的判断变成 O(1)（LFU 换桶逻辑全靠它）。

```python
    def append(self,node):
        previous=self.tail.prev; previous.next=node; node.prev=previous; node.next=self.tail; self.tail.prev=node; self.size+=1
```

四根指针把 node 插到 tail 之前（最新端）。因为哨兵永远存在，previous 至少是 head，不需要任何判空。

```python
    def remove(self,node):
        node.prev.next=node.next; node.next.prev=node.prev; node.prev=node.next=None; self.size-=1
```

摘节点只需让左右邻居互相牵手绕过它，再把节点自己的两根指针清成 None（防止悬空引用被误用）。O(1)，且不需要链表头——这就是双向链表相对单链表（还得从头找前驱）的优势。

```python
    def pop_left(self):
        if not self.size: raise IndexError('empty node list')
        node=self.head.next; self.remove(node); return node
```

从最旧端摘一个并**返回它**——返回是为了让调用方拿到 victim.key 去同步删哈希表。对空链表调用是程序错误，直接抛 IndexError 而不是静默返回 None。

### 类一：`LRUCache`

```python
    def __init__(self,capacity):
        if capacity<0: raise ValueError('nonnegative capacity required')
        self.capacity=capacity; self.nodes={}; self.order=_NodeList()
```

负容量直接报错（0 是合法的，语义见下）。nodes 是 key→节点 的字典；order 是那条"旧→新"的链。

```python
    def _touch(self,node): self.order.remove(node); self.order.append(node)
```

"访问刷新"= 摘下来再接尾部。所有"刚被用过"的语义都汇聚在这两行。

```python
    def get(self,key):
        if key not in self.nodes: return -1
        node=self.nodes[key]; self._touch(node); return node.value
```

查不到返回 −1（题目契约）；查到了必须 touch（读也算访问）再返回值。

```python
    def put(self,key,value):
        if key in self.nodes:
            node=self.nodes[key]; node.value=value; self._touch(node); return
        if not self.capacity: return
        if len(self.nodes)==self.capacity:
            victim=self.order.pop_left(); del self.nodes[victim.key]
        node=_CacheNode(key,value); self.nodes[key]=node; self.order.append(node)
```

四个分支逐条看：已有键 → 只更新 value 并 touch（不新增节点、不触发淘汰）；容量 0 → 直接丢弃；满了 → 从链头踢最旧者，并用 victim.key 同步清理字典（节点里存 key 就是为这一步）；最后新建节点登记进两个结构。

### 类二：`LFUCache`

```python
    def __init__(self,capacity):
        if capacity<0: raise ValueError('nonnegative capacity required')
        self.capacity=capacity; self.nodes={}; self.buckets={}; self.minimum=0
```

buckets 是 频次 → _NodeList 的字典；minimum 0 是空缓存的占位值（首个节点进来就会变成 1）。

```python
    def _touch(self,node):
        old=node.frequency; bucket=self.buckets[old]; bucket.remove(node)
        if not bucket.size:
            del self.buckets[old]
            if self.minimum==old: self.minimum+=1
        node.frequency+=1; self.buckets.setdefault(node.frequency,_NodeList()).append(node)
```

换桶三步：从 old 桶摘出；若 old 桶空了就删掉桶（字典不留空链表，cell4 的不变量"哈希中的每个活节点恰出现于一条链表"才好验证），且**只有当空掉的正是最小桶**时才 minimum+=1（刚才搬走的节点就在 old+1 桶，新最小非它莫属）；频次 +1 后接进 f+1 桶，`setdefault` 在桶不存在时现建一条。

```python
    def get(self,key):
        if key not in self.nodes: return -1
        node=self.nodes[key]; self._touch(node); return node.value
```

和 LRU 的 get 一字不差，只是 touch 的含义从"移到链尾"变成"换到高一层桶的尾部"。

```python
    def put(self,key,value):
        if key in self.nodes:
            node=self.nodes[key]; node.value=value; self._touch(node); return
        if not self.capacity: return
        if len(self.nodes)==self.capacity:
            bucket=self.buckets[self.minimum]; victim=bucket.pop_left(); del self.nodes[victim.key]
            if not bucket.size: del self.buckets[self.minimum]
        node=_CacheNode(key,value); self.nodes[key]=node; self.buckets.setdefault(1,_NodeList()).append(node); self.minimum=1
```

与 LRU 的差别全在淘汰和入桶两处：淘汰去 minimum 桶拿"最不经常用、且其中最久未用"的（桶内 pop_left 就是 LRU 并列规则）；踢空桶就删掉（minimum 不用修，下一行马上重置）。新节点以频次 1 入 1 号桶尾部，`self.minimum=1` 收尾。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么 LRU 头部一定是"最久未访问"？** 这条链有个好性质：每次访问（get 或 put，包括更新旧键）都把节点搬到尾部，所以一个节点离头部越近，就说明它越久没被搬过——"搬到尾部"的时间戳是全局递增的，链表顺序就是访问时间顺序。踢头部就是踢最久未访问者，语义和结构完全一致。

**为什么 LFU 的 minimum 维护不会错？** 梳理所有会动 minimum 的场合：（1）touch 搬空了 minimum 桶——搬走的那个节点此刻就在 f+1 桶里活着，所以最小频次必然恰好变成 f+1，`+1` 不是猜测而是推理；（2）淘汰踢空了 minimum 桶——马上有频次 1 的新节点进来，minimum 直接归 1，天然正确；（3）touch 搬空的是非最小桶——minimum 本来就不指它，不受影响。三种场合全覆盖，minimum 任何时刻都等于真实最小频次。

**为什么不会出现"两份状态打架"？** 哈希表里存的和链表里挂的是**同一个节点对象**：字典的 value 是引用，不是拷贝。改 node.value、搬 node 位置，字典和链表看到的是同一次修改。cell1 说"二者不能各保存一份独立状态"，落点就在这里。

**复杂度，代入数字感受一下：** 每次 get/put 只做常数次哈希操作（平均 O(1)）和常数次链表指针改接（严格 O(1)），没有任何循环扫链的步骤。容量 10⁵ 的缓存跑 10⁶ 次操作，也就是约 10⁶ 量级的常数操作，秒级。空间是 O(capacity)——节点数永远不超过容量（put 前先踢）。cell4 最后声明了前提：这是**顺序调用**的接口，没有加并发锁；多线程同时 get/put 会撕坏链表，需要自己加锁或改用并发结构。

## 六、测试用例在测什么

cell8 是一场大规模随机对拍 + 结构体检，容量从 0 到 4 各跑 500 步随机操作（key 0..7，get/put 各一半概率）：

- **LRU 的参照**是 `OrderedDict`：put 前先删旧键或 `popitem(last=False)` 踢最旧，get 命中后 `move_to_end`——把"更新也算访问""踢最旧"这两条语义用标准库复述一遍。
- **LFU 的参照**是 `reference[key]=(value, 频次, 时间戳)` 三元组，时间戳 clock 每步递增；淘汰时按 `min((频次, 时间戳))` 选受害者——(频次, 时间戳) 的字典序正是"先比频次、并列比新旧"的完整规则。这本身就是练习 2 要你手写的"慢速时间戳模型"。
- **结构体检 `inspect(bucket)`**：正向走一遍链表，逐点断言 `node.prev is previous and previous.next is node`（双向指针严格互指）、节点不重复、size 与实际长度相等；再反向走一遍断言和正向完全互逆。它抓的是"指针撕坏""size 记错"这类返回值正确但结构已烂的暗伤。
- **一致性断言**：LRU 链上的 key 序列 == OrderedDict 的键序（从旧到新）；`set(lru.nodes.values())` == 链上节点集合（哈希表和链表没有各存一份幽灵状态）；LFU 每个桶内节点的 frequency 字段与桶号一致、桶内顺序 == 按时间戳排序的该频次键列表；所有桶节点并集 == nodes 字典 == 参照字典（不多不少）；`lfu.minimum` == 参照中的真实最小频次。
- **capacity=0 那一轮**专测"put 不存任何节点、get 恒 −1"的契约；500 步里混合出现的"更新已存在键"（参照里 `del slow[key]` 再重插的分支）专测练习 1 的刷新语义。

## 七、练习思路提示

**练习 1（更新已有键时刷新优先级）：** 提示：想清楚三个具体问题——put 更新旧键要不要算一次访问？（本章：算，两个缓存的 put 分支都调 `_touch`。）put 更新会不会触发淘汰？（不会，节点数没变。）LFU 更新会不会变最小频次？（可能：唯一一个频次 1 的键被更新升到 2，minimum 应跟着 +1，找出这个场景。）手算示例建议：容量 1 的 LFU，put(1,1)、put(1,9)、put(2,2)——如果 put 更新不算访问或 minimum 没跟对，第三步踢错人。

**练习 2（慢速时间戳参照）：** 提示：参照结构只需要一个字典 key→(value, freq, last_used)，每次 get/put 都把 last_used 设成全局递增 clock；get 直接查；put 满了就按 (freq, last_used) 字典序找最小者踢。它每次操作 O(capacity)（要扫全表找最小），慢，但简单到不会错——这正是参照的职责。写完拿它与本章实现随机对拍（就像 cell8 那样），并解释为什么"慢而对"的东西有资格当裁判。

## 八、对应 LeetCode 题目

- **146. LRU Cache（LRU 缓存）**：`LRUCache` 的原题，练的是"哈希定位 + 哨兵双向链表维护访问序"这套 O(1) 组合拳，以及"更新也算访问、容量 0 不存"的语义边界。
- **460. LFU Cache（LFU 缓存）**：`LFUCache` 的原题，在 146 之上多练两件事：频次桶的换桶维护，以及 minimum 的"+1 与归 1"两条推理规则——并列时桶内 LRU 的规则也藏在这题里。
