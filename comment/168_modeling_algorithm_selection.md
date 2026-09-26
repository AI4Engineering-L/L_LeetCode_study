# N168 · 约束建模与算法选择训练 —— 说人话详解

> 对应 notebook：`notebooks/21_mastery/168_modeling_algorithm_selection.ipynb`

## 一、这章要解决什么问题？（问题描述）

同一道题——"找出和至少为 target 的**最短**连续子数组长度，无解返回 -1"——在两个不同的输入约束下有两个完全不同的正确解法。这一章的目标不是学一个新算法，而是练"看到约束、提出候选、验证前提"的建模能力（不看题目标签猜解法）。

**版本 A（元素非负）**：输入 `nums=[2,3,1,2,4,3]`、`target=7`，输出 2，因为子数组 `[4,3]` 的和恰好 7 且长度最短。这个版本用普通滑动窗口就能解。

**版本 B（元素可负）**：输入 `nums=[1,-1,3]`、`target=3`，输出 1，因为最后一个元素 `[3]` 自己就够 3。把中间的 `-1` 包进来反而要 3 个元素。这个版本滑动窗口**会算错**——notebook 实测朴素窗口在它身上给出 3（错误），正确答案是 1。这题需要前缀和 + 单调双端队列。

一句话点题（cell1 原话的意思）：同一个问题，删掉"非负"这个约束就改变了解法。为什么？因为非负数保证了"窗口右扩只会让和变大、左缩只会让和变小"这条单调性，滑动窗口的单向排除全靠它；有负数时这条单调性断了，必须换模型。

## 二、关键概念（定义）

- **滑动窗口**：左右指针 left/right 夹住一段连续区间，right 一步步右移扩张，必要时 left 右移收缩。它成立的前提是"区间和有单调性"——扩张不减少、收缩不增大，这样才能放心地"排除"一批不可能的答案。
- **前缀和（prefix sum）**：`prefix[j] = nums[0..j-1]` 的和，`prefix[0]=0`。任意区间和 `nums[i..j-1] = prefix[j]-prefix[i]`。它把"区间和问题"改写成"两个前缀值之差"，是处理负数的标准换模型手法。
- **单调双端队列（monotonic deque）**：一个下标队列，保持对应的前缀值从队头到队尾严格递增。两头都能弹：队尾弹掉"被支配的候选"，队头弹掉"已经用过的起点"。O(n) 的关键就是每个下标至多进出各一次。
- **支配关系（dominance）**：如果较新的下标 i 的前缀值不比老下标 k 的更大（`prefix[k] >= prefix[i]` 且 k 更老），那么 i 是更好的起点——它离终点更近（区间更短）且 `prefix[j]-prefix[i]` 更容易达标。于是老候选 k 被 i 支配，永远用不到，直接从队尾删掉。这就是 cell1 说的"旧候选被支配"。
- **前提（precondition）与适用域**：每个算法都有它成立的前提，比如普通窗口要求"全部元素非负、target 为正"。`compare_candidates` 里对不满足前提的方法明确写 `'inapplicable: negative element'` 而不是偷偷换方法兜底——发现前提不满足时应当**暴露**，而不是掩盖。
- **候选排除**：建模时按"目标类型（最短区间）、数据性质（有没有负数）、约束（连续子数组）"逐项筛掉不适用的候选，而不是靠题目关键词套模板。
- **暴力对照（brute force）**：枚举所有 O(n²) 个区间的和取最短。它只用于小规模核验（cell8 用它当标准答案），因为大规模跑不动。

## 三、解决思路（一步步推导）

**Step 1：非负版——滑动窗口"进 right、缩 left"。** 对每个 right，把 `nums[right]` 加进窗口和 `total`；只要 `total>=target` 就记录窗口长度并从左边吐出一个元素（吐完可能还够，继续吐）。为什么敢吐？因为元素非负，左边元素留着只会让窗口更长，不可能换来更短的最优解。

**Step 2：手算非负版 `[2,3,1,2,4,3]`, target=7。**

| right | total（进） | 收缩动作 | answer |
|---|---|---|---|
| 0 | 2 | 不够 | — |
| 1 | 5 | 不够 | — |
| 2 | 6 | 不够 | — |
| 3 | 8 | 记 4；吐 2 → 6，停 | 4 |
| 4 | 10 | 记 4；吐 3 → 7；吐 1 → 6，停 | 3 |
| 5 | 9 | 记 3；吐 2 → 7；吐 4 → 3，停 | 2 |

最终 answer=2，对应窗口 `[4,3]`。

**Step 3：有负数时同一套逻辑怎么错。** 跑 `[1,-1,3]`, target=7 换成 3：right=2 时 total=3 达标，记长度 3；吐掉 1 之后 total=2 不够了，停——它**永远不知道**`[3]` 这位更短的候选，因为"吐掉左边"在有负数时可能让和变大（这里吐 -1 会从 2 变 3），单调性没了。cell8 实测这个错误版本返回 3，而暴力给出 1。

**Step 4：有负数版——前缀和改写目标。** 求"最小 j-i 使 `P[j]-P[i]>=target`"。固定 j 时，要找的是"最靠右的 i 且 P[i] 足够小"。对 `[1,-1,3]`：`prefix=[0,1,0,3]`。`prefix[3]-prefix[2]=3-0=3>=3`，所以答案 `3-2=1`——起点 2 的前缀值 0 比 起点 0 的 0 一样小但更近，起点 0 被支配。

**Step 5：单调队列维护"没被支配的起点"。** 从左到右扫 j，队列存候选起点下标，保持前缀值递增。两头各弹一次：队头——只要 `current-prefix[队头]>=target`，这个起点对当前 j 已经达标，记录长度后弹掉（以后 j 更大只会更长，它不会再更优）；队尾——只要 `prefix[队尾]>=current`，队尾被 current 支配（更老且不更小），弹掉。

**Step 6：手算单调队列版 `[1,-1,3]`, target=3。**

| j | prefix[j] | 弹队头 | 弹队尾 | 入队后队列 | answer |
|---|---|---|---|---|---|
| 0 | 0 | — | — | [0] | — |
| 1 | 1 | 1-0=1<3 不弹 | 队尾 P[0]=0 < 1 不弹 | [0,1] | — |
| 2 | 0 | 0-0=0<3 不弹 | P[1]=1≥0 弹 1；P[0]=0≥0 弹 0 | [2] | — |
| 3 | 3 | 3-P[2]=3≥3：记 3-2=1，弹 2 | 空 | [3] | 1 |

最终 answer=1，对应区间 `[3]`。和第三节的错误结果 3 对比，正是本章想让你看见的差异。

**Step 7：比较表。** `compare_candidates` 对每个用例成对输出两个方法的结果，非负前提不满足时标 `'inapplicable: negative element'`。cell6 的表格四行：`([2,3,1,2,4,3],7)→(2,2)`、`([1,-1,3],3)→(inapplicable, 1)`、`([0,0,1],2)→(-1,-1)`（总和才 1，无解）、`([],1)→(-1,-1)`（空数组边界）。

## 四、代码逐段讲解

cell3 是纯 Python，三个函数。

**solve_min_length_positive（非负滑动窗口）：**

```python
def solve_min_length_positive(nums, target):
    """Nonnegative values, positive target; return -1 when no nonempty window works."""
    if target <= 0 or any(x < 0 for x in nums):
        raise ValueError('Requires nonnegative elements and positive target')
    left = total = 0
    answer = len(nums)+1
    for right,value in enumerate(nums):
        total += value
        while total >= target:
            answer = min(answer,right-left+1)
            total -= nums[left]
            left += 1
    return -1 if answer > len(nums) else answer
```

第一段是前提的代码化：target 非正或数组含负数就直接 ValueError——这个方法**拒绝**在适用域外工作。`answer` 初始化成 `len(nums)+1`（哨兵，比任何合法长度都大）。循环里 right 每进一个元素就加进 total；内层 while 在"达标"时记下当前窗口长度并从左边吐元素——注意顺序是"先记录再吐"，所以每个达标窗口都会被看到。最后哨兵没被更新就说明无解，返回 -1。docstring 也写明了契约。

**solve_min_length_signed（前缀和 + 单调队列）：**

```python
def solve_min_length_signed(nums, target):
    if target <= 0:
        raise ValueError('Positive target required')
    prefix = [0]
    for value in nums:
        prefix.append(prefix[-1]+value)
    candidates = deque()
    answer = len(nums)+1
    for right,current in enumerate(prefix):
        while candidates and current-prefix[candidates[0]] >= target:
            answer = min(answer,right-candidates.popleft())
        while candidates and prefix[candidates[-1]] >= current:
            candidates.pop()
        candidates.append(right)
    return -1 if answer > len(nums) else answer
```

这版只要求 target 为正（元素可负）。先建前缀数组：`prefix[0]=0`，之后每个前值加当前元素。`candidates` 是单调双端队列，存的是下标。主循环遍历每个 right（含 j=0 的空前缀）：第一个 while 处理队头——若当前前缀减队头前缀已达标，队头这个起点的最短终点就是当前 right（再往后只会更长），记录长度后弹掉，能连续弹就连续弹；第二个 while 处理队尾——前缀值不小于当前值的旧候选都被当前支配，弹掉；最后把 right 入队。两个 while 保证每个下标至多进出队列各一次，这就是 O(n) 的来源。

**compare_candidates（对照表）：**

```python
def compare_candidates(cases):
    rows = []
    for nums,target in cases:
        positive_result = solve_min_length_positive(nums,target) if all(x>=0 for x in nums) else 'inapplicable: negative element'
        rows.append((nums,target,positive_result,solve_min_length_signed(nums,target)))
    return rows
```

对每个用例先判"全非负"：满足才调窗口版，否则明确写上"因含负元素不适用"；signed 版总是可以跑。返回的四元组行直接喂给 cell6 的 `show_table`，生成第三节 Step 7 里那张四行比较表。注意它的立场：不适用就标记，不自动改用强方法"兜底"——那是掩盖建模错误。

## 五、为什么是对的？复杂度是多少？（说人话）

**非负窗口的正确性**依赖单调性：因为元素非负，right 扩张不会让和变少、left 收缩不会让和变大；所以当某个 left 对当前 right 已达标时，更右的 right 对这个 left 也达标但窗口更长，left 可以安全吐掉、永不回头。**signed 版的正确性**分两头说：队尾删除依据支配关系——被弹的旧起点"更老且前缀值不小"，任何未来终点对它达标的话对新起点更达标且区间更短，它不可能再成为最优；队头删除依据"该起点的最短终点已经找到"——终点只会越来越远，以后再配对只会更长。两者合起来，队列里始终留着真正有希望的候选。**负数反例**（`[1,-1,3]`）的存在直接证明了"非负"前提不能删，删了推导就断——这是 cell4 说的"负数反例否定该前提缺失时的推导"。

**复杂度**：普通窗口每个元素最多进一次出一次，时间 O(n)，额外空间 O(1)（就 left、total、answer 三个变量）；signed 版每个下标至多入队、出队各一次，时间 O(n)，前缀数组加队列空间 O(n)。放到具体规模上感受：n=10^5 时两个 O(n) 解法都在几十万次基本操作量级、毫秒级跑完；O(n²) 的暴力要百亿量级，必然超时；signed 版多花的 O(n) 空间对 10^5 只是几十万个整数，通常完全可接受。暴力对照是 O(n²) 起步的（还要每次求和），只配在小规模上当裁判。

**一个容易忽略的不变量**：signed 版的队列任意时刻保持"前缀值从队头到队尾严格递增"。你可以拿第三节的表格核对——每次入队前队尾的清理正是为了维持它；有了这条不变量，"队头是最有希望的起点（前缀最小、下标最小）"才永远成立。

## 六、测试用例在测什么

cell8 的测试分四块：

- **穷举对照**：`for n in range(6)` 配 `itertools.product([-1,0,2],repeat=n)`——把长度 0 到 5、元素取值 {-1,0,2} 的所有数组全部枚举（共 1+3+9+27+81+243=364 个），对每个再试 target 1、2、3、5。断言 signed 版永远等于暴力 `brute` 的结果；元素全非负时窗口版也必须等于暴力。这是"对拍"式验证：小规模全覆盖，两个独立实现一致。
- **定点用例**：`solve_min_length_signed([1,-1,3],3)==1`——本章的核心反例，答案 1（区间 `[3]`）。
- **前提检查**：`solve_min_length_positive([1,-1,3],3)` 必须抛 ValueError——含负数还硬跑才是 bug，抛错是契约的正确执行（`try/except/else` 的写法：没抛反而要 AssertionError）。
- **错误版本的暴露**：测试里故意再定义一个 `invalid_plain_window`（就是把窗口逻辑抄到含负数上跑），断言它在 `[1,-1,3],3` 上返回 3、而暴力返回 1——用实测数字展示"前提不满足时方法给出错误答案而非报错"的后果，这正是"比较表要标 inapplicable"的理由。

## 七、练习思路提示

**练习 1（去掉题目标签重新建模）**：提示：拿几道你做过的题，把标题和标签遮住，只看输入输出和约束，按清单过一遍——目标是最优化还是判定？数据是静态还是动态、有没有负数/有序性/值域限制？要求的结构是子数组、子序列还是区间集合？每回答一项就划掉一批候选（比如"要最短、元素可负"就划掉普通窗口，留下前缀和系）。然后反着验证：给自己的每个候选写一句"它依赖的前提"，找一个小例子手算确认。本章的两个 solve 函数就是这条流水线的成品，可以对照。

**练习 2（写出每种候选算法必须成立的前提）**：提示：至少覆盖本章出场的三类——普通滑动窗口（元素非负/有序可排除、target 为正、求连续区间）、前缀和+单调队列（区间和可加分解、目标可用两前缀之差表达）、暴力枚举（无前提但 O(n²) 只配核验）。对每条前提配一个"删掉它就出错"的具体反例——`[1,-1,3]` 就是窗口版的现成反例，另外想想：target=0 时窗口版为什么直接拒绝？（长度 1 的任何非负元素都满足 `>=0`，"最短"退化得没有意义，所以契约上要求正 target。）写成"前提 → 反例"对照表，验证时可跑本章接口。

## 八、对应 LeetCode 题目

- **209. Minimum Size Subarray Sum（canonical）**：元素非负版的"和至少为 target 的最短子数组"，练的就是 `solve_min_length_positive` 的滑动窗口与它的单调性前提。
- **862. Shortest Subarray with Sum at Least K（comparison）**：元素可负的同题异构，练的是 `solve_min_length_signed` 的前缀和 + 单调双端队列与支配关系删除。
- **300. Longest Increasing Subsequence（comparison）**：目标是"最长"而非"最短"、结构是子序列而非子数组，但它同样用"维护未被支配候选"的思路（贪心+二分的递增尾巴数组），用来对照体会"目标类型和数据性质如何决定候选结构"。

**迁移心法（本章的真收获）**：拿到题先别想"这题是滑动窗口模板题吗"，而是按顺序问三句——目标是什么类型（最短/最长/计数/判定）？数据有什么性质（非负？有序？值域）？结构有什么约束（连续/不连续/至多 k 次）？三句答完，候选自然收敛，再逐条核对每个候选的前提，找不到反例才动手写。`compare_candidates` 那个"inapplicable"标记就是这套流程落地后的样子：明确说"这个方法在这儿不适用"，比默默给一个错答案诚实得多。

如果你想自测是否真的掌握了，最简单的办法是：遮住 notebook 的 cell1 推导，只看 `solve_min_length_signed` 的代码，口头复述"队头为什么敢弹、队尾为什么敢弹、为什么每个下标只进出一次"这三问；三问都能对着第三节的表格说清楚，这一章就算过关了。
