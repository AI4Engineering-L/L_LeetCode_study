# N029 · 可变窗口与最短覆盖 —— 说人话详解

> 对应 notebook：`notebooks/03_pointers_windows/029_variable_windows.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章同时解决两个经典问题，它们共用同一套"滑动窗口"骨架，但优化方向完全相反。

**问题 A（最长无重复子串）**：给你一个字符串 s，你要找出其中最长的一段连续子串，要求这段子里没有任何字符重复。具体例子：输入 `s='abcabcbb'`，输出 `3`。为什么是 3？因为整个串里最长的无重复片段是 `'abc'`（出现在下标 0~2），长度 3；你往后不管怎么取，比如 `'abca'` 就有两个 `a`，不合法。

**问题 B（最短覆盖子串）**：给你字符串 s 和目标串 t，你要在 s 里找一段**最短**的连续子串，使得 t 里每个字符（含重复）都被这段覆盖至少同样次数。具体例子：输入 `s='ADOBECODEBANC'`、`t='ABC'`，输出 `'BANC'`。为什么是 `'BANC'`？因为这四个字母里 A、B、C 各出现一次，刚好覆盖 `t='ABC'`；而 s 里更短的候选（比如 `'BAN'` 缺 C、`'ANC'` 缺 B）都盖不全，所以 `'BANC'` 就是最短答案。

注意两个问题的"方向"相反：问题 A 想让窗口**尽量长**，一出现重复就收缩；问题 B 想让窗口**尽量短**，一旦盖住了 t 就立刻收缩，看还能缩到多短。

## 二、关键概念（定义）

- **可变窗口（滑动窗口）**：用两个下标 `left` 和 `right` 圈住一段连续区间，`right` 不断右移扩大窗口，`left` 视情况右移缩小窗口。你可以把它想象成一把在字符串上滑动的尺子，两头都能动。
- **窗口有效条件**：判断当前窗口是否"合法"的判据。问题 A 的判据是"窗口内每个字符出现次数都不超过 1"；问题 B 的判据是"窗口里 t 的每个字符都够了数量"。写滑动窗口题的第一步永远是把这个条件写清楚。
- **频次表 / Counter**：一个字典，key 是字符，value 是该字符在当前窗口里出现了几次。窗口右移时加一，左移时减一，这样任何时刻都能 O(1) 查询某个字符的出现次数。
- **缺失计数（missing）**：问题 B 专用的一个整数，表示"还差几个字符才能盖住 t"。它等于 t 中尚未被窗口满足的字符个数总和。missing 变成 0 就代表窗口盖住了 t。用它的好处是不用每步都遍历整个 need 字典去比对。
- **计入重复字符**：t 如果是 `'AAB'`，那窗口里必须有两个 A 和一个 B，只统计"出现过哪些字符种类"是不够的，必须按个数记账。这是本章代码用 `Counter(t)` 而不是 `set(t)` 的原因。
- **可行性单调前提**：滑动窗口能工作的隐藏前提——窗口越长越"容易违法"（问题 A）或"容易满足"（问题 B），即合法性随窗口长度单调变化，所以违反后收缩一定能在有限步内恢复合法。如果约束不单调（比如带负数的和），这套收缩逻辑就会失效。

## 三、解决思路（一步步推导）

我们先讲问题 A 的思路：

- **Step 1**：让 `right` 从左到右扫过整个串，每步把 `s[right]` 计入频次表。
- **Step 2**：如果 `counts[s[right]]` 变成了 2（出现重复），说明窗口非法，这时不断把 `left` 右移、把 `s[left]` 移出频次表，直到重复消失。
- **Step 3**：窗口重新合法后，用当前长度 `right-left+1` 去更新答案 `best`。因为 right 只前进、left 只在必要时前进，每个字符进出窗口最多各一次。
  - 两个问题的"何时更新答案"正好相反：问题 A 在窗口**合法时**更新（窗口越长越好）；问题 B 在窗口**刚合法、收缩途中**更新（窗口越短越好）。cell1 那句"两个问题的更新时机相反"说的就是这个。

手算演示（问题 A，`s='abcaac'`，这也是 notebook 小实例用的数据）：

| right | 读入 | 收缩动作 | 合法窗口 | 长度 |
|---|---|---|---|---|
| 0 | a | 无 | `a` | 1 |
| 1 | b | 无 | `ab` | 2 |
| 2 | c | 无 | `abc` | 3 |
| 3 | a | a 重复，移出 s[0]='a'，left=1 | `bca` | 3 |
| 4 | a | a 重复，连移 b、c、a，left=4 | `a` | 1 |
| 5 | c | 无 | `ac` | 2 |

最终 best = 3。这张表就是 notebook cell6 运行 `show_table` 画出来的东西，你可以先手算再运行核对。

表格里最值得盯的是 right=4 那一行：读入第二个 a 后窗口 `bcaa` 里有两个 a，第一次移出 b 还没解决（重复的是 a），第二次移出 c 也没解决，第三次移出 a 才把 a 的计数降回 1。这说明收缩循环移出的字符**不一定**是引发重复的那个字符，它只是按顺序把左端清出去，直到重复消失为止。

问题 B 的思路反过来：

- **Step 1**：把 t 拆成 `need=Counter(t)`（每个字符要几个），`missing=len(t)`（总共还缺几个字符）。
- **Step 2**：right 右移读入字符 c：如果 `need[c]>0`（c 是还缺的字符），missing 减一；然后无论如何 `need[c]-=1`。注意 need[c] 会变成负数，负数表示"窗口里这种字符多出来了"，这是刻意设计的记账方式。
- **Step 3**：一旦 `missing==0`（窗口盖住 t 了），就进入收缩循环：先记录当前窗口为候选答案，再把 `s[left]` 移出；如果移出后 `need[old]` 变成正数，说明我们把必需字符丢了，missing 加一、退出收缩。
- **Step 4**：记录答案时只存下标 `(left, right+1)`，最后再切一次片，避免在循环里反复复制子串。

手算演示（问题 B，`s='ADOBECODEBANC'`，`t='ABC'`，只列 missing 归 0 的关键时刻）：

| right 读入 | 事件 | 窗口变化 | best |
|---|---|---|---|
| 5 (C) | missing 3→0，首次合法 | `[0,6)`='ADOBEC' | 'ADOBEC'（长 6） |
| 5 收缩 | 移出 A 后 need[A] 变正，missing=1 | [1,6) 起，暂停 | — |
| 10 (A) | missing 1→0，再次合法 | [1,11) 起 | 不更新 |
| 10 收缩 | 连移 D、O、B、E 到 [5,11)，都是多余字符 | 最短到 [5,11) 长 6 | 与 6 打平，不更新 |
| 12 (C) | missing 1→0，第三次合法 | [6,13) 起 | — |
| 12 收缩 | 连移 O、D、E、B、A 到 [10,13) | 最短到 [10,13) 长 3 | **'BANC'**，最终答案 |

收缩阶段能连移 4 个字符是因为 need 里它们都是 0 或负数（多余），移出后 need 不变正、missing 保持 0，循环就继续；一旦移出的字符让 need 变正（说明丢了必需字符），missing 加一、循环立刻停。

## 四、代码逐段讲解

先看 `length_of_longest_substring`，逐字照抄如下：

```python
from collections import Counter

def length_of_longest_substring(s):
    counts=Counter(); left=best=0
    for right,c in enumerate(s):
        counts[c]+=1
        while counts[c]>1:
            counts[s[left]]-=1; left+=1
        best=max(best,right-left+1)
    return best
```

- `counts=Counter(); left=best=0`：counts 是空频次表；left 是窗口左端；best 记录历史最长长度，初始 0（空串答案就是 0）。
- `for right,c in enumerate(s)`：right 从 0 走到末尾，c 是当前读入的字符。
- `counts[c]+=1`：新字符进窗口，先记账。
- `while counts[c]>1:`：刚进来的 c 出现了两次，窗口非法。注意这里只检查 c 一个字符就够了，因为除了 c 之外的字符在上一轮结束时都没重复。
- `counts[s[left]]-=1; left+=1`：把左端字符移出窗口并右移 left，一行干两件事，循环直到 c 不再重复。
- `best=max(best,right-left+1)`：此时窗口是"以 right 结尾的最长合法子串"，拿它的长度更新答案。

再看 `min_window`，逐字照抄如下：

```python
def min_window(s,t):
    if not t: return ''
    need=Counter(t); missing=len(t); left=0; best=None
    for right,c in enumerate(s):
        if need[c]>0: missing-=1
        need[c]-=1
        while missing==0:
            if best is None or right-left+1<best[1]-best[0]: best=(left,right+1)
            old=s[left]; need[old]+=1; left+=1
            if need[old]>0: missing+=1
    return '' if best is None else s[best[0]:best[1]]
```

- `if not t: return ''`：目标串为空串时直接返回空串，挡住无意义的输入。
- `need=Counter(t); missing=len(t)`：need 记录每个字符还"欠"几个；missing 是欠账总数。注意 `Counter` 查不存在的 key 会返回 0 而不报错，所以后面 `need[c]` 对 s 特有的字符也能安全访问。
- `if need[c]>0: missing-=1`：如果 c 正好是还欠着的字符，这笔进账能抵一元欠款。
  - 注意判断条件是 `need[c]>0` 而不是 `need[c]`：need[c] 可能是 0（刚好够）或负数（多余），这两种情况下进一个 c 都不能减少 missing。
- `need[c]-=1`：不管是不是欠着的字符都记一笔。对 s 特有的字符，need[c] 会从 0 变 -1，表示"多余一个"。
  - 这一行和上一行顺序不能换：必须先判断"进来的这个 c 能不能抵欠款"，再统一减一。
- `while missing==0:`：欠款还清，窗口合法。进入"边收缩边记录"的循环。
- `if best is None or right-left+1<best[1]-best[0]: best=(left,right+1)`：当前窗口比历史最短更短时，只记录下标对 `(left, right+1)`，注意右端存的是开区间端点 right+1，方便切片。第一次找到合法窗口时 best 还是 None，所以有 `best is None` 这个分支。
- `old=s[left]; need[old]+=1; left+=1`：把左端字符移出、记账、左移。如果移出后 `need[old]>0`，说明我们把一个必需字符丢掉了，欠款重新出现。
- `if need[old]>0: missing+=1`：欠款加一，下一轮 `while missing==0` 条件不成立，自然退出收缩。
- `return '' if best is None else s[best[0]:best[1]]`：从头到尾都没盖住过 t 就返回空串，否则按记录的下标切片返回。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么对（问题 A）**：right 每走一步，我们都在违反时把 left 推到"恰好不再违反"的位置。这样每轮结束时的窗口，就是"以这个 right 结尾的所有合法子串里最长的那个"。每个可能的右端点我们都考察过它的最优左端点，所以全局最大值不会漏。另外 left 和 right 都只前进不后退，所以窗口移动总量有上限，循环一定会停。

**为什么对（问题 B）**：对每个 right，只要窗口合法我们就不断左移 left 并逐个记录，等于把"以这个 right 结尾的所有能盖住 t 的左端位置"全部试了一遍，留下了最短的。合法性用 missing 一个整数维护，判断是 O(1) 的。反过来，当 missing>0 时我们不收缩，也不会漏掉候选——因为窗口不够盖住 t 时再收缩只会更盖不住。

**复杂度**：两个函数里，right 走了 |s| 步；left 全程也最多走 |s| 步（它从不回头），所以虽然有两层循环，总操作次数还是把每个字符"进窗一次、出窗一次"，加起来约 2|s| 次，也就是 O(|s|+|t|)。举个具体数字：s 长度十万时，大约二十万次基本操作，一瞬间就算完；如果暴力枚举所有子串再逐个检查，是十万平方量级（百亿次），根本跑不完。空间上只开了字符频次表，大小由字符集决定（比如全是小写字母就最多 26 项），记作 O(σ)。

## 六、测试用例在测什么

cell8 的断言逐条解释：

- `assert length_of_longest_substring('abcabcbb')==3`：正常值测试。LeetCode 3 的样例，答案 `'abc'` 长 3，验证主逻辑没跑偏。
- `assert length_of_longest_substring('')==0`：边界值测试。空串一个字符都没有，best 从 0 出发从未被更新，答案应为 0，挡住"空输入返回垃圾值"的实现。
- `assert min_window('ADOBECODEBANC','ABC')=='BANC'`：正常值测试。LeetCode 76 的样例，覆盖了"找到第一个合法窗口后还要继续扫描、后面出现更短答案"的完整流程。
- `assert min_window('a','aa')==''`：特殊值测试。t 需要**两个** a 而 s 只有一个，考察你是否正确处理目标里的重复字符——如果实现只看字符种类（用 set），这里就会错误地返回 `'a'`。
- 后面的大循环：用 `itertools.product` 枚举长度 0~5 的全部 `ab` 二进制串（共 2^0+...+2^5=63 个），对每个串和四种目标 t（`'a','ab','aa','bba'`），用暴力枚举所有子串算出参考答案，再和本章实现对拍。拆开看：
  - `ref=max((r-l for l in range(n+1) for r in range(l,n+1) if len(set(s[l:r]))==r-l),default=0)`：暴力求最长无重复——枚举所有子串，`len(set(...))==r-l` 表示"子串长度等于不同字符数"，即无重复；`default=0` 处理连空串都枚举不到合法解的情况（n=0）。
  - `candidates=[s[l:r] for ... if not (Counter(t)-Counter(s[l:r]))]`：暴力找覆盖子串。`Counter(t)-Counter(win)` 是"t 比窗口多出来的部分"，结果为空（假值取反为真）表示窗口盖住了 t。
  - `expected=min(candidates,key=len) if candidates else ''`：最短覆盖的参考答案；一个都没有就是空串。
  - `assert len(ans)==len(expected)` 只比长度不比内容：因为同样最短的可能有多个，比内容会误杀正确实现；后面 `if ans: assert not (Counter(t)-Counter(ans))` 再单独确认返回的串确实覆盖 t。
  - 四种 t 里特意放了 `'aa'` 和 `'bba'`，都是带重复字符的目标，保证"按个数记账"这个点被反复测到。

## 七、练习思路提示

- **练习 1（构造只用集合无法处理重复目标字符的反例）**：提示：让 t 含有同一个字符两次，而 s 里这个字符的两个出现位置隔得很开。比如 `t='aa'`、`s='ab_a...'`。你先手算正确答案（必须包含两个 a 的最短子串），再说明"只统计字符种类的集合版"为什么会返回一个只含一个 a 的错误窗口。验证时可以写三行暴力：枚举 s 的所有子串，用 `Counter(t)-Counter(win)` 判断覆盖，取最短。
- **练习 2（解释非负和窗口的适用条件）**：提示：想象约束从"无重复"换成"窗口内数字之和不超过 target"。如果数组全是非负数，窗口变长和只会变大或不变，所以违反后不断移出左端一定能让和降回限额以内——这就是收缩能停下来的保证。然后想一个带负数的输入，比如 `[5, -10, 5]`、target 取某个值，手算演示"移出左端后和反而变大/缩小左端跳过了更优解"的现象，说明单调性断了这套逻辑就失效。

## 八、对应 LeetCode 题目

- **3. Longest Substring Without Repeating Characters**：这题就是本章的 `length_of_longest_substring` 本体，练的是"频次表 + 重复即收缩"的最长窗口套路。
- **76. Minimum Window Substring**：这题就是本章的 `min_window` 本体，练的是"missing 计数 + 满足即收缩取最短"的反向窗口，以及目标含重复字符时必须按个数记账。
