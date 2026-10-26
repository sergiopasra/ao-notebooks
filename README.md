# ao-notebooks

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sergiopasra/ao-notebooks/master)

# Astronomy notebooks

Unless otherwise stated, the educational content of this repository
(text, explanations, exercises, figures and images) is licensed under
the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).

Code examples contained in the notebooks are licensed under the MIT License.

The code used to build and generate this Jupyter Book is also licensed
under the MIT License.

## PDFs

To build one PDF per tema (requires TeX Live with `xelatex` and `latexmk`):

    python build_pdfs.py                  # all temas in _toc.yml
    python build_pdfs.py tema-1 tema-2    # only some temas

The PDFs are written to `ao_notebooks/_build/pdf/`.
