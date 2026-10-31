"""Check that the audit reports every planted flaw it is meant to catch.

    python evals/check_fixtures.py [fixture-name ...]
    python evals/check_fixtures.py --coverage

For each eval-kit/fixtures/<name>.defects.json, serves <name>/docs under its repository subpath,
runs the skill's audit.mjs (no screenshots), and checks that every defect with an "audit_id" is
reported under that id ("[id]" in the output). Defects without one are found by looking at
screenshots and are graded in agent evals instead. Needs Python 3, Node 22+ and Chrome, like the audit.

--coverage needs no browser: it checks that every finding id in scripts/lib/findings.mjs has a
planted flaw in some fixture, or an entry in UNTESTED below saying why not. A new check therefore
ships with a fixture. Exit code 1 when a planted flaw goes unreported or an id is uncovered.
"""
import json
import re
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

# Finding ids with no planted flaw yet, and why. Remove an entry when a fixture covers it.
UNTESTED = {
    'duplicate-id': 'predates the fixtures; plain DOM check',
    'h1-count': 'predates the fixtures; plain DOM check',
    'control-name': 'predates the fixtures; plain DOM check',
    'iframe-title': 'predates the fixtures; no fixture embeds an iframe',
    'nav-dangling': 'predates the fixtures; plain DOM check',
    'citation-hidden': 'predates the fixtures',
    'method-hidden': 'predates the fixtures',
    'icon-font': 'tested by hand in v1.3.0 (a page with Font Awesome markup and no script)',
    'title-break': 'predates the fixtures; every kit build hits it once and fixes it',
    'teaser-heights': 'predates the fixtures',
    'image-upscaled': 'predates the fixtures',
    'video-poster': 'predates the fixtures',
    'video-size': 'predates the fixtures',
    'root-relative': 'flawed-v1 D4 triggers it alongside resource-missing',
    'range-requests': 'needs a server without range support; preview_server.py always has it',
    'motion-video': 'predates the fixtures',
    'wrong-base': 'needs the page served at / instead of its subpath; tested by hand',
    'focus-trap': 'predates the fixtures',
    'focus-hidden': 'predates the fixtures',
    'focus-skipped': 'predates the fixtures',
    'contents-menu': 'interaction failures of a bundled component; the clean template passes',
    'more-works': 'interaction failures of a bundled component; the clean template passes',
    'copy-button': 'interaction failures of a bundled component; the clean template passes',
    'figure-viewer': 'flawed-v1 D4 makes one figure fail to load in the viewer',
    'carousel': 'interaction failures of a bundled component; the clean template passes',
    'check-stopped': 'reports a crash of the check itself, not a page defect',
    'typography-baseline': 'missing template elements; any non-template page triggers it',
}


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


def specs():
    return {p.name[:-len('.defects.json')]: json.loads(p.read_text(encoding='utf-8'))
            for p in sorted(FIXTURES.glob('*.defects.json'))}


def coverage():
    ids = re.findall(r"^\s*\['([a-z0-9-]+)',", (SCRIPTS / 'lib' / 'findings.mjs').read_text(encoding='utf-8'), re.M)
    planted = {d['audit_id'] for spec in specs().values() for d in spec['defects'] if d.get('audit_id')}
    uncovered = [i for i in ids if i not in planted and i not in UNTESTED]
    stale = [i for i in UNTESTED if i in planted or i not in ids]
    print(f'{len(ids)} finding ids: {len(planted & set(ids))} with a planted flaw, {len(set(ids) & set(UNTESTED))} listed as untested.')
    for i in uncovered:
        print(f'  UNCOVERED {i}: add a planted flaw with "audit_id": "{i}" to a fixture, or list it in UNTESTED with a reason')
    for i in stale:
        print(f'  STALE {i}: remove it from UNTESTED (it is now planted, or no longer an id)')
    return not uncovered and not stale


def main():
    if '--coverage' in sys.argv:
        sys.exit(0 if coverage() else 1)
    all_specs = specs()
    names = sys.argv[1:] or list(all_specs)
    missing = 0
    for name in names:
        spec = all_specs[name]
        base = spec['serve'].split('--base', 1)[1].split()[0]
        planted = [d for d in spec['defects'] if d.get('audit_id')]
        output = audit(name, base)
        found = [d for d in planted if f'[{d["audit_id"]}]' in output]
        print(f'{name}: {len(found)} of {len(planted)} planted flaws reported by the audit '
              f'({len(spec["defects"]) - len(planted)} more are for agents to find by looking)')
        for d in planted:
            if d not in found:
                missing += 1
                print(f'  MISSING {d["id"]}: expected [{d["audit_id"]}] ({d["defect"][:80]})')
        if 'Summary:' not in output:
            missing += 1
            print('  the audit did not finish:\n' + '\n'.join('    ' + line for line in output.strip().splitlines()[-8:]))
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
