import ast
from pathlib import Path
from typing import Dict, List, Set, Any


def find_python_imports(file_path: str) -> List[str]:
    """
    Extract all imports from a Python file.
    """

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return list(set(imports))

    except Exception:
        return []


def find_function_references(
    repo_path: str,
    function_name: str, **kwargs) -> List[str]:
    """
    Search repository for usages of a function.
    """

    matches = []

    repo = Path(repo_path)

    for file in repo.rglob("*.py"):

        try:
            content = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            if f"{function_name}(" in content:
                matches.append(str(file))

        except Exception:
            continue

    return matches


def get_python_files(
    repo_path: str
) -> List[str]:
    """
    Return all Python files in repository.
    """

    repo = Path(repo_path)

    ignored_dirs = {
        ".venv",
        "venv",
        "__pycache__",
        ".git"
    }

    python_files = []

    for file in repo.rglob("*.py"):

        if any(
            ignored in file.parts
            for ignored in ignored_dirs
        ):
            continue

        python_files.append(str(file))

    return python_files


def build_dependency_map(
    repo_path: str
) -> Dict[str, List[str]]:
    """
    Build import dependency graph.
    """

    dependency_map = {}

    files = get_python_files(repo_path)

    for file_path in files:

        imports = find_python_imports(file_path)

        dependency_map[file_path] = imports

    return dependency_map


def extract_defined_symbols(file_path: str) -> List[str]:
    """
    Extract all class names, function names, and top-level variable definitions from a Python file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        symbols = []
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        symbols.append(target.id)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    symbols.append(node.target.id)
        return symbols
    except Exception:
        return []


def get_candidate_modules(file_path: str, repo_path: str) -> List[str]:
    """
    Generate candidate python import paths for a file relative to the repo.
    """
    try:
        rel = Path(file_path).resolve().relative_to(Path(repo_path).resolve())
    except Exception:
        rel = Path(file_path)
    
    parts = list(rel.with_suffix("").parts)
    candidates = []
    for i in range(len(parts)):
        sub = parts[i:]
        sub = [p for p in sub if p != "src"]
        if not sub:
            continue
        candidates.append(".".join(sub))
    return list(dict.fromkeys(candidates))


def analyze_dependencies(
    repo_path: str,
    target_files: List[str], **kwargs) -> Dict[str, Any]:
    """
    Analyze related files based on exact AST symbol imports and reference tracing.
    """
    affected_files = set(target_files)
    edges = []

    for target_file in target_files:
        if not Path(target_file).exists():
            full_path = Path(repo_path) / target_file
            if not full_path.exists():
                continue
            target_file_abs = str(full_path.resolve())
        else:
            target_file_abs = str(Path(target_file).resolve())

        symbols = extract_defined_symbols(target_file_abs)
        candidate_modules = get_candidate_modules(target_file_abs, repo_path)
        target_stem = Path(target_file_abs).stem

        # Select unique symbols to trace via string search
        unique_symbols = [s for s in symbols if len(s) > 4 and s not in {"types", "client", "error", "helper"}]
        # Ensure target_stem is also tracked
        if target_stem not in symbols:
            symbols.append(target_stem)

        # Search python files in repo
        for path in Path(repo_path).rglob("*.py"):
            if any(ignored in path.parts for ignored in {".git", "__pycache__", ".venv", "venv", "dist", "build"}):
                continue
            if str(path.resolve()) == target_file_abs:
                continue

            try:
                source = path.read_text(encoding="utf-8")
                # Fast pre-check: if no candidate module/stem/unique symbol is in content, skip parsing
                if not (target_stem in source or any(m in source for m in candidate_modules) or any(s in source for s in unique_symbols)):
                    continue
                tree = ast.parse(source)
            except Exception:
                continue

            lines = source.splitlines()
            def get_line(lineno):
                if 1 <= lineno <= len(lines):
                    return lines[lineno - 1].strip()
                return ""

            matched = False
            imported_modules = {}
            imported_symbols = {}

            # Parse imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.name
                        asname = alias.asname or name
                        imported_modules[asname] = name
                        
                        normalized_name = name.replace("src.", "")
                        if normalized_name in candidate_modules or any(name.endswith(cand) for cand in candidate_modules):
                            matched = True
                            edges.append({
                                "from_file": str(path.relative_to(repo_path)),
                                "to_file": target_file,
                                "symbol": target_stem,
                                "relationship": "module_reference",
                                "evidence": get_line(node.lineno)
                            })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    normalized_module = module.replace("src.", "")
                    is_candidate = (
                        normalized_module in candidate_modules 
                        or any(module.endswith(cand) for cand in candidate_modules)
                        or (node.level > 0 and (target_stem in module or not module))
                    )
                    
                    for alias in node.names:
                        name = alias.name
                        asname = alias.asname or name
                        imported_symbols[asname] = (module, node.lineno, get_line(node.lineno))
                        
                        if is_candidate and (name in symbols or name == target_stem):
                            matched = True
                            edges.append({
                                "from_file": str(path.relative_to(repo_path)),
                                "to_file": target_file,
                                "symbol": name,
                                "relationship": "imports",
                                "evidence": get_line(node.lineno)
                            })

            # Check usages/references
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if node.id in symbols and node.id in imported_symbols:
                        matched = True
                        exists = any(
                            e["from_file"] == str(path.relative_to(repo_path))
                            and e["to_file"] == target_file
                            and e["symbol"] == node.id
                            and e["relationship"] == "symbol_reference"
                            for e in edges
                        )
                        if not exists:
                            edges.append({
                                "from_file": str(path.relative_to(repo_path)),
                                "to_file": target_file,
                                "symbol": node.id,
                                "relationship": "symbol_reference",
                                "evidence": get_line(node.lineno)
                            })
                elif isinstance(node, ast.Attribute):
                    parts = []
                    curr = node
                    while isinstance(curr, ast.Attribute):
                        parts.append(curr.attr)
                        curr = curr.value
                    if isinstance(curr, ast.Name):
                        parts.append(curr.id)
                        parts.reverse()
                        last_part = parts[-1]
                        if last_part in symbols:
                            prefix = ".".join(parts[:-1])
                            if prefix in imported_modules or any(prefix == alias or imported_modules.get(alias) == prefix for alias in imported_modules):
                                matched = True
                                exists = any(
                                    e["from_file"] == str(path.relative_to(repo_path))
                                    and e["to_file"] == target_file
                                    and e["symbol"] == last_part
                                    and e["relationship"] == "symbol_reference"
                                    for e in edges
                                )
                                if not exists:
                                    edges.append({
                                        "from_file": str(path.relative_to(repo_path)),
                                        "to_file": target_file,
                                        "symbol": last_part,
                                        "relationship": "symbol_reference",
                                        "evidence": get_line(node.lineno)
                                    })

            if matched:
                affected_files.add(str(path.relative_to(repo_path)))

    return {
        "target_files": target_files,
        "affected_files": sorted(list(affected_files)),
        "edges": edges
    }



def extract_functions(
    file_path: str, **kwargs) -> List[str]:
    """
    Extract function names from file.
    """

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            tree = ast.parse(
                f.read()
            )

        functions = []

        for node in ast.walk(tree):

            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):
                functions.append(
                    node.name
                )

        return functions

    except Exception:
        return []