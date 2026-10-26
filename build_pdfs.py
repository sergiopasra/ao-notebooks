"""Build one PDF per tema of the book.

Chapters are grouped by the title of their first heading, dropping the
subsection number: 'Tema 1.1', 'Tema 1.2'... go together in 'Tema 1'.

Usage:
    python build_pdfs.py                    # all temas in _toc.yml
    python build_pdfs.py tema-1 tema-2      # only the given temas

The PDFs are written to ao_notebooks/_build/pdf/
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

BOOK = Path(__file__).resolve().parent / "ao_notebooks"
BUILD = BOOK / "_build"
PDF_DIR = BUILD / "pdf"


def chapter_title(chapter):
    """Return the first level-1 heading of the chapter file, e.g. 'Tema 1.1'"""
    with open(BOOK / f"{chapter}.md", encoding="utf-8") as fd:
        for line in fd:
            if line.startswith("# "):
                return line[2:].strip()
    return chapter


def group_title(title):
    """Return the tema of a chapter title, e.g. 'Tema 1.1' -> 'Tema 1'"""
    return re.sub(r"\.\d+$", "", title)


def slugify(title):
    return title.lower().replace(" ", "-")


def find_jupyter_book():
    exe = Path(sys.executable).with_name("jupyter-book")
    if exe.exists():
        return str(exe)
    return shutil.which("jupyter-book")


def build_group(jb, title, entries, config):
    slug = "ao-" + slugify(title)

    workdir = BUILD / "pdf-temas" / slugify(title)
    workdir.mkdir(parents=True, exist_ok=True)

    toc = {"format": "jb-book", "root": "index", "chapters": entries}
    toc_path = workdir / "toc.yml"
    with open(toc_path, "w", encoding="utf-8") as fd:
        yaml.safe_dump(toc, fd, allow_unicode=True, sort_keys=False)

    cfg = dict(config)
    cfg["title"] = f"{config['title']}. {title}"
    cfg["latex"] = {"latex_documents": {"targetname": f"{slug}.tex"}}
    cfg_path = workdir / "config.yml"
    with open(cfg_path, "w", encoding="utf-8") as fd:
        yaml.safe_dump(cfg, fd, allow_unicode=True, sort_keys=False)

    chapters = ", ".join(entry["file"] for entry in entries)
    print(f"--- Building {title} ({chapters})", flush=True)
    result = subprocess.run(
        [
            jb, "build", str(BOOK),
            "--builder", "pdflatex",
            "--toc", str(toc_path),
            "--config", str(cfg_path),
            "--path-output", str(workdir),
        ]
    )
    pdf = workdir / "_build" / "latex" / f"{slug}.pdf"
    if result.returncode != 0 or not pdf.exists():
        print(f"*** Failed to build {title}", file=sys.stderr)
        return None

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    dest = PDF_DIR / pdf.name
    shutil.copy(pdf, dest)
    return dest


def main(args):
    jb = find_jupyter_book()
    if jb is None:
        sys.exit("jupyter-book not found")

    with open(BOOK / "_toc.yml", encoding="utf-8") as fd:
        toc = yaml.safe_load(fd)
    with open(BOOK / "_config.yml", encoding="utf-8") as fd:
        config = yaml.safe_load(fd)

    groups = {}
    for entry in toc["chapters"]:
        if "sections" in entry:
            title = group_title(chapter_title(entry["file"]))
            groups.setdefault(title, []).append(entry)

    if args:
        unknown = set(args) - {slugify(title) for title in groups}
        if unknown:
            names = ", ".join(slugify(title) for title in groups)
            sys.exit(f"Unknown temas: {', '.join(sorted(unknown))}. Available: {names}")
        groups = {t: e for t, e in groups.items() if slugify(t) in args}

    built, failed = [], []
    for title, entries in groups.items():
        dest = build_group(jb, title, entries, config)
        if dest:
            built.append(dest)
        else:
            failed.append(title)

    print()
    for dest in built:
        print(f"PDF: {dest}")
    for title in failed:
        print(f"FAILED: {title}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
