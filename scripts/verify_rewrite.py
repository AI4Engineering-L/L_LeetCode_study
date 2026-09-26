"""Check teaching structure, retained algorithms/tests, and standalone executability.

This verifies concrete artifacts. It does not certify all prose, solve open exercises,
or claim acceptance by LeetCode's online judge. Run after execute_course.py.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import json
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import nbformat

from course_builder import LESSONS, ROOT, SPEC
from rewrite_from_comments import VERSION, digest


def source_hash(nb):
    value = json.dumps([[c.cell_type, c.source] for c in nb.cells],
                       ensure_ascii=False, separators=(',', ':'))
    return digest(value)


def same_ast(left, right):
    return ast.dump(ast.parse(left)) == ast.dump(ast.parse(right))


def check_one(spec, execution):
    path = ROOT / spec['path']
    nb = nbformat.read(path, as_version=4)
    nbformat.validate(nb)
    record = {'id': spec['id'], 'path': spec['path'], 'verification': 'failed'}
    assert nb.metadata.course.id == spec['id'], 'Wrong chapter ID'
    rewrite = nb.metadata.course.rewrite
    assert rewrite['version'] == VERSION, 'Wrong rewrite version'
    comment = ROOT / rewrite['comment_path']
    assert rewrite['comment_sha256'] == digest(comment.read_text(encoding='utf-8')), 'Comment changed after build'
    assert execution['execution'] == nb.metadata.course.execution == 'passed', 'Fresh-kernel execution missing'
    assert execution['source_sha256'] == source_hash(nb), 'Execution report belongs to different source'

    tags = {tag for cell in nb.cells for tag in cell.metadata.get('tags', [])}
    required = {'plain-explanation', 'foundations', 'derivation', 'core-code',
                'code-explanation', 'implementation', 'visualization', 'tests',
                'exercise-hints', 'standalone'}
    assert required <= tags, f'Missing teaching sections: {required - tags}'
    for tag in ('plain-explanation', 'foundations', 'derivation', 'code-explanation'):
        text = '\n'.join(c.source for c in nb.cells if tag in c.metadata.get('tags', []))
        assert len(text) > 100, f'{tag} contains only a heading'
    for c in nb.cells:
        if 'exercise-hints' in c.metadata.get('tags', []):
            assert c.source.count('<details>') == c.source.count('</details>') == 1, 'Broken collapsed exercise hints'

    implementation = '\n\n'.join(c.source for c in nb.cells if 'implementation' in c.metadata.get('tags', []))
    original = LESSONS[spec['number']]
    assert same_ast(implementation, original['code']), 'Algorithm changed while reformatting'
    tests = [c for c in nb.cells if 'tests' in c.metadata.get('tags', [])]
    assert len(tests) == 1, 'Expected exactly one regression-test cell'
    expected_tests = ast.parse(original['tests']).body
    actual_tests = ast.parse(tests[0].source).body
    assert len(actual_tests) >= len(expected_tests)
    assert all(ast.dump(a) == ast.dump(b) for a, b in zip(expected_tests, actual_tests)), 'Original regression tests removed or changed'

    standalone = [c for c in nb.cells if 'standalone' in c.metadata.get('tags', [])]
    assert len(standalone) == 1, 'Expected one complete, independently runnable program'
    full = standalone[0].source
    assert digest(full) == rewrite['standalone_sha256'], 'Standalone source hash mismatch'
    assert same_ast(full, implementation + '\n\n' + tests[0].source), 'Full program differs from teaching implementation/tests'
    code_cells = [c for c in nb.cells if c.cell_type == 'code']
    assert all(c.execution_count is not None for c in code_cells), 'An executable cell was not run'
    assert not any(o.output_type == 'error' for c in code_cells for o in c.outputs), 'Saved error output'

    # A new process, isolated Python path, and an empty working directory prevent
    # variables/imports from earlier notebook cells or repository files leaking in.
    with tempfile.TemporaryDirectory(prefix='leetcode-standalone-') as directory:
        program = Path(directory) / 'lesson.py'
        program.write_text(full, encoding='utf-8')
        completed = subprocess.run([sys.executable, '-I', str(program)], cwd=directory,
                                   text=True, capture_output=True, timeout=90)
    assert completed.returncode == 0, completed.stderr[-5000:] or completed.stdout[-5000:]
    marker = f"{spec['id']}: 所有本章断言通过"
    assert marker in completed.stdout, 'Standalone regression-test completion marker missing'
    record.update(verification='passed', standalone_execution='passed',
                  algorithm_ast_unchanged=True, original_tests_preserved=True,
                  notebook_source_sha256=source_hash(nb), standalone_sha256=digest(full),
                  comment_sha256=rewrite['comment_sha256'],
                  code_cells=len(code_cells), total_cells=len(nb.cells),
                  markdown_characters=sum(len(c.source) for c in nb.cells if c.cell_type == 'markdown'),
                  standalone_stdout=completed.stdout.strip(),
                  standalone_stderr=completed.stderr.strip())
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', nargs='*', help='Optional chapter IDs; omit for full verification')
    args = parser.parse_args()
    for source in sorted((ROOT / 'scripts').glob('lessons_*.py')):
        importlib.import_module(source.stem)
    entries = SPEC['notebooks']
    expected = {n['path'] for n in entries}
    actual = {str(p.relative_to(ROOT)) for p in (ROOT / 'notebooks').rglob('*.ipynb')}
    assert actual == expected and len(actual) == 175, 'Fixed curriculum paths mismatch'
    if args.ids:
        wanted = {x.upper() for x in args.ids}
        entries = [n for n in entries if n['id'] in wanted]
        assert len(entries) == len(wanted), 'Unknown chapter ID'
    execution = json.loads((ROOT / 'reports/execution.json').read_text())
    executed = {n['id']: n for n in execution['results']}
    results = []
    for spec in entries:
        try:
            item = check_one(spec, executed[spec['id']])
        except Exception as error:
            item = {'id': spec['id'], 'path': spec['path'], 'verification': 'failed',
                    'error': f'{type(error).__name__}: {error}'}
        results.append(item)
        print(item['id'], item['verification'], item.get('error', '').split('\n')[0], flush=True)
    passed = sum(x['verification'] == 'passed' for x in results)
    report = {
        'version': VERSION, 'updated_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(), 'notebook_total': len(actual),
        'checked': len(results), 'passed': passed, 'failed': len(results)-passed,
        'full_course_verified': len(results) == 175 and passed == 175,
        'source_brief': {'path': 'comment/REWRITE_BRIEF.md',
                         'present': (ROOT / 'comment/REWRITE_BRIEF.md').exists(),
                         'used': False,
                         'note': '指定文件在本次读取的仓库快照中不存在；采用用户本轮要求、comment/README.md 与 175 份同名逐章意见。'},
        'comment_readme_sha256': digest((ROOT / 'comment/README.md').read_text()),
        'scope': 'Teaching-section structure, unchanged implementation ASTs, retained tests, fresh-kernel source matching, and isolated standalone execution. Not exhaustive prose or online-judge verification.',
        'results': results,
    }
    (ROOT / 'reports/rewrite_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    lines = ['# Notebook 教学改写与验收', '',
             f"- 已检查：{len(results)} / 175；通过：{passed}；失败：{len(results)-passed}。",
             '- 每章：通俗解释、基础知识、手算推导、核心片段、分段实现、示例可视化、测试讲解、练习、独立完整代码。',
             '- 算法实现经 AST 比较保持不变；原有回归测试保留，另增加定向测试。',
             '- 完整代码在新 Python 进程、隔离导入路径与空工作目录中独立执行；SQL、Shell、JS、线程调用真实运行时。',
             '- 每章报告绑定源码 SHA-256，重建后不能沿用旧的执行结论。', '',
             '## 采用的意见与边界', '',
             '`comment/REWRITE_BRIEF.md` 在所读取的快照中不存在，未声称已读取或吸收。改写采用用户明确要求、`comment/README.md` 以及 175 份同名逐章说明；原意见文件未修改。', '',
             '## 定向纠错与补强', '',
             '| 章节 | 修订 |', '|---|---|',
             '| N001 | 区分确定性与正确性；实例方法、判题接口、字长成本。 |',
             '| N002 | 分支反例 5 不误写为 25；补 100°C→212°F 与非法正整数输入测试。 |',
             '| N029 | BANC 长度为 4、区间 [9,13)；纠正收缩轨迹与丢弃左端点的证明，增加真实计数轨迹。 |',
             '| N064 | 明确选/不选、保存副本、撤销；标准库独立枚举对照及别名测试；输出内存计入复杂度。 |',
             '| N113 | 消除数位 DP 的过度规模承诺，保留位数和递归边界。 |',
             '| N163 | 同一到期时刻不保证实际完成顺序；结果顺序与完成顺序区分。 |', '',
             '## 核验范围', '',
             '以上通过表示实际执行及列出的结构、源码和测试检查通过，不表示所有讲解已经逐句专家复审，也不表示全部代表题都提交过 LeetCode。未完成练习不作为空实现塞入可执行单元格。', '',
             '## 逐章结果', '', '| ID | 验收 | 可执行单元格 | 独立完整代码 |', '|---|---|---:|---|']
    lines += [f"| {x['id']} | {x['verification']} | {x.get('code_cells','—')} | {x.get('standalone_execution','—')} |" for x in results]
    (ROOT/'reports/REWRITE_REPORT.md').write_text('\n'.join(lines)+'\n')
    if passed != len(results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
