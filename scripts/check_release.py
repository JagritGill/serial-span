"""Allowlisted release files, syntax, local links and heuristic disclosure scan."""

import ast
from pathlib import Path
import re
import stat
from urllib.parse import unquote, urlsplit

FILES = frozenset('''
.github/workflows/verify.yml
.gitignore
AGENTS.md
LICENSE
NOTICE.md
README.md
docs/architecture.md
docs/related-work.md
examples/cycle.json
examples/half.json
examples/weighted.json
examples/wrap.json
scripts/check_examples.py
scripts/check_release.py
serial_span/__init__.py
serial_span/__main__.py
serial_span/core.py
serial_span/input.py
serial_span/report.py
tests/test_cli.py
tests/test_core.py
tests/test_release.py
'''.split())
PATTERNS = [r'AKIA[0-9A-Z]{16}', r'gh[pousr]_[A-Za-z0-9]{30,}',
            r'-----BEGIN [A-Z ]*PRIVATE KEY-----', r'/(?:Users|home)/[A-Za-z0-9_.-]+/']


def check(root):
    root = Path(root).resolve()
    actual = set()
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if relative.parts[0] == '.git':
            continue
        if path.is_symlink():
            raise ValueError('symlink in release')
        if not path.is_dir():
            actual.add(relative.as_posix())
    if actual != FILES:
        raise ValueError(f'inventory mismatch: missing={sorted(FILES-actual)} extra={sorted(actual-FILES)}')
    links = syntax = 0
    for name in sorted(FILES):
        path = root / name
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o644 or info.st_size > 100000:
            raise ValueError(f'unsupported release file mode/size: {name}')
        content = path.read_text(encoding='utf-8')
        if any(ord(c) < 32 and c not in '\n\t' for c in content):
            raise ValueError(f'control byte: {name}')
        if any(re.search(p, content) for p in PATTERNS):
            raise ValueError(f'credential/private-path pattern: {name}')
        if name.endswith('.py'):
            ast.parse(content, filename=name)
            syntax += 1
        if name.endswith('.md'):
            for target in re.findall(r'\]\(([^)]+)\)', content):
                parsed = urlsplit(target)
                if parsed.scheme or not parsed.path:
                    continue
                destination = (path.parent / unquote(parsed.path)).resolve()
                if not destination.is_relative_to(root) or not destination.is_file():
                    raise ValueError(f'bad local link: {name}')
                links += 1
    return dict(files=len(FILES), local_links=links, python_syntax_files=syntax)


if __name__ == '__main__':
    print(check(Path(__file__).resolve().parents[1]))
