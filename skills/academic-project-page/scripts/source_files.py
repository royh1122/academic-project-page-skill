"""Read the project's source files as text, for check_numbers.py and check_links.py. Not run directly."""
import shutil
import subprocess
from pathlib import Path


def pdf_text(path, links=False):
    """Return (text, extractor name), or (None, None) when no extractor is available.

    With links=True, PyMuPDF also adds each page's link targets; pdftotext gives text only.
    """
    try:
        try:
            import pymupdf
        except ImportError:
            import fitz as pymupdf
        with pymupdf.open(path) as document:
            parts = []
            for page in document:
                parts.append(page.get_text())
                if links:
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


def missing(paths):
    """The paths that do not exist, for an argparse error."""
    return [p for p in paths if not Path(p).exists()]


def source_files(arguments):
    """Expand the arguments into (path, explicit) pairs: a folder gives its files outside .git, a file itself."""
    files = []
    for argument in arguments:
        path = Path(argument)
        if path.is_dir():
            files += [(p, False) for p in sorted(path.rglob('*')) if p.is_file() and '.git' not in p.parts[:-1]]
        else:
            files.append((path, True))
    return files


def read_source(path, text_suffixes, extractors, read_any=False, links=False):
    """The file's text: PDFs through pdf_text, text files by suffix (or any file when read_any), else ''."""
    if path.suffix.lower() == '.pdf':
        text, extractor = pdf_text(path, links)
        if text is None:
            print(f'note: skipped {path} (install PyMuPDF or pdftotext to read PDFs)')
            return ''
        extractors.add(extractor)
        return text
    if read_any or path.suffix.lower() in text_suffixes:
        return path.read_text(encoding='utf-8', errors='ignore')
    return ''
