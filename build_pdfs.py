"""Build one PDF per chapter (tema) of the book.

Usage:
    python build_pdfs.py            # all chapters with sections in _toc.yml
    python build_pdfs.py prob11     # only the given chapters

The PDFs are written to ao_notebooks/_build/pdf/
"""

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


def find_jupyter_book():
    exe = Path(sys.executable).with_name("jupyter-book")
    if exe.exists():
        return str(exe)
    return shutil.which("jupyter-book")


def build_chapter(jb, entry, config):
    chapter = entry["file"]
    title = chapter_title(chapter)
    slug = "ao-" + title.lower().replace(" ", "-")

    workdir = BUILD / "pdf-temas" / chapter
    workdir.mkdir(parents=True, exist_ok=True)

    toc = {"format": "jb-book", "root": "index", "chapters": [entry]}
    toc_path = workdir / "toc.yml"
    with open(toc_path, "w", encoding="utf-8") as fd:
        yaml.safe_dump(toc, fd, allow_unicode=True, sort_keys=False)

    cfg = dict(config)
    cfg["title"] = f"{config['title']}. {title}"
    cfg["latex"] = {"latex_documents": {"targetname": f"{slug}.tex"}}
    cfg_path = workdir / "config.yml"
    with open(cfg_path, "w", encoding="utf-8") as fd:
        yaml.safe_dump(cfg, fd, allow_unicode=True, sort_keys=False)

    print(f"--- Building {title} ({chapter})", flush=True)
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

    chapters = [entry for entry in toc["chapters"] if "sections" in entry]
    if args:
        chapters = [entry for entry in chapters if entry["file"] in args]

    built, failed = [], []
    for entry in chapters:
        dest = build_chapter(jb, entry, config)
        if dest:
            built.append(dest)
        else:
            failed.append(entry["file"])

    print()
    for dest in built:
        print(f"PDF: {dest}")
    for chapter in failed:
        print(f"FAILED: {chapter}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
