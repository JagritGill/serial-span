from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.check_release import FILES, check

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in FILES:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def test_inventory_mutations(self):
        self.assertEqual(check(self.root)['files'], len(FILES))
        extra = self.root / 'unexpected.txt'
        extra.write_text('synthetic')
        with self.assertRaises(ValueError): check(self.root)
        extra.unlink()
        (self.root / 'LICENSE').unlink()
        with self.assertRaises(ValueError): check(self.root)

    def test_disclosure_patterns(self):
        p = self.root / 'NOTICE.md'
        for value in ['AK'+'IA'+'Z'*16, 'gh'+'p_'+'x'*36,
                      '/'+'Users'+'/synthetic/file', '-----BEGIN '+'RSA PRIVATE KEY-----']:
            p.write_text(value)
            with self.assertRaises(ValueError): check(self.root)

    def test_mode_symlink_and_link(self):
        p = self.root / 'NOTICE.md'
        p.write_text('[missing](missing.md)')
        with self.assertRaises(ValueError): check(self.root)
        p.write_text('safe'); p.chmod(0o755)
        with self.assertRaises(ValueError): check(self.root)
        p.unlink(); p.symlink_to(self.root / 'README.md')
        with self.assertRaises(ValueError): check(self.root)

    def test_syntax_and_control_bytes(self):
        p = self.root / 'serial_span/__init__.py'
        p.write_text('def (')
        with self.assertRaises(SyntaxError): check(self.root)
        p.write_text('"safe"\n')
        (self.root / 'NOTICE.md').write_bytes(b'x\x00')
        with self.assertRaises(ValueError): check(self.root)


if __name__ == '__main__':
    unittest.main()
