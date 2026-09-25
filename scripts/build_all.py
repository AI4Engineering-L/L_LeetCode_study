"""Materialize the authored lesson modules; execution is a separate explicit command."""
from pathlib import Path
import importlib
import argparse
from course_builder import build
for source in sorted(Path(__file__).parent.glob('lessons_*.py')):
    importlib.import_module(source.stem)
parser = argparse.ArgumentParser()
parser.add_argument('--ids', nargs='*')
args=parser.parse_args()
build({int(x.lstrip('Nn')) for x in args.ids} if args.ids else None)
