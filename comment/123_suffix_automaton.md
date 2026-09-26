# N123 · 后缀自动机与子串状态 —— 说人话详解

> 对应 notebook：`notebooks/14_string_algorithms/123_suffix_automaton.ipynb`

## 一、这章要解决什么问题？（问题描述）

这章要造一台"子串识别机"：你把一个字符串 s 一个字符一个字符喂给它，它内部就长出一台自动机，能识别 s 的所有子串；而且这台机器的体积只和 s 的长度成正比（不是平方）。有了它，两类问题顺手就解：

1. s 里有多少个不同的非空子串？例子：s = 'ababa'，答案是 9：a, b, ab, ba, aba, bab, abab, baba, ababa。暴力要把 15 个子串全部生成再去重；自动机只需要把每个状态"管辖"的子串数目加起来。
2. 两个序列的最长公共连续段（注意是任意可比较的符号，不限于字符）。例子：a = [1,2,3,2,1]，b = [3,2,1,4,7]，答案是 3，因为公共连续段 [3,2,1] 出现在两边（a 的下标 2–4、b 的下标 0–2），没有更长的。做法是把 a 建成自动机，再让 b 像走 AC 自动机那样在上面匹配，失配就沿链接缩短。

后缀自动机（SAM）为什么省空间？因为它不给每个子串单开一个节点，而是把"出现结束位置完全相同"的一族子串合并成一个状态。这就是本章标题里"子串状态"的含义。

## 二、关键概念（定义）

- **endpos 集合**：一个子串 w 在 s 中所有"结束位置"组成的集合。例如 'ababa' 里 'b' 的 endpos 是 {1,3}，'ab' 的 endpos 是 {2}。endpos 相同的子串，行为完全一样（在同样的位置"落地"），可以合并管理。
- **状态（endpos 等价类）**：SAM 的一个节点 v 代表"endpos 相同的一整族子串"。这一族子串的长度恰好连续地铺满一个区间 (length[link[v]], length[v]]，左开右闭。区间最长的那个一定是"最长相配串"，最短的比后缀链接指向的类最长者再短 1。
- **length（len）**：length[v] 是状态 v 管辖的最长子串长度。v 里的其他子串都是这个最长者不断掐头得到的后缀（掐到 endpos 变化为止）。
- **后缀链接（link）**：从状态 v 指向"管辖 v 的最短子串再掐一个头之后那个更短等价类"的指针。沿 link 走，子串越来越短、endpos 集合越来越大。根状态 0 的 link 是 −1，表示链到头；初始状态的 length 是 0（管空串）。
- **last**：始终指向"当前整个已读入串"所在的状态。每次 extend 从 last 出发做收尾工作，然后 last 移到新状态。这让 SAM 天生支持"在线"构建——字符串流式喂入，随时可用。
- **克隆（clone）**：追加新字符时，某个老状态可能"太胖"——它管辖的长度区间里，短的一部分该接受新出现位置、长的一部分不该。这时复制出一个新状态（克隆体），拷贝它的转移表、把最大长度砍短，让长短两族各归各的状态。克隆是 SAM 构建里唯一需要仔细体会的动作。
- **转移（next）**：next[v] 是状态 v 的出边字典，键是符号、值是目标状态。从根沿转移走 k 步读出的串一定是 s 的子串；SAM 能且只能接受 s 的全部子串。
- **失配走 link（匹配不变量）**：在 SAM 上扫描另一个序列时，状态与"当前已匹配后缀长度"共同保持：当前状态管辖的子串里包含"b 中刚结束的这段的后缀中，仍可作为 a 的子串继续延伸的最长者"。失配时沿 link 缩短，正是 KMP/AC 自动机失配思想在子串层面的翻版。

## 三、解决思路（一步步推导）

- Step 1：理解"一个状态管一族长度"。对 s='ababa' 逐字符构建，得到下面这张表（就是 notebook cell6 打印的表）：

| 状态 v | 最短长度 | 最长长度 length[v] | 后缀链接 link[v] | 转移 next[v] |
|---|---|---|---|---|
| 0（根） | 0 | 0 | −1 | {'a':1, 'b':2} |
| 1 | 1 | 1 | 0 | {'b':2} |
| 2 | 1 | 2 | 0 | {'a':3} |
| 3 | 2 | 3 | 1 | {'b':4} |
| 4 | 3 | 4 | 2 | {'a':5} |
| 5 | 4 | 5 | 3 | {} |

- Step 2：读懂这张表。s = a(0) b(1) a(2) b(3) a(4)。状态 2 管辖长度 1..2 的两兄弟：'b'（出现在下标 1、3 结束）和 'ab'（同样在下标 1、3 结束，因为每次 'b' 前面恰好都是 'a'），endpos 同为 {1,3}，所以合并成一个状态。再看状态 3：'ba' 和 'aba' 都恰好在下标 2、4 结束，endpos 同为 {2,4}，也合成一族，长度铺满 2..3。你可以自查剩下几个状态：状态 4 管 'bab'、'abab'（endpos {3}），状态 5 管 'ababa'（endpos {4}），状态 1 管 'a'（endpos {0,2,4}）。
- Step 3：数不同子串。状态 v 管辖的子串个数就是 length[v] − length[link[v]]（长度区间 (link 最长, 自身最长] 里的每一个长度一个串）。把非根状态全加起来：状态 1 贡献 1−0=1，状态 2 贡献 2−0=2，状态 3 贡献 3−1=2，状态 4 贡献 4−2=2，状态 5 贡献 5−3=2，合计 9，与 notebook 打印的"不同子串 9"一致。
- Step 4：看一次克隆。换串 s='abb'（下标 0,1,2）。读完 "ab" 时，'b' 和 'ab' 都只在下标 1 结束，endpos 同为 {1}，所以它们同属状态 2（长度 1..2）。喂第三个字符 'b'（落在下标 2）时，'b' 的 endpos 扩成 {1,2}，而 'ab' 仍是 {1}——一族被劈成两半。构建代码发现 length[p]+1 ≠ length[q]（1 ≠ 2），于是克隆出状态 4：拷贝状态 2 的转移、length 定为 1（只管 'b'）、link 沿用 2 的旧 link（0）；随后把指向旧状态 2 的 'b' 边改指向克隆体，旧状态 2 的 link 改指克隆体。从此 'b' 归克隆体、'ab' 归旧状态 2，各自安好。
- Step 5：匹配演示。拿 a=[1,2,3,2,1] 建机，再扫 b=[3,2,1,4,7]，维护"当前匹配长度 matched"：
  - 读 3：根有 '3' 边，走过去，matched=1。
  - 读 2：当前状态有 '2' 边，matched=2。
  - 读 1：有 '1' 边，matched=3，best 更新为 3。
  - 读 4：当前状态没有 '4' 边，沿 link 退一步、matched 收缩到 min(3, 新状态的 length)——能缩到 1 再到 0 逐级尝试，直到根也没有 '4'，彻底清零。
  - 读 7：同样清零。最终 best=3，正是 [3,2,1]。
  - 这个"失配沿 link 缩短、绝不倒退扫描指针"的节奏，和 KMP 一模一样。

## 四、代码逐段讲解

### 4.1 __init__：初始状态

```python
class SuffixAutomaton:
    def __init__(self): self.next=[{}]; self.link=[-1]; self.length=[0]; self.last=0
```

- 机器初始只有一个状态 0：它代表空串，没有出边（next=[{}]）、没有后缀链接（link=[-1]，−1 表示"链到头"）、长度 0。last=0 表示"整个已读串"此刻就是空串。

### 4.2 extend：追加一个符号（全章最难的 20 行）

```python
    def extend(self,symbol):
        cur=len(self.next); self.next.append({}); self.length.append(self.length[self.last]+1); self.link.append(0); p=self.last
        while p!=-1 and symbol not in self.next[p]: self.next[p][symbol]=cur; p=self.link[p]
        if p==-1: self.link[cur]=0
        else:
            q=self.next[p][symbol]
            if self.length[p]+1==self.length[q]: self.link[cur]=q
            else:
                clone=len(self.next); self.next.append(self.next[q].copy()); self.length.append(self.length[p]+1); self.link.append(self.link[q])
                while p!=-1 and self.next[p].get(symbol)==q: self.next[p][symbol]=clone; p=self.link[p]
                self.link[q]=self.link[cur]=clone
        self.last=cur; return cur
```

- 第一行一口气创建新状态 cur（新符号必然造出"整个已读串+1"这个新子串），它的 length 是 last 的 length 加一；link 先占位为 0。p 从 last 出发。
- 第一个 while：沿着后缀链接往上爬，凡是"还没有 symbol 出边"的祖先都补一条指向 cur 的边。这一步的含义是：所有以 symbol 结尾的新后缀，都从这些状态可达 cur。爬到有边的 p 或到头（−1）为止。
- `if p==-1: self.link[cur]=0`：一路爬到根之外，说明 symbol 是全新字符，cur 的后缀链接直接归到根。
- 否则看 p 已有的那条边通向的 q，分两种情况：
  - `self.length[p]+1==self.length[q]`：q 的最长子串恰好是"p 的最长子串接 symbol"，长度咬合无缝。这种情况最省事，cur 的后缀链接指到 q 即可。
  - 否则 q"太胖"（它管辖的长度区间跨了界），进入克隆分支：新开 clone 状态，`self.next.append(self.next[q].copy())` 逐字拷贝 q 的转移表（克隆体必须能走 q 能走的所有路），`self.length.append(self.length[p]+1)` 把克隆体的最大长度砍到 p 的长度加一，link 沿用 q 的旧 link。接着第二个 while 沿后缀链把"原来指向 q 的 symbol 边"改道指向 clone（`self.next[p].get(symbol)==q` 用 get 避免键不存在时报错）。最后 `self.link[q]=self.link[cur]=clone` 把旧 q 和 cur 都挂到克隆体下面。
- `self.last=cur` 收尾：新读入的整个串现在住进 cur。返回 cur 方便外部追踪。

### 4.3 count_distinct_substrings_sam：状态长度差求和

```python
def count_distinct_substrings_sam(s):
    sam=SuffixAutomaton()
    for c in s: sam.extend(c)
    return sum(sam.length[v]-sam.length[sam.link[v]] for v in range(1,len(sam.next)))
```

- 前三行把 s 喂进自动机。最后一行把每个非根状态管辖的子串个数（长度区间的长度）加总。range 从 1 开始是跳过代表空串的根——根不该贡献任何非空子串。

### 4.4 longest_common_subarray_sam：最长公共连续段

```python
def longest_common_subarray_sam(a,b):
    sam=SuffixAutomaton()
    for x in a: sam.extend(x)
    state=matched=best=0
    for x in b:
        while state and x not in sam.next[state]: state=sam.link[state]; matched=min(matched,sam.length[state])
        if x in sam.next[state]: state=sam.next[state][x]; matched+=1
        else: state=matched=0
        best=max(best,matched)
    return best
```

- 前两行把序列 a 在线建成自动机（符号是整数也没关系，只要能当字典的键）。state/matched/best 分别是"当前状态、当前连续匹配长度、历史最好成绩"。
- `while state and x not in sam.next[state]: state=sam.link[state]; matched=min(matched,sam.length[state])` 是失配收缩：当前状态接不上 x 时，沿后缀链接换一个管辖"更短后缀"的状态；matched 必须跟着收缩，而且不能超过新状态的 length（新状态管的最长子串就那么长）。`state and` 挡住根——根不许再跳。
- `if x in sam.next[state]` 接得上就走一步、matched 加一；`else: state=matched=0` 是"缩到根仍接不上"，彻底清零重来。每读一个符号用 best 记录最大值。

## 五、为什么是对的？复杂度是多少？（说人话）

正确性抓三点。

第一，状态的含义始终成立：状态 v 代表 endpos 相同、长度连续铺满 (length[link[v]], length[v]] 的一族子串。为什么长度是连续的一段？因为同一个 endpos 的集合里，若长串 w 在，那 w 的每个"掐头后缀"的 endpos 只会变大或不变；不变的那些正好比 w 短一截、两截……直到某次掐头后 endpos 变大，那条分界线就是 link 指向的类。所以每个类恰是一段连续长度，贡献 length[v]−length[link[v]] 个不同子串——计数函数就是这么来的。

第二，克隆保全了转移的语义。克隆发生时，旧状态 q 的类确实被新字符劈成了两半：短的部分该享受新的结束位置、长的部分不该。克隆体接管短的部分（转移表整个拷贝，所以从克隆体出发能走的路和 q 原来一模一样），旧 q 保留长的部分，改边的那段 while 把"应该通向短类"的入口全部改道。做完这些，每个子串重新有且只有一个归属状态，自动机识别的子串集合没有多一个也没有少一个。

第三，匹配的收缩不会丢最优解。扫描 b 时，若 x 接不上，我们就退到"当前匹配串的更短后缀"再试；任何以 x 结尾的公共连续段，其前一段一定是 a 的某个子串、也一定在自动机的某个状态里，沿 link 逐级缩短恰好按长度从长到短枚举了所有候选后缀，所以能接上的最长者一定被找到。matched 收缩到新状态的 length 是必要的对账：换到新状态后，你手里的匹配串长度不可能超过它的管辖上限。

复杂度（拿具体规模感受）：

- 构建：教科书结论是长度 n 的串，SAM 状态数不超过 2n−1、转移数不超过 3n−4，构建总代价是 O(n) 级别（本实现用字典存转移并整表拷贝克隆体，按字典平均代价算线性；若字母表巨大，拷贝克隆体的成本要另算）。n=10⁵ 时状态也就二十万上下，建得飞快。
- 计数：构建 O(n) + 一遍求和 O(状态数)，整体线性。同一问题用 N122 的后缀数组是 O(n log² n)，SAM 更快但要付更高的理解成本。
- 匹配：建 a 花 O(n)，扫 b 时每读一个符号 matched 最多涨 1、每次跳 link 只降不升，总步数 O(n+m)。例：n=m=10⁵ 时约几十万次操作，瞬间完成；平方 DP 同样规模要 10¹⁰ 格，差着一到两个数量级。

## 六、测试用例在测什么

```python
assert longest_common_subarray_sam([1,2,3,2,1],[3,2,1,4,7])==3
```
这条是 LeetCode 718 的官方示例：公共连续段是 [3,2,1]，长度 3。它同时测了两件本章特色：一是符号可以是整数（字典键只要是可哈希对象就行），二是"匹配很长一段后突然失配"时沿 link 收缩的逻辑（读到 4 时必须从 matched=3 一路缩到 0）。

```python
words=[''.join(p) for n in range(7) for p in product('ab',repeat=n)]
```
随后的大循环对长度 0–6 的全部 a/b 串做三重体检：
- `assert all(sam.length[sam.link[v]]<sam.length[v] ...)` 查结构不变量：每个非根状态的最短长度必须严格大于其 link 的最长长度（长度区间既不重叠也不颠倒）。这条不过，说明克隆或链接挂错了。
- 不同子串数三方对拍：SAM 计数 == 暴力集合大小 == N122 后缀数组公式 n(n+1)/2 − ΣLCP。三种原理不同的算法给出同一个数，这是很强的交叉验证。
- 最后两重循环（对 words[:31]，即长度 ≤ 4 的串两两配对）把"最长公共连续段"与四重循环的暴力解逐一对照，覆盖了"两串无公共元素""一串为空""多个并列最长"等边角情形。

## 七、练习思路提示

**练习 1（字符边推广为整数边）**：其实本章代码天生就支持——转移用字典 next[v] 存，键可以是任何可哈希符号，测试里 [1,2,3,2,1] 已经在用整数边了。你要做的是把"推广"落实成文档和验证：输入输出约定（符号需可哈希、序列可以是 list）、边界（空序列应返回 0 个子串/匹配长度 0），并手算一个小例子，比如 a=[1,1,2] 的不同"子段"数（1,2,11,112,12 共 5 个）与程序对照。再进一步可以讨论：如果符号全集很大（比如任意 64 位整数），字典转移的常数和克隆拷贝的成本会怎样变化。

**练习 2（SAM 与平方 DP 解 718 对比）**：718 的常规解法是 dp[i][j] = "以 a[i−1]、b[j−1] 结尾的最长公共连续段"，转移是相等时 dp[i−1][j−1]+1，时间空间都是 O(n·m)。你的对照要点：SAM 路线是 O(n+m) 时间、状态线性空间，但代码复杂、常数不小；DP 路线简单直接，n=m=1000（718 的真实规模）只有百万格，完全够用。结论要写诚实：SAM 并非 718 的必需算法，它是"同一问题的更重武器"；把两种解在同一个手算例子（比如 [1,2,3] × [2,3,4]）上都推一遍，最能看清两者的差异。

## 八、对应 LeetCode 题目

- **718. Maximum Length of Repeated Subarray（延伸题）**：求两个数组的最长公共连续子数组。本章 longest_common_subarray_sam 就是它的 SAM 解，练习的重点是把 SAM 解和平方 DP 解做对比，理解"更优复杂度"与"更复杂实现"之间的取舍。
- **1044. Longest Duplicate Substring（延伸题）**：求最长重复子串，与 N122 的后缀数组路线同题。用 SAM 的视角看，重复子串就是"出现次数 ≥ 2 的子串"，可以沿 endpos/后缀链接统计每个状态的 Right 集合大小后取最大长度；这题练的是把本章"状态 = endpos 等价类"的思想迁移到计数场景。
