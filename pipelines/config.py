# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import annotations

import os
import pathlib

# Packaging
MAIN_PACKAGE = "hikari"
TEST_PACKAGE = "tests"
EXAMPLE_SCRIPTS = "examples"

# Directories
ARTIFACT_DIRECTORY = "public"
DOCUMENTATION_DIRECTORY = "docs"

# Linting and test configs
PYPROJECT_TOML = "pyproject.toml"
COVERAGE_HTML_PATH = pathlib.Path(ARTIFACT_DIRECTORY, "coverage", "html")


if "READTHEDOCS_OUTPUT" in os.environ:
    DOCUMENTATION_OUTPUT_PATH = os.environ["READTHEDOCS_OUTPUT"] + "/html"
else:
    DOCUMENTATION_OUTPUT_PATH = pathlib.Path(ARTIFACT_DIRECTORY, "docs")


# Reformatting paths
REFORMATTING_FILE_EXTS = (
    ".py",
    ".pyx",
    ".pyi",
    ".c",
    ".cpp",
    ".cxx",
    ".hpp",
    ".hxx",
    ".h",
    ".yml",
    ".yaml",
    ".html",
    ".htm",
    ".js",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".css",
    ".md",
    ".dockerfile",
    "Dockerfile",
    ".editorconfig",
    ".gitattributes",
    ".json",
    ".gitignore",
    ".dockerignore",
    ".txt",
    ".sh",
    ".bat",
    ".ps1",
    ".rb",
    ".pl",
)
PYTHON_REFORMATTING_PATHS = (MAIN_PACKAGE, TEST_PACKAGE, EXAMPLE_SCRIPTS, "scripts", "pipelines", "noxfile.py")
FULL_REFORMATTING_PATHS = (
    *PYTHON_REFORMATTING_PATHS,
    *(f for f in pathlib.Path.cwd().glob("*") if f.is_file() and f.suffix.endswith(REFORMATTING_FILE_EXTS)),
    ".github",
    "docs",
    "changes",
)
