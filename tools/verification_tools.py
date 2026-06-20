from pathlib import Path
from typing import Dict, List


def verify_files_exist(
    repo_path: str,
    files: List[str], **kwargs) -> Dict:
    """
    Verify files exist in repository.
    """

    existing_files = []
    missing_files = []

    repo = Path(repo_path)

    for file in files:

        full_path = repo / file

        if full_path.exists():
            existing_files.append(file)
        else:
            missing_files.append(file)

    return {
        "passed": len(missing_files) == 0,
        "existing_files": existing_files,
        "missing_files": missing_files
    }


def verify_retrieval_evidence(
    files: List[str],
    retrieved_context: List[str], **kwargs) -> Dict:
    """
    Verify files were actually retrieved by RAG.
    """

    evidence_found = []
    missing_evidence = []

    context_text = " ".join(
        retrieved_context
    ).lower()

    for file in files:

        if file.lower() in context_text:
            evidence_found.append(file)
        else:
            missing_evidence.append(file)

    return {
        "passed": len(missing_evidence) == 0,
        "evidence_found": evidence_found,
        "missing_evidence": missing_evidence
    }


def verify_dependency_evidence(
    files: List[str],
    dependency_files: List[str], **kwargs) -> Dict:
    """
    Verify files appear in dependency analysis.
    """

    evidence_found = []
    missing_evidence = []

    dependency_set = set(
        dependency_files
    )

    for file in files:

        if file in dependency_set:
            evidence_found.append(file)
        else:
            missing_evidence.append(file)

    return {
        "passed": len(missing_evidence) == 0,
        "evidence_found": evidence_found,
        "missing_evidence": missing_evidence
    }


def verify_plan(
    files_to_modify: List[str],
    repo_path: str,
    retrieved_context: List[str],
    dependency_files: List[str], **kwargs) -> Dict:
    """
    Comprehensive verification of a contribution plan.
    """

    file_check = verify_files_exist(
        repo_path,
        files_to_modify
    )

    retrieval_check = verify_retrieval_evidence(
        files_to_modify,
        retrieved_context
    )

    dependency_check = verify_dependency_evidence(
        files_to_modify,
        dependency_files
    )

    passed = (
        file_check["passed"]
        and retrieval_check["passed"]
        and dependency_check["passed"]
    )

    return {
        "passed": passed,
        "file_check": file_check,
        "retrieval_check": retrieval_check,
        "dependency_check": dependency_check
    }