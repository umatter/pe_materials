"""Build and check the course notebooks (Colab, R runtime).

Notebooks are generated from Python build scripts so that the setup, key and
helper cells are identical everywhere and the helper code comes from
materials/R/or_chat.R.

    from nbtools import md, code, standard_cells, write_notebook
    cells = [md("# Title"), *standard_cells(["readr"]), code("or_chat('hi')")]
    write_notebook(cells, "materials/b1/01_first_call.ipynb")

Check a notebook locally (runs all code cells with Rscript, key from the
environment instead of the input cell):

    python3 materials/tools/nbtools.py run materials/b1/01_first_call.ipynb
"""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = "umatter/pe_materials"


def colab_url(path_in_repo: str) -> str:
    return f"https://colab.research.google.com/github/{REPO}/blob/main/{path_in_repo}"


def _src(text: str) -> list:
    lines = text.strip("\n").split("\n")
    return [l + "\n" for l in lines[:-1]] + [lines[-1]]


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": _src(text)}


def code(text: str, tags=None) -> dict:
    meta = {"tags": tags} if tags else {}
    return {"cell_type": "code", "metadata": meta, "execution_count": None,
            "outputs": [], "source": _src(text)}


def standard_cells(packages=()) -> list:
    """Setup, key and helper cells, in this order, for every notebook."""
    pkgs = ", ".join(f'"{p}"' for p in ["httr2", "jsonlite", *packages])
    helper = (ROOT / "R" / "or_chat.R").read_text()
    return [
        md("## Setup\nRun the next three cells once, from top to bottom. "
           "Run them again after a runtime restart."),
        code(f"""# Packages: installs only what is missing
ensure_packages <- function(pkgs) {{
  missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
  if (length(missing) > 0) install.packages(missing)
  invisible(NULL)
}}
ensure_packages(c({pkgs}))""", tags=["setup"]),
        code("""# Your OpenRouter key: paste it into the box and press Enter.
# The output is cleared right away so the key is not shown or saved.
Sys.setenv(OPENROUTER_API_KEY = readline("Paste your OpenRouter key: "))
IRdisplay::clear_output()
cat("Key set:", nzchar(Sys.getenv("OPENROUTER_API_KEY")))""", tags=["key"]),
        code("# Helper functions: or_chat() sends a prompt, parse_json_reply() reads JSON replies\n"
             + helper, tags=["helper"]),
    ]


def write_notebook(cells: list, path) -> None:
    nb = {
        "nbformat": 4, "nbformat_minor": 0,
        "metadata": {
            "kernelspec": {"name": "ir", "display_name": "R", "language": "R"},
            "language_info": {"name": "R"},
            "colab": {"provenance": []},
        },
        "cells": cells,
    }
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")


def run(path) -> int:
    """Run a notebook's code cells with Rscript; the key cell is skipped."""
    nb = json.loads(pathlib.Path(path).read_text())
    chunks = []
    for c in nb["cells"]:
        if c["cell_type"] != "code" or "key" in c.get("metadata", {}).get("tags", []):
            continue
        chunks.append("".join(c["source"]))
    with tempfile.NamedTemporaryFile("w", suffix=".R", delete=False) as f:
        f.write("\n\n".join(chunks))
        script = f.name
    workdir = pathlib.Path(path).parent
    return subprocess.call(["Rscript", script], cwd=workdir)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "run":
        sys.exit(run(sys.argv[2]))
    print(__doc__)
