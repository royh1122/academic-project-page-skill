"""Check that the audit reports every planted flaw it is meant to catch.

    python evals/check_fixtures.py [fixture-name ...]

For each eval-kit/fixtures/<name>.defects.json, serves <name>/docs under its repository subpath,
runs the skill's audit.mjs (no screenshots), and checks that every defect with an "audit_match"
substring appears in the audit's output. Defects without one are found by looking at screenshots
and are graded in agent evals instead. Needs Python 3, Node 22+ and Chrome, like the audit.
Exit code 1 when any planted flaw goes unreported.
"""
import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / 'eval-kit' / 'fixtures'
SCRIPTS = ROOT / 'skills' / 'academic-project-page' / 'scripts'


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def audit(name, base):
    port = free_port()
    server = subprocess.Popen([sys.executable, str(SCRIPTS / 'preview_server.py'), '--root', str(FIXTURES / name / 'docs'),
                               '--base', base, '--port', str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f'http://127.0.0.1:{port}/{base}/'
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(url, timeout=2)
                break
            except OSError:
                time.sleep(0.25)
        with tempfile.TemporaryDirectory() as out:
            result = subprocess.run(['node', str(SCRIPTS / 'audit.mjs'), url, '--no-screenshots', '--out', out],
                                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
        return result.stdout + result.stderr
    finally:
        server.terminate()
        server.wait(timeout=10)


def main():
    names = sys.argv[1:] or sorted(p.name[:-len('.defects.json')] for p in FIXTURES.glob('*.defects.json'))
    missing = 0
    for name in names:
        spec = json.loads((FIXTURES / f'{name}.defects.json').read_text(encoding='utf-8'))
        base = spec['serve'].split('--base', 1)[1].split()[0]
        planted = [d for d in spec['defects'] if d.get('audit_match')]
        output = audit(name, base)
        found = [d for d in planted if d['audit_match'] in output]
        print(f'{name}: {len(found)} of {len(planted)} planted flaws reported by the audit '
              f'({len(spec["defects"]) - len(planted)} more are for agents to find by looking)')
        for d in planted:
            if d not in found:
                missing += 1
                print(f'  MISSING {d["id"]}: expected "{d["audit_match"]}" ({d["defect"][:80]})')
        if not planted or 'Audited ' not in output:
            missing += 1
            print('  the audit did not run:\n' + '\n'.join('    ' + line for line in output.strip().splitlines()[-8:]))
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
