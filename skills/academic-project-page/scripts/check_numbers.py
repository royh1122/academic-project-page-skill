"""Check that every number on the page appears in the project's source files.

    python check_numbers.py docs/index.html paper/ results/tables/ README.md

A page number matches when some source number rounds to it at the page's precision,
directly or as a proportion shown as a percentage (0.935 -> 93.5). Integers below 10 are
skipped. Unmatched numbers are listed with context: correct each one or trace it to a
derivation you can state (a sum, a difference, a count). Exit code 1 when any are unmatched.
PDF sources are read with PyMuPDF (fitz) when installed, else with the pdftotext command (Poppler, MiKTeX,
Xpdf); the extractor used is named in the output. With neither, PDFs are skipped with a note.
"""
import argparse
import html
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from source_files import missing, read_source, source_files

# Standalone numbers only: digits touching letters (hashes, IDs, labels such as P70) are not values,
# except a factor written with a trailing x ("1.36x"), which pages often render as "1.36×".
NUMBER = re.compile(r'(?<![\w.])(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?!(?!x\b)\w)')
TEXT_SUFFIXES = {'.md', '.csv', '.tsv', '.tex', '.txt', '.json', '.html', '.yaml', '.yml', '.log', '.bib'}


def split_dimensions(text):
    # "2560×1440" and "2560x1440" are two numbers; PDF extraction often drops the spaces around the sign.
    return re.sub(r'(?<=\d)\s*[x×]\s*(?=\d)', ' x ', text)


def visible_text(markup):
    markup = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', markup)
    markup = re.sub(r'(?s)<!--.*?-->', ' ', markup)
    text = html.unescape(re.sub(r'<[^>]+>', ' ', markup))
    return split_dimensions(re.sub(r'\s+', ' ', text.replace('−', '-').replace(' ', ' ').replace(' ', ' ')))


def to_decimal(token):
    return Decimal(token.replace(',', ''))


def rounded(value, places):
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('page', help='the page, such as docs/index.html')
    parser.add_argument('sources', nargs='+', help='files or folders the numbers came from')
    args = parser.parse_args()
    if missing([args.page, *args.sources]):
        parser.error(f'not found: {", ".join(missing([args.page, *args.sources]))}')
    page = Path(args.page)
    text = visible_text(page.read_text(encoding='utf-8'))

    files = [f for f, _ in source_files(args.sources)]
    extractors = set()
    sources = [to_decimal(m.group()) for f in files if f.resolve() != page.resolve()
               for m in NUMBER.finditer(split_dimensions(read_source(f, TEXT_SUFFIXES, extractors)))
               if len(m.group().replace(',', '').replace('.', '')) <= 15]

    found, unmatched, cache = 0, [], {}
    for match in NUMBER.finditer(text):
        token = match.group()
        value = to_decimal(token)
        places = len(token.split('.')[1]) if '.' in token else 0
        if places == 0 and value < 10:
            continue
        found += 1
        if places not in cache:
            cache[places] = {rounded(s, places) for s in sources} | {rounded(s * 100, places) for s in sources if s <= 1}
        if value not in cache[places]:
            start, end = max(0, match.start() - 50), min(len(text), match.end() + 30)
            unmatched.append(f'{token:>12}  ...{text[start:end].strip()}...')

    print(f'{found} numbers checked against {len(files)} source file(s); {len(unmatched)} unmatched.')
    if extractors:
        print(f'PDFs read with {" and ".join(sorted(extractors))}.')
    for line in unmatched:
        print(line)
    sys.exit(1 if unmatched else 0)


if __name__ == '__main__':
    main()
