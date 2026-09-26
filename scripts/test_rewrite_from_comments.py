"""Regression tests for the notebook transformation, not for algorithm answers."""
import ast
import unittest

from rewrite_from_comments import implementation_chunks, readable_code, split_markdown


class RewriteTests(unittest.TestCase):
    def check_roundtrip(self, source):
        formatted = readable_code(source)
        cells = '\n\n'.join(code for _, code in implementation_chunks(formatted))
        self.assertEqual(ast.dump(ast.parse(source)), ast.dump(ast.parse(cells)))

    def test_cache_decorator_retained(self):
        self.check_roundtrip('from functools import cache\n@cache\ndef f(x):\n    return x + 1\n')

    def test_multiple_decorators_retained(self):
        self.check_roundtrip('@a\n@b(2)\nclass C:\n    pass\n')

    def test_compact_statements_expanded(self):
        source = 'def f(x):\n    if x: return 1\n    a=2; b=3\n    return a+b\n'
        self.check_roundtrip(source)
        self.assertNotIn(';', readable_code(source))

    def test_nested_decorator_retained(self):
        self.check_roundtrip('class C:\n    @staticmethod\n    def f(x):\n        return x\n')

    def test_embedded_native_program_retained(self):
        source = 'JS_SOURCE = r"""function f(x) {\n  return x + 1;\n}\n"""\n'
        self.check_roundtrip(source)
        self.assertIn('  return x + 1;', readable_code(source))

    def test_details_not_split_between_cells(self):
        source = '<details>\n<summary>Hint</summary>\n\n' + ('paragraph\n\n' * 40) + '</details>'
        cells = split_markdown(source, limit=30)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0].count('<details>'), cells[0].count('</details>'))

    def test_code_fence_not_split(self):
        source = '```python\n' + ('print(1)\n\n' * 40) + '```'
        self.assertEqual(len(split_markdown(source, limit=30)), 1)

    def test_ordinary_paragraphs_split(self):
        self.assertGreater(len(split_markdown('long paragraph\n\n' * 40, limit=30)), 1)


if __name__ == '__main__':
    unittest.main()
