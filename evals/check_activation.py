"""Activation (trigger) eval: does the skill's description make an agent load the skill for the right requests?

    python evals/check_activation.py [--description "..."] [--runs 3] [--workers 4] [--model sonnet]

For each query in evals/activation.json, starts `claude -p` in a fresh temporary project that holds only a probe skill
(the real name and description, a stub body) and stops after the agent's first turn. A query counts as triggered when
that turn loads the skill (a Skill call, or a read of its SKILL.md). Reports the trigger rate per query, and passes when
every should-trigger query triggers in at least half its runs and every near miss in fewer than half.

Use --description to try a variant before editing SKILL.md. If the skill is also installed for your user (the plugin),
the agent may load that copy instead; both count, so test a variant with the plugin disabled. Needs the Claude Code CLI
(`claude`) on PATH, and uses your account's model quota: 36 queries x 3 runs is about 108 short calls.
Same query format as the skill-creator trigger eval; this runner works on Windows, macOS and Linux.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / 'skills' / 'academic-project-page' / 'SKILL.md'
NAME = 'academic-project-page'


def description():
    m = re.search(r'^description:\s*(.+)$', SKILL.read_text(encoding='utf-8'), flags=re.M)
    return m.group(1).strip()


def triggered(stream):
    """True when the first turn loads the skill: a Skill tool call naming it, or a read of its SKILL.md."""
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') != 'assistant':
            continue
        for block in event.get('message', {}).get('content', []):
            if block.get('type') != 'tool_use':
                continue
            text = json.dumps(block.get('input', {}))
            if NAME in text and (block.get('name') == 'Skill' or 'SKILL.md' in text):
                return True
    return False


def run_once(claude, query, desc, model, timeout):
    with tempfile.TemporaryDirectory() as tmp:
        skill_dir = Path(tmp) / '.claude' / 'skills' / NAME
        skill_dir.mkdir(parents=True)
        (skill_dir / 'SKILL.md').write_text(
            f'---\nname: {NAME}\ndescription: {json.dumps(desc)}\n---\n\nProbe copy for the activation eval.\n',
            encoding='utf-8')
        cmd = [claude, '-p', query, '--output-format', 'stream-json', '--verbose', '--max-turns', '1']
        if model:
            cmd += ['--model', model]
        try:
            r = subprocess.run(cmd, cwd=tmp, capture_output=True, timeout=timeout, encoding='utf-8', errors='replace')
            return triggered(r.stdout)
        except subprocess.TimeoutExpired as e:
            out = e.stdout.decode('utf-8', 'replace') if isinstance(e.stdout, bytes) else (e.stdout or '')
            return triggered(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--description', help='Description to test instead of the one in SKILL.md')
    ap.add_argument('--runs', type=int, default=3)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--model')
    ap.add_argument('--timeout', type=int, default=120)
    ap.add_argument('--json', help='Also write the results to this file')
    args = ap.parse_args()
    claude = shutil.which('claude')
    if not claude:
        sys.exit('claude (the Claude Code CLI) is not on PATH')
    desc = args.description or description()
    queries = json.loads((ROOT / 'evals' / 'activation.json').read_text(encoding='utf-8'))['queries']
    jobs = [(i, q) for i, q in enumerate(queries) for _ in range(args.runs)]
    with ThreadPoolExecutor(args.workers) as pool:
        hits = list(pool.map(lambda j: run_once(claude, j[1]['query'], desc, args.model, args.timeout), jobs))
    rates = [0] * len(queries)
    for (i, _), hit in zip(jobs, hits):
        rates[i] += hit
    wrong = 0
    results = []
    for q, n in zip(queries, rates):
        rate = n / args.runs
        ok = rate >= 0.5 if q['should_trigger'] else rate < 0.5
        wrong += not ok
        results.append({**q, 'trigger_rate': rate, 'pass': ok})
        print(f"{'ok  ' if ok else 'MISS'} {rate:4.0%}  {'trigger ' if q['should_trigger'] else 'near miss'}  {q['query'][:90]}")
    pos = [r for r in results if r['should_trigger']]
    neg = [r for r in results if not r['should_trigger']]
    print(f"\nShould trigger: {sum(r['pass'] for r in pos)}/{len(pos)}; near misses left alone: "
          f"{sum(r['pass'] for r in neg)}/{len(neg)}; {args.runs} run(s) per query")
    if args.json:
        Path(args.json).write_text(json.dumps({'description': desc, 'runs': args.runs, 'results': results}, indent=2),
                                   encoding='utf-8')
    sys.exit(1 if wrong else 0)


if __name__ == '__main__':
    main()
