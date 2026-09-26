# N170 · 正确性证明与反例工作坊 —— 说人话详解

> 对应 notebook：`notebooks/21_mastery/170_proofs_and_counterexamples_workshop.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章的方法论解决的问题是：**你心里"觉得"一个贪心策略是对的，怎么把这个直觉变成一份别人能检查的完整论证？以及，当题目条件（前提）变了之后，怎么系统地找出旧论证失效的反例？** 核心工具是两个：一是让算法返回"证据"（witness），再用一个独立的验证器去检查这份证据；二是用小规模穷举去搜反例，专打"少了前提的推理"。

承载这套方法论的例题是"分段可行性判断"：给一个**非负**数组 `nums`、阈值 `limit` 和段数上限 `groups`，问能否把数组切成至多 `groups` 个连续段，使每段的和都不超过 `limit`。

具体到数字的小例子：`nums=[7,2,5,10,8]`，`limit=18`，`groups=2`。贪心策略是"每段尽量装满再切下一刀"：

- 第 1 段从 7 开始：7、+2=9、+5=14 都没超 18；再装 10 就是 24，超了，所以在下标 3 前切一刀。第 1 段是 `[7,2,5]`，和为 14。
- 第 2 段从 10 开始：10、+8=18，恰好压线没超。第 2 段是 `[10,8]`，和为 18。
- 一共切出 2 段（`cuts=[3,5]`），2 ≤ groups=2，所以答案是"可行"，并且函数把这组切点当证据交出来。

而"反例"那一半演示的是：一旦允许负数，"某个单元素超过阈值 ⇒ 整个问题无解"这条推理就破产了。比如 `nums=[-2,1]`、`limit=0`、`groups=1`：最大元素 1 > 0，旧推理会说无解；但整段 `[-2,1]` 的和是 -1 ≤ 0，一段就装下了，明明有解。这一章教你把这两种论证都写得可检查。

## 二、关键概念（定义）

- **见证 / 证据（witness）**：算法判定"可行"时不只返回 True，还返回具体方案（每段的右开端点 `cuts`）。我们需要它是因为"有具体方案"可以被人或程序独立复核，而一个光秃秃的 True 无法区分"真可行"和"算法算错了"。
- **验证器（witness validator）**：一个独立的小函数 `verify_witness_partition`，它不关心你怎么得到 `cuts`，只检查给定的分段是否覆盖全数组、是否非空有序、每段和是否超阈值。它是"证明与测试分工"里的裁判。
- **循环不变量**：循环每轮都保持成立的性质（比如贪心里"total 始终是当前段的和，且当前段不超过 limit"）。写证明时先说清不变量，循环结束时代入不变量就能得出结论。
- **交换论证（exchange argument）**：证明贪心最优的经典套路——假设存在一个别的合法解和贪心不同，就把它的某个选择"换成"贪心的选择，论证换完之后仍然合法、且目标不变差。反复交换即可把任意解改造成贪心解。
- **归纳**：把"对前 k 个元素成立"推广到"对前 k+1 个元素也成立"的推理方式；交换论证通常要配合归纳才能覆盖所有段。
- **终止性**：论证算法会停下来（循环变量每轮严格递增、递归规模严格变小），和正确性是两份独立的证明责任。
- **负例 / 反例（counterexample）**：一个具体输入，它满足"错误推理的输入域"却让结论不成立。反例的作用是反驳"缺少前提的推理"，精确标出旧结论的适用边界。
- **证明与测试分工**：证明负责"所有输入都对"，测试负责"抓实现 bug、守住回归"。测试通过不等于证明了正确性，两者互补。

## 三、解决思路（一步步推导）

我们把整章工作流按顺序展开，仍用 `nums=[7,2,5,10,8]`、`limit=18`、`groups=2`。

- **Step 1：写清主张和前提。** 主张是"非负数组上，贪心（当前段尽量长）给出的段数最少，因此用它判断可行性是对的"。前提有两条：数值非负、limit 非负。把前提写进函数的输入检查里（代码里 `raise ValueError` 的那三行）。
- **Step 2：让成功带回证据。** 判定成功时不返回裸 True，而是返回 `(True, cuts)`，其中 `cuts` 是每段的右开端点（不含端点本身），本例是 `[3,5]`。失败时返回 `(False, [])`——没有方案就没有证据。
- **Step 3：写独立验证器。** 验证器按同样口径检查 `cuts`：末尾必须恰好是 `len(nums)`（覆盖到头）；每个端点必须严格大于前一个（段非空）且不超过长度；每段 `sum(nums[previous:end])` 不得超过 `limit`。它**接受带负数的输入**，因为它只做算术比较、不做任何贪心推断，所以还能拿去验证反例里的分段。
- **Step 4：贪心逐元素扫一遍（手算）。** 从头累加：7→9→14→(24 超，切一刀，从 0 重新累加 10)→18。结束后补上终点 5，得到 `cuts=[3,5]`。这一步的循环不变量是"total 一直是当前已装入段的和且不超过 limit"。
- **Step 5：验证证据。** 把 `cuts=[3,5]` 喂给验证器：段 `[0,3)` 是 `[7,2,5]` 和 14 ≤ 18 ✓；段 `[3,5)` 是 `[10,8]` 和 18 ≤ 18 ✓；端点严格递增、终点对齐 ✓。验证器返回 True，主张"可行"就有了可检查的证据。
- **Step 6：交换论证补上"贪心最优"。** 假设另一个合法分段的第 1 刀比贪心更早，就把这把刀**右移**到贪心位置：前段变长但仍然合法（贪心本来就装得下），被移走的元素非负，所以后一段的和只会变小、负担不会增大。对每一把刀重复这个交换，任何合法解都能改造成贪心分段而不增加段数——所以贪心段数最少，用它对比 `groups` 判可行性是对的。
- **Step 7：撤掉前提，搜反例。** 允许负数后重审 Step 6：被移走的元素如果是负数，"右移不增加后段负担"就不再成立；同时"单元素超阈值 ⇒ 无解"也失效。用程序在长度 1–3、取值 -2..3、limit 0..3 的小空间里穷举，条件是"含负数、最大元素超过 limit、但总和不超过 limit"。第一个命中就是 `{'nums': [-2, 1], 'limit': 0, 'groups': 1, 'valid_cuts': [2]}`：一段装下全部、和为 -1 ≤ 0，验证器确认可行。
- **Step 8：守住生产函数的边界。** 反例只用来**反驳推理**，不拿含负数的数组去调用只承诺非负输入的 `feasible_partition` 再宣称"算法错了"——事实上它会对负数输入直接抛 `ValueError`。证明负责界定适用范围，测试负责守住这个范围，这就是"证明与测试分工"的落点。

cell6 的两张表对应 Step 5 和 Step 7：第一张表列出 `(start, exclusive end, segment, sum)` = `(0,3,[7,2,5],14)` 和 `(3,5,[10,8],18)`；第二张表把反例字典逐字段打出来，你可以直接读出"旧推理判断无解（False 的意思是那个主张不成立），但 `valid_cuts=[2]` 真实有解"。

把这套流程串成一句话：**主张要带前提、成功要带证据、证据要能被独立核验、前提被撤掉时用最小反例精确标出失效点**——这四件事合起来，就是"把直觉改写为完整论证"的完整操作手册。

## 四、代码逐段讲解

### 1. 贪心可行性 `feasible_partition`

```python
def feasible_partition(nums, limit, groups):
    """Nonnegative values; return (feasible, exclusive_end_cuts)."""
    if limit<0 or groups<1 or any(x<0 for x in nums):
        raise ValueError('Nonnegative values/limit and positive groups required')
    if not nums:return True,[]
    if max(nums)>limit:return False,[]
    cuts=[];total=0
    for i,value in enumerate(nums):
        if total+value>limit:
            cuts.append(i)
            total=0
        total+=value
    cuts.append(len(nums))
    return (True,cuts) if len(cuts)<=groups else (False,[])
```

- 文档字符串第一件事就是声明前提："Nonnegative values"——前提写进契约，而不是靠注释口头约定。
- 第一组 `if` 是前提检查：limit 非负、groups 至少 1、数组元素全部非负，违反就抛异常。这正对应第一节说的"含负数输入不属于本函数的适用域"。
- `if not nums:return True,[]`：空数组是边界情形，切成 0 段即可，证据为空列表。
- `if max(nums)>limit:return False,[]`：这是**非负前提下的快速否决**——某个单元素本身就超过阈值，任何包含它的段都超，所以无解。注意这一行依赖非负性（对含负数数组它是错的），Step 7 的反例打的就是这条推理。
- 主循环就是贪心：`total` 维护当前段的和；一旦 `total+value>limit`，就把当前元素的**下标 i 记为新段的起点**（也就是上一段的右开端点，不含端点），把 `total` 清零后重新累加。循环结束补一个 `len(nums)` 作为最后一段的终点。
- 返回语句同时完成判定和给证：切出来的段数 `len(cuts)` 不超过 `groups` 就返回 `(True, cuts)`，否则返回 `(False, [])`。段数最少性由 Step 6 的交换论证背书，代码本身不需要重复论证。

### 2. 独立验证器 `verify_witness_partition`

```python
def verify_witness_partition(nums, cuts, limit):
    """Witness validator also accepts signed values; no greedy inference is made."""
    if not nums:return cuts==[]
    if not cuts or cuts[-1]!=len(nums):return False
    previous=0
    for end in cuts:
        if not isinstance(end,int) or not previous<end<=len(nums):return False
        if sum(nums[previous:end])>limit:return False
        previous=end
    return previous==len(nums)
```

- 空数组时唯一合法的证据是空 cuts，直接比对。
- `if not cuts or cuts[-1]!=len(nums):return False`：证据必须把数组覆盖到头，最后一刀必须正好落在末尾。
- 循环体一次检查一个端点：`isinstance(end,int)` 防止传进浮点或布尔；`previous<end<=len(nums)` 同时保证"段非空（严格大于）"和"不越界"；`sum(nums[previous:end])>limit` 检查该段是否超阈值。
- `previous=end` 推进窗口；最后 `return previous==len(nums)` 收口。整个函数只做核对、不做任何贪心推断，所以它能验收任何来源的分段——包括含负数反例里的 `[2]`。

### 3. 反例搜索 `find_small_greedy_counterexample`

```python
def find_small_greedy_counterexample():
    from itertools import product
    # The nonnegative proof uses 'a too-large singleton makes the task impossible'.
    # Negative neighbors can invalidate that inference, even with just one group.
    for n in range(1,4):
        for nums in product(range(-2,4),repeat=n):
            for limit in range(4):
                if any(x<0 for x in nums) and max(nums)>limit and sum(nums)<=limit:
                    return {'nums':list(nums),'limit':limit,'groups':1,
                            'invalid_greedy_claim':False,'valid_cuts':[n]}
    raise AssertionError('The enumerated domain should contain a counterexample')
```

- 三层循环穷举的域刻意很小：长度 1–3、元素取值 -2..3（既含负数又有正数）、limit 0..3。反例搜索只在玩具规模上做，永远不会进入正式求解路径。
- 命中条件是三件事同时成立：数组含负数（撤掉了前提）、`max(nums)>limit`（旧推理会据此判"无解"）、`sum(nums)<=limit`（整段一刀就合法，说明实际有解）。三条撞在一起，旧推理就被驳倒了。
- 返回的字典把证据打包：`valid_cuts:[n]` 是"整个数组一段"这个真实方案，`invalid_greedy_claim:False` 标记旧主张的结论。最后的 `raise AssertionError` 是防御：如果穷举域里居然找不到反例，说明搜索域设计错了，应当失败而不是静默返回。

## 五、为什么是对的？复杂度是多少？（说人话）

**贪心为什么对。** 交换论证的关键一步**不是**"把当前段拉长看起来更好"，而是：把别人方案里更早的一刀右移到贪心位置时，前段装的是贪心本来装得下的元素所以仍合法，而被移走的元素是非负的，后一段的和只会不变或变小，绝不会超限。这个"移走的东西不重"恰好用到了非负性——把前提换成含负数，这一步立刻塌掉，这就是为什么前提必须写进函数契约。反复做这种交换，任何一个合法分段都能被改造成贪心分段而且段数不增加，于是"贪心切出的段数 ≤ 任何合法分段的段数"，用 `len(cuts)<=groups` 判可行性就是对的。

再单独看一下那条快速否决（`max(nums)>limit` 无解）：它其实是一条一行的微型证明——非负前提下，超限的单元素无论被放进哪一段都会拖垮那一段，所以无解。它和主循环各自独立成立，互不依赖。

**验证器为什么可信。** 它只核对给定分段是否满足定义（覆盖、非空、有序、每段不超限），完全不去推断"最少需要几段"。正因为它不下这种推断，它才可以独立地验收反例里的含负数分段——裁判不需要会做题，只需要会查卷。

**终止性。** 贪心的主循环变量 i 每轮严格加一、最多走 n 步；验证器沿 cuts 端点严格递增地走一遍也必然结束。两个函数都没有可能不终止的分支（反例穷举的三层循环也各自有界）。

**代价。** 贪心和验证器都是把数组从头扫到尾，时间 O(n)：例子里的 5 个元素，贪心扫 5 步，验证器对 cuts 里的每个端点做一次切片求和。证据数组 `cuts` 的空间按段数算是 O(groups)，构造阶段最坏（每个元素都超限单成一段）是 O(n)。反例穷举只在长度 ≤3 的小数组上跑，成本可以忽略，而且明确不放进求解路径。拿具体规模说：哪怕数组十万元素，贪心也只是十万次加法和比较，一步到位。

## 六、测试用例在测什么

cell8 的断言可以分成四组来看。先给一个总览：第 1 组测正常值加证据核验，第 2 组是贪心对暴力的小规模全量对拍，第 3 组专攻验证器的边界负例，第 4 组把反例和前提守卫钉死。

1. **正常值的证据测试**：`ok,cuts=feasible_partition([7,2,5,10,8],18,2)` 之后断言 `ok`、`len(cuts)<=2`、并且 `verify_witness_partition(...)` 通过。它同时测了"判定对"和"给的证据经得起独立核验"两件事——后者才是本章的特色。
2. **对拍穷举**：先在测试里现写一个 `brute_partition`（用 `itertools.combinations` 枚举所有可能的切点组合，找到第一个能通过验证器的分段），然后对长度 0–4、取值 0..2 的全部数组 × limit 0..4 × groups 1..3 的组合，断言贪心的判定和暴力一致；可行时还断言段数不超 groups 且证据过验证器。这是"证明与测试分工"的测试一侧：交换论证管一般性，穷举管实现 bug。
3. **验证器的负例三连**（输入 `nums=[1,2]`、`limit=3`）：
   - `verify_witness_partition([1,2],[0,2],3)` 应为 False：第一个端点是 0，意味着开头的段是空的，验证器必须拒绝空段。
   - `verify_witness_partition([1,2],[1],3)` 应为 False：最后端点是 1 而不是 2，数组没被覆盖完。
   - `verify_witness_partition([1,2],[2,2],3)` 应为 False：两个端点相同，末尾出现空段，同样拒绝。
   这三条都是**边界值测试**，专咬"端点重合/越界/没盖满"这几类验证器最容易写漏的坑。
4. **反例与前提守卫**：取出 `find_small_greedy_counterexample()` 的结果后，断言验证器接受它的 `valid_cuts`（含负数输入下"整段一刀"确实合法）、断言 `max(nums)>limit`（确认旧推理在此输入上会给出错误结论）；最后用 try/except 断言 `feasible_partition([-2,1],0,1)` 抛出 `ValueError`——生产函数对超出契约的输入必须显式拒绝，而不是悄悄给个错误答案。

## 七、练习思路提示

- **练习 1（分别证明二分单调、区间贪心和 Dijkstra）**：三题共用本章模板。二分单调性要证的是"判定函数在答案轴上单侧为真"（若 x 可行则 x+1 也可行，或反过来），写清楚判定函数是什么、单调方向怎么由它推出。区间贪心（按右端点排序选不重叠）用交换论证：任何解里第一个没选的区间可以换成右端点更小的贪心选择而不破坏后面。Dijkstra 则围绕不变量"已定案集合中每个点的距离已是精确最短路"加归纳，配合边权非负这一前提（想想撤掉非负权它会怎么塌）。每个证明先给一个 3–5 个元素的手算例子，再用暴力实现或本章验证器复核。
- **练习 2（撤掉前提后失败的输入）**：照抄 Step 7 的套路——先写出原证明里哪一步用到了前提（比如非负性、无环、右端点排序），然后构造一个只违反这一条前提、其余都保持的小输入，手算展示旧结论不再成立，并用验证器/暴力解确认新输入下的真实答案。关键是把"失败的输入"和"失败的那一步推理"对应起来，而不是随便扔一个跑不通的样例。

## 八、对应 LeetCode 题目

- **410. Split Array Largest Sum（comparison）**：这一题是"分段 + 每段和不超过阈值"的正式版——把 limit 当二分变量、用本章这类贪心可行性判定做检查函数，练的是"可行性判定 + 交换论证"的组合。
- **435. Non-overlapping Intervals（comparison）**：按右端点排序的贪心，练的是和本章同款的交换论证——把任意解的第一个选择换成右端点更小的选择，后面只会更宽裕。
- **743. Network Delay Time（comparison）**：Dijkstra 的标准载体，练的是"不变量 + 归纳 + 非负权前提"三件套，正好对应练习 1 的第三小问。

notebook 结尾照例提醒：这些题号用于知识映射，本章实现遵循教学契约，不要把教学实例当成官方题的完整答案。
