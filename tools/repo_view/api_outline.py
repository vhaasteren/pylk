#!/usr/bin/env python3
"""Generate API outline for Python files in the repository."""
from __future__ import annotations

import ast
import os
import subprocess
from typing import Callable, List, Optional

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "tests"}


def git_py_files() -> List[str]:
    """Get Python files tracked by git, excluding test files."""
    files: List[str] = []
    try:
        out = subprocess.check_output(
            ["git", "ls-files", "*.py"], stderr=subprocess.DEVNULL
        ).decode()
        files = [line.strip() for line in out.splitlines() if line.strip()]
        # Filter out test files
        files = [f for f in files if not f.startswith("tests/")]
        if files:
            return files
    except Exception:
        pass
    for root, dirs, names in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            if n.endswith(".py") and not n.startswith("test_"):
                files.append(os.path.join(root, n))
    return files


# Optional unparser (Py ≥ 3.9), else None
ast_unparse: Optional[Callable[[ast.AST], str]]
try:
    from ast import unparse as _ast_unparse  # type: ignore[attr-defined]

    ast_unparse = _ast_unparse
except Exception:
    ast_unparse = None


def unparse(node: Optional[ast.AST]) -> str:
    """Safely unparse an AST node."""
    if node is None:
        return ""
    if ast_unparse is not None:
        try:
            return ast_unparse(node)
        except Exception:
            return ""
    return ""  # best-effort on older Python


def fmt_default(d: Optional[ast.expr]) -> str:
    """Format default value, truncating if too long."""
    if d is None:
        return ""
    s = unparse(d)
    return s if s and len(s) <= 20 else "..."


def fmt_arg(arg: ast.arg, default: Optional[ast.expr] = None) -> str:
    """Format function argument with type annotation and default."""
    name, ann = arg.arg, unparse(arg.annotation)
    s = name + (f": {ann}" if ann else "")
    if default is not None:
        s += f"={fmt_default(default)}"
    return s


def format_args(a: ast.arguments) -> str:
    """Format function arguments with proper syntax."""
    parts: List[str] = []
    posonly = a.posonlyargs or []
    args = a.args or []
    all_pos = posonly + args
    ndef = len(a.defaults or [])
    defaults: List[Optional[ast.expr]] = [None] * (len(all_pos) - ndef) + (a.defaults or [])
    cur = [fmt_arg(arg, d) for arg, d in zip(all_pos, defaults)]
    if posonly:
        cur.insert(len(posonly), "/")
    parts += cur
    if a.vararg:
        parts.append("*" + fmt_arg(a.vararg))
    elif a.kwonlyargs:
        parts.append("*")
    for kw, d in zip(a.kwonlyargs or [], a.kw_defaults or []):
        parts.append(fmt_arg(kw, d))
    if a.kwarg:
        parts.append("**" + fmt_arg(a.kwarg))
    return "(" + ", ".join(parts) + ")"


def first_line(doc: Optional[str]) -> str:
    """Get first line of docstring."""
    return (doc or "").strip().splitlines()[0].strip() if doc else ""


def outline(path: str) -> str:
    """Generate API outline for a Python file."""
    try:
        src = open(path, "r", encoding="utf-8", errors="ignore").read()
        tree = ast.parse(src, filename=path)
    except Exception as e:
        return f"# [parse error] {e}"
    out: List[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            out.append(f"class {node.name}:  # {first_line(ast.get_docstring(node))}")
            for n in node.body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    sig = format_args(n.args)
                    ret = unparse(n.returns)
                    prefix = "async def " if isinstance(n, ast.AsyncFunctionDef) else "def "
                    line = f"  {prefix}{n.name}{sig}"
                    if ret:
                        line += f" -> {ret}"
                    line += f"  # {first_line(ast.get_docstring(n))}"
                    out.append(line)
            out.append("")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sig = format_args(node.args)
            ret = unparse(node.returns)
            prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
            line = f"{prefix}{node.name}{sig}"
            if ret:
                line += f" -> {ret}"
            line += f"  # {first_line(ast.get_docstring(node))}"
            out.append(line)
    return "\n".join(out).rstrip()


def main():
    """Generate API outline for all Python files."""
    files = git_py_files()
    if not files:
        print("# No Python files found")
        return

    for p in sorted(files):
        print(f"<===== {p} =====>")
        print(outline(p))
        print()


if __name__ == "__main__":
    main()
