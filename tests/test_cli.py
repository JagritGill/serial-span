import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run([sys.executable,'-B','-m','serial_span',*map(str,args)],
                          cwd=ROOT,text=True,capture_output=True,timeout=10)


class CliTests(unittest.TestCase):
    def test_cycle_gate_json(self):
        r=run('examples/cycle.json','--json','--check')
        self.assertEqual(r.returncode,1);self.assertEqual(r.stderr,'')
        report=json.loads(r.stdout)
        self.assertFalse(report['coherent'])
        self.assertEqual(report['witness']['serials'],['0','100','200'])
        self.assertEqual(report['largest_coherent_subset']['excluded_count'],1)

    def test_wrap_gate_and_plain_report(self):
        r=run('examples/wrap.json','--check')
        self.assertEqual(r.returncode,0)
        self.assertIn('span=12',r.stdout)
        r=run('examples/cycle.json')
        self.assertEqual(r.returncode,0)
        self.assertIn('comparison cycle: 0 < 100 < 200 < 0',r.stdout)

    def assert_bad(self,data):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'input.json');p.write_bytes(data);r=run(p)
        self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'')
        self.assertNotIn('Traceback',r.stderr)
        self.assertNotIn('\x1b',r.stderr)

    def test_json_parser_rejections(self):
        for data in [b'{',b'NaN',b'Infinity',b'{"bits":8,"bits":8,"serials":["0"]}',
                     b'1'*5000,b'['*2000+b']'*2000,b'null']:
            self.assert_bad(data)

    def test_bytes_and_resource_limits(self):
        for data in [b'\xff',b'\xef\xbb\xbf{}',b' '*32769,
                     b'{"bits":8,"serials":["bad\\u001b[31m"]}']:
            self.assert_bad(data)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'exact.json');raw=b'{"bits":8,"serials":["0"]}'
            p.write_bytes(raw+b' '*(32768-len(raw)))
            self.assertEqual(run(p,'--check').returncode,0)

    def test_reject_nonregular_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            real=Path(d,'real');real.write_text('{"bits":8,"serials":["0"]}')
            link=Path(d,'link');link.symlink_to(real)
            fifo=Path(d,'fifo');os.mkfifo(fifo)
            for p in [Path(d),link,fifo,Path(d,'missing')]:
                r=run(p);self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'')

    def test_argument_errors(self):
        for args in [(),('examples/cycle.json','--unknown')]:
            r=run(*args);self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'')

    def test_64_bit_json_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'wide.json')
            p.write_text(json.dumps(dict(bits=64,serials=[str(2**64-2),'1'])))
            r=run(p,'--json','--check')
        self.assertEqual(r.returncode,0)
        report=json.loads(r.stdout)
        self.assertEqual(report['minimum_arc'],dict(start=str(2**64-2),end='1',span='3'))
        self.assertIsInstance(report['modulus'],str)
        self.assertEqual(report['modulus'],str(2**64))


if __name__=='__main__':unittest.main()
