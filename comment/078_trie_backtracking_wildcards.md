# N078 · Trie与回溯的组合 —— 说人话详解

> 对应 notebook：`notebooks/10_trees_tries/078_trie_backtracking_wildcards.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章其实一次性解决两个经典问题，它们共用同一个"前缀树"思想。

**问题 A（通配符词典）：** 你要先往一个"词典"里 `addWord` 存一堆单词，之后用 `search` 查询。查询串里可以带通配符 `.`，一个 `.` 必须匹配**恰好一个**字母（不是任意长度）。比如你存了 `bad`、`dad`、`mad`，那么查 `'.a.'` 应该返回 True，因为 bad/dad/mad 三个词都是"任意字母 + a + 任意字母"的形式；查 `'b..'` 也是 True（bad 匹配）；但查 `'..'` 是 False，因为词典里没有任何两个字母的词。

**问题 B（网格搜词）：** 给你一个字母网格和一堆单词，问哪些单词能被"拼"出来。规则是：从任意格子出发，每一步只能走到上下左右相邻的格子，每个格子在同一条路径里最多用一次，把走过的字母连起来正好等于某个单词，就算找到。具体例子（notebook 的小实例就是它）：

```
o a a n
e t a e
i h k r
i f l v
```

词典是 `['oath','pea','eat','rain']`，输出是 `['eat','oath']`。为什么是这两个？

- `oath`：o(第0行第0列) → a(0,1) → t(1,1) → h(2,1)，四步都是相邻移动，成立。
- `eat`：e(1,3) → a(1,2) → t(1,1)，成立。
- `pea` 与 `rain`：网格里虽然有 p…… 其实根本没有 p 和 r 组成的合法路径（网格里连 p 都没有），所以拼不出来。

如果对每个单词单独做一次网格深搜，词典一大就慢得离谱。本章的核心是：把所有单词放进一棵 Trie，搜索时"走一步查一步前缀"，前缀对不上立刻回头。

## 二、关键概念（定义）

- **Trie（前缀树，也叫字典树）：** 一棵多叉树，从根走到某个节点所经过的字符连起来，就是一个"前缀"。所有单词共享公共前缀部分的路，比如 `eat` 和 `eatery` 前 3 个字符走的是同一串节点。为什么需要它：网格搜索走到第 k 步时，我们只想知道"有没有单词以目前拼出的 k 个字母为前缀"，Trie 能 O(k) 回答，而逐词比对要 O(单词数 × k)。
- **TrieNode / children / terminal：** Trie 的节点只有两个字段：`children` 是"下一个字符 → 子节点"的字典；`terminal` 是布尔标记，表示"到这个节点为止恰好是一个完整单词"。注意"是完整单词"和"还有后续"可以同时成立，比如 `eat` 是词，`eats` 也是词。
- **通配符 `.`：** 查询里的 `.` 匹配恰好一个任意字符。所以遇到 `.` 时不能只看一个孩子，要把当前节点的**所有**孩子都试一遍，相当于在 Trie 上也做了一次分支搜索。
- **回溯（backtracking）：** 一条路走不通就退回上一步换条路走的搜索方式。这里"路"就是网格路径，"退回"时必须把之前做的临时修改（比如标记格子已用）撤销掉，否则会污染其他分支。
- **剪枝（pruning）：** 提前发现"这条分支不可能成功"就立刻放弃。本章的剪枝依据是：如果当前拼出的字符串不是任何词典词的前缀，那么再往下拼更不可能是，直接返回。
- **原地标记访问 + 恢复：** 本章不用单独的 visited 集合，而是把走过的格子临时改成 `None`（`board[r][c]=None`），回溯前再改回原字母。`char is None` 的检查就是在挡"这个格子已经在当前路径上"的情况。
- **结果去重（弹出终止标记）：** 找到一个词后，把它的终止标记从 Trie 里删掉（`node.pop(None,None)`）。这样同一个词就算能从第二条路径拼出来，第二次也找不到标记了，自然不会重复进结果。
- **嵌套 dict 形式的 Trie：** `find_words` 里没有用类，而是用"字典套字典"表示 Trie：`{'o':{'a':{'t':{'h':{None:'oath'}}}}}`。`None` 这个键当终止标记用，值直接存完整单词，找到时不用再自己拼字符串。

## 三、解决思路（一步步推导）

**Step 1：先把所有单词建成一棵 Trie。** 插入 `oath` 和 `eat` 之后，根的 `o` 分支和 `e` 分支各自往下长，互不干扰；如果再插入 `oats`，它会复用 `o-a-t` 三个节点再分叉。这就是"共享"：公共前缀只存一份。

**Step 2：从网格每个格子出发做 DFS，同时沿着 Trie 下走。** 状态是三元组：格子位置 (r,c)、当前 Trie 节点、以及（隐含在棋盘上的）已访问格子。进入格子 (r,c) 前先问：`board[r][c]` 这个字符是不是当前 Trie 节点的孩子？不是就 return——这就是剪枝。

**Step 3：到达某个节点时先收词，再继续。** 如果该节点带着终止标记，先把词收进结果并删除标记；但**不要停**，因为这个节点可能还有孩子（比如找到 `eat` 后还可能拼出 `eats`）。

**Step 4：回溯时恢复现场。** 把格子改回 `None` 是临时的，递归完四个方向后必须改回原字母；如果某个 Trie 节点既没有孩子也没有终止标记了，就把它从父字典里删掉，下次别的路径走到这里直接被剪掉。

**手算演示（find_words 找 `oath`）：**

- 起点 (0,0)，字符 `o`。根节点有孩子 `o`（词典里 oath 的第一个字母），走下去，到达节点 `N_o`。
- 邻居有 (0,1)=`a`、(1,0)=`e`。`N_o` 的孩子只有 `a`（oath 第二个字母），所以只有 (0,1) 这一支活着。到达 `N_oa`。把 (0,0) 临时置 None。
- 从 (0,1) 出发，邻居 (0,0) 已是 None（跳过）、(0,2)=`a`、(1,1)=`t`。`N_oa` 的孩子只有 `t`，所以走 (1,1)。到达 `N_oat`。
- 从 (1,1) 出发，邻居 (0,1)=`a`（不是 `h`，剪枝）、(2,1)=`h`、(1,0)=`e`、(1,2)=`a`。只有 (2,1) 匹配，走到 `N_oath`，这个节点带终止标记，收词 `oath`，删除标记。
- 四步都封死，逐层回溯，把格子 (2,1)、(1,1)、(0,1)、(0,0) 依次恢复成原字母。

而搜 `rain` 时，从任何一个 `r` 格子（只有 (2,3)）出发，第二步要找 `a` 的邻居：(1,3)=`e`、(3,3)=`v`，都不是 `a`，立刻剪枝，`rain` 永远不会被发现——正确，因为确实拼不出来。

**手算演示（WordDictionary 查 `'.a.'`）：** 从根出发，i=0 处字符是 `.`，于是根的每个孩子都要试：词典有 bad/dad/mad，根的孩子是 `b`、`d`、`m` 三个节点。任取一支（比如 `b`），i=1 处字符是 `a`，看 `b` 节点有没有孩子 `a`——有；i=2 处是 `.`，再枚举 `ba` 节点的所有孩子，发现有 `d`；i=3 等于词长，返回该节点的 terminal=True。三支里只要有一支返回 True，`any(...)` 就是 True。

## 四、代码逐段讲解

**第一段：TrieNode 和 Trie（面向对象版，服务于 WordDictionary）。**

```python
class TrieNode:
    def __init__(self): self.children={}; self.terminal=False

class Trie:
    def __init__(self): self.root=TrieNode()
    def insert(self,word):
        node=self.root
        for c in word:
            if c not in node.children: node.children[c]=TrieNode()
            node=node.children[c]
        node.terminal=True
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

- `TrieNode.__init__`：每个新节点一开始孩子为空、不是单词结尾。
- `insert`：从根开始逐个字符往下走；字符不存在就现建一个节点；走完最后一个字符后，把落点节点标记 `terminal=True`。插入 `bad` 就是建 `b→a→d` 三个节点。
- `_walk`：私有辅助函数，沿着 text 一个字符一个字符走，中途断了返回 `None`，否则返回终点节点。它是 `search` 和 `startsWith` 的公共部分。
- `search`：走完整词后还要确认终点节点的 `terminal` 是 True。`node is not None and node.terminal` 这个写法先保证节点存在再取属性，否则 None 会报错。
- `startsWith`：只要前缀能走下去就行，不关心是不是完整单词。比如插入了 `eats`，那么 `startsWith('eat')` 也是 True。

**第二段：WordDictionary，在 Trie 上处理通配符。**

```python
class WordDictionary:
    def __init__(self): self.trie=Trie()
    def addWord(self,word): self.trie.insert(word)
    def search(self,word):
        def visit(node,i):
            if i==len(word): return node.terminal
            if word[i]=='.': return any(visit(child,i+1) for child in node.children.values())
            child=node.children.get(word[i]); return child is not None and visit(child,i+1)
        return visit(self.trie.root,0)
```

- `visit(node,i)` 的含义是：从节点 node 出发，匹配 word 从第 i 个字符到末尾，能否成功。
- `i==len(word)` 是递归出口：字符都匹配完了，答案就是"这个节点是不是某个单词的结尾"。
- 遇到 `.` 时用 `any(...)` 对所有孩子递归，只要有一个分支成功就算成功。`any` 加生成器的写法是惰性求值：第一个 True 一出现，剩下的孩子就不再试了。
- 普通字符用 `node.children.get(word[i])`：字典的 `get` 在键不存在时返回 None 而不是抛异常，下一行 `child is not None and visit(...)` 就把"没这个孩子"和"有孩子继续递归"合并成了一句。
- 注意 `search` 完全不碰网格——问题 A 和问题 B 是两个独立问题，只是共享 Trie 这个数据结构。

**第三段：find_words，网格 + 嵌套字典 Trie + 回溯。**

```python
def find_words(board,words):
    if not board or not board[0]: return []
    root={}
    for word in words:
        if not word: raise ValueError('nonempty dictionary words required')
        node=root
        for c in word: node=node.setdefault(c,{})
        node[None]=word
    rows,cols=len(board),len(board[0]); result=[]
    def visit(r,c,parent):
        char=board[r][c]
        if char is None or char not in parent: return
        node=parent[char]; found=node.pop(None,None)
        if found is not None: result.append(found)
        board[r][c]=None
        try:
            for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr,nc=r+dr,c+dc
                if 0<=nr<rows and 0<=nc<cols: visit(nr,nc,node)
        finally: board[r][c]=char
        if not node: del parent[char]
    for r in range(rows):
        for c in range(cols): visit(r,c,root)
    return result
```

- `if not board or not board[0]: return []`：挡两种退化输入——board 是空列表、或每一行都是空列表。此时没有任何格子可走，直接返回空结果。
- `if not word: raise ValueError(...)`：空字符串会构建出"根上挂一个 None 标记"的畸形结构（任何起点都匹配零个字符），所以直接报错拒绝，而不是默默给出可疑结果。
- `node=node.setdefault(c,{})` 是建 Trie 的紧凑写法：如果 node 已有键 c 就返回它，没有就先存一个空字典再返回。一行顶三行（查、建、取）。最后 `node[None]=word` 在单词末节点挂上 None 键当终止标记，值就是完整单词——找到时直接 append，不用反拼路径。
- `visit(r,c,parent)` 里 parent 是"当前路径对应的那层字典"。第一行取格子字符；`char is None` 说明格子已被当前路径用过（回溯中的原地标记），`char not in parent` 说明这个字符不能延续任何前缀——两种情况都直接 return，前者防重用格子，后者就是剪枝。
- `node.pop(None,None)` 一箭双雕：取出终止标记（找到词就 append），同时把它从 Trie 里删掉实现去重；第二个参数 None 表示"键不存在时返回 None 而不抛异常"。
- `board[r][c]=None` 把当前格子标记为已访问；`try/finally` 保证无论递归过程发生什么，`board[r][c]=char` 一定会执行，棋盘被完整恢复——这就是测试里 `b==before` 能通过的原因。
- `if not node: del parent[char]`：递归回来后如果这个 Trie 节点已经空了（词被收走、孩子也删光了），就把它从父字典里删掉。之后任何别的路径再走到同一前缀，`char not in parent` 直接剪掉，避免反复探索死分支。
- 最外层双重循环保证从每个格子都尝试一次起点，`rows,cols=len(board),len(board[0])` 一行给两个变量赋值，是 Python 的元组解包。

## 五、为什么是对的？复杂度是多少？（说人话）

**剪枝为什么安全：** 如果目前拼出的字符串不是任何词典词的前缀，那么在它后面继续加字母，得到的更长的字符串当然也不会变成词典词（一个词的前缀必须从第一个字母就开始吻合）。所以此刻放弃，不会漏掉任何答案。

**找到词为什么不停：** 收词只是路过时顺手摘果子。比如词典同时有 `eat` 和 `eater`，你在 `e-a-t` 节点收了 `eat`，但这个节点下面还挂着 `e-r`，不继续走就会漏掉 `eater`。所以收词和继续递归是两件独立的事。

**回溯为什么能去重且不破坏棋盘：** 棋盘修改被 `try/finally` 包住，退出一层前一定恢复；Trie 侧的修改（弹出终止标记、删除空节点）是永久性的，但它删的都是"已经收进结果、不可能再需要"的信息，所以只影响效率（变快），不影响正确性。

**复杂度：** 设网格 R 行 C 列，最长单词长度 L，词典所有词总长 S。

- 建 Trie：O(S)。比如词典总长是 10 万字符，就是大约 10 万次字典操作，一瞬间完成。
- 网格搜索：最坏情况每个格子都要出发，每次出发的路径分支是 4 个方向但来路不能走所以约 3 分支，深 L 层，粗略上界 O(RC·4·3^(L-1))，notebook 写成 O(RC·4ᴸ)。这是指数级——但只在没有剪枝的病态输入上才逼近；实际中 Trie 剪枝会把绝大多数分支在前一两层就掐死。
- 空间：Trie 本身 O(S)，递归栈最深 O(L)。

拿具体数字感受一下：3×3 网格、词长 10，上界约 9×4×3⁹ ≈ 70 万次格子访问，普通电脑毫秒级；若是 30×30 且完全不剪枝，那才是天文数字——这就是剪枝在实战里的意义。

## 六、测试用例在测什么

```python
wd=WordDictionary()
for w in ['bad','dad','mad']: wd.addWord(w)
assert wd.search('.a.') and wd.search('b..') and not wd.search('..')
```

- `'.a.'`：中间字母固定、两端通配。bad/dad/mad 都符合，测通配符"分支枚举"是否正常。
- `'b..'`：首字母固定、后面通配。b 开头只有 bad（3 个字母），测"通配符出现在尾部"。
- `'..'`：**边界值**——长度对不上。词典里全是 3 字母词，2 个字符的查询必须返回 False，防止实现"长度不够也返回 True"。

```python
b=[list('oaan'),list('etae'),list('ihkr'),list('iflv')]; before=deepcopy(b)
assert set(find_words(b,['oath','pea','eat','rain','eat']))=={'oath','eat'} and b==before
```

- 词典里 `eat` 出现了两次：测去重——没有终止标记弹出机制的话，结果里会有两个 eat。
- `b==before`：用 deepcopy 存了运行前的棋盘，运行后逐一比对，测"回溯后棋盘完全恢复"这个副作用契约。
- `pea`、`rain` 在结果外：测不会虚报拼不出的词。

```python
def slow_exist(board,word): ...  # 逐词暴力 DFS
for values in product('ab',repeat=4):
    b=[list(values[:2]),list(values[2:])]; before=deepcopy(b)
    assert set(find_words(b,words))=={w for w in words if slow_exist(b,w)} and b==before
```

这是一组**穷举对拍**：所有 2×2 的 a/b 棋盘共 2⁴=16 种，词典是所有长度 1–3 的 a/b 字符串共 14 个。对每个棋盘，用独立写的慢速逐词 DFS 算"标准答案"，再和 find_words 的输出比集合相等。16×14 种组合把小规模情况全部覆盖，能抓住"漏词、多词、破坏棋盘"三类错误。

## 七、练习思路提示

**练习 1（对比逐词搜索和共享 Trie 搜索）：** 思路方向是"让公共前缀发挥作用"。构造一个很多词共享长前缀的词典（例如 `ab`、`aba`、`abb`……），分别跑逐词搜索和 Trie 搜索，数一下各自"进入格子的次数"或直接掐表。提示：逐词搜索里每个词都要从每个格子重新起步；Trie 搜索里公共前缀只走一遍，前缀失配一次等于同时否决了所有共享它的词。写清楚输入（棋盘、词典）和输出（找到的词集合、计数），边界可以先测空棋盘和单格棋盘。

**练习 2（重复词与前缀词）：** 提示两个坑点。其一，重复词：嵌套字典写法里 `node[None]=word` 对同一个词第二次插入只是覆盖同一个键，天然不会重复存储——想清楚为什么。其二，前缀词：词典放 `['eat','eater']`，网格要能同时拼出两者；关键在于收走 `eat` 的终止标记后，这个节点仍有孩子 `r`，递归必须继续。手算示例可以用一行的棋盘 `e a t e r`，先预测输出再运行验证。

## 八、对应 LeetCode 题目

- **211. Design Add and Search Words Data Structure：** 就是本章的 WordDictionary，练"Trie + 通配符 `.` 的分支递归"，`addWord`/`search` 接口完全一致。
- **212. Word Search II：** 就是本章的 find_words，练"网格回溯 + Trie 剪枝 + 收词去重 + 恢复棋盘"的完整组合，是本章压轴应用。
