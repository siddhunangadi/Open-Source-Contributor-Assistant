# tests/test_tool_contracts.py

import inspect
from tools.ingest_tool import ingest_repository


def test_ingest_repository_signature_matches_tool_schema():
    signature = inspect.signature(ingest_repository)

    expected_params = {
        "repo_url",
        "full_name",
        "html_url",
    }

    actual_params = set(signature.parameters.keys())

    assert expected_params.issubset(actual_params)


def test_retrieve_architecture_context_signature():
    from tools.retrieval_tools import retrieve_architecture_context
    signature = inspect.signature(retrieve_architecture_context)
    params = list(signature.parameters.keys())
    assert "repo_path" in params
    assert "repository_description" in params


def test_retrieve_file_context_signature():
    from tools.retrieval_tools import retrieve_file_context
    signature = inspect.signature(retrieve_file_context)
    params = list(signature.parameters.keys())
    assert "repo_path" in params
    assert "file_path" in params
    assert "query" in params
