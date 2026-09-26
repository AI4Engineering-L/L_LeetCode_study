# N161 · JavaScript基础、闭包与对象 —— 说人话详解

> 对应 notebook：`notebooks/19_specialized_tracks/161_javascript_fundamentals_closures.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章用三道 LeetCode 的"函数工厂"题（2667/2620/2665）把 JavaScript 最核心的机制——**闭包**——练一遍，同时对比 JS 和 Python 的语义差异。所谓函数工厂，就是"一个函数，调用它之后返回另一个函数，返回的函数还带着自己的私有状态"。三道题递进：造一个怎么调都返回固定字符串的函数；造一个越调越大一的计数器；造一个带加一、减一、复位三个方法的计数器对象。

给你一个具体到数字的例子（cell6 的真实轨迹）。执行 `const a = createCounter(5)` 后，每次调 `a()` 的返回值是：

```
第一次 a() → 5   （内部 current 从 5 变成 6）
第二次 a() → 6   （current 变成 7）
再调 b = createCounter(-1)：b() → -1，a 的进度不受影响
第三次 a() → 7
```

为什么 a 能"记住"自己数到几了？因为 `createCounter` 里的局部变量 `current` 被返回的那个函数**捕获**了——这就是闭包。为什么 b 从 -1 开始数、完全不干扰 a？因为**每调用一次工厂函数就新建一个独立的 `current`**，两个计数器各数各的。还有一个容易翻车的契约：普通计数器 `createCounter` 返回的是**旧值**再自增（3、4、5……），而带复位的 `createCounterWithReset` 的 `increment` 返回的是**新值**——这个差别是返回值契约，测试就盯着它。

用 Python 的眼光看，`createCounter` 大概相当于下面这段等价实现：

```python
def create_counter(n):
    current = n            # 对应 JS: let current = n
    def counter():
        nonlocal current   # Python 必须声明 nonlocal 才能改外层变量
        old = current
        current += 1       # JS 一行 current++ 顶这里三行
        return old
    return counter
```

语义几乎同构：Python 靠 `nonlocal` 显式声明"我要改外层的变量"，JS 的闭包函数天然就能读写外层的 `let`。差异在细节：JS 函数对参数个数不敏感（多了忽略、少了当 undefined），Python 会直接 TypeError；JS 的 `==` 会隐式转型（`'5' == 5` 为 true），Python 的 `==` 不会。这一章的目标（cell0 原话）就是"理解 JS 与 Python 语义差异并保留闭包状态"。

## 二、关键概念（定义）

- **let / const**：JS 声明变量的两个现代关键字。`let current = n` 声明一个可变的块级变量；`const` 声明后不能再重新赋值（但对象内容仍可变）。老式的 `var` 没有块级作用域，容易出诡异 bug，本章不用。
- **'use strict' 与 ===**：严格模式让 JS 对危险写法直接报错。比较运算用三等号 `===`（严格相等，类型不同直接判不等），不要用会偷偷做类型转换的 `==`（`'5' == 5` 竟然是 true）。测试里用的 `node:assert/strict` 也贯彻同样的严格精神。
- **undefined / null**：JS 的两种"没有"。`undefined` 是"压根没赋值"（比如没传的参数）；`null` 是"故意置空"。Python 只有一个 `None`，JS 拆成两个，语义要分清。
- **数组与对象**：JS 的数组 `[1,2,3]` 类似 Python 的 list；对象 `{ increment(){...} }` 类似 dict，但可以在里面直接写方法（简写形式的函数属性）。
- **闭包（closure）**：函数记住自己**被定义时**所在词法环境里的变量绑定。关键点是 cell1 那句话："闭包捕获的是词法环境中的绑定，不是调用时复制的常数"——计数器函数捕获的是 `current` 这个**变量本身**（绑定），所以每次调用读到的都是最新值；如果捕获的是创建那一刻的数值拷贝，计数器就永远只会返回初始值。
- **词法环境（lexical environment）**：一段代码"看得见"的变量集合，由代码书写位置决定。内层函数天生看得见外层函数的局部变量，这是闭包能成立的原因。
- **私有状态**：`current` 只活在工厂函数内部，外界没有任何途径直接读写它，只能通过返回的函数间接操作——面向对象里"封装"的效果，用闭包几行就实现了。
- **后置 `++` 与前置 `++`**：`current++` 先把旧值交出去、再加一（返回旧值）；`++current` 先加一、再交出去（返回新值）。本章两个计数器恰好一个用一个，是精心设计的对照。
- **this / 原型（导览）**：JS 里函数的 `this` 指向谁取决于**怎么调用**（和 Python 方法的 self 很不一样）；原型是对象共享方法的旧机制。本章代码不需要它们，知识点里只作导览，练习 2 会碰箭头函数的 this 差异。

把 JS 和 Python 最容易踩的差异浓缩成一张速查：

- 相等比较：JS 用 `===`（`==` 会隐式转型），Python 的 `==` 本身就是严格语义。
- 空值：JS 分 `undefined`（没赋值）和 `null`（主动置空），Python 只有 `None`。
- 参数：JS 多传忽略、少传得 undefined；Python 按签名严格匹配，错配即 TypeError。
- 自增：JS 有 `++`/`--` 且分前置后置；Python 没有，得手写 `x += 1` 并自己决定先返回还是先加。
- **Node.js**：让 JS 脱离浏览器跑在命令行的运行时。本章把 JS 源码交给 `node -e` 真实执行（notebook 里跑的是 v22.16.0），Python 只负责组织和显示，不做 JS 模拟。

## 三、解决思路（一步步推导）

**Step 1：最简单的工厂——忽略一切参数。** `createHelloWorld()` 返回一个函数，这个函数不管你传什么都返回 `'Hello World'`。实现要点是 rest 参数 `(...args)`：它把任意个数、任意类型的参数全部收进 args 数组，然后一个都不用——所以 `hello()` 和 `hello(1, null, {})` 的结果完全相同。这一步是闭包的"空载运行"：返回的函数没捕获任何变量，只返回常数，先用它确认"函数能当返回值"这个机制本身没问题，再进入带状态的后两步。

**Step 2：带私有状态的计数器。** `createCounter(n)` 做三件事：`let current = n`（初始化只发生这一次）；`return function () { return current++; }`（交出访问内部状态的钥匙）；之后外界每次调用这把钥匙，读旧值、再让 current 前进一格。手算 `createCounter(3)` 的调用序列：第 1 次返回 3（current 变 4），第 2 次返回 4（变 5），第 3 次返回 5。归纳一下（cell4 的论证）：第 k 次调用返回 n+k−1。**重新调用 `createCounter(3)` 会再开一个全新的环境**，新计数器又从 3 开始——两个计数器互不干扰，这就是"独立环境"。

**Step 3：升级成有三个方法的对象。** `createCounterWithReset(init)` 这次不返回单个函数，而是返回一个对象字面量，里面三个方法**共享同一个 `current`**：`increment()` 用前置 `++current` 返回新值；`decrement()` 用 `--current` 返回减一后的新值；`reset()` 把 current 写回 `init` 并返回它。手算 `createCounterWithReset(5)` 的测试序列（cell8 数据）：

| 调用 | 动作 | current 变化 | 返回值 |
|------|------|-------------|--------|
| `c.increment()` | ++current | 5 → 6 | **6**（新值，前置++） |
| `c.reset()` | current = init | 6 → 5 | **5** |
| `c.decrement()` | --current | 5 → 4 | **4** |
| `c.reset()` | current = init | 4 → 5 | **5** |

对照 Step 2：如果 `createCounter(3)` 第 1 次调用也想返回"新值 4"，那它必须用 `++current`——但 LeetCode 2620 的契约就是返回 3、4、5（旧值），所以那里必须用后置 `++`。**返回值契约决定用哪种自增写法**，不能看着差不多就混着写。

**Step 4：让 Node 替我们验证。** 本章的执行模型是：JS 源码存成字符串，`run_js(额外代码)` 把"源码 + 额外代码"拼起来交给 `node -e` 真跑，Python 只收回 stdout。这样每一条结论（独立环境、新旧值契约、复位语义）都是真 JS 引擎给的答案，不是我们脑补的。

## 四、代码逐段讲解

cell3 由一段原生 JS 和一个 Python 执行器组成，逐段看。

**第 1 段：JS 源码本体（cell6 用 Code 块原样展示过）。**

```javascript
'use strict';
function createHelloWorld() {
  return function (...args) { return 'Hello World'; };
}
function createCounter(n) {
  let current = n;
  return function () { return current++; };
}
function createCounterWithReset(init) {
  let current = init;
  return {
    increment() { return ++current; },
    decrement() { return --current; },
    reset() { current = init; return current; }
  };
}
```

第一行 `'use strict'` 打开严格模式，整份源码受更严的规则约束。`createHelloWorld` 里的 `(...args)` 是 rest 参数，"来多少参数都收下但忽略"，这是 2667 题的正规解法。`createCounter` 里 `let current = n` 这行**只在工厂被调用时执行一次**，之后返回的内层函数闭包引用这个 `current`；`return current++` 是"交出旧值、状态前移"。`createCounterWithReset` 返回对象字面量，`increment() {...}` 是方法的简写（等价于 `increment: function() {...}`），三个方法都引用同一个 `let current`，所以它们操作的是同一份状态；`reset` 里 `current = init` 用的 `init` 同样是被闭包捕获的参数——**初始值本身也被记住了**，复位才能回到"构造时的初值"而不是 0。

**第 2 段：Python 执行器。**

```python
def run_js(extra):
    result = subprocess.run(['node', '-e', JS_SOURCE + '\n' + extra],
                            text=True, capture_output=True, check=True, timeout=20)
    return result.stdout
```

`node -e` 的意思是"把后面这串字符串当 JS 源码执行"；这里把三个工厂函数的源码和调用方代码（`extra`）拼在一起跑。`capture_output=True` 收 stdout/stderr，`check=True` 让 Node 报错（非零退出码）立刻变成 Python 异常，`timeout=20` 防挂死。返回 `result.stdout`，也就是 console.log 打出来的内容——cell6 靠它拿到闭包轨迹，cell8 靠它拿到"Node assertions passed"这行回执。

cell6 的用法值得看一眼，它就是这套执行器的工作样板：先用 `Code(JS_SOURCE, language='javascript')` 把源码原样展示出来（我们第四节贴的就是这份展示），然后一行 JS 混合调用——`const a=createCounter(5), b=createCounter(-1)` 建两个计数器、交错调用四次、用 `JSON.stringify` 把 `[['a',a()],['a',a()],['b',b()],['a',a()]]` 打成 JSON——Python 侧 `json.loads` 解析后交给 `show_table` 渲染成"闭包 → 返回值"的轨迹表。于是第一节那张手算表（5、6、-1、7）就是从真实 Node 引擎（cell6 另打印了版本 v22.16.0）里流出来的。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么对？** cell4 给了两条论证。第一条是**独立性**：每次调用工厂函数，都会执行一遍 `let current = ...`，也就创建了一个新的词法环境；返回的函数捕获的是**自己那次**的环境，所以 a、b 两个计数器的 `current` 是两个不同的变量，谁也碰不到谁。而 `createCounterWithReset` 返回的三个方法捕获的是**同一个**环境的同一个 `current`，所以 increment 加的、decrement 减的、reset 写回的，都是同一份账本。第二条是**归纳**：对 `createCounter(n)`，第 1 次调用返回 n 并把 current 变成 n+1；假设第 k 次返回 n+k−1，则第 k+1 次返回 n+k——所以第 k 次调用一定返回 n+k−1，这就是调用序列 3、4、5 的数学版。reset 的正确性也简单：它把状态硬写回 init，相当于把"账本"转回构造那一刻的初态，之后的归纳从头再来。

**复杂度怎么说？** 这一章没有循环、没有数据结构，三个工厂都是：构造一次 O(1)，每次调用 O(1)，每个计数器只存一个数字，状态 O(1)。拿量级感受：就算你把一个计数器连调一千万次，每次调用的成本仍是常数，只是 current 会涨到一千万——而 cell4 顺手划了个边界：JS 的 Number 超过 2^53−1 这个"安全整数"上限后精度会出问题，本章不涉及那种场景（真遇到了得换 BigInt）。换句话说，本章的复杂度不在"算得快不快"，而在"想得对不对"——三道题的通过与否取决于你是否理解"绑定被共享""前后置自增返回值不同""reset 回到构造初值"这三个语义点，它们全都和运行次数无关。

## 六、测试用例在测什么

本章的验证方式很特别：**断言写在 JS 里，用 Node 自带的 `node:assert/strict` 在真实 JS 引擎里跑**，Python 只负责调 `run_js` 和打印回执。所以下面每条 assert 都是货真价实的 JS 断言。看之前先把预期押好：

- `hello()` 和 `hello(1,null,{})` 都是 `'Hello World'`
- 交错调用 `[a(),a(),b(),a(),b()]` 是 `[3,4,3,5,4]`
- 对象序列 `[c.increment(),c.reset(),c.decrement(),c.reset()]` 是 `[6,5,4,5]`
- 三个序列都能在手算表里逐项找到出处，说明推导闭环。

1. `assert.equal(hello(), 'Hello World')` —— **正常值**：无参调用返回固定字符串，工厂第一次验收。
2. `assert.equal(hello(1, null, {}), 'Hello World')` —— **参数边界**：故意塞数字、null、对象三种类型的参数，验证 rest 参数"全收全忽略"的契约；换 Python 的固定参数列表早就 TypeError 了，这里必须安然无恙。
3. `assert.deepEqual([a(),a(),b(),a(),b()], [3,4,3,5,4])` —— **独立性 + 旧值契约**：a、b 都从 3 出发，调用交错进行——a 返回 3、4 后，b 返回 3 证明自己有**独立的** current；接着 a 返回 5 证明自己的进度没被 b 打断；最后 b 返回 4 收尾。整条序列同时锁死了"初始值正确""每次加一""返回旧值""两个闭包互不干扰"四件事，是本章最核心的一条断言。
4. `assert.deepEqual([c.increment(),c.reset(),c.decrement(),c.reset()], [6,5,4,5])` —— **新值契约 + 复位**：第一项 6（不是 5！）专门验证 `increment` 用前置 `++` 返回新值，和第 3 条的旧值契约形成对照；两次 reset 都返回 5，验证"恢复到构造时的初值"（哪怕中间已经加加减减过）；decrement 返回 4 验证减法方向。如果有人把 increment 写成 `current++`，这条断言会立刻抓住 5 ≠ 6 的出入。
5. 最后 `console.log('Node assertions passed')` 打出回执，Python 侧看到这行输出（连同中文的"N161: 所有本章断言通过"）才算整章通过——这是"跨语言测试也要有可观测证据"的体现。

## 七、练习思路提示

- **练习 1（重新创建计数器 vs 复用计数器）**：提示——设计对照实验：`createCounter(3)` 调五次得到 a1..a5，每个只调一次，预期全都返回 3（每次工厂调用都是新环境）；对比"复用同一个 a 连调五次"得到 3、4、5、6、7。手算写清楚两种时间线里 `current` 的每一次变化，再用 `run_js` 把两条轨迹 console.log 出来验证。边界可以加问一句：把计数器赋给另一个变量 `const d = a`，d 和 a 是同一个闭包还是两个？（提示：函数是对象，赋值不复制环境。）
- **练习 2（解释箭头函数的 this 差异）**：提示——先造证据：定义一个普通方法 `function f() { return this; }` 和箭头函数 `const g = () => this;`，分别作为对象方法调用、裸调用，把返回的 this 打出来对比。预期方向：普通函数的 this 看**调用方式**（`obj.f()` 里 this 是 obj），箭头函数**没有自己的 this**，用的是定义处外层的 this（模块顶层是 undefined 或 module.exports，视严格模式而定）。用 `run_js` 跑真实 Node 结果来支撑你的解释，边界可以试试 `setTimeout` 回调里两种函数的 this 各指向谁。写结论时给自己列三个检查点：

- 普通函数：this 在**调用那一刻**确定，`obj.f()` 与裸调用 `f()` 结果不同。
- 箭头函数：this 在**定义那一刻**继承外层，之后怎么调用都不变。
- 对照 Python：方法的 self 在绑定时就固定，更像箭头函数而不是普通函数。

## 八、对应 LeetCode 题目

- **2667. Create Hello World Function**：练"返回函数 + rest 参数忽略输入"，对应 `createHelloWorld`，闭包的最小入门。
- **2620. Counter**：练"闭包捕获变量绑定 + 后置 `++` 返回旧值"契约，对应 `createCounter`。
- **2665. Counter II**：练"多方法共享同一词法环境 + 前置 `++` 返回新值 + reset 回初值"，对应 `createCounterWithReset`。
- **2695. Array Wrapper**（extension）：同属函数/对象工厂家族的延伸题，练把闭包状态思想迁移到"对象 + valueOf 自定义运算"上，本章的"私有状态 + 方法集"套路可以直接套用。

做题顺序建议照 2667 → 2620 → 2665 来，最后拿 2695 做迁移检验：三道 canonical 题从"无状态工厂"到"单状态函数"再到"多方法共享状态"，一层一层加码，正好是闭包的完整练习曲线。
