# N118 · KMP与Z函数 —— 说人话详解

> 对应 notebook：`notebooks/14_string_algorithms/118_kmp_and_z_function.ipynb`

## 一、这章要解决什么问题？（问题描述）

字符串匹配的朴素做法是：把模式串对齐文本的每个位置，一位一位比，不匹配就把文本指针往回退一格、重新来。这样最坏要 O(n·m)——比如在 `aaaaaa…a` 里找 `aaab`，每次都对齐、每次都几乎比满、每次失败都从头再来。问题出在：**已经比过相等的那段信息被白白扔掉了**。本章学两个"复用已匹配信息"的结构：

1. **KMP / 前缀函数：** 失配时不退文本指针，只把模式串"自己往右缩"到既是前缀又等于已匹配后缀的位置，然后接着比。
2. **Z 函数：** 对每个位置 i 问"s[i:] 和整个串 s 的开头能匹配多长"，用一个记忆区间（Z-box）避免重复比较。

本章接口实现了四个功能：`prefix_function(s)`（算前缀函数）、`kmp_find(text, pattern)`（找第一次出现）、`z_function(s)`（算 Z 数组）、`sum_scores(s)`（Z 函数的直接应用题），另附 `kmp_find_all` 输出所有（可重叠）匹配。

**具体到数字的例子：** 在文本 `ababab` 里找模式 `abab`，匹配位置是 **[0, 2]**。注意 2 这个位置和 0 的匹配重叠了两个字符（ab**ab**ab 的前一个 ab 同时是后一个 abab 的后缀）——朴素法扫到 0 号匹配后从头再来会漏掉它，KMP 靠"匹配后回跳到前缀函数"把它接住。再如 `sum_scores('babab')`：串长 5，Z 值 [0,0,3,0,1]，总分 5+3+1=**9**。

## 二、关键概念（定义）

- **前缀函数 pi（最长真前后缀）：** pi[i] = s[0..i] 里"最长的、既是前缀又是后缀、且比整段短"的长度。比如 `abab` 的 pi = [0,0,1,2]：到 `aba` 时 `a` 既是开头又是结尾；到 `abab` 时 `ab` 既是开头又是结尾。
- **失配链接（failure link）：** 失配时把已匹配长度 j 换成 pi[j−1] 再试。含义是：刚才匹配上的那段 pattern[0..j−1] 要"缩短成一个既是它前缀、又等于它后缀"的串，才有资格充当新的已匹配前缀。这个缩短可能连锁发生（一次接一次跳），所以代码里是 while 循环。
- **Z 函数：** z[i] = 从 i 开始的后缀与整个串的最长公共前缀长度。本章约定 **z[0] = 0**（有些教材记 z[0]=n，注意区分）。
- **Z 区间（Z-box）：** 目前遇到的"最靠右的、已知与串开头完全相等的区间" [left, right)。新的 i 落在区间内时，s[i..] 与开头的相等关系可以参照"平移 left 个位置的那段旧知识"直接抄过来，不用重新比。
- **重叠匹配：** 一次完整匹配之后不把已匹配长度清零，而是回跳 j=pi[m−1]，让下一个匹配可以与前一个共享字符（`ababab` 里的 0 和 2 就是这么找出来的）。
- **总比较次数 / 均摊线性：** KMP 的 j 每个文本字符最多加 1、只会减少且永远 ≥0，所以"减少"总量被"增加"总量封顶，整个扫描是线性的。Z 函数同理：右边界 right 只前进不后退，总前进量 O(n)。

## 三、解决思路（一步步推导）

### 3.1 前缀函数：自己和自己错位匹配

- **Step 1：** pi[0]=0（单字符没有真前后缀）。算 pi[i] 时，先继承 pi[i−1]：如果 s[i]==s[pi[i−1]]，那 pi[i]=pi[i−1]+1，因为上一个位置的 border 再延长一格仍然前后缀都成立。
- **Step 2：** 如果不等，就沿着失配链接一路缩短：j=pi[j−1]，再试 s[i]==s[j]，直到匹配或 j 归零。
- **Step 3：** 扫文本时维护 j = "模式串前缀与已读文本后缀匹配的长度"，失配就跳链接，文本指针 i 永不后退。

**手算 `prefix_function('ababab')`（notebook 第 6 格的表格）：**
- i=1('b')：继承 j=0，'b'≠'a'，pi[1]=0；
- i=2('a')：j=0，'a'=='a' → j=1，pi[2]=1；
- i=3('b')：j=1，s[3]='b' 等于 s[1]='b' → j=2，pi[3]=2；
- i=4('a')：j=2，'a'==s[2]='a' → 3；i=5('b')：j=3 → 4。
结果 pi=[0,0,1,2,3,4]——周期串每往后一格，border 恰好加一。

### 3.2 KMP 扫描与重叠匹配

**手算 `kmp_find_all('ababab','abab')`（pi=[0,0,1,2]）：**

- i=0('a')：j 0→1；i=1('b')：j 1→2；i=2('a')：j 2→3；i=3('b')：j 3→4==m，**命中，起点 3−4+1=0**；为允许重叠，j 回跳 pi[3]=2（保留已确认的 "ab"）。
- i=4('a')：pattern[2]='a'，j 2→3；i=5('b')：pattern[3]='b'，j 3→4==m，**命中，起点 5−4+1=2**。
- 输出 [0,2]。看到关键点了吗：第二个匹配完全没回退文本指针，全靠那次 j=pi[3]=2 的回跳"白捡"了两个已匹配字符。

### 3.3 Z 函数：抄盒子里的旧答案

- **Step 1：** 维护最右 Z-box [left,right)。i 在盒内时，s[i..right) 与 s[i−left..right−left) 逐位相同（盒子的定义），所以 z[i] 至少可以先抄 min(right−i, z[i−left])：如果 z[i−left] 没超出盒子，答案就是它（不需要也无法再扩展）；否则先给到盒边，再逐字符试。
- **Step 2：** 试完若 i+z[i] 超过 right，就把盒子挪到 i 这里。

**手算 `z_function('ababab')`：**
- i=1：盒空，比 s[0]='a' vs s[1]='b' 不等，z[1]=0。
- i=2：逐个比，s[2..5]='abab' 与开头 'abab' 全等，z[2]=4；盒子更新为 [2,6)。
- i=3：在盒内，抄 min(6−3, z[1]=0)=0；验证 s[0] vs s[3] 不等，z[3]=0。
- i=4：在盒内，抄 min(6−4, z[2]=4)=2；i+2=6 已到串尾，z[4]=2。
- i=5：抄 min(1, z[3]=0)=0，验证不等，z[5]=0。
结果 z=[0,0,4,0,2,0]，即第 6 格表格的 Z 值列。

### 3.4 应用：sum_scores

LC2223 要求对每个 i 算 LCP(s, s[i:]) 再求和。i=0 项是整串自己（长 len(s)，因为约定 z[0]=0 要单独补）；i≥1 项就是 z[i]。所以答案 = len(s) + Σz[i]，这正是一行代码 `len(s)+sum(z_function(s))`。`'babab'`：5 + (0+0+3+0+1) = **9**。

## 四、代码逐段讲解

### 4.1 `prefix_function(s)`

```python
def prefix_function(s):
    pi=[0]*len(s)
    for i in range(1,len(s)):
        j=pi[i-1]
        while j and s[i]!=s[j]: j=pi[j-1]
        if s[i]==s[j]: j+=1
        pi[i]=j
    return pi
```

- `pi=[0]*len(s)`：pi[0] 天然是 0，先全部填 0。
- `j=pi[i-1]`：从上一个位置的 border 长度开始试，这是"最好情况候选"。
- `while j and s[i]!=s[j]: j=pi[j-1]`：`j and` 保证 j=0 时停（0 号位置没法再缩）；不等就把 border 缩成"border 的 border"再试——这就是失配链接的连锁跳。
- `if s[i]==s[j]: j+=1`：匹配上了就把 border 延长一格。走到这里 j 可能是 0（此时若 s[i]==s[0] 则 j=1，否则保持 0）。
- `pi[i]=j`：记录答案，同时供下一轮继承。

### 4.2 `kmp_find_all(text, pattern)` 与 `kmp_find(text, pattern)`

```python
def kmp_find_all(text,pattern):
    if not pattern: return list(range(len(text)+1))
    pi=prefix_function(pattern); j=0; out=[]
    for i,c in enumerate(text):
        while j and c!=pattern[j]: j=pi[j-1]
        if c==pattern[j]: j+=1
        if j==len(pattern): out.append(i-j+1); j=pi[j-1]
    return out

def kmp_find(text,pattern):
    if not pattern: return 0
    pi=prefix_function(pattern); j=0
    for i,c in enumerate(text):
        while j and c!=pattern[j]: j=pi[j-1]
        if c==pattern[j]: j+=1
        if j==len(pattern): return i-j+1
    return -1
```

- `if not pattern: ...`：空模式的约定。空串出现在每个"缝隙"里：位置 0..len(text) 共 n+1 个，`list(range(len(text)+1))`；只找第一个时就是位置 0。
- 扫描循环与前缀函数"同构"：j 是当前匹配长度，`while j and c!=pattern[j]: j=pi[j-1]` 失配回跳，`if c==pattern[j]: j+=1` 匹配延长。文本指针 i 从头到尾只向前。
- `if j==len(pattern): out.append(i-j+1)`：匹配满了，起点是 i−j+1（i 是最后一个匹配字符的下标）。
- `j=pi[j-1]`（find_all 版）：命中后不清零而是回跳到最长 border，**这一步就是"重叠匹配"的实现**——`ababab` 的第二次命中全靠它。
- `kmp_find` 与 `kmp_find_all` 唯一的区别是命中即 `return i-j+1`，扫完没命中返回 −1。

### 4.3 `z_function(s)`

```python
def z_function(s):
    z=[0]*len(s); left=right=0
    for i in range(1,len(s)):
        if i<right: z[i]=min(right-i,z[i-left])
        while i+z[i]<len(s) and s[z[i]]==s[i+z[i]]: z[i]+=1
        if i+z[i]>right: left,right=i,i+z[i]
    return z
```

- `z=[0]*len(s); left=right=0`：z[0] 按约定为 0；初始盒子是空区间 [0,0)。
- `if i<right: z[i]=min(right-i,z[i-left])`：i 在盒内，先抄平移过来的旧答案 z[i−left]，但**不能越过盒子的右边界**——盒子只担保到 right 为止，越界部分没担保，所以用 min 封顶，留待下一步验证。
- `while i+z[i]<len(s) and s[z[i]]==s[i+z[i]]: z[i]+=1`：逐字符扩展。如果抄来的值没顶到盒边，这一步通常立即失败（答案已经确定）；顶到盒边才会真的往外比。
- `if i+z[i]>right: left,right=i,i+z[i]`：匹配延伸到了比 right 更远的地方，把盒子搬过来。right 只进不退，是线性时间的保证。

### 4.4 `sum_scores(s)`

```python
def sum_scores(s): return len(s)+sum(z_function(s))
```

- 一行实现 3.4 节的公式：`len(s)` 补上 i=0（整串与自身的 LCP，因为 z[0]=0 的约定），`sum(...)` 累加所有 i≥1 的 LCP。

## 五、为什么是对的？复杂度是多少？（说人话）

**KMP 为什么不漏匹配？** 扫描时 j 的含义是"模式串前缀中，与已读文本后缀相等的最长长度"。失配时，能"继承"部分匹配的前缀必须既是 pattern[0..j−1] 的前缀、又是它的后缀——也就是它的 border。pi 链条 pi[j−1], pi[pi[j−1]−1], … 恰好按从长到短把所有 border 排好队，while 循环挨个试，一个候选都不丢。而任何漏掉的匹配都需要某个更短的 border 成立才能接上，所以不会漏。

**为什么是线性的？** 拿具体账本算：每个文本字符 j 最多 +1，所以整个循环里 j 的总增量 ≤ n；while 循环每次让 j 变小，而 j 永远 ≥ 0，所以总减量 ≤ 总增量 ≤ n。加起来比较次数不超过 2n 的量级。文本 10^6、模式 10^5 时，KMP 约做 110 万次字符比较；朴素法在 `aaaa…` 这种输入上最坏要 10^11 次，差了五个数量级。

**Z 函数为什么能抄？** 盒子 [left,right) 的定义是"s[left..right−1] 与 s[0..right−left−1] 完全相等"。i 在盒内时，把这段相等关系平移：s[i..] 开头的一段与 s[i−left..] 的对应段相同。于是 z[i−left]（关于 s[i−left] 的旧答案）在不超过盒子范围的条件下对 s[i] 同样成立。唯一不能直接抄的情形是旧答案顶穿了盒子右端——盒子没担保那么远——所以封顶到 right−i 再老实逐字符验证。

**几个约定别搞混：** 本章 z[0]=0（教材里也有记 z[0]=n 的，sum_scores 里那个 len(s) 就是为这个约定补的）；空模式匹配 n+1 个边界位置；前缀函数和 Z 数组都是 O(n) 时间、O(n) 空间；KMP 匹配 O(|text|+|pattern|) 时间、O(|pattern|) 辅助空间（全部匹配再加大小的输出数组）。

## 六、测试用例在测什么

```python
assert kmp_find_all('ababab','abab')==[0,2]
assert kmp_find('abc','d')==-1 and kmp_find('abc','')==0
assert sum_scores('babab')==9
```

- 第 1 条：重叠匹配的核心行为——[0,2] 而不是只有 [0]，专测命中后 `j=pi[j-1]` 那一步（清零版会得到 [0]）。
- 第 2 条：两个边界。找不到返回 −1；空模式约定在位置 0 匹配。
- 第 3 条：Z 函数应用的官方样例，5+3+1=9，第 3.4 节手算过。

第 4 段是系统化暴力对拍：

- `words` 收集了长度 0..5 的全部 63 个 a/b 二元串。对每个 s、每个下标 i：用定义式 `max(k for k ... if s[:k]==s[i-k+1:i+1])` 直接算真前后缀的最大长度，与 pi[i] 比；用 `max(k ... if s[:k]==s[i:i+k])` 直接算 LCP，与 z[i] 比（i≥1）。
- 再取前 15 个词（含空串）当模式，`kmp_find(s,p)` 与内置 `s.find(p)` 比，`kmp_find_all(s,p)` 与 `[i for i in range(len(s)+1) if s.startswith(p,i)]` 比——`startswith(p, i)` 是"位置 i 开始是否匹配"的最直白翻译，连空模式的 n+1 个位置都自动对上。
- 这一段把两个结构在所有小输入上的行为和定义完全对齐，等于用穷举验证了"回跳链条不漏匹配""Z-box 抄写不出错"。

## 七、练习思路提示

- **练习 1（输出所有重叠匹配）：** 提示——关键是想清楚"命中之后 j 该设成什么"：设 0 会漏掉重叠匹配，设 pi[m−1] 恰好保留既是前缀又是后缀的那截。手算例：`('ababab','abab')` → [0,2]（3.2 节全程演示）；再自测边界：模式比文本长（应输出空）、空模式（n+1 个位置）、单字符模式。最后和 `[i for i in range(len(t)+1) if t.startswith(p,i)]` 对拍。
- **练习 2（构造多次回跳的周期串）：** 提示——找会让失配链接连跳的串，典型是同字符长跑，比如 `aaaab`：算 pi 时 i=4('b') 处，j 从 pi[3]=3 出发，'b'≠s[3]、跳 pi[2]=2、再跳 pi[1]=1、再跳 pi[0]=0，链 3→2→1→0 一口气跳到底。建议你画一张表：每行记 (i, 进入时的 j, 每次跳变, 最终 pi[i])，统计总比较次数，验证它确实随串长线性而不是平方。周期串（如 `ababab…`）则展示"border 逐位 +1、一次匹配后大步回跳"的另一种模式。

## 八、对应 LeetCode 题目

- **28. Find the Index of the First Occurrence in a String**：这就是 `kmp_find` 的原题——练"扫描循环 + 失配回跳"的最纯形态。
- **459. Repeated Substring Pattern**：用前缀函数判周期性——若 pi[n−1] 是最长 border，则 n−pi[n−1] 是最小周期，能整除 n 就说明整串由小段重复构成，练的是把 border 和周期联系起来。
- **2223. Sum of Scores of Built Strings**：这就是 `sum_scores` 的原题——练 Z 函数的定义式直接落地：每个后缀与整串的 LCP 之和。
