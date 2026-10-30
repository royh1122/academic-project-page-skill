"""Check that every external link on the page comes from the project's source files.

    python check_links.py docs/index.html paper/ README.md CITATION.cff --allow https://lab.example.edu/

Lists every external URL in the page (links, embeds, meta tags, JSON-LD) and flags any that
appear in none of the sources, plus empty, "#" and placeholder links. arXiv, DOI and YouTube
links match on their identifier, so an abs link to a paper the sources cite as "arXiv:2401.01234"
passes; other links match their address, or a deeper page of a source address. The template's own
links (fonts, icon styles, the template credits, the licence) are skipped. Pass --allow for each
link the user gave you outside the files (in the request or the chat). Exit code 1 when any are
flagged. With no source files (a Polish or Audit of a page alone), the links are listed as
unverified, and only empty and placeholder links fail. PDF sources are read with PyMuPDF (text and link targets) when installed, else with the
pdftotext command (text only); the extractor used is named in the output.
"""
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

URL = re.compile(r'''https?://[^\s"'<>`\\(){}\[\]]+''')
TEXT_SUFFIXES = {'.md', '.rst', '.txt', '.tex', '.bib', '.cff', '.json', '.yaml', '.yml', '.toml',
                 '.html', '.htm', '.csv', '.tsv', '.ipynb', '.cfg'}
# The template's own links: asset hosts, its credits and licence. Never content.
TEMPLATE_LINKS = ('fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com',
                  'unpkg.com', 'use.fontawesome.com', 'kit.fontawesome.com', 'schema.org',
                  'github.com/eliahuhorwitz/academic-project-page-template', 'nerfies.github.io',
                  'creativecommons.org/licenses')
# Hosts whose first path segment is an account, not a project: a source naming the account
# does not verify every repository under it.
ACCOUNT_HOSTS = {'github.com', 'gitlab.com', 'huggingface.co', 'bitbucket.org', 'codeberg.org'}
ARXIV = re.compile(r'arxiv\.org/(?:abs|pdf|html)/((?:\d{4}\.\d{4,5})|(?:[a-z.-]+/\d{7}))', re.I)
DOI = re.compile(r'doi\.org/(10\.\d{4,9}/[^\s?#]+)', re.I)
YOUTUBE = re.compile(r'(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=|shorts/)|youtu\.be/)([\w-]{11})', re.I)
PLACEHOLDER = re.compile(r'example\.(?:com|org)|your[-_](?:repo|paper|project|username)|/user\.github\.io/repo', re.I)


def key(url):
    """The address without scheme, www, fragment, trailing slash or .git, in lower case."""
    url = html.unescape(url).split('#')[0].rstrip('.,;:')
    url = re.sub(r'^https?://(www\.)?', '', url, flags=re.I)
    path, _, query = url.partition('?')
    path = re.sub(r'(\.git)?/*$', '', path)
    return (path + ('?' + query if query else '')).lower()


def page_links(markup):
    markup = re.sub(r'(?s)<!--.*?-->', ' ', markup)
    # Template tokens such as [INSERT VIDEO ID] count as placeholders, not as links to check.
    markup, inserts = re.subn(r'''\b(href|src|data|content)\s*=\s*"[^"]*\[INSERT[^"]*"''', r'\1="placeholder"', markup)
    links = [html.unescape(m.group()) for m in URL.finditer(markup)]
    empty = re.findall(r'''<a\b[^>]*\bhref\s*=\s*(?:""|''|"\s*#\s*"|'\s*#\s*'|"javascript:[^"]*")''', markup, re.I)
    return links, len(empty) + inserts


def pdf_text(path):
    """Return (text including link targets, extractor name), or (None, None) when none is available."""
    try:
        import fitz
        with fitz.open(path) as document:
            parts = []
            for page in document:
                parts.append(page.get_text())
                parts += [link['uri'] for link in page.get_links() if link.get('uri')]
            return ' '.join(parts), 'PyMuPDF'
    except ImportError:
        pass
    if shutil.which('pdftotext'):
        result = subprocess.run(['pdftotext', '-enc', 'UTF-8', str(path), '-'], capture_output=True)
        if result.returncode == 0:
            return result.stdout.decode('utf-8', errors='ignore'), 'pdftotext'
        print(f'note: pdftotext could not read {path}')
    return None, None


def source_text(path, explicit, extractors):
    if path.suffix.lower() == '.pdf':
        text, extractor = pdf_text(path)
        if text is None:
            print(f'note: skipped {path} (install PyMuPDF or pdftotext to read PDFs)')
            return ''
        extractors.add(extractor)
        return text
    if explicit or path.suffix.lower() in TEXT_SUFFIXES:
        return path.read_text(encoding='utf-8', errors='ignore')
    return ''


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0 if args else 2)
    allowed = [args[i + 1] for i, a in enumerate(args) if a == '--allow' and i + 1 < len(args)]
    paths = [a for i, a in enumerate(args) if a != '--allow' and (i == 0 or args[i - 1] != '--allow')]
    page = Path(paths[0])
    links, empty = page_links(page.read_text(encoding='utf-8'))

    files = []
    for argument in paths[1:]:
        path = Path(argument)
        files += [(p, False) for p in sorted(path.rglob('*')) if p.is_file() and '.git' not in p.parts[:-1]] \
            if path.is_dir() else [(path, True)]
    extractors = set()
    text = ' '.join(source_text(f, explicit, extractors) for f, explicit in files if f.resolve() != page.resolve())
    text += ' ' + ' '.join(allowed)
    # git@github.com:owner/repo.git and other scp-style remotes name the same repository.
    text = re.sub(r'git@([\w.-]+):', r'https://\1/', text)
    plain = re.sub(r'https?://(www\.)?', '', text, flags=re.I).lower()
    source_keys = {key(u) for u in URL.findall(text)}

    def verified(url):
        for pattern in (ARXIV, DOI, YOUTUBE):
            match = pattern.search(url)
            if match:
                ident = match.group(1).lower().rstrip('.')
                return re.search(re.escape(ident) + r'(?![\w])', text, re.I) is not None or (
                    pattern is DOI and ident in plain)
        k = key(url)
        if re.search(re.escape(k) + r'(?![\w-])', plain):
            return True
        for s in source_keys:
            segments = s.split('/')[1:]
            if k.startswith(s + '/') and len(segments) >= (2 if s.split('/')[0] in ACCOUNT_HOSTS else 1):
                return True
        return False

    checked, flagged, placeholders, seen = 0, [], [], set()
    for url in links:
        k = key(url)
        if k in seen or any(k.startswith(t) for t in TEMPLATE_LINKS):
            continue
        seen.add(k)
        checked += 1
        if not verified(url):
            (placeholders if PLACEHOLDER.search(url) else flagged).append(url)

    sources = len([f for f, _ in files if f.resolve() != page.resolve()])
    if not sources and not allowed:
        print(f'{checked} external links listed; no source files given, so none could be verified. '
              f'{len(placeholders) + empty} placeholder or empty.')
    else:
        print(f'{checked} external links checked against {sources} source file(s) and {len(allowed)} allowed; '
              f'{len(flagged)} not found, {len(placeholders) + empty} placeholder or empty.')
    if extractors:
        print(f'PDFs read with {" and ".join(sorted(extractors))}.')
    for url in flagged:
        print(f'  {"unverified:    " if not sources and not allowed else "not in sources:"} {url}')
    if not sources and not allowed:
        flagged = []
    for url in placeholders:
        print(f'  placeholder:    {url}')
    if empty:
        print(f'  {empty} link(s) with an empty, "#", javascript: or [INSERT ...] target')
    sys.exit(1 if flagged or placeholders or empty else 0)


if __name__ == '__main__':
    main()
