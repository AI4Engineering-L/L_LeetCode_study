# N052 · 表达式解析与计算 —— 说人话详解

> 对应 notebook：`notebooks/07_stack_queue/052_expression_parsing_stacks.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决两件事：**给一个字符串形式的算式，算出正确的结果**，以及**给一串后缀表达式，用栈把它算出来**。难点有三个：

1. **优先级**：`3+2*2` 必须先算乘法。输入 `3+2*2` → 输出 7 → 因为 2*2=4，再 +3；如果你从左到右硬算就会得到 10，那就错了。
2. **括号和一元负号**：`1-(2-(3+4))` 输入 → 输出 6 → 因为最里层 3+4=7，中间 2-7=-5，最外层 1-(-5)=6。这里既有嵌套括号，又有"减号后面跟括号"造成的负数。单独一个负号开头（如 `-3/2`）也要能处理，结果按"向零截断"是 -1。
3. **后缀表达式（逆波兰）**：运算符写在两个操作数后面，比如 `['2','1','+','3','*']` 表示 `(2+1)*3`，输出 9。它不需要括号，用栈从左到右扫一遍就能算。

另外有个隐藏考点：**整数除法要向零截断**。Python 的 `//` 是向下取整（`-3//2` 得 -2），而题目要的是丢掉小数部分（`-3/2` 得 -1），所以不能直接用 `//`，也不能转 float（cell1 特别警告：大整数转 float 会丢精度）。

## 二、关键概念（定义）

- **操作数栈（operand stack）**：算后缀表达式用的栈，里面只存已经算出来的数值。遇到数字压栈，遇到运算符就弹出两个数算完再压回去。
- **后缀表达式 / 逆波兰表达式（RPN）**：把运算符放在两个操作数后面的写法，比如 `2 1 +` 就是 `2+1`。它的好处是完全不需要括号和优先级规则——谁先来谁先算。
- **递归下降解析（recursive descent）**：把"表达式"按语法层层分解：expression（加减层）调用 term（乘除层），term 调用 factor（最小单元层），factor 再调用 expression 处理括号。每一层是一个函数，语法结构就是函数调用结构。
- **语法层级（expression / term / factor）**：expression 只管加减；term 只管乘除；factor 管"不可再分"的东西——整数、一元正负号、括号子表达式。优先级不是靠特殊判断实现的，而是靠"乘除层比加减层更深、先被调用返回"天然保证的。
- **一元负号**：出现在数字或括号前面的负号，比如 `-3` 或 `-(2+3)`。它和减号是同一个字符，但在 factor 里"一个表达式开头位置"读到它时，它就是一元负号。
- **向零截断除法（truncation toward zero）**：小数部分直接扔掉、往 0 的方向靠。-3/2 = -1.5 → -1（不是 -2）；7/-2 = -3.5 → -3。这是大多数竞赛题的整数除法约定。
- **结合性（左结合）**：同优先级的运算从左到右算。`(12+8)/3*2` 要按 `((12+8)/3)*2` 算：20/3=6，6*2=12；如果先算 3*2 就会得 20/6=3，错。代码里 term 的 while 循环从左到右滚动，就是左结合的实现。

## 三、解决思路（一步步推导）

**eval_rpn 的步骤：**

1. 从左到右读 token。
2. 是数字就转成 int 压栈。
3. 是运算符就弹出两个数：**先弹出来的是右操作数 b，后弹的是左操作数 a**，算 `a op b` 再压回。顺序搞反的话减法和除法会直接算错。
4. 全部读完，栈里应恰好剩一个数，就是答案；多于一个说明表达式残缺。

**手算演示（cell6 的表格，tokens = `['2','1','+','3','*']`）：**

| token | 动作 | 值栈 |
|-------|------|------|
| 2 | 压栈 | [2] |
| 1 | 压栈 | [2, 1] |
| + | 弹 b=1、a=2，算 2+1 | [3] |
| 3 | 压栈 | [3, 3] |
| * | 弹 b=3、a=3，算 3*3 | [9] |

对应的中缀式就是 `(2+1)*3 = 9`。注意第二个运算符 `*` 弹出的 a 是**上一个运算的结果** 3，这正是"子表达式结果压栈"的含义。

**calculate_precedence（`_Parser(s, allow_mul=True)`）的步骤：**

1. `parse()` 调 `expression()`：先拿一个 term，然后只要看到 `+` 或 `-` 就再拿一个 term，合并。
2. `term()` 调 `factor()`：先拿一个 factor，然后只要看到 `*` 或 `/` 就再拿一个 factor，合并。这一层在 `allow_mul=False` 时（basic 模式）被跳过，直接透传 factor。
3. `factor()` 处理三种最小情况：一元 `+/-`（读掉符号后递归调用自己再取负/取正）、`(`（读掉左括号后递归调用 expression 算整个子式，再要求读到 `)`）、多位整数（逐位 `value*10+digit` 累积）。

**手算演示：`3+2*2`——** expression 先调 term；term 调 factor 得 3，看到下一个字符 `+` 不属于 `*/`，term 返回 3；expression 看到 `+`，再调一次 term：factor 得 2，看到 `*`，再取一个 factor 得 2，算 2*2=4，term 返回 4；expression 算 3+4=7。你可以清楚看到"乘法发生在 term 层、加法发生在 expression 层"，优先级就是调用层级。

**手算演示：`-3/2`——** expression→term→factor：第一个字符是 `-`，这是一元负号；读掉它，递归 factor 得 3，返回 -3。回到 term，看到 `/`，取 factor 得 2，`trunc_div(-3,2)`：绝对值相除 3//2=1，两数符号不同取负 → -1。

## 四、代码逐段讲解

**向零截断除法（逐字照抄）：**

```python
def trunc_div(a,b):
    if b==0: raise ZeroDivisionError('division by zero')
    value=abs(a)//abs(b)
    return -value if (a<0) != (b<0) else value
```

- `if b==0` 先挡除零：直接抛 ZeroDivisionError，而不是给出一个错误数字。
- `abs(a)//abs(b)`：两个都取绝对值再做向下取整除法——正数的向下取整等于向零截断，所以商的绝对值是对的。
- `(a<0) != (b<0)` 用"符号是否不同"决定取不取负：异号商为负，同号（包括都为正）为正。这就是绕开 Python 负数 `//` 的地板行为的关键。比如 -3//2 在 Python 里是 -2，但 trunc_div(-3,2) 是 -1。

**后缀求值（逐字照抄）：**

```python
def eval_rpn(tokens):
    stack=[]
    for token in tokens:
        if token not in ('+','-','*','/'):
            stack.append(int(token)); continue
        b=stack.pop(); a=stack.pop()
        stack.append(a+b if token=='+' else a-b if token=='-' else a*b if token=='*' else trunc_div(a,b))
    if len(stack)!=1: raise ValueError('malformed expression')
    return stack[0]
```

- `if token not in (...)`：不是四个运算符之一就当成数字，`int(token)` 转换后压栈，`continue` 进入下一个 token。
- `b=stack.pop(); a=stack.pop()`：先弹的是右操作数。对 `+`、`*` 无所谓，但对 `-`、`/` 至关重要——`2 1 -` 必须是 2-1=1 而不是 1-2=-1。
- 压回那一长串是嵌套的条件表达式，等价于"token 是 + 就 a+b，否则是 - 就 a-b……"，一路 else 下来最后只剩 `/`，用 trunc_div 保证截断语义。
- `if len(stack)!=1`：合法表达式算完只会剩一个结果；剩多了说明操作数比运算符多（如 `2 3`），这是格式错误的兜底检查。

**递归下降解析器（逐字照抄，逐段讲）：**

```python
class _Parser:
    def __init__(self,s,allow_mul): self.s=s; self.i=0; self.allow_mul=allow_mul
    def peek(self):
        while self.i<len(self.s) and self.s[self.i].isspace(): self.i+=1
        return self.s[self.i] if self.i<len(self.s) else None
```

- `self.i` 是当前读到的位置下标；`allow_mul` 是模式开关：False 关掉乘除（basic 计算器），True 打开（含优先级的计算器）。
- `peek()` 先用 while 跳过所有空白字符，然后**看一眼**下一个字符但不消费它；读完了就返回 None。注意跳空白发生在 peek 内部，所以其他函数完全不用管空格。

```python
    def factor(self):
        c=self.peek()
        if c in ('+','-'):
            self.i+=1; value=self.factor(); return -value if c=='-' else value
```

- factor 一上来先 peek。如果是一元 `+/-`，消费这个符号，**递归调用 factor** 得到它后面的值，再决定取不取负。递归让 `--3`（双重负号）甚至 `-(-3)` 这类链式情况自动成立。
- 一元正号也支持：读掉 `+`，原样返回值。

```python
        if c=='(':
            self.i+=1; value=self.expression()
            if self.peek()!=')': raise ValueError('missing closing parenthesis')
            self.i+=1; return value
```

- 括号分支：消费 `(`，然后**回到最高层**调 expression 算出整个子表达式，紧接着必须看到 `)`，否则抛"缺右括号"；最后消费 `)` 并返回子式结果。括号里可以装任何复杂的东西，因为 expression 会层层往下再回到这里。

```python
        if c is None or not '0'<=c<='9': raise ValueError('expected integer')
        value=0
        while self.i<len(self.s) and '0'<=self.s[self.i]<='9':
            value=value*10+int(self.s[self.i]); self.i+=1
        return value
```

- 前一行是错误兜底：既不是符号、不是括号、又不是数字字符，说明输入不合法（比如 `3+a`），立刻报错。
- 数字分支用 `value*10+digit` 把多位数逐位累积：`"12"` 先得 1，再得 1*10+2=12。这样 12 是一个完整的操作数，而不会被当成 1 和 2。

```python
    def term(self):
        value=self.factor()
        while self.allow_mul and self.peek() in ('*','/'):
            op=self.peek(); self.i+=1; other=self.factor()
            value=value*other if op=='*' else trunc_div(value,other)
        return value
    def expression(self):
        value=self.term()
        while self.peek() in ('+','-'):
            op=self.peek(); self.i+=1; other=self.term()
            value=value+other if op=='+' else value-other
        return value
    def parse(self):
        value=self.expression()
        if self.peek() is not None: raise ValueError('unconsumed input')
        return value
```

- term：先取一个 factor，然后**从左到右**循环消化所有 `*` `/`——左结合就是这样实现的：`12+8)/3*2` 里的 `/3*2` 会先算 `/3` 再算 `*2`。乘除用 trunc_div。
- expression：结构完全相同，只是对象换成 term 和加减。因为 term 先返回，乘除总是先算完，优先级就实现了。
- parse：算完后 peek 必须是 None；如果还剩字符（比如 `1+2)` 的孤立右括号），说明有没被消费的输入，报错。

```python
def calculate_basic(s): return _Parser(s,False).parse()
def calculate_precedence(s): return _Parser(s,True).parse()
```

- 两个接口只是同一个解析器的两种配置：basic 不认识乘除（对应 LC224 的纯加减+括号），precedence 全支持（对应 LC227）。

## 五、为什么是对的？复杂度是多少？（说人话）

- **为什么优先级一定对**：cell4 说"每个解析函数消费且仅消费其语法层级的一个合法表达式"。用大白话讲：expression 想合并两个 term 之前，term 已经把连在一起的乘除全部算完了才返回；term 想拿操作数时，factor 也已经把括号里的整个子式算成了一个数。所以任何乘除的结果，永远在加减动手之前就已经变成一个数了——这不是碰巧的扫描顺序，而是函数调用一层包一层的必然结果。括号之所以能整体当一个数用，是因为 factor 遇到 `(` 会递归调 expression，把里面全部算完才回来。
- **为什么除法语义对**：所有除法都走 trunc_div，两步"绝对值地板除 + 按符号修正"保证任何符号组合都向零截断；测试里专门用 10³⁰ 量级的大数验证没有走 float 路线（float 只有约 15~17 位有效数字，10³⁰ 级别必然失真）。
- **复杂度**：每个字符最多被 peek/消费常数次，时间是 O(n)（cell4 原文：O(n) 字符扫描）。空间上，eval_rpn 的栈最坏 O(n)；递归解析器每层括号、每个一元负号都要下探一层递归，嵌套或一元链最坏是 O(n) 递归深度——cell4 特别提醒：如果输入可能嵌套几十万层括号，要改成显式栈（迭代版）防止递归爆栈。日常规模（比如 n=10⁴）下，O(n) 就是万级操作，毫无压力。

## 六、测试用例在测什么

- `assert eval_rpn(['2','1','+','3','*'])==9`：正常情况，验证弹栈顺序 a op b 和"结果回栈再参与后续运算"。
- `assert calculate_precedence('3+2*2')==7`：优先级——乘法必须先于加法。这条专防"从左到右无脑算"（那会得 10）。
- `assert calculate_precedence('-3/2')==-1`：两个考点合一：一元负号能出现在开头；除法向零截断（Python 的 `-3//2` 是 -2，用 `//` 直接写就错了）。
- `assert calculate_basic('1-(2-(3+4))')==6`：basic 模式的嵌套括号 + 内层结果为负数（2-7=-5）再被减（1-(-5)=6）。这条测递归括号和双重取负。
- `assert calculate_precedence('(12+8)/3*2')==12`：左结合 + 多位整数 + 截断除法三合一。`((20)/3)*2 = 6*2 = 12`；如果先算 `3*2` 或忘了多位数解析都会翻车。
- `assert trunc_div(-(10**30+1),3)==-((10**30+1)//3)`：大整数精度。被除数超过 10³⁰，float 存不下它的精确值；这条专防"转 float 再截断"的实现。
- 最后两层的 for 循环（a、b 各取 -4..4）：**81 种符号与数值组合的穷举**，包括 0、正正、负负、正负组合。`calculate_basic(f'({a})-({b})')==a-b` 验证减法与括号包裹的负数（如 `(1)-(-4)`），`calculate_precedence(f'({a})*({b})+3')==a*b+3` 验证乘法含负操作数后再加。这类"程序生成的批量断言"比手写几条更能覆盖边角。

## 七、练习思路提示

- **练习 1（一元负号案例）**：提示：从三个位置收集用例——表达式开头（`-3+1`）、括号开头（`-(-3)`、`1-(-2)`）、乘号后面（`2*-3`）。先手算预测每个的值，再跑 `calculate_precedence` 对答案。进阶可以追问链式负号 `--3` 为什么等于 3：顺着 factor 的递归走一遍，每层读掉一个负号、对内层结果取一次反。边界别忘了 `-(10**30)` 这种大数取负，确认没有精度问题。
- **练习 2（Python 整除 vs 题意截断）**：提示：列一张四象限表——a、b 各取正负（如 7/2、-7/2、7/-2、-7/-2），分别写出 Python `//` 的结果和 trunc_div 的结果，你会发现只有"恰好整除"或"同号"时两者一致，异号不整除时 `//` 会多往负方向走一步（floor 性质）。再想一个会被坑到的真实例子：`calculate_precedence('(1-4)/2')` 应该是 -1，用 `//` 会得 -2。最后回答：为什么不能 `int(a/b)`？用 a=10³⁰+1 代入试试，float 表示不了这个数。

## 八、对应 LeetCode 题目

- **150. Evaluate Reverse Polish Notation**：练操作数栈——数字压栈、运算符弹两个算一个，本章 `eval_rpn` 就是它的直接实现（含向零截断的坑）。
- **224. Basic Calculator**：练"加减 + 括号 + 一元负号"的解析，对应 `calculate_basic`（`allow_mul=False` 那条线）。
- **227. Basic Calculator II**：练"含乘除优先级、无括号"的四则运算，对应 `calculate_precedence`，考点是乘除先算和左结合。
