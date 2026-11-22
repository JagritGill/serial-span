import argparse
import json
import sys

from . import InputError, analyze
from .input import load
from .report import render


def main(argv=None):
    parser = argparse.ArgumentParser(description='Audit a local wrapping serial batch without network access.')
    parser.add_argument('snapshot', help='regular UTF-8 JSON file')
    parser.add_argument('--json', action='store_true', help='emit JSON; serial-sized values remain decimal strings')
    parser.add_argument('--check', action='store_true', help='exit 1 unless the whole batch fits strictly within half a turn')
    args = parser.parse_args(argv)
    try:
        report = analyze(load(args.snapshot))
    except InputError as exc:
        print(f'serial-span: invalid input: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else render(report))
    return 1 if args.check and not report['coherent'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
