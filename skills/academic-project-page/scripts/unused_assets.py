"""List files under <site>/static that no HTML, CSS, or JS file in the site references.

    python unused_assets.py docs
"""
import sys
from pathlib import Path

site = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
sources = [p for p in site.rglob('*') if p.suffix in {'.html', '.css', '.js'} and p.is_file()]
text = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in sources)
unused = [p for p in sorted((site / 'static').rglob('*')) if p.is_file() and p.name not in text]
for path in unused:
    print(f'{path.relative_to(site)}\t{path.stat().st_size // 1024} KB')
print(f'{len(unused)} unreferenced file(s)' if unused else 'No unreferenced files.')
