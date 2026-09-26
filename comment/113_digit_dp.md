# N113 · 数位DP、上界与前导零 —— 说人话详解

> 对应 notebook：`notebooks/13_dynamic_programming/113_digit_dp.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章处理的是一类"数数字"问题：给你一个可能非常大的整数 n（比如 10^9 这个量级），让你统计 1 到 n 之间有多少个数满足某种"按位"的限制。本章实现了三个具体问题：

1. 有多少个正整数 ≤ n，且每一位数字互不相同（例如 135 合法，11 和 121 非法）；
2. 把 1 到 n 全部写下来，数字字符"1"一共出现了多少次；
3. 有多少个正整数 ≤ n，且每一位都来自给定的小集合（例如只允许 {0,1,3}，那么 103 合法、102 非法）。

**为什么不能暴力？** 如果 n 是 10^9，你就要循环十亿次，每次还要检查每一位，Python 跑几分钟都算不完。数位DP 的思路是：不再一个数一个数地数，而是"一位一位地填"，把拥有相同填法前途的状态合并起来一起数。

**给一个具体到数字的例子（输入 → 输出 → 为什么）：** 取 n=20，问互异数字正整数有多少个，答案是 19。原因是：1~9 这 9 个一位数全都合法；10~20 之间，10、12、13、…、19、20 这 10 个合法（只有 11 因为两个 1 重复被排除）；9+10=19。下面的推导我们会用代码把这个 19 一格一格算出来。

## 二、关键概念（定义）

- **数位DP（digit DP）：** 一种特殊的动态规划。普通 DP 按"阶段"推进，数位 DP 按"十进制的第几位"推进，从最高位往最低位填数字，边填边维护约束。
- **tight（顶到上界）：** 表示"前几位填的数字和上界 n 的前几位一模一样"，这一位 therefore 只能填到上界当前位为止；一旦某一位填了比上界小的数，后面的位就自由了（0~9 随便填）。它解决"不能超过 n"这个限制。
- **started（已经开始填真正的数字）：** 区分"还没开始的前导零"和"真正的数字 0"。比如数 20 时，那个 0 是真数字；而把 5 写成 "05" 时，前面的 0 只是占位符。前导零不算数字、不参与查重。
- **digit mask（已用数字的位掩码）：** 一个 10 位二进制数，第 d 位是 1 就表示数字 d 已经用过。比如用过 1 再用 3，mask 就是 `0000001010`（第 1 位和第 3 位是 1）。它用来查"每一位互不相同"。notebook 里打印的 `[(1, '0000000010'), (2, '0000000100'), (3, '0000001000'), (4, '0000010000')]` 就是 `1<<d` 的样子。
- **记忆化（memoization，这里用 `@cache`）：** 把算过的状态答案存起来，下次遇到完全相同的状态直接查表返回，不再重算。
- **区间差分：** 想数 [L,R] 区间内的个数，就先数"≤R 的个数"再减去"≤L−1 的个数"。所以本章所有函数都只实现"≤n"版本。
- **0 是否计入：** 全程只填前导零、一个真数字都没填的路径，对应的是"空"或 0，不是正整数，所以最后一位填完时要把它排除掉（`int(started)`）。

## 三、解决思路（一步步推导）

我们以 `count_special_numbers(20)` 为例，一步步手算。先把 20 拆成数字列表 `digits=[2,0]`，然后从第 0 位（十位）开始填。

- **Step 1：** 把 n 转成数字列表，后面所有比较都按位进行，这样 n 多大都不怕，长度只是位数 D。
- **Step 2：** 从最高位开始，逐位枚举这一位填什么数字 d。能填的上限由 tight 决定：还贴着上界就最多填到 `digits[i]`，一旦自由了就能填到 9。
- **Step 3：** 更新 tight。如果"原来是贴着的，而且这一位填的正好等于上界这一位"，那么下一位仍然贴着；否则下一位自由。这样保证拼出来的数永远 ≤ n。
- **Step 4：** 处理前导零。如果还没 started 且填的是 0，那这个 0 是占位符：mask 不变、started 保持 False，直接进入下一位。
- **Step 5：** 真正填了数字（d>0，或者已 started 后填 0），检查 mask 里这个数字用过没有，没用过就把 mask 的第 d 位点亮，started 变 True。
- **Step 6：** 填完所有位（i 走到尽头）时，只有 started 为 True 才算数出一个正整数，返回 1；否则返回 0。
- **Step 7：** 记忆化。状态 (i, mask, tight, started) 相同的子问题答案必然相同，用 `@cache` 存起来。

**手算 `count_special_numbers(20)`（digits=[2,0]）：**

- 第 0 位，贴着上界（tight=True），limit=2，d 可以试 0、1、2：
  - d=0：还没开始且填 0 → 是前导零。进入第 1 位，tight 变成 False（0≠2，已经自由）。第 1 位 limit=9：填 0 仍算空（最终 0 个）；填 1~9 各出一个一位数。这一支共 **9 个**（就是 1~9 在两位框架里的表达）。
  - d=1：开始真填，mask=0b10，tight 变 False（1<2）。第 1 位 limit=9，但 1 已用过：可填 0、2、3、…、9，共 **9 个**（10、12、…、19，11 被排除）。
  - d=2：mask=0b100，tight 保持 True（2==2）。第 1 位 limit=0，只能填 0，且 0 没用过 → **1 个**（就是 20）。
- 合计 9+9+1=**19**，和函数返回值一致。

**再手算 `count_digit_one(13)`：** 把 0~13 都写成两位（补前导零）：00,01,…,13。个位上出现 1 的是 01、11 共 2 次；十位上出现 1 的是 10、11、12、13 共 4 次；前导零不贡献任何 1。总共 2+4=**6**，这就是函数的答案。

notebook 第 6 格还生成了一张对照表（上界 0、9、20、99、135），对应结果：互异数字个数 0、9、19、90、110；数字 1 出现次数 0、1、12、20、70；仅用 {0,1,3} 构成的个数 0、2、5、8、17。你可以用同样的逐位方法抽查其中任意一格，比如 99 的互异数 = 9 个一位数 + 81 个两位互异数 = 90。

## 四、代码逐段讲解

### 4.1 `count_special_numbers(n)`：数"每位互异"的正整数

```python
from functools import cache

def count_special_numbers(n):
    if n<=0: return 0
    digits=list(map(int,str(n)))
    @cache
    def f(i,mask,tight,started):
        if i==len(digits): return int(started)
        limit=digits[i] if tight else 9; total=0
        for d in range(limit+1):
            new_tight=tight and d==digits[i]
            if not started and d==0: total+=f(i+1,mask,new_tight,False)
            elif not mask>>d&1: total+=f(i+1,mask|1<<d,new_tight,True)
        return total
    return f(0,0,True,False)
```

- `if n<=0: return 0`：挡住 0 和负数——1 到 0（或负数）之间没有任何正整数，直接返回 0，避免 `str(n)` 对负数带出负号。
- `digits=list(map(int,str(n)))`：把 20 变成 `[2,0]`，之后只按位比较。
- `@cache`：记忆化装饰器，自动以 (i,mask,tight,started) 为 key 缓存，相同的子问题只算一次。
- `if i==len(digits): return int(started)`：所有位填完了。`int(started)` 把布尔转成 1/0：填过真数字才算一个正整数，全程前导零（对应空数/0）不计入。
- `limit=digits[i] if tight else 9`：紧凑的条件表达式——贴着上界时这一位最多填到上界的数字，否则可以填到 9。
- `new_tight=tight and d==digits[i]`：只有"原来贴着且这一位恰好又贴着"才继续贴；任何一步松开就永远松开。
- `if not started and d==0:` 这一支是前导零：mask 不变（0 不占用），started 保持 False。
- `elif not mask>>d&1:` 把 mask 右移 d 位再取最低位，检查数字 d 是否用过；没用过就 `mask|1<<d` 点亮第 d 位，started 置 True。
- `return f(0,0,True,False)`：初始状态——第 0 位、空 mask、贴着上界、尚未开始。

### 4.2 `count_digit_one(n)`：数数字 1 出现的总次数

```python
def count_digit_one(n):
    if n<=0: return 0
    digits=list(map(int,str(n)))
    @cache
    def f(i,tight):
        if i==len(digits): return 1,0
        count=ones=0
        for d in range((digits[i] if tight else 9)+1):
            ways,tail_ones=f(i+1,tight and d==digits[i]); count+=ways; ones+=tail_ones+(d==1)*ways
        return count,ones
    return f(0,True)[1]
```

- 这个函数返回的是**二元组** `(count, ones)`：从第 i 位往后能拼出的数的"个数"，以及这些数里数字 1 出现的"总次数"。最后 `f(0,True)[1]` 只取第二个分量。
- 它没有 started/mask：这里把所有数都当成定长 D 位（允许前导零）来拼，因为前导零不会变出"1"，所以统计结果不受影响。
- 基例 `return 1,0`：空后缀有 1 种拼法，含 0 个 1。
- `ones+=tail_ones+(d==1)*ways` 是核心：`tail_ones` 是后缀里已有的 1；如果当前位填的是 1，那么**每一种**后缀都会让总次数多 1，所以再加 `(d==1)*ways`（布尔当 0/1 用，乘法展开就是"是 1 加 ways，否则加 0"）。

### 4.3 `count_from_digit_set(digits,n)`：只用给定集合里的数字

```python
def count_from_digit_set(digits,n):
    if n<=0: return 0
    allowed={int(d) for d in digits}
    if not allowed<=set(range(10)): raise ValueError('single decimal digits required')
    bound=list(map(int,str(n)))
    @cache
    def f(i,tight,started):
        if i==len(bound): return int(started)
        limit=bound[i] if tight else 9; total=0
        if not started: total+=f(i+1,tight and bound[i]==0,False)
        for d in sorted(allowed):
            if d>limit or not started and d==0: continue
            total+=f(i+1,tight and d==bound[i],True)
        return total
    return f(0,True,False)
```

- `allowed={int(d) for d in digits}`：把字符串集合转成整数集合；`if not allowed<=set(range(10))` 校验输入必须是 0~9 的单个数字，传别的字符直接抛 `ValueError`，不悄悄给错答案。
- `if not started: total+=f(i+1,tight and bound[i]==0,False)`：这一行处理"继续填前导零"。注意前导零**不需要**属于 allowed；而 tight 的更新条件是 `bound[i]==0`——只有上界这一位本来就是 0，填 0 才继续贴着上界（比如上界是 105，你在第 0 位填 0 会立刻小于 1，就自由了）。
- `for d in sorted(allowed)`：按固定顺序遍历集合（sorted 只是让遍历顺序确定）。
- `if d>limit or not started and d==0: continue`：跳过超过当前上限的数字；也跳过"还没开始时的 0"（0 不能当首位真数字，前导零已由上面单独那行处理）。一旦 started 为 True，集合里的 0 就是普通数字，比如 10、30、103 都合法。
- 末态 `int(started)` 同样排除"全前导零"的路径。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么缓存是对的：** 只要"填到第几位、用过哪些数字、是否还贴着上界、是否已开始"这四件事完全一样，那么从这个状态出发，后面还能填什么、受什么限制、最终能数出多少个数，就完全一样。换句话说，未来只由状态决定，与前面具体填了哪些数无关，所以同一个状态算一次就够了。

**为什么前导零要单独处理：** 前导零是占位符，不是数的一部分，所以它不占用 mask（第 4.1 节里 `d==0` 那支 mask 原样传下去），也不要求属于允许集合（4.3 节）。一旦 started 为 True，再填的 0 就是真数字，必须查重、必须属于集合。而如果整条路径从头到尾都是前导零，说明一个有效数字都没填，它不代表任何正整数，所以末态用 `int(started)` 把它排除——这就是"0 不计入"。

**为什么数 1 的递推是对的：** 总次数拆成两块相加：一块是后缀自己已经贡献的 1（`tail_ones`）；另一块是"当前这一位填了 1"带来的新增——当前位每和一种后缀组合一次，就多出现一个 1，所以新增恰好是后缀种数 `ways`。两块加起来正好不丢不重。

**复杂度（用具体数字感受一下）：** 设 D 是 n 的十进制位数。互异数字版的状态是"位置 D × mask 2^10 × tight 2 × started 2"，每个状态转移最多试 10 个数字，所以大约是 O(D·2^10·10) 次操作。n 取 10^9 时 D=10，10×1024×10 ≈ 十万次基本操作，一瞬间就算完；对比暴力循环的十亿次，快了四个数量级还不止。数 1 版状态只有"位置 × tight"，是 O(D·10)：n=10^9 时也就两百次左右的转移。集合版是 O(D·|集合|)。缓存占的空间就是各自的状态数，互异版最多约 D·1024·4 个条目，对教学题的整数位数完全没压力。需要注意：这套写法假定了常规题目规模的位数，如果数字长到几万位，递归深度会先出问题，要改成迭代写法。

## 六、测试用例在测什么

```python
assert count_special_numbers(20)==19 and count_special_numbers(135)==110
assert count_digit_one(13)==6
assert count_special_numbers(0)==count_digit_one(0)==count_from_digit_set(['0'],20)==0
for n in range(251):
    ...
print('N113: 所有本章断言通过')
```

- 第 1 条：两个"已知答案值"的抽查。20→19 我们在第三节手算过；135→110 可以拆开验证：9 个一位数 + 81 个两位互异数 + 三位数里 1bc≤135 的互异组合 20 个（b=0 时 c 取 2~9 共 8 个；b=2 时 120~129 里去掉 121、122 共 8 个；b=3 时 c≤5 且 c∉{1,3}，即 130、132、134、135 共 4 个）→ 9+81+20=110。
- 第 2 条：`count_digit_one(13)==6` 是小输入的正常值检查：1、10、11（两个 1）、12、13，共 6 次，对应第三节的按位手算。
- 第 3 条：三个边界一起测。n=0 时三个函数都该返回 0（没有正整数 ≤ 0）；集合只有 {'0'} 时也返回 0，因为"只由 0 构成的正整数"根本不存在——0 自己不算正整数，这条专门盯住"0 是否计入"的末态逻辑。
- 第 4 条循环：对 0~250 的每个 n，用一行暴力真值交叉验证三个函数——`len(set(str(x)))==len(str(x))` 判每位互异；`str(x).count('1')` 直接数字符；`set(str(x))<=set(digits)` 判每位都在集合里。集合还换了对称的四种：空集、{'0','1'}、{'1','3','5'}、{'0','2','9'}，覆盖"不含 0""含 0""空集"等不同形态。250 以内都一致，说明实现和暴力契约吻合。

## 七、练习思路提示

- **练习 1（定长带前导零 vs 不定长整数计数）：** 提示——"长度恰为 L 的数字串"（允许 052 这种）和"不超过 L 位的正整数"是两个不同的计数对象。前者没有 started 的概念，每一位都是普通字符，0 也要在集合/查重里；后者才有前导零问题。建议先写清楚输入输出和边界（比如 L=0、空集合怎么办），给一个手算示例：用 {1,3} 组成长度恰为 3 的串有 2^3=8 个，而 ≤333 且由 {1,3} 构成的正整数有 2+4+8=14 个，两者明显不同。最后用暴力枚举字符串/整数对拍验证。
- **练习 2（区间 [L,R] 差分）：** 提示——本章函数都是"≤n"版，那么 [L,R] 内的个数就是 g(R)−g(L−1)。注意两个坑：L−1 可能是 0（函数返回 0，正好不需要特殊处理）；L=1 时下界减出来是 0 也对。手算示例：互异数字在 [10,20] 的个数 = g(20)−g(9) = 19−9 = 10，你可以逐个列出来核对（10,12,…,19,20）。

## 八、对应 LeetCode 题目

- **2376. Count Special Integers**：这题就是 `count_special_numbers` 的原题场景——统计 ≤n 且每一位数字互不相同的正整数个数，练的是 tight + started + mask 三件套的完整配合。
- **233. Number of Digit One**：这题是 `count_digit_one` 的原题场景——统计 1..n 中数字 1 出现的总次数，练的是"逐位统计贡献"：当前位是 1 时，新增次数等于后缀的种数。
- **902. Numbers At Most N Given Digit Set**：这题是 `count_from_digit_set` 的原题场景——给定数字集合，问能拼出多少个 ≤n 的正整数；原题集合不含 0，本章实现允许含 0，处理了更一般的情况（0 只能出现在非首位）。
