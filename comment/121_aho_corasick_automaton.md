# N121 · Aho–Corasick多模式匹配 —— 说人话详解

> 对应 notebook：`notebooks/14_string_algorithms/121_aho_corasick_automaton.ipynb`

## 一、这章要解决什么问题？（问题描述）

这章要解决"多模式串匹配"：先给你一小本词典（若干个模式串），再给你一段长文本，你要一次性找出所有模式在文本里的每次出现（报告"在哪个下标结束、命中了哪个模式"）。

举个具体例子：词典 patterns = ['he','she','hers','his']，文本 text = 'ushers'。答案是 [(3,0), (3,1), (5,2)]，翻译成人话是：下标 3 处同时结束了 'she'（模式 1，占下标 1–3）和 'he'（模式 0，占下标 2–3），下标 5 处结束了 'hers'（模式 2，占下标 2–5）。为什么下标 3 能命中两个？因为 "she" 这个词本身就以 "he" 结尾，两个模式在同一位置"撞车"，一个都不能漏报。

暴力做法是把每个模式单独拿去文本里扫一遍，代价是 O(模式数 × 文本长)；词典一大就扛不住。Aho–Corasick（AC 自动机）把整本词典做成一台自动机，文本从头到尾只扫一遍，就能同时汇报所有模式的所有出现。它还能"流式"工作：字符一个个来、来一个答一次"到目前为止是否刚结束某个模式"，这正好对应 LeetCode 1032 那种数据流题目。

## 二、关键概念（定义）

- **多模式匹配**：不是一个模式找一处，而是 K 个模式找全部出现位置。难点在于不同的模式会共享前缀（he / hers / his 都以 h 开头）、还会互为后缀（she 以 he 结尾），信息要共享才省力。
- **Trie（前缀树）**：把所有模式串按字符一条边一条边地插进一棵树，公共前缀共用同一段路径。树里每个节点代表"某个模式的一个前缀"。本章的 next 是一个字典数组，next[u] 记录节点 u 有哪些字符出边、通向谁。
- **状态（不变量）**：扫描到文本某个位置时，自动机停在某个节点 state。这个节点的含义是一个重要约定：state 代表"当前已读文本的最长后缀，并且这个后缀恰好是某个模式的前缀"。自动机的一切动作都是为了在读入下一个字符后仍然维持这个约定。
- **失败指针（fail link）**：每个节点 u 有一条 fail 边，指向"Trie 中 u 所代表串的最长真后缀对应的节点"。当主转移走不通（当前节点没有想要的字符出边）时，我们跳到 fail 指向的节点再试，那里代表一个更短、但仍然可能续上的候选前缀。它的作用和 KMP 的失配函数一样：失配不回退文本指针，只回退模式侧的状态。
- **BFS 建 fail**：失败指针是按层算的。根的儿子 fail 到根；更深的节点 v（父亲 u、边字符 c）的 fail，从 u 的 fail 出发沿 fail 链往下找，找到第一个有 c 出边的节点 f，fail[v] = next[f][c]。先算浅层再算深层，保证查的时候答案都已就绪，所以用 BFS 队列。
- **输出传播（输出继承）**：一个节点可能在结束多个模式。走到节点 v 时，不仅 v 自己结束的模式算命中，fail[v] 结束的、fail[fail[v]] 结束的……整条失败链上结束的模式也都算命中（因为它们是 v 的后缀）。本章实现干脆在建表时把失败链上的输出拷贝进 output[v]，一步到位；生产实现常用"输出链接"避免拷贝。
- **重叠匹配**：'aaa' 里 'aa' 出现两次（下标 0–1 和 1–2），它们互相重叠。AC 自动机按"结束下标"逐位汇报，天然覆盖重叠的情况。
- **流式状态**：StreamChecker 把 state 存在对象里，每来一个字符就走一步转移，随时能回答"刚结束的文本后缀里有没有词典词"。这就是把自动机当成一台可暂停的机器来用。
- **摊还分析**：单次转移最坏可能沿 fail 链跳很多步，但"深度"每读一个字符最多涨 1、每次跳 fail 只降不升，降的总量不会超过涨的总量，所以整段文本所有跳步加起来仍是线性级别。

## 三、解决思路（一步步推导）

- Step 1：把词典插成 Trie。模式 'he'（pid 0）、'she'（pid 1）、'hers'（pid 2）、'his'（pid 3）逐个插入：'he' 开出 0→1('h')→2('e')；'she' 开出 0→3('s')→4('h')→5('e')；'hers' 复用 0→1→2 再延长 2→6('r')→7('s')；'his' 复用 0→1 再分岔 1→8('i')→9('s')。在模式终点挂上模式号：output[2]=[0]、output[5]=[1]、output[7]=[2]、output[9]=[3]。
- Step 2：BFS 算失败指针并传播输出。我们手算几个关键节点：
  - 节点 4（"sh"）：它的 fail 从父亲 3 的 fail（=0）出发找 'h' 出边，根有 'h' 出边指向 1，所以 fail[4]=1——"sh" 的最长真后缀 "h" 恰是 Trie 里的节点 1。
  - 节点 5（"she"）：fail[5]=2（"she" 的最长真后缀 "he" 是节点 2），并且 output[5] 继承了 output[2]，变成 [1,0]——这就是"she 也以 he 结尾"在数据结构里的体现。
  - 节点 9（"his"）与节点 7（"hers"）：两者的 fail 都是 3（后缀 "s"）。
- Step 3：建好后的整张表就是 notebook cell6 打印出来的这张：

| 状态 | Trie出边 | 失败指针 | 模式ID(output) |
|---|---|---|---|
| 0（根） | {'h':1, 's':3} | 0 | [] |
| 1（"h"） | {'e':2, 'i':8} | 0 | [] |
| 2（"he"） | {'r':6} | 0 | [0] |
| 3（"s"） | {'h':4} | 0 | [] |
| 4（"sh"） | {'e':5} | 1 | [] |
| 5（"she"） | {} | 2 | [1,0] |
| 6（"her"） | {'s':7} | 0 | [] |
| 7（"hers"） | {} | 3 | [2] |
| 8（"hi"） | {'s':9} | 0 | [] |
| 9（"his"） | {} | 3 | [3] |

- Step 4：扫描文本 'ushers'，一格一格演：
  - i=0 读 'u'：状态 0 没有 'u' 出边，根的兜底规则是"原地不动"，状态仍 0。
  - i=1 读 's'：走 0→3，output[3] 为空。
  - i=2 读 'h'：走 3→4（"sh"），output[4] 为空。
  - i=3 读 'e'：走 4→5（"she"），output[5]=[1,0]，汇报 (3,1) 和 (3,0)——两个模式在同一位置撞车。
  - i=4 读 'r'：节点 5 没有 'r' 出边，跳 fail 到 2（"he"），2 有 'r' 边，走 2→6（"her"）。注意文本下标从没回退，回退的只是自动机状态。
  - i=5 读 's'：走 6→7（"hers"），output[7]=[2]，汇报 (5,2)。
  - 最终 matches = [(3,1), (3,0), (5,2)]，与 notebook 的打印完全一致。
- Step 5：流式版本。StreamChecker 只是把上面扫描循环拆开：字符来一个走一步，query 返回 output[state] 非空与否。它不报告命中了哪个词，只回答"是/否"，正对 LC 1032 的题面。

## 四、代码逐段讲解

### 4.1 build：建 Trie + BFS 装 fail 和 output

```python
from collections import deque

class AhoCorasick:
    def __init__(self,patterns=None):
        self.build([] if patterns is None else patterns)
```

- `__init__` 里那句三元表达式表示：调用者不给词典就按空词典建，避免可变默认参数的经典坑。

```python
    def build(self,patterns):
        self.patterns=list(patterns); self.next=[{}]; self.fail=[0]; self.output=[[]]
        for pid,pattern in enumerate(self.patterns):
            if not pattern: raise ValueError('empty patterns are excluded')
            node=0
            for c in pattern:
                if c not in self.next[node]:
                    self.next[node][c]=len(self.next); self.next.append({}); self.fail.append(0); self.output.append([])
                node=self.next[node][c]
            self.output[node].append(pid)
        return self
```

- 三个数组按节点下标平行存放：next[u] 是 u 的出边字典，fail[u] 是失败指针，output[u] 是 u 结束的模式号列表。根节点 0 三个数组各占一个初始元素。
- `if not pattern: raise ValueError(...)` 是防御性检查：空串会在每个位置都匹配、语义上无穷 reporting，干脆禁止输入。
- 插入循环是标准 Trie 写法：当前节点没有字符 c 的边就新建节点（新节点的 fail 先占位为 0），然后 node 走过去。走完整个模式后，`self.output[node].append(pid)` 在终点挂上模式号。重复模式会往同一个节点挂两个不同 pid，这正是"重复模式保留不同 ID"的实现方式。

```python
        queue=deque(self.next[0].values())
        while queue:
            u=queue.popleft()
            for c,v in self.next[u].items():
                f=self.fail[u]
                while f and c not in self.next[f]: f=self.fail[f]
                self.fail[v]=self.next[f].get(c,0)
                self.output[v].extend(self.output[self.fail[v]]); queue.append(v)
        return self
```

- `queue=deque(self.next[0].values())` 把根的直接孩子入队。它们的 fail 在建节点时已经占位为 0（指向根），正好是正确答案，所以循环只需处理"深度 ≥ 2"的节点。
- 对 u 的每条出边 c→v：`f=self.fail[u]` 从父亲的失败指针起步；`while f and c not in self.next[f]: f=self.fail[f]` 沿失败链下滑，直到某个节点有 c 出边或者 f 变成 0（根）。`self.fail[v]=self.next[f].get(c,0)` 取那条边作为 v 的失败指针；若一路滑到根都没有，就兜底为 0。
- `self.output[v].extend(self.output[self.fail[v]])` 是输出传播：v 的失败指针结束的模式也是 v 的后缀匹配，直接拷进 v 的输出列表。因为 BFS 先浅后深，被拷贝的 output[fail[v]] 早已是"继承完毕"的完整版本。
- 注意这里 fail 链每层只查一次 while，最坏情况下这条 while 可能走很长（稀疏实现的短板，复杂度一节细说）。

### 4.2 step：单字符转移（带失配回退）

```python
    def step(self,state,letter):
        while state and letter not in self.next[state]: state=self.fail[state]
        return self.next[state].get(letter,0)
```

- 这四行是 AC 自动机的心脏。`while state and ...` 一旦当前状态没有 letter 出边，就沿失败指针往更短的后缀候选跳；`state` 变成 0（根）时循环停住，因为根是最后的兜底。
- 最后一行 `return self.next[state].get(letter,0)`：如果（跳完之后的）状态有 letter 边就走过去；连根都没有这条边（说明这个字符不属于任何模式的开头），就回到 0。文本指针永远不回退，这是它比暴力快的根源。

### 4.3 scan：整段扫描

```python
    def scan(self,text):
        state=0; matches=[]
        for i,c in enumerate(text):
            state=self.step(state,c)
            matches.extend((i,pid) for pid in self.output[state])
        return matches
```

- 扫描从根（state=0）出发，每个字符调一次 step。`enumerate` 给出字符下标 i，它正好就是"匹配结束位置"。
- `matches.extend((i,pid) for pid in self.output[state])` 把当前状态输出列表里的每个模式号配上下标 i 收进结果。由于 output 已经在建表时做过传播，这里不需要再沿失败链逐层查。

### 4.4 StreamChecker：流式封装

```python
class StreamChecker:
    def __init__(self,words): self.automaton=AhoCorasick(words); self.state=0
    def query(self,letter):
        if len(letter)!=1: raise ValueError('one character per query')
        self.state=self.automaton.step(self.state,letter)
        return bool(self.automaton.output[self.state])
```

- `__init__` 一次性建好自动机并把状态拨到根；`query` 每次只喂一个字符。`if len(letter)!=1` 挡住"一次传整串"的误用，这是接口契约检查。
- `bool(self.automaton.output[self.state])` 把"输出列表非空"翻译成 True/False。因为 output 建表时已含失败链继承，这里自然覆盖"后缀命中"的情况。

## 五、为什么是对的？复杂度是多少？（说人话）

正确性的核心是那个状态约定：任意时刻，state 始终代表"已读文本的最长后缀，且该后缀是某个模式的前缀"。

- 转移为什么保持这个约定：读入新字符后，如果最长候选能延长，我们走 Trie 边延长，约定保住；如果不能延长，我们把候选换成它的最长真后缀（跳一次 fail）再试，跳 fail 的过程枚举的正是"越来越短的后缀候选"，第一个能接上新字符的就是新的最长候选。到根都接不上，说明任何模式前缀都接不上，回到根是唯一正确选择。
- 输出为什么齐全：一个模式 p 在下标 i 结束，等价于"文本前 i+1 个字符以 p 结尾"，等价于"当前最长候选的后缀链上有一个节点正好是 p 的终点"。我们在建表时把失败链上的终点全部拷贝进了每个节点的 output，所以走到任何状态时一次查表就能报出全部命中，既不漏（链条全覆盖）也不多报（列表里每个 pid 都对应真实的后缀匹配）。同一位置命中多个模式、模式彼此重复，都会以不同 pid 分别记录。

复杂度（结合具体规模感受）：

- 扫描：文本长 T=10⁶ 时，主循环就是一百万次 step。单个 step 最坏要沿 fail 链跳很多下，但把"状态的深度"想象成水位——每读一个字符水位最多涨 1，每次跳 fail 水位只降不升，而水位总共涨不超过 T，所以全程跳 fail 的总步数不超过 T。整体是 O(T + 报告数)：报告数是指输出的匹配条目数，比如文本是 10⁶ 个 'a'、词典含 'a' 和 'aa'，光匹配结果就有约 2×10⁶ 条，谁也省不掉这部分写输出的时间。
- 构建：本章是稀疏实现（出边用字典存，不补全自动机的所有转移），建 fail 时 while 链最坏可退到很浅，保守估计 O(M·L)，M 是 Trie 节点数、L 是最长模式长度；词典总长 10⁵ 时这一步也远比扫文本便宜。output 拷贝会放大空间（最坏每个节点都拖着一份长列表），工业实现改用"输出链接"（output 里只存自己的 pid，查询时沿 fail 链追）来省空间，思路和并查集路径类似，你先知道有这回事即可。
- 单次 query：最坏一次 query 可能跳长 fail 链，但按上面的水位论证，整条流摊还下来是每字符平均 O(1)。

## 六、测试用例在测什么

```python
patterns=['he','she','hers','his']; ac=AhoCorasick(patterns)
assert sorted(ac.scan('ushers'))==[(3,0),(3,1),(5,2)]
```
这条测正常输入，重点考"同位置多模式撞车"：下标 3 必须同时报 'he' 和 'she'，漏掉继承输出的实现只能报出一个。用 sorted 是因为 scan 的报告顺序（先 pid 1 再 pid 0）和元组排序不同，比的是集合内容。

```python
ac=AhoCorasick(['a','a','ba'])
assert sorted(ac.scan('ba'))==[(1,0),(1,1),(1,2)]
```
这条专测重复模式：词典里有两个一模一样的 'a'，它们必须以不同 pid（0 和 1）各报一次，再加上 'ba' 经 fail 继承报出的 'a'（pid 0 又一次），所以下标 1 处共三条记录。谁要是顺手做了去重，这条立刻挂。

```python
patterns=['a','ab','bab','b','aba']; ac=AhoCorasick(patterns)
for n in range(8):
    for chars in product('ab',repeat=n):
        ...
```
这段是"对拍"：枚举所有长度 0–7 的 a/b 文本，用最直白的判断 `text[:i+1].endswith(p)` 生成标准答案，断言 scan 的结果与之一致；同时用 StreamChecker 逐字符 query，断言每一步的 True/False 等于"是否有任一模式是当前前缀的后缀"。它把"重叠匹配、流式一致性、结束下标口径"一次性全锁死。

## 七、练习思路提示

**练习 1（与倒序 Trie 解 1032 对照）**：LC 1032 的另一路解法是把所有词倒着存进一棵普通 Trie，流式地保留"最近 L 个字符"（L 为最长词长度），每来一个字符就沿着"倒序窗口"从后往前查 Trie，查到任意节点是词终点就返回 True。你要做的对照是：AC 自动机每字符摊还 O(1) 步转移，而倒序 Trie 每次查询最坏要回看 L 个字符；两者预处理都是建一棵树。建议你用词典 ['he','she','hers','his'] 和输入流 'u','s','h','e','r','s' 手写两边的逐步判定表，看两路在哪些时刻返回 True。

**练习 2（总复杂度必须计入报告匹配数）**：提示词就是答案方向——算法不可能比"输出本身的长度"更快。你构造一个极端例子即可说明：词典 ['a','aa']，文本是 n 个 'a'，匹配条目数约为 n + (n−1) = 2n−1 条，所以任何算法都至少要 Θ(n) 时间来写这些结果，"O(T) 扫描"必须写成 O(T + Z)，Z 是报告数。写清输入输出与边界（比如 Z 可能为 0），再用手算例子验证 scan 的输出条数确实等于 Z。

## 八、对应 LeetCode 题目

- **1032. Stream of Characters（延伸题）**：给你一堆词，然后字符流一个一个到达，每个字符之后要回答"最近若干字符是否拼出词典里的某个词"。这题练的正是本章的流式状态：StreamChecker 类几乎就是题解本体，逐字符 step + 查 output 非空即可；用倒序 Trie 的解法（练习 1）则是它的对照组。
