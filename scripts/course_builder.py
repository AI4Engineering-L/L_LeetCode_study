"""Build self-contained notebooks from reviewed lesson content and the fixed specification."""
from pathlib import Path
import json
import textwrap
import nbformat

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / 'specs/curriculum.json').read_text())
LESSONS = {}

TABLE = '''from IPython.display import display, HTML
from html import escape

def show_table(headers, rows):
    """Render a small, explicit state trace; no network or hidden algorithm code."""
    head = ''.join('<th>' + escape(str(x)) + '</th>' for x in headers)
    body = ''.join('<tr>' + ''.join('<td>' + escape(str(x)) + '</td>' for x in row) + '</tr>' for row in rows)
    display(HTML('<table><thead><tr>' + head + '</tr></thead><tbody>' + body + '</tbody></table>'))
'''

NODES = '''class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def list_to_nodes(values):
    dummy = tail = ListNode()
    for value in values:
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next

def nodes_to_list(head):
    values, seen = [], set()
    while head is not None:
        if id(head) in seen:
            raise ValueError('cycle in a supposedly finite list')
        seen.add(id(head))
        values.append(head.val)
        head = head.next
    return values
'''


def add(number, derivation, code, demo, tests, proof, cost, *, note=''):
    if number in LESSONS:
        raise ValueError(f'Duplicate lesson {number}')
    LESSONS[number] = dict(derivation=derivation, code=textwrap.dedent(code).strip(),
                           demo=textwrap.dedent(demo).strip(), tests=textwrap.dedent(tests).strip(),
                           proof=proof, cost=cost, note=note)


def build(selected=None):
    for spec in SPEC['notebooks']:
        number = spec['number']
        if number not in LESSONS or (selected is not None and number not in selected):
            continue
        lesson = LESSONS[number]
        if not all(lesson[k] for k in ['derivation', 'code', 'demo', 'tests', 'proof', 'cost']):
            raise ValueError(f'Incomplete lesson {number}')
        for key in ['code','demo','tests']:
            compile(lesson[key], f"N{number:03d}:{key}", 'exec')
        prereq = ', '.join(spec['prerequisites']) or '无'
        problems = '\n'.join(
            f"- {p['id']}. {p['title']}（{p['role']}）" + (f"：[官方入口]({p['official_url']})" if p.get('official_url') else '')
            for p in spec['representative_problems'])
        body = [
            nbformat.v4.new_markdown_cell(f"# {spec['id']} · {spec['title']}\n\n**目标：** {spec['teaching_goal']}。\n\n**先修：** {prereq}。本章自包含，依次运行即可；建议先读推导，再预测输出。\n\n**知识点：** {'；'.join(spec['knowledge_points'])}。"),
            nbformat.v4.new_markdown_cell('## 从问题到算法\n\n' + lesson['derivation']),
            nbformat.v4.new_markdown_cell('## 最小实现\n\n'+ ('\n\n'.join(['**本章接口：** ' + '、'.join('`'+x+'`' for x in spec['required_code']),lesson['note']])).strip()),
            nbformat.v4.new_code_cell(lesson['code']),
            nbformat.v4.new_markdown_cell('## 正确性、前提与复杂度\n\n' + lesson['proof'] + '\n\n**代价：** ' + lesson['cost']),
            nbformat.v4.new_markdown_cell('## 小实例与可视化\n\n先手算，再运行。下表由当前内核中的代码和显式小实例生成；不是预制答案图片。'),
            nbformat.v4.new_code_cell(TABLE + '\n' + lesson['demo']),
            nbformat.v4.new_markdown_cell('## 自动测试\n\n以下断言检查实现契约。测试通过不等同于一般性证明，也不表示已经提交 LeetCode 官方评测。'),
            nbformat.v4.new_code_cell(lesson['tests'] + f"\nprint('{spec['id']}: 所有本章断言通过')"),
            nbformat.v4.new_markdown_cell('## 练习：先独立完成\n\n' + '\n\n'.join(f"**练习 {i+1}：** {x}。写明输入输出与边界，先给一个手算示例，再用本章接口或独立暴力解验证。" for i,x in enumerate(spec['exercises'])) + '\n\n未完成练习不阻断教学区 Run All。验收时解释为什么正确，不只展示运行截图。'),
            nbformat.v4.new_markdown_cell('## 代表题与迁移\n\n' + problems + '\n\n这些题用于知识映射；本章实现遵循上文明确的教学契约。除原规格注明已核对身份的条目外，本轮未重新联网核验全部题面、收费权限或平台语言支持。不要把同概念教学实例当作所有官方题的完整答案。'),
            nbformat.v4.new_markdown_cell('## 自测与下一步\n\n不看代码，复述状态、不变量和一个失效条件；改变一个输入约束，判断实现是否仍成立。确认能解释边界测试后，按 `specs/curriculum.json` 的 `learning_order` 进入下一章。')
        ]
        for i,c in enumerate(body):
            c.id = f'n{number:03d}-c{i:02d}'
        nb = nbformat.v4.new_notebook(cells=body, metadata={
            'kernelspec': {'display_name':'Python 3','language':'python','name':'python3'},
            'language_info': {'name':'python'},
            'course': {'id':spec['id'],'spec_version':SPEC['version'],'prerequisites':spec['prerequisites'],
                       'runtime':spec['runtime'],'generation':'implemented','execution':'not_run',
                       'problem_statement_review':'not_reverified_in_this_build'}
        })
        from rewrite_from_comments import enrich_notebook
        nb = enrich_notebook(nb, spec, ROOT)
        nbformat.validate(nb)
        path = ROOT / spec['path']
        path.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(nb, path)
    print(f'Available content: {len(LESSONS)} lessons. Notebook files: {len(list((ROOT / "notebooks").rglob("*.ipynb")))}')
