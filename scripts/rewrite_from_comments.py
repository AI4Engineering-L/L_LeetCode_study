"""Integrate the chapter-specific teaching notes without replacing reviewed algorithms.

The source of explanations is comment/<notebook-stem>.md. Algorithm definitions and
regression tests remain those of the existing lesson modules. Generated notebooks
contain both small implementation cells and one independently runnable full program.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'comment-rewrite-v1'
SECTION_NAMES = dict(zip('一二三四五六七八', range(1, 9)))

# Correct identifiable errors in the supplied explanations, not executable code.
REPLACEMENTS = {
    1: [
        ('整体分四步。', '整体分五步。'),
        ('方法名 `sum` 和参数名 `num1`、`num2` 也是题目规定的，照抄即可。',
         '方法名和调用接口应与题目模板一致。位置参数的局部名字可以改变；初学时保留模板命名更便于核对。'),
        ('Python 的类方法约定第一个参数接收实例自身', 'Python 的实例方法约定第一个参数接收实例自身'),
    ],
    2: [
        ('会返回 25 ≠ 10', '会返回 5 ≠ 10'),
        ('加三分支推理', '加两种情况的推理'),
        ('三条 isclose 断言', '两条 isclose 断言'),
        ('而摄氏温度任何实数都有意义，公式对任何输入都给出合法输出，就不需要守卫。',
         '温度换算函数在这里实现数值公式；物理温度是否低于绝对零度，是另外的输入约束，不能由公式可计算推出物理上有意义。'),
        ('输入多大都是常数次操作，所以时间和空间都是 O(1)。',
         '固定字长模型下是 O(1)。Python 整数可任意精度；整数运算的实际代价还取决于位数。'),
    ],
    29: [
        ('要求这段子里没有任何字符重复', '要求这段子串里没有任何字符重复'),
        ('这四个字母里 A、B、C 各出现一次，刚好覆盖', '这四个字母中包含 A、B、C，能够覆盖'),
        ('所以违反后收缩一定能在有限步内恢复合法。',
         '因此应按各自条件决定收缩时机：无重复窗口在非法时收缩，覆盖窗口在合法时收缩。'),
    ],
    64: [
        ('这三道题的共同点是：答案没法一步算出，只能一步一步"试"出来。',
         '这三道题都要求列出具体方案，而不是只计算方案数；因此必须访问每个要输出的方案。'),
        ('本层允许选的最小下标', '本层允许选的最小数值'),
        ('枚举算法至少要把所有答案打印一遍', '显式枚举算法至少要构造或输出全部答案'),
    ],
    113: [
        ('这一位 therefore 只能填到', '这一位只能填到'),
        ('这样 n 多大都不怕，长度只是位数 D。',
         '这样状态规模主要随位数 D 增长；Python 递归实现仍受递归深度与内存限制。'),
        ('Python 跑几分钟都算不完。', '直接枚举的计算量会很大。'),
    ],
    163: [
        ('和完成顺序（1→2→0）无关', '和完成顺序无关；同一到期时刻的先后不能靠这张示意图保证'),
        ('Promise 回调排队的队列，比定时器先执行。',
         'Promise 回调进入微任务队列；当前同步代码结束后，运行时会在适当的微任务检查点处理它们，不能据此保证所有异步工作的全局先后。'),
    ],
}


CORRECTNESS_REVISIONS = {
    1: """**正确性。** 题目要求返回两个整数的和。`sum_two(a, b)` 的返回表达式恰好是 `a + b`，因此直接满足目标。`Solution.sum` 原样传入两个参数并返回计算结果，所以这层接口不改变答案。没有外部状态有利于复现，但本身不是正确性证明：一个永远返回 0 的函数也没有外部状态，却不满足一般的求和要求。

**复杂度。** 固定字长模型下，一次加法需要 O(1) 时间和 O(1) 额外空间。Python 使用任意精度整数；按位数计成本时，两个至多 b 位的整数相加需要 O(b) 时间，结果也可能占 O(b) 空间。额外的函数调用会增加运行开销，但不改变这里的渐近量级，具体耗时不能脱离运行环境断言。

**边界。** `print(a+b)` 只展示信息，不能替代 `return a+b`。传入字符串时 `+` 会拼接而不是做整数加法；类型注解不会在运行时自动拒绝这类输入。正确性总是相对于已经约定的输入类型和目标而言。""",
    29: """**最长无重复子串。** 处理当前右端字符后，若出现重复就左移，直到再次无重复。右端相同的更短窗口不可能给出更大的长度；更长窗口则已经含重复。因此这一轮记录的是以当前右端结尾的最长合法窗口。枚举全部右端就不会漏掉全局答案。

**最短覆盖子串。** 每当 `missing == 0` 时，先记录候选，再移走左端字符。不能说每轮都重新枚举了所有历史左端点：已经丢弃的左端不会再回来。为什么仍然不漏最优解？因为丢弃某个左端时，已经记录过它对应的合法窗口；以后固定这个左端再扩大右端，只会更长，不可能改善最短答案。若 `missing > 0`，收缩只会减少字符，不会把缺失变成满足，所以应继续扩张。

**代价。** 右端最多前进 |s| 次，左端也最多前进 |s| 次。频次表操作按平均 O(1) 计时，算法总时间是 O(|s|+|t|)，不是两层循环就必然 O(|s|²)。空间为 O(σ)，σ 是实际存入频次表的不同字符数。实现只保存最佳边界，最后切片生成答案。

**可视化的额外代价。** 本章演示版会保存多个子串快照，便于观察状态。这会额外复制字符串，最坏可能需要 O(|s|²) 的记录时间和空间；上面的线性复杂度只属于返回最终答案的 `min_window`，不属于轨迹收集器。""",
    64: """**完备性与唯一性。** 对元素互不相同的输入，每个子集对应唯一的一串“选或不选”的决策，递归访问全部决策序列，因此不漏不重。排列在每层选择一个尚未使用的位置；每个排列同样对应唯一决策路径。组合只从当前值往后选，使同一组数的不同顺序不再重复出现。含重复值的输入需要额外去重规则，本章不能自动保证值级别唯一。

**撤销与副本。** 递归返回时，`path.pop()` 和 `used` 的恢复把状态还原到进入分支前。相邻分支才不会相互污染。保存答案时要用 `path.copy()`：否则答案数组里多次存入的是同一个可变列表的引用。

**复杂度要算输出。** 子集时间为 O(n·2ⁿ)，排列为 O(n·n!)，组合为 O(k·C(n,k))；这里包含构造答案副本的成本。工作栈、当前路径与使用标记的额外空间是 O(n)，但完整返回值还需要与全部输出元素数量相当的空间。例如 10! 已经有 3,628,800 个排列，不能只看工作栈很小就断言内存没有问题。

**枚举与计数不同。** 只问方案数时，公式或动态规划可能避免逐个生成；要求列出所有方案时，算法必须付出构造输出的成本。输入规模变大后，应先估算输出数量，再决定是全部保留、逐个生成，还是改问计数问题。""",
}

WINDOW_DERIVATION = r'''先区分两个问题的目标，不能只记一份窗口模板。

**最长无重复子串。** `counts[c]` 是窗口内字符 `c` 的个数。右端读入字符后，如果该字符重复，就依次移走左端字符；恢复无重复后，才用 `right-left+1` 更新最长长度。例如 `abcaac` 的合法窗口依次是 `a`、`ab`、`abc`、`bca`、`a`、`ac`，最长为 3。读入第二个连续的 `a` 时，仅移走 `b` 不能消除重复，需要继续移走 `c` 和旧的 `a`。

**最短覆盖子串。** `need[c]` 不是窗口频次，而是“目标需要的次数减去窗口中已有的次数”；负值表示有富余。`missing` 是尚未满足的字符总个数，包含目标中的重复字符。右端加入一个仍然缺少的字符时，`missing` 减一。它变成 0 后，先保存候选答案，再试着移走左端字符；一旦移走必需字符，停止收缩。

以 `s='ADOBECODEBANC'`、`t='ABC'` 为例，统一用左闭右开区间 `[left, end)`：

| 右端位置 | 仍能覆盖的最短候选 | 长度 | 再移走哪个字符会失去覆盖 |
|---|---|---:|---|
| 5，读到 `C` | `[0,6)` = `ADOBEC` | 6 | 下标 0 的 `A` |
| 10，读到 `A` | `[5,11)` = `CODEBA` | 6 | 下标 5 的 `C` |
| 12，读到 `C` | `[9,13)` = `BANC` | 4 | 下标 9 的 `B` |

因此答案是 `BANC`，长度 **4**。`[10,13)` 是 `ANC`，长度 3，却缺少 `B`，不能记为答案。下方的运行轨迹会用实际计数状态核对这三次候选。

两个问题都只让左右端点向前移动，但更新答案的条件不同。保存答案下标，最后只切片一次，避免在收缩循环中反复复制字符串。'''

WINDOW_TRACE = '''
def trace_min_window(s, t):
    """记录真实合法候选；返回答案及 (右端, 左端, 右开端, 子串, 缺失数)。"""
    if not t:
        return '', []
    need = Counter(t)
    missing = len(t)
    left = 0
    best = None
    rows = []
    for right, char in enumerate(s):
        if need[char] > 0:
            missing -= 1
        need[char] -= 1
        while missing == 0:
            rows.append((right, left, right + 1, s[left:right + 1], missing))
            if best is None or right + 1 - left < best[1] - best[0]:
                best = (left, right + 1)
            removed = s[left]
            need[removed] += 1
            left += 1
            if need[removed] > 0:
                missing += 1
    return ('' if best is None else s[best[0]:best[1]]), rows

answer, trace_rows = trace_min_window('ADOBECODEBANC', 'ABC')
assert answer == min_window('ADOBECODEBANC', 'ABC') == 'BANC'
assert len(answer) == 4
assert (12, 9, 13, 'BANC', 0) in trace_rows
assert all(Counter('ABC') <= Counter(row[3]) for row in trace_rows)
show_table(['右端下标', 'left', 'end（不含）', '合法候选', 'missing'], trace_rows)
'''

BACKTRACK_TRACE = '''
def trace_subsets(nums):
    """把选、不选、保存和撤销事件显式记录下来。"""
    path = []
    result = []
    events = []
    def visit(index):
        events.append((index, '进入', tuple(path)))
        if index == len(nums):
            result.append(path.copy())
            events.append((index, '保存副本', tuple(path)))
            return
        events.append((index, '不选当前元素', tuple(path)))
        visit(index + 1)
        path.append(nums[index])
        events.append((index, '选当前元素', tuple(path)))
        visit(index + 1)
        path.pop()
        events.append((index, '撤销选择', tuple(path)))
    visit(0)
    assert path == []
    return result, events

traced_subsets, backtrack_events = trace_subsets([1, 2])
assert traced_subsets == subsets([1, 2]) == [[], [2], [1], [1, 2]]
show_table(['待处理下标', '动作', 'path 快照'], backtrack_events)
'''

EXTRA_TESTS = {
    2: '''
# 冰点不足以区分华氏公式的斜率，增加非零摄氏度用例。
assert math.isclose(convert_temperature(100)[1], 212, abs_tol=1e-9)
try:
    smallest_even_multiple(0)
except ValueError:
    pass
else:
    raise AssertionError('必须拒绝不符合正整数契约的 0')
assert (2 * 5 if 5 % 2 == 0 else 5) == 5
''',
    29: '''
assert min_window('ADOBECODEBANC', 'ABC') == 'BANC'
assert len(min_window('ADOBECODEBANC', 'ABC')) == 4
assert min_window('aab', 'ab') == 'ab'
assert min_window('abc', '') == ''
''',
    64: '''
# 用标准库独立枚举，比较方案本身，而不只比较数量。
import itertools
for n in range(6):
    items = list(range(n))
    expected = {combo for k in range(n + 1) for combo in itertools.combinations(items, k)}
    assert set(map(tuple, subsets(items))) == expected
    assert set(map(tuple, permute(items))) == set(itertools.permutations(items))
copy_check = subsets([1, 2])
unchanged = [part.copy() for part in copy_check[1:]]
copy_check[0].append(99)
assert copy_check[1:] == unchanged
''',
}


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def readable_code(source):
    """Expand compact suites; preserve readable multiline embedded native sources."""
    parsed = ast.parse(source)
    pieces = []
    for node in parsed.body:
        multiline = any(isinstance(x, ast.Constant) and isinstance(x.value, str)
                        and '\n' in x.value for x in ast.walk(node))
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and multiline:
            text = ast.get_source_segment(source, node)
        else:
            text = ast.unparse(node)
        pieces.append(text)
    result = '\n\n'.join(pieces)
    if ast.dump(ast.parse(result)) != ast.dump(parsed):
        raise ValueError('Formatting changed the program AST')
    return result


def sections(text):
    parts = re.split(r'^## ([一二三四五六七八])、[^\n]*\n', text, flags=re.M)
    result = {i: [] for i in range(1, 9)}
    for index in range(1, len(parts), 2):
        number = SECTION_NAMES[parts[index]]
        content = parts[index + 1].strip()
        if content not in result[number]:
            result[number].append(content)
    joined = {key: '\n\n'.join(value) for key, value in result.items()}
    # N002 has its test discussion inside section five and a duplicated section-three heading.
    if not joined[6] and 'cell8 逐条看：' in joined[5]:
        joined[5], joined[6] = joined[5].split('cell8 逐条看：', 1)
    if any(not joined[key].strip() for key in joined):
        raise ValueError('A chapter note is missing a required teaching section')
    return joined


def clean_prose(text, number):
    names = {0: '学习目标', 1: '思路推导', 2: '接口说明', 3: '分段实现',
             4: '正确性与复杂度', 5: '运行示例', 6: '运行示例',
             7: '自动测试', 8: '自动测试', 9: '练习', 10: '题目映射', 11: '掌握检查'}
    chunks = re.split(r'(```[\s\S]*?```)', text)
    for i in range(0, len(chunks), 2):
        s = chunks[i]
        for old, new in REPLACEMENTS.get(number, []):
            s = s.replace(old, new)
        s = re.sub(r'\bcell\s*(\d+)\b', lambda m: '“' + names.get(int(m[1]), '对应代码') + '”部分', s, flags=re.I)
        s = re.sub(r'(?:notebook\s*)?第\s*([0368])\s*格', lambda m: '“' + names[int(m[1])] + '”部分', s)
        s = s.replace('逐字照抄', '对应实现').replace('零注释、紧凑写法', '可展开阅读的实现')
        s = s.replace('绿灯', '通过').replace('说人话', '直观解释')
        # This old structure description is no longer applicable after the rewrite.
        s = re.sub(r'顺带认识一下整本课程 notebook 的固定结构[^\n]*', '', s)
        chunks[i] = s
    return ''.join(chunks).strip()


def normalize_explanation(text):
    """Avoid repeating a whole old compressed program in the explanation section."""
    def replace(match):
        language, source = match.group(1), match.group(2)
        if language.lower() in {'python', 'py', 'javascript', 'js', 'sql', 'bash', 'sh'}:
            if len(source.splitlines()) > 12:
                return '（对应程序见下方分段实现与完整代码。）'
            if language.lower() in {'python', 'py'}:
                try:
                    source = readable_code(source)
                except SyntaxError:
                    pass  # A loop body or a single return is an explanatory fragment.
        return f'```{language}\n{source.strip()}\n```'
    return re.sub(r'```([^\n]*)\n([\s\S]*?)```', replace, text)


def split_markdown(text, limit=1800):
    """Split at paragraph boundaries outside fences, without cutting tables or code."""
    parts, current, fenced, details = [], [], False, 0
    for line in text.splitlines():
        if line.lstrip().startswith('```'):
            fenced = not fenced
        if not fenced:
            details += line.count('<details>') - line.count('</details>')
        if not line.strip() and not fenced and details == 0 and sum(map(len, current)) >= limit:
            parts.append('\n'.join(current).strip())
            current = []
        else:
            current.append(line)
    if current:
        parts.append('\n'.join(current).strip())
    return [part for part in parts if part]


def assignment_literal(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    return None


def core_excerpt(source, spec):
    n = spec['number']
    if 152 <= n <= 156:
        values = assignment_literal(source, 'SQL_QUERIES')
        name, query = next(iter(values.items()))
        return 'sql', query, name
    if n == 160:
        values = assignment_literal(source, 'SHELL_SOURCES')
        name, script = next(iter(values.items()))
        return 'bash', script, name
    if 161 <= n <= 163:
        native = assignment_literal(source, 'JS_SOURCE')
        functions = re.split(r'\n(?=(?:async )?function |class )', native)
        body = functions[1] if len(functions) > 1 else native
        return 'javascript', body, '本章第一个 JavaScript 接口'
    if 164 <= n <= 167:
        source = assignment_literal(source, 'THREAD_SOURCE')
    tree = ast.parse(source)
    candidates = [x for x in tree.body if isinstance(x, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))]
    wanted = re.match(r'[A-Za-z_]\w*', spec['required_code'][0])
    node = next((x for x in candidates if wanted and x.name == wanted[0]), None)
    if node is None:
        node = next((x for x in candidates if x.name not in {'ListNode', 'TreeNode'}), candidates[0] if candidates else None)
    if node is None:
        return 'python', readable_code(source), '本章核心操作'
    label = node.name
    if isinstance(node, ast.ClassDef) and len(ast.unparse(node).splitlines()) > 65:
        methods = [x for x in node.body if isinstance(x, ast.FunctionDef) and not x.name.startswith('__')]
        node = next((x for x in methods if not x.name.startswith('_')), methods[0])
        label += '.' + node.name
    return 'python', ast.unparse(node), label


def implementation_chunks(source):
    pieces, imports = [], []
    for node in ast.parse(source).body:
        text = ast.get_source_segment(source, node)
        if getattr(node, 'decorator_list', []):
            text = '\n'.join('@' + ast.unparse(d) for d in node.decorator_list) + '\n' + text
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(text)
            continue
        if imports:
            pieces.append(('导入本章使用的库', '\n'.join(imports)))
            imports = []
        name = getattr(node, 'name', '')
        if not name and isinstance(node, ast.Assign):
            name = ', '.join(ast.unparse(x) for x in node.targets)
        pieces.append((name or '初始化与接口绑定', text))
    if imports:
        pieces.append(('导入本章使用的库', '\n'.join(imports)))
    return pieces


def enrich_notebook(nb, spec, root=ROOT):
    """Called by course_builder on its freshly constructed 12-cell source notebook."""
    if len(nb.cells) != 12 or [nb.cells[i].cell_type for i in (3, 6, 8)] != ['code'] * 3:
        raise ValueError('Expected the reviewed source notebook; do not overwrite unknown layouts')
    number = spec['number']
    comment_path = root / 'comment' / (Path(spec['path']).stem + '.md')
    comment_text = comment_path.read_text(encoding='utf-8')
    sec = {key: clean_prose(value, number) for key, value in sections(comment_text).items()}
    if number == 29:
        sec[3] = WINDOW_DERIVATION
    if number in CORRECTNESS_REVISIONS:
        sec[5] = CORRECTNESS_REVISIONS[number]
    if number == 163:
        sec[3] = sec[3].replace('和完成顺序（1→2→0）无关', '与完成顺序无关；任务 0 和 2 的先后不作保证')
        sec[1] = sec[1].replace('完成顺序是 1ms、2ms、3ms', '理想化时钟下可能按 1ms、2ms、3ms 完成；实际先后还取决于调度')
    if number == 2:
        sec[6] = sec[6].replace('补救办法是自己在练习里补一条', '本次已增加一条').replace('——本套断言没盖到的角落，练习里补上', '，用于补齐原测试的盲区')
    original = nb.cells[3].source
    code = readable_code(original)
    original_tests = nb.cells[8].source
    test_nodes = ast.parse(original_tests).body
    success = ast.unparse(test_nodes.pop())
    tests = readable_code(ast.unparse(ast.Module(body=test_nodes, type_ignores=[])))
    tests += '\n' + EXTRA_TESTS.get(number, '') + '\n' + success
    demo = nb.cells[6].source
    if number == 29:
        demo += WINDOW_TRACE
    if number == 64:
        demo += BACKTRACK_TRACE
    language, core, label = core_excerpt(code, spec)
    body = []

    def md(text, tag=None):
        for part in split_markdown(text):
            cell = nbformat.v4.new_markdown_cell(part)
            if tag:
                cell.metadata['tags'] = [tag]
            body.append(cell)

    def cell(source, tag):
        c = nbformat.v4.new_code_cell(source.strip())
        c.metadata['tags'] = [tag]
        body.append(c)

    md(nb.cells[0].source
       + f'\n\n**配套讲解来源：** [同名逐章意见](../../comment/{comment_path.name})。')
    md('本章阅读顺序：**先明白问题 → 补基础 → 手算 → 看核心片段 → 分段运行 → 核对测试**。'
       '需要复制使用时，跳到末尾“完整代码”，它包含全部依赖、实现和测试。')
    md('## 1. 通俗解释：输入什么，要得到什么\n\n' + sec[1], 'plain-explanation')
    md('## 2. 基础知识：先读懂这些词\n\n' + sec[2], 'foundations')
    md('## 3. 思路推导：从小例子开始\n\n' + sec[3], 'derivation')
    md(f'## 4. 核心代码：{label}\n\n'
       '先关注决定答案的状态与更新操作。这是完整实现的对应片段，不是另一套解法；'
       '导入、辅助结构及其余接口在下一节补全。\n\n'
       f'```{language}\n{core.strip()}\n```', 'core-code')
    md('### 逐段读懂代码\n\n' + normalize_explanation(sec[4]), 'code-explanation')
    md('## 5. 分段实现：按顺序运行\n\n' + nb.cells[2].source.split('\n\n', 1)[-1])
    for name, source in implementation_chunks(code):
        md('### ' + name)
        cell(source, 'implementation')
    md('## 6. 运行示例与状态可视化\n\n'
       '先预测结果再运行。手算表帮助解释过程；下面的表由当前实现计算。'
       '若表只展示输入输出，它并不代替内部状态轨迹。')
    cell(demo, 'visualization')
    md('## 7. 正确性、适用条件与复杂度\n\n'
       + nb.cells[4].source.split('\n\n', 1)[-1])
    md('### 展开理解\n\n' + sec[5], 'correctness-explanation')
    md('## 8. 单元测试：每个用例在检查什么\n\n' + normalize_explanation(sec[6]), 'test-explanation')
    cell(tests, 'tests')
    md('## 9. 练习：先尝试，再看提示\n\n'
       + '\n\n'.join(f'**练习 {i + 1}：** {x}。' for i, x in enumerate(spec['exercises'])))
    md('<details>\n<summary>展开思路提示（不是完整答案）</summary>\n\n'
       + sec[7] + '\n\n</details>', 'exercise-hints')
    md('## 10. 完整代码：可独立运行\n\n'
       '下面这一格包含**全部导入、全部接口和验证用例**，不依赖前面的单元格。'
       '可以重启内核后只运行这一格，也可以复制到 `.py` 文件后运行。'
       '在 Notebook 中 Run All 时会再验证一次，这是为独立复制使用保留的完整版本。'
       + ('\n\n本章包含真实的 SQL／Shell／JavaScript／线程程序，Python 部分负责创建示例、调用运行时和断言。'
          '嵌入的程序源码也在下面完整显示；缺少相应运行时应安装依赖，不能用模拟结果替代。' if number >= 152 and number <= 167 else ''))
    full = '# 完整实现：本单元格不依赖其他单元格。\n' + code + '\n\n# 示例与回归测试\n' + tests
    cell(full, 'standalone')
    md('## 11. 代表题与迁移\n\n' + sec[8]
       + '\n\n**题面入口：** ' + ' · '.join(f"[{p['id']}]({p['official_url']})" for p in spec['representative_problems'] if p.get('official_url'))
       + '\n\n题目用于知识映射；本章完整代码遵循教学接口，不等于每道题的完整平台提交。')
    md('## 12. 掌握检查\n\n'
       '合上代码，说明输入输出、核心变量的含义、每次更新为什么成立，以及一个边界情况。'
       '再完成一道练习，不能只凭“运行通过”判断掌握。\n\n'
       '**继续学习：** [课程索引](../../COURSE_INDEX.md)。')
    for i, c in enumerate(body):
        c.id = f'n{number:03d}-r{i:03d}'
    result = nbformat.v4.new_notebook(cells=body, metadata=copy.deepcopy(nb.metadata))
    result.metadata.course.execution = 'not_run'
    result.metadata.course.rewrite = {
        'version': VERSION,
        'comment_path': str(comment_path.relative_to(root)),
        'comment_sha256': digest(comment_text),
        'algorithm_ast_unchanged': ast.dump(ast.parse(code)) == ast.dump(ast.parse(original)),
        'original_test_ast_sha256': digest(ast.dump(ast.parse(original_tests))),
        'standalone_sha256': digest(full.strip()),
        'brief_present': (root / 'comment/REWRITE_BRIEF.md').exists(),
    }
    nbformat.validate(result)
    return result
