"""Run on the isolated judge host with its data root and a saved website plan."""
import argparse
import importlib.util
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--root', required=True)
    parser.add_argument('--mode', choices=('check', 'apply', 'rollback'), default='check')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('problem_code_storage', Path(__file__).with_name('problem_code_storage.py'))
    storage = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(storage)
    plan = json.loads(Path(args.plan).read_text())
    if plan.get('version') != 1:
        raise ValueError('Unsupported problem numbering plan')
    rows = plan['rows']
    storage.check_storage(rows, args.root, rollback=args.mode == 'rollback')
    if args.mode != 'check':
        storage.rename_storage(rows, args.root, rollback=args.mode == 'rollback',
                               journal=Path(args.plan).with_suffix('.judge-journal.jsonl'))
    print('%s: %d problem data directories' % (args.mode, len(rows)))


if __name__ == '__main__':
    main()
