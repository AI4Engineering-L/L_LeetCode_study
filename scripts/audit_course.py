"""Validate fixed paths, saved execution evidence and specification interface roots.

This is a structural audit, not a replacement for algorithm or teaching review.
"""
from pathlib import Path
import json
import re
import nbformat

ROOT = Path(__file__).resolve().parents[1]

def audit():
    spec = json.loads((ROOT/'specs/curriculum.json').read_text())
    report_path = ROOT/'reports/execution.json'
    report = json.loads(report_path.read_text())
    records = {item['id']:item for item in report['results']}
    expected = {entry['path'] for entry in spec['notebooks']}
    actual = {str(path.relative_to(ROOT)) for path in (ROOT/'notebooks').rglob('*.ipynb')}
    assert actual == expected and len(actual) == 175
    cells = 0
    for entry in spec['notebooks']:
        nb = nbformat.read(ROOT/entry['path'],as_version=4)
        nbformat.validate(nb)
        assert nb.metadata.course.id == entry['id']
        assert nb.metadata.course.execution == 'passed'
        assert records[entry['id']]['execution'] == 'passed'
        code = [cell for cell in nb.cells if cell.cell_type == 'code']
        assert code and all(cell.execution_count is not None for cell in code)
        assert not any(output.output_type == 'error' for cell in code for output in cell.outputs)
        assert any(f"{entry['id']}: 所有本章断言通过" in output.get('text','')
                   for cell in code for output in cell.outputs)
        source = '\n'.join(cell.source for cell in code)
        for interface in entry['required_code']:
            root = re.search(r'[A-Za-z_]\w*',interface)
            if root:
                assert root[0] in source, (entry['id'], interface)
        cells += len(code)
    report['artifact_audit'] = {
        'fixed_paths_match_spec': True,
        'notebook_count': len(actual),
        'executed_code_cells': cells,
        'saved_error_outputs': 0,
        'required_interface_roots_present': True,
        'scope': 'Structural and saved-output audit only; not a semantic proof or a full teaching review.',
        'problem_statements_reverified_in_this_build': False,
        'official_online_judge_submissions': 0
    }
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report['artifact_audit'],ensure_ascii=False,indent=2))

if __name__=='__main__':
    audit()
