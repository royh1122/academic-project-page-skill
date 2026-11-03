"""Check that the theme's three sources agree: style-fidelity.md's token tables, the :root tokens in
static/css/index.css, and the colours in references/theme-profile.json.

    python evals/check_theme_tokens.py

Each table row that names tokens and values must match index.css (hex colours compared in lower case,
other values with whitespace collapsed; a gradient by its colours in order). Every colour in the
profile must be the value of some :root token. Exit code 1 on any mismatch. CI runs it.
"""
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / 'skills' / 'academic-project-page'
HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')


def css_tokens():
    css = (SKILL / 'static' / 'css' / 'index.css').read_text(encoding='utf-8')
    root = re.search(r':root\s*{(.*?)}', css, re.S).group(1)
    root = re.sub(r'/\*.*?\*/', '', root, flags=re.S)
    return {m.group(1): ' '.join(m.group(2).split()) for m in re.finditer(r'(--[\w-]+)\s*:\s*([^;]+);', root)}


def table_rows():
    """(line number, tokens, values) for each row of the token tables whose first two cells name tokens and values."""
    rows = []
    lines = (SKILL / 'references' / 'style-fidelity.md').read_text(encoding='utf-8').splitlines()
    for number, line in enumerate(lines, 1):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 3 or not cells[0].startswith('`--'):
            continue
        tokens = re.findall(r'`(--[\w-]+)`', cells[0])
        values = re.findall(r'`([^`]+)`', cells[1])
        if values and len(tokens) == len(values):
            rows.append((number, tokens, values))
    return rows


def same(documented, actual):
    documented, actual = ' '.join(documented.split()), ' '.join(actual.split())
    if '→' in documented:  # a gradient, documented by its colours
        return [c.lower() for c in HEX.findall(documented)] == [c.lower() for c in HEX.findall(actual)]
    return documented.lower() == actual.lower()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    tokens, problems = css_tokens(), []
    rows = table_rows()
    for number, names, values in rows:
        for name, value in zip(names, values):
            if name not in tokens:
                problems.append(f'style-fidelity.md:{number}: {name} is not on :root in index.css')
            elif not same(value, tokens[name]):
                problems.append(f'style-fidelity.md:{number}: {name} is {value} in the table but {tokens[name]} in index.css')

    profile = (SKILL / 'references' / 'theme-profile.json').read_text(encoding='utf-8')
    values = {v.lower() for v in tokens.values()}
    for colour in sorted({c.lower() for c in HEX.findall(json.dumps(json.loads(profile)))}):
        if colour not in values:
            problems.append(f'theme-profile.json: {colour} is not the value of any :root token in index.css')

    checked = sum(len(names) for _, names, _ in rows)
    print(f'{checked} documented tokens checked against {len(tokens)} on :root; {len(problems)} mismatch(es).')
    for problem in problems:
        print('  ' + problem)
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
