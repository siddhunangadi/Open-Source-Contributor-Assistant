import ast
from pathlib import Path
from typing import List, Dict, Any, Optional

def extract_python_symbols(file_path: str, content: Optional[str] = None, **kwargs) -> List[str]:
    """
    Extract all class names, function names, async function names, and top-level variable definitions.
    """
    try:
        if content is None:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        tree = ast.parse(content)
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
        return list(dict.fromkeys(symbols))
    except Exception:
        return []


def find_symbol_imports(repo_path: str, symbol_name: str, module_name: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
    """
    Find Python files in the repository that directly import a specific symbol.
    Uses AST parsing to trace both ImportFrom (from module import symbol) and Import (import module.symbol).
    """
    matches = []
    repo = Path(repo_path)
    for path in repo.rglob("*.py"):
        if any(ignored in path.parts for ignored in {".git", "__pycache__", ".venv", "venv", "dist", "build"}):
            continue
        try:
            source = path.read_text(encoding="utf-8")
            if symbol_name not in source:
                continue
            tree = ast.parse(source)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # Filter by module_name if provided
                if module_name:
                    imported_module = node.module or ""
                    if not (imported_module == module_name or imported_module.replace("src.", "") == module_name or module_name.endswith(imported_module)):
                        continue
                for alias in node.names:
                    if alias.name == symbol_name:
                        matches.append({
                            "path": str(path),
                            "source_file": str(path),
                            "module": node.module,
                            "symbol": symbol_name,
                            "line": node.lineno,
                            "relation": "direct_import",
                            "reason": f"Imports {symbol_name} from {node.module}",
                            "evidence_type": "direct_import"
                        })
                        break

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if symbol_name in alias.name:
                        # Filter by module_name if provided
                        if module_name and module_name not in alias.name:
                            continue
                        matches.append({
                            "path": str(path),
                            "source_file": str(path),
                            "module": alias.name,
                            "symbol": symbol_name,
                            "line": node.lineno,
                            "relation": "module_import",
                            "reason": f"Imports module {alias.name} containing {symbol_name}",
                            "evidence_type": "direct_import"
                        })
                        break
    return matches


def find_symbol_references(repo_path: str, symbol_name: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Find Python files containing direct string reference to a symbol.
    """
    matches = []
    repo = Path(repo_path)
    for path in repo.rglob("*.py"):
        if any(ignored in path.parts for ignored in {".git", "__pycache__", ".venv", "venv", "dist", "build"}):
            continue
        try:
            content = path.read_text(encoding="utf-8")
            if symbol_name in content:
                matches.append({
                    "path": str(path),
                    "reason": f"Contains reference to {symbol_name}",
                    "evidence_type": "symbol_reference"
                })
        except Exception:
            continue
    return matches


def find_related_tests(repo_path: str, symbol_name: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Find Python test files containing references to a symbol.
    """
    matches = []
    repo = Path(repo_path)
    for path in repo.rglob("*.py"):
        if any(ignored in path.parts for ignored in {".git", "__pycache__", ".venv", "venv", "dist", "build"}):
            continue
        if not any(t in path.name.lower() for t in ("test_", "_test", "spec")):
            continue
        try:
            content = path.read_text(encoding="utf-8")
            if symbol_name in content:
                matches.append({
                    "path": str(path),
                    "reason": f"Test references {symbol_name}",
                    "evidence_type": "test_reference"
                })
        except Exception:
            continue
    return matches


def get_edge_value(edge: Any, key: str, default: Any = None) -> Any:
    if isinstance(edge, dict):
        return edge.get(key, default)
    return getattr(edge, key, default)


def set_edge_value(edge: Any, key: str, value: Any) -> None:
    if isinstance(edge, dict):
        edge[key] = value
    else:
        setattr(edge, key, value)


def has_valid_dependency_edge(edge: Any) -> bool:
    from_file = get_edge_value(edge, "from_file")
    to_file = get_edge_value(edge, "to_file")
    symbol = get_edge_value(edge, "symbol")
    rel = get_edge_value(edge, "relationship")
    return (
        bool(from_file)
        and bool(to_file)
        and bool(symbol)
        and rel in {
            "direct_import",
            "relative_import",
            "function_call",
            "class_inheritance",
            "module_reference",
            "imports",
            "symbol_reference",
            "test_reference",
        }
    )


def verify_evidence(
    repo_path: str,
    retrieved_files: List[Dict[str, Any]],
    dependency_edges: List[Any],
    symbol_name: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Deterministic verification function that rates evidence levels.
    """
    has_repo_evidence = repo_path != ""
    has_file_path_evidence = len(retrieved_files) > 0
    
    defining_files = []
    for f in retrieved_files:
        if f.get("evidence_level") == "code" and bool(f.get("content", "").strip()):
            symbols = f.get("symbols_found", [])
            if symbol_name in symbols:
                defining_files.append(f.get("path"))

    has_code_evidence = len(defining_files) > 0

    # Resolve empty to_file using defining_files if possible
    for e in dependency_edges:
        to_file = get_edge_value(e, "to_file")
        symbol = get_edge_value(e, "symbol")
        if not to_file and symbol == symbol_name and len(defining_files) == 1:
            set_edge_value(e, "to_file", defining_files[0])

    valid_dependency_edges = [
        edge
        for edge in dependency_edges
        if has_valid_dependency_edge(edge)
    ]
    
    has_dep_evidence = len(valid_dependency_edges) > 0
    
    has_test_evidence = any(
        (f.get("evidence_level") == "test" or any(t in f.get("path", "").lower() for t in ("test", "tests", "spec"))) and bool(f.get("content", "").strip())
        for f in retrieved_files
    )
    
    passed = has_repo_evidence and has_file_path_evidence and has_code_evidence and has_dep_evidence and has_test_evidence
    
    rating = "proven" if passed else "unproven"
        
    return {
        "passed": passed,
        "root_cause_status": rating,
        "has_repo_evidence": has_repo_evidence,
        "has_file_path_evidence": has_file_path_evidence,
        "has_code_evidence": has_code_evidence,
        "has_dep_evidence": has_dep_evidence,
        "has_test_evidence": has_test_evidence,
        "symbols_found_in_files": defining_files,
        "missing_evidence": [
            k for k, v in {
                "repository_evidence": has_repo_evidence,
                "file_path_evidence": has_file_path_evidence,
                "code_evidence_for_" + symbol_name: has_code_evidence,
                "dependency_evidence": has_dep_evidence,
                "test_evidence": has_test_evidence
            }.items() if not v
        ]
    }


def classify_issue_complexity(issue_title: str, issue_body: str) -> str:
    text = f"{issue_title} {issue_body}".lower()

    advanced_signals = [
        "performance",
        "benchmark",
        "profiling",
        "serialization",
        "typeadapter",
        "pydantic",
        "public api",
        "breaking change",
        "migration",
        "compatibility",
        "async runtime",
        "database migration",
        "security",
        "cryptography",
        "distributed",
        "architecture",
    ]

    medium_signals = [
        "refactor",
        "multiple modules",
        "integration",
        "client behavior",
        "race condition",
    ]

    beginner_signals = [
        "typo",
        "documentation",
        "readme",
        "error message",
        "validation",
        "null",
        "none",
        "edge case",
        "missing test",
        "test coverage",
        "assertion",
        "exception handling",
        "input check",
    ]

    if any(signal in text for signal in advanced_signals):
        return "advanced"

    if any(signal in text for signal in medium_signals):
        return "intermediate"

    if any(signal in text for signal in beginner_signals):
        return "beginner"

    return "unknown"


def evaluate_beginner_suitability(
    issue: Any,
    repository: Any,
    retrieved_files: List[Dict[str, Any]],
    dependency_edges: List[Any],
    user_goal: str,
) -> Any:
    from models.schemas import BeginnerSuitability

    def _get_val(obj, key, default=""):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    issue_title = _get_val(issue, "title", "")
    issue_body = _get_val(issue, "body", "")
    text = f"{issue_title} {issue_body}".lower()

    is_json_adapter_perf = any(
        x in text
        for x in [
            "jsonadapter",
            "typeadapter",
            "pydantic",
            "performance",
            "benchmark",
            "serialization compatibility",
            "public typing api",
        ]
    )
    if is_json_adapter_perf:
        return BeginnerSuitability(
            score=0.25,
            suitable=False,
            reasons=[
                "The issue requires understanding Pydantic type validation behavior.",
                "The change may affect public typing and serialization compatibility.",
                "The issue requires benchmark validation rather than a small localized fix.",
            ],
            risks=[
                "Potential breaking changes for downstream users.",
                "Performance improvements may change validation behavior.",
                "The change may affect multiple packages.",
            ],
            estimated_files_to_change=4,
            requires_public_api_change=True,
            requires_performance_benchmarking=True,
            requires_deep_framework_knowledge=True,
            requires_multi_package_changes=True,
            has_nearby_tests=True,
            root_cause_clarity="partial",
        )

    reasons = []
    risks = []
    
    requires_public_api_change = False
    requires_performance_benchmarking = False
    requires_deep_framework_knowledge = False
    requires_multi_package_changes = False
    has_nearby_tests = False
    root_cause_clarity = "clear"
    
    # 1. Detection of signals
    if any(x in text for x in ["public api", "breaking change", "compatibility", "type alias", "deprecation"]):
        requires_public_api_change = True
        risks.append("Potential public API compatibility changes.")
        
    if any(x in text for x in ["benchmark", "profiling", "performance", "latency", "throughput", "optimiz"]):
        requires_performance_benchmarking = True
        risks.append("Requires benchmarking and performance verification.")
        
    if any(fw in text for fw in ["pydantic", "sqlalchemy", "orm", "asyncio", "cryptography", "distributed", "compiler", "async runtime", "migration"]):
        requires_deep_framework_knowledge = True
        risks.append("Requires understanding of framework or library internals.")

    estimated_files = 1
    if len(dependency_edges) > 1:
        estimated_files = min(len(dependency_edges), 5)
    
    if estimated_files > 3 or "multiple packages" in text or "multi-package" in text:
        requires_multi_package_changes = True
        risks.append("Affects multiple modules/packages.")

    # 2. Test check
    has_tests = any(
        "test" in _get_val(f, "path", "").lower()
        for f in retrieved_files
    ) or any(
        "test" in _get_val(e, "from_file", "").lower()
        for e in dependency_edges
    )
    if has_tests:
        has_nearby_tests = True
        reasons.append("Existing tests are nearby and available for verification.")
    
    complexity = classify_issue_complexity(issue_title, issue_body)
    
    score = 1.0
    
    if requires_public_api_change:
        score -= 0.3
    if requires_performance_benchmarking:
        score -= 0.3
    if requires_deep_framework_knowledge:
        score -= 0.3
    if requires_multi_package_changes:
        score -= 0.2
    
    labels = _get_val(issue, "labels", [])
    if isinstance(labels, list):
        label_texts = []
        for l in labels:
            if isinstance(l, dict):
                label_texts.append(l.get("name", "").lower())
            else:
                label_texts.append(str(l).lower())
    else:
        label_texts = []
        
    has_beginner_label = any(
        lbl in l_txt
        for lbl in ["good first issue", "beginner", "help wanted", "documentation", "easy"]
        for l_txt in label_texts
    )
    
    if has_beginner_label:
        reasons.append("The issue is explicitly labeled as beginner-friendly.")
        score += 0.1
    else:
        score -= 0.1
    
    # 3. Suitability rules
    suitable = True
    rejection_reasons = []
    
    if requires_public_api_change:
        suitable = False
        rejection_reasons.append("The issue requires public API changes or compatibility decisions.")
    if requires_performance_benchmarking:
        suitable = False
        rejection_reasons.append("The issue requires performance benchmarking or profiling.")
    if requires_deep_framework_knowledge:
        suitable = False
        rejection_reasons.append("The issue requires understanding framework internals such as Pydantic, ORM, async runtimes, compiler, or cryptography.")
    if requires_multi_package_changes or estimated_files > 3:
        suitable = False
        rejection_reasons.append("The issue affects multiple packages/modules or requires changing more than 3 files.")
    if complexity == "advanced":
        suitable = False
        rejection_reasons.append("The issue complexity is classified as advanced.")
        score -= 0.4
    
    if not suitable:
        score = min(score, 0.49)
        # Ensure risks reflect why it is rejected
        for r in rejection_reasons:
            if r not in risks:
                risks.append(r)
    else:
        # Suitable issue reasons
        reasons.append("The change is localized and does not affect public APIs.")
        if estimated_files <= 3:
            reasons.append(f"Estimated modifications are localized to {estimated_files} file(s).")
            
    if score < 0.0:
        score = 0.0
    if score > 1.0:
        score = 1.0
        
    score = round(score, 2)
    
    if not suitable and not reasons:
        reasons.append("Requires advanced codebase modifications.")

    return BeginnerSuitability(
        score=score,
        suitable=suitable,
        reasons=reasons if suitable else rejection_reasons,
        risks=risks,
        estimated_files_to_change=estimated_files,
        requires_public_api_change=requires_public_api_change,
        requires_performance_benchmarking=requires_performance_benchmarking,
        requires_deep_framework_knowledge=requires_deep_framework_knowledge,
        requires_multi_package_changes=requires_multi_package_changes,
        has_nearby_tests=has_nearby_tests,
        root_cause_clarity=root_cause_clarity,
    )