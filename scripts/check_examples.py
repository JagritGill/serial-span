"""Run the documented synthetic reports and gate outcomes."""

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    cases = [
        (['examples/cycle.json'], 0, False, 2),
        (['examples/cycle.json', '--check'], 1, False, 2),
        (['examples/cycle.json', '--json', '--check'], 1, False, 2),
        (['examples/wrap.json', '--check'], 0, True, 4),
        (['examples/wrap.json', '--json', '--check'], 0, True, 4),
        (['examples/half.json', '--json', '--check'], 1, False, 2),
        (['examples/weighted.json', '--json'], 0, False, 4),
        (['examples/weighted.json', '--check'], 1, False, 4),
    ]
    for args, code, coherent, retained in cases:
        result = subprocess.run([sys.executable, '-B', '-m', 'serial_span', *args],
                                cwd=ROOT, text=True, capture_output=True, timeout=10)
        assert result.returncode == code, (args, result.returncode, result.stderr)
        assert not result.stderr, (args, result.stderr)
        if '--json' in args:
            report = json.loads(result.stdout)
            assert report['coherent'] == coherent
            assert report['largest_coherent_subset']['retained_count'] == retained
            if args[0].endswith('weighted.json'):
                assert report['largest_coherent_subset']['retained_records'] == [2,3,4,5]
            if args[0].endswith('half.json'):
                assert report['undefined_observation_pairs'] == 2
        else:
            assert f'coherent={str(coherent).lower()}' in result.stdout
            assert f'retain={retained}' in result.stdout
    print('8 CLI examples passed, including expected --check exit 1 cases.')


if __name__ == '__main__':
    main()
