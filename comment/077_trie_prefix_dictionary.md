# N077 · Trie的前缀状态与词典查询 —— 说人话详解

> 对应 notebook：`notebooks/10_trees_tries/077_trie_prefix_dictionary.ipynb`

## 一、这章要解决什么问题？（问题描述）

你有一本词典（一堆单词）和源源不断的查询："这个词在不在词典里？""有多少词以这个前缀开头？"如果用普通哈希集合存，第一个问题 O(1) 就能答，但第二个问题只能把词典翻个底朝天。Trie（前缀树/字典树）把"共享前缀"变成树上的同一段路，让两类查询都只要"按着查询词的字符在树上走一遍"。本章实现 `Trie` 的插入、查词、查前缀三个操作，外加一个综合应用 `replace_words`：英语里派生词很多（cattle、rattled、battery），给定词根表 `[cat, bat, rat]`，要把句子里的每个词替换成它的最短词根。

举一个具体到数字的例子。输入词典 `['cat','bat','rat']` 和句子 `'the cattle was rattled by the battery'`，`replace_words` 输出 `'the cat was rat by the bat'`。为什么？cattle 沿着 c→a→t 走到第 3 个字符时恰好踩到词根 cat 的终点标记，于是 cattle 被砍成 cat；rattled 变成 rat、battery 变成 bat；而 the、was、by 没有任何词根匹配（连第一个字符都对不上），原样保留。这个过程不需要把 600 个词典词挨个拿来比对——只需沿着每个单词自己走，这正是 Trie 的价值。

## 二、关键概念（定义）

- **Trie（前缀树）**：一棵多叉树，**边上标字符、节点表状态**。从根走到某个节点所经过的字符连起来，就是这个节点代表的"前缀"。它专门用来存一堆字符串，并让"共享前缀"在物理上共享同一段路径，节省重复。
- **字符边**：节点不存字符本身，字符存在"父到子的连线"上。本章实现里，每个节点带一个字典 `children`，键是字符、值是指向孩子节点的引用——"查询字符 c 有没有出边"就是一次字典查询 `c in node.children`。
- **前缀状态**：cell1 的核心句子：一个节点表示"某个前缀存在"这个状态，**不代表它是一个完整单词**。比如存了 apple 后，走到 ap 这个节点只能说明"有单词以 ap 开头"，不能说明 ap 本身在词典里。
- **终止标记（terminal）**：节点上的一个布尔开关，"到我这为止的字符串是一个完整单词"时才打开。它和前缀状态互相独立：`app` 是词、`apple` 也是词时，app 节点和 apple 节点各自亮灯。查词和查前缀的唯一区别就是"走到之后看不看这盏灯"。
- **空串与空前缀**：空前缀 `''` 走零步就到根，永远"存在"（`startsWith('')` 恒真）；空串算不算词取决于根节点的灯亮不亮——本章 Trie 允许 `insert('')` 把根的灯点亮（但 `replace_words` 的词典里禁止空词根，否则会把每个词都替换成空）。
- **字符集与空间**：Trie 的节点总数至多是"所有插入单词的长度之和加一"（外加一个根），因为每插入一个字符最多新建一个节点。如果用数组而不是字典存孩子，就要按字符集大小（比如 26 个字母）预付空间，词典稀疏时很浪费；本章用字典按需分配，空间与实际用到的字符数成正比。

## 三、解决思路（一步步推导）

- **Step 1：插入 = 沿字符开路。** 插 `apple`：从根出发，依次问"a 有出边吗？"没有就新建节点，有就顺着走；然后 p、p、l、e 一路同样处理，最后把 e 终点的 `terminal` 设为 `True`。共享前缀自动复用：接着插 `app`，前三个字符 a、p、p 的路已经存在，直接走到第三个 p，把它（不是 e 那个节点）的灯点亮。把这两个插入的每一步列成表（"新建"表示这步修了新节点，"复用"表示走现成的路）：

| 插入词 | 字符 | 动作 | 落点状态 |
|--------|------|------|----------|
| apple | a | 新建 | a 节点，灯灭 |
| apple | p | 新建 | ap 节点，灯灭 |
| apple | p | 新建 | app 节点，灯灭 |
| apple | l | 新建 | appl 节点，灯灭 |
| apple | e | 新建 | apple 节点，**点灯** |
| app | a | 复用 | 到 a 节点 |
| app | p | 复用 | 到 ap 节点 |
| app | p | 复用 | app 节点，**点灯** |

第二次插入 app 没有新建任何节点——一个新节点都没修，这就是"共享前缀共享路径"的直观形态。
- **Step 2：查词 = 走完 + 看灯。** `search('app')` 沿 a、p、p 走到第三个 p 节点，返回它的 `terminal`；灯亮才是词，灯灭只说明"有词以它开头"。
- **Step 3：查前缀 = 只走不看灯。** `startsWith('ap')` 只要能走到 ap 节点（没在半路断掉）就返回真。
- **Step 4：手算 cell6 的小词典。** 依次插入 `['app','apple','apt']`，整棵树长成（节点旁标注 terminal）：

```
ε (根, 灯灭)
└── a (灯灭)
    └── p (灯灭)
        ├── p (灯亮, 即 "app")
        │   └── l (灯灭)
        │       └── e (灯亮, 即 "apple")
        └── t (灯亮, 即 "apt")
```

cell6 的表格用深度优先把这棵树逐行打印出来，每行是"前缀状态 / 是否完整单词 / 有哪些出边字符"：根 ε（灯灭，出边 a）、a（灯灭，出边 p）、ap（灯灭，出边 p 和 t）、app（灯亮，出边 l）、appl（灯灭，出边 e）、apple（灯亮，无出边）、apt（灯亮，无出边）。注意 `ap` 灯灭——没有任何单词恰好是 ap，但它是 app、apple、apt 的公共前缀，所以节点必须存在。

- **Step 5：词根替换 = 走单词、见灯就砍。** 对句子里每个词 `word`：沿 word 的字符在 Trie 里走，每走一步检查一次"到当前节点的灯亮了吗"；亮了立刻返回 `word[:i+1]`（砍到第 i+1 个字符，即最短匹配词根）。半路字符接不上（比如 the 的 t 在根上就没有出边）说明没有任何词根匹配，原样返回整个词。为什么第一次亮灯就是"最短词根"？因为我们是从短到长逐字符前进的，越早亮灯的词根越短；又因为我们是沿着 word 自己的字符走的，砍出来的必然是 word 的前缀，绝不可能把 cat 匹配到 dog 上。把整句话的七个词逐个走一遍（词典 cat/bat/rat 的树只有 c、b、r 三条根出边）：

| 原词 | 走 Trie 的过程 | 结果 |
|------|----------------|------|
| the | 第一步 t 在根上就接不上 | the（原样） |
| cattle | c→a→t 第三步灯亮 | cat |
| was | 第一步 w 接不上 | was |
| rattled | r→a→t 第三步灯亮 | rat |
| by | 第一步 b 接得上，第二步 y 接不上 | by |
| the | 同第一行 | the |
| battery | b→a→t 第三步灯亮 | bat |

注意 battery 这一行的潜在陷阱：它沿着 b、a、t 走到 bat 灯亮就立刻停了，完全不用管 battery 后面还有没有路——短路是替换快的关键。

## 四、代码逐段讲解

### 1. 节点与树的基本骨架

```python
class TrieNode:
    def __init__(self): self.children={}; self.terminal=False

class Trie:
    def __init__(self): self.root=TrieNode()
```

每个节点只有两个字段：`children`（字符 → 孩子节点的字典）和 `terminal`（是否完整单词的开关）。树本身只持有一个根节点；根代表空前缀 ε。

### 2. 插入

```python
    def insert(self,word):
        node=self.root
        for c in word:
            if c not in node.children: node.children[c]=TrieNode()
            node=node.children[c]
        node.terminal=True
```

逐字符前进：出边不存在就当场新建（`if c not in node.children` 这行是"按需分配空间"的体现），存在就复用——这就是共享前缀被自动合并的地方。循环结束时 `node` 停在 word 的最后一个字符上，`node.terminal=True` 点灯。重复插入同一个词只是把同一盏灯再点亮一次，没有任何副作用（幂等）。

### 3. 走路工具与两个查询

```python
    def _walk(self,text):
        node=self.root
        for c in text:
            if c not in node.children: return None
            node=node.children[c]
        return node
    def search(self,word):
        node=self._walk(word); return node is not None and node.terminal
    def startsWith(self,prefix): return self._walk(prefix) is not None
```

`_walk` 是公共工具：沿字符走，断在半路返回 `None`，走完全程返回终点节点。两个查询都是薄薄一层包装：`search` 要求"走到 + 灯亮"，`startsWith` 只要求"走到"。`text` 是空串时循环不执行，直接返回根节点——所以 `startsWith('')` 天生返回真，`search('')` 的答案就看根的灯。

### 4. 词根替换

```python
def replace_words(dictionary,sentence):
    trie=Trie()
    for word in dictionary:
        if not word: raise ValueError('replacement roots must be nonempty')
        trie.insert(word)
    def replace(word):
        node=trie.root
        for i,c in enumerate(word):
            if c not in node.children: return word
            node=node.children[c]
            if node.terminal: return word[:i+1]
        return word
    return ' '.join(replace(word) for word in sentence.split())
```

前半段建树，其中 `if not word: raise ValueError` 挡住空词根：空词根的灯在根节点上，任何词第一步就会"亮灯"被替换成空串，整句话会被毁掉，所以干脆拒绝。内层函数 `replace` 逐字符走 word：`i` 是当前字符的下标；接不上边返回原词；每前进一格就检查一次 `node.terminal`，灯亮返回 `word[:i+1]`——注意是 `i+1`，因为 Python 切片不含右端点，第 i 个字符要算进去。最后一行把句子按空格拆词、逐词替换、再用空格拼回去。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么"走到 + 灯亮"就等于"在词典里"？** Trie 里从根到任何节点的路径是唯一的（每一步选哪个孩子由当前字符唯一决定），这条路径拼出的字符串也是唯一的。插入一个词时，我们把它的每个字符铺成一条独一无二的路径，并在终点点灯。所以查询时能完整走完一条路，就说明插入过某个词铺过这段路；终点灯亮，就说明恰好有词在这停下。灯是独立记账的：插 app 不会点亮 apple 的灯，插 apple 也不会点亮 app 的灯，前缀共享但词尾信息互不干扰。

**为什么第一次亮灯就是最短词根？** 替换时我们沿着 word 自己的字符一个一个走，走的深度越深，对应的前缀越长。从 i=0 开始每走一步就检查一次灯，所以最先遇到的亮灯节点必然对应"word 的最短匹配前缀"。由于整个过程只沿着 word 的路径走，永远不需要拿词典里的词来逐个比对——这也是它比暴力法（每个词和全部词典词比前缀）快的根本原因。

**复杂度**：一次插入或查询，代价与字符串长度 L 成正比（每字符一次字典操作），即 O(L)；L=10³ 的长词也就是一千次字典查询，一瞬间的事。整棵树的节点数至多是"所有插入单词的长度之和加一"，比如词典总字符数 10⁵，树最多十万个零一个节点，内存开销和词典规模同数量级。`replace_words` 对句子的每个词只扫它自己的字符，总扫描量是句子长度加词典长度这个线性级别，不存在词典大小乘以句子长度那种平方爆炸。

## 六、测试用例在测什么

- `trie.insert('apple'); assert trie.search('apple') and not trie.search('app') and trie.startsWith('app')`：一箭三雕的核心语义测试。apple 是词所以 search 真；app 只是 apple 的前缀、自己不是词，search 必须假而 startsWith 必须真——这正是"前缀状态"和"完整单词"两条信息分离的直接检验，也是初学者最容易混的地方。
- `trie.insert('app'); trie.insert('app'); assert trie.search('app')`：重复插入同一个词两次，不炸、不重复建节点，状态照常正确——测的是插入的幂等性。
- `assert trie.startsWith('') and not trie.search('')`：空前缀恒真（走零步到根）、空串目前不是词（根的灯还灭着），测的是 `_walk` 对空输入的天然行为。
- `trie.insert(''); assert trie.search('')`：把空串本身插成词后根灯亮，search('') 变真——测的是"空串是合法键"这个边界，说明根节点和其它节点地位平等。
- `assert replace_words(['cat','bat','rat'],'the cattle was rattled by the battery')=='the cat was rat by the bat'`：LeetCode 648 的原题样例，覆盖了"匹配替换（cattle→cat）""无匹配保留（the、was、by）"两种命运，是对整条流水线的端到端验收。

## 七、练习思路提示

- **练习 1（支持删除词且保住共享前缀）**：提示——最简单的版本只需把终点节点的 `terminal` 设回 `False`，路径上的节点留着（顶多 wasted，正确性不受影响）。难点在"剪枝"：删掉 app 后，如果 a→p→p 这条链上没有任何词再用（app 节点灯灭且无孩子），这些节点应该回收，否则树越长越胖。方向：从终点往回走，"灯灭且无孩子"的节点才可以安全摘除；一遇到灯亮或有其他孩子的节点立刻停。手算例子：词典 {app, apple}，删 apple——apple 的 e 节点、l 节点变成孤魂要回收，但 app 节点必须留下，因为 app 本身是词。边界：删一个不存在的词应该怎么做（无事发生还是报错）需要你写下约定。
- **练习 2（哈希完整词查询 vs 前缀查询）**：提示——拿 Python 的 `set` 当对照组做实验：查"apple 在不在"，set 和 Trie 都是飞快；查"有没有词以 app 开头"，set 只能遍历全部成员逐个 `startswith('app')`，代价是词典大小 O(总词数 × 前缀长)，而 Trie 依旧 O(前缀长)。再从内存角度反向比较：set 每个词独立存一份完整字符串，Trie 共享前缀但每字符多背一个字典对象的架子钱。设计一组实验数据（大量共享前缀的词 vs 完全无共享的词），量一量两种结构的构建时间和查询时间，把结论写成两三句话。

## 八、对应 LeetCode 题目

- **208. Implement Trie (Prefix Tree)**：实现前缀树，直接对应本章的 `Trie` 类三件套，考的就是"节点表前缀状态 + terminal 表词尾"这套语义。
- **648. Replace Words**：词根替换，直接对应 `replace_words`，练的是"沿着查询词自己走、见灯即停"的短路技巧，省掉对词典的暴力枚举。
