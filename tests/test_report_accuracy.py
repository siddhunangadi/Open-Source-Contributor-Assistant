# tests/test_report_accuracy.py

import pytest
from agents.supervisor import SupervisorAgent
from models.initial_state import create_initial_state
from models.schemas import DependencyEdge
from app import build_final_markdown, ensure_blank_lines_around_tables

class MockResponse:
    def __init__(self, content):
        self.content = content

class MockLLM:
    def __init__(self, content=""):
        self.content = content
    def invoke(self, prompt, **kwargs):
        if self.content:
            return MockResponse(self.content)
            
        import re
        repo_matches = re.findall(r"'full_name': '([^']+)'", prompt)
        repo_name = repo_matches[0] if repo_matches else "unknown/repo"
        
        retrieved_paths = []
        for line in prompt.splitlines():
            if line.strip().startswith("- File: `"):
                path_match = re.search(r"- File: `([^`]+)`", line)
                if path_match:
                    retrieved_paths.append(path_match.group(1))

        evidence_rows = []
        for path in retrieved_paths:
            evidence_rows.append(f"| [CODE READ] | {path} | Verified fact |")
        evidence_table = "\n".join(evidence_rows) if evidence_rows else "| Badge | File | Verified fact |"

        mock_content = f"""
# Final Contribution Recommendation

## Repository
[repo](https://github.com/{repo_name})

## Issue
- What is proven:
  - Proven facts here.
- What is not proven yet:
  - Not proven facts here.

## Evidence Collected
| Badge | File | Verified fact |
|---|---|---|
{evidence_table}

## Dependency Trace
No direct importer or test reference to JSONAdapter was confirmed from retrieved evidence.

## Recommended Next Investigation
- Generic step 1.
- Generic step 2.

## Risks
- Risks here.

## Evidence Gaps
- Evidence gaps here.
"""
        return MockResponse(mock_content)

def test_markdown_tables_blank_lines():
    # Test blank line helper logic
    test_input = """
## Evidence Collected
| Badge | File | Verified fact |
|-------|------|----------------|
| [DEFINES] | types.py | Defines JSONAdapter |
## Next Steps
"""
    output = ensure_blank_lines_around_tables(test_input)
    assert "\n\n| Badge | File | Verified fact |" in output
    assert "Defines JSONAdapter |\n\n## Next Steps" in output

def test_stray_div_tags():
    # Test that building and rendering report contains no stray </div> or HTML layout wrappers
    state = create_initial_state("test")
    state["final_answer"] = "# Report\n| A | B |\n|---|---|\n| 1 | 2 |"
    
    # Render final markdown using build_final_markdown
    report = build_final_markdown(state)
    
    # The output should not contain any </div> or custom layout HTML wrapper tags
    assert "</div>" not in report
    assert "result-wrap" not in report
    assert "report-box" not in report

def test_isolation_cross_runs():
    # 1. A gfi-bot run after a supabase-py run contains no supabase paths or URLs.
    agent = SupervisorAgent()
    agent.answer_llm = MockLLM()

    # Supabase-py run state simulation
    state_supabase = create_initial_state("Fix postgrest JSONAdapter performance")
    repo_supabase = {
        "name": "supabase-py",
        "full_name": "supabase/supabase-py",
        "html_url": "https://github.com/supabase/supabase-py"
    }
    state_supabase["selected_repository"] = repo_supabase
    state_supabase["repository"] = repo_supabase
    state_supabase["repo_path"] = "data/repos/supabase_supabase-py"
    state_supabase["selected_issue"] = {
        "title": "JSONAdapter performance issue",
        "body": "JSONAdapter is slow"
    }
    
    # Add supabase evidence and file
    state_supabase["retrieved_files"].append({
        "path": "data/repos/supabase_supabase-py/src/postgrest/types.py",
        "github_url": "https://github.com/supabase/supabase-py/blob/main/src/postgrest/types.py",
        "content": "class JSONAdapter:\n    pass",
        "symbols_found": ["JSONAdapter"],
        "evidence_level": "code"
    })
    state_supabase["evidence"].append({
        "claim": "Verified file postgrest/types.py exists",
        "source_type": "github_file",
        "source_path": "data/repos/supabase_supabase-py/src/postgrest/types.py",
        "source_url": "https://github.com/supabase/supabase-py/blob/main/src/postgrest/types.py",
        "confidence": 1.0,
        "verified": True
    })
    
    report_supabase = agent.generate_final_answer(state_supabase)
    assert "supabase-py" in report_supabase
    
    # Gfi-bot run state simulation (started freshly with create_initial_state)
    state_gfi = create_initial_state("Fix missing class in gfi-bot")
    repo_gfi = {
        "name": "gfi-bot",
        "full_name": "osslab-pku/gfi-bot",
        "html_url": "https://github.com/osslab-pku/gfi-bot"
    }
    state_gfi["selected_repository"] = repo_gfi
    state_gfi["repository"] = repo_gfi
    state_gfi["repo_path"] = "data/repos/osslab-pku_gfi-bot"
    state_gfi["selected_issue"] = {
        "title": "Python classes not found",
        "body": "cannot import GFIResponse"
    }
    
    # Add gfi-bot file
    state_gfi["retrieved_files"].append({
        "path": "data/repos/osslab-pku_gfi-bot/gfibot/backend/models.py",
        "github_url": "https://github.com/osslab-pku/gfi-bot/blob/main/gfibot/backend/models.py",
        "content": "class GFIResponse:\n    pass",
        "symbols_found": ["GFIResponse"],
        "evidence_level": "code"
    })
    state_gfi["evidence"].append({
        "claim": "Verified file gfibot/backend/models.py exists",
        "source_type": "github_file",
        "source_path": "data/repos/osslab-pku_gfi-bot/gfibot/backend/models.py",
        "source_url": "https://github.com/osslab-pku/gfi-bot/blob/main/gfibot/backend/models.py",
        "confidence": 1.0,
        "verified": True
    })

    # Add a mock supabase file to retrieved_files to simulate vector leak
    state_gfi["retrieved_files"].append({
        "path": "data/repos/supabase_supabase-py/src/postgrest/types.py",
        "github_url": "https://github.com/supabase/supabase-py/blob/main/src/postgrest/types.py",
        "content": "class JSONAdapter:\n    pass",
        "symbols_found": ["JSONAdapter"],
        "evidence_level": "code"
    })
    state_gfi["evidence"].append({
        "claim": "Leaked file postgrest/types.py",
        "source_type": "github_file",
        "source_path": "data/repos/supabase_supabase-py/src/postgrest/types.py",
        "source_url": "https://github.com/supabase/supabase-py/blob/main/src/postgrest/types.py",
        "confidence": 1.0,
        "verified": True
    })

    report_gfi = agent.generate_final_answer(state_gfi)
    
    # 2. A supabase-py run after a gfi-bot run contains no gfi-bot paths or URLs
    assert "supabase" not in report_gfi
    assert "postgrest" not in report_gfi
    assert "JSONAdapter" not in report_gfi

def test_evidence_conciseness_and_tree_filtering():
    # 3. Final evidence table contains at most 12 items.
    # 4. Unrelated [PATH ONLY] files are excluded from final evidence.
    agent = SupervisorAgent()
    agent.answer_llm = MockLLM()
    state = create_initial_state("Fix postgrest types JSONAdapter performance")
    repo = {
        "name": "supabase-py",
        "full_name": "supabase/supabase-py",
        "html_url": "https://github.com/supabase/supabase-py"
    }
    state["selected_repository"] = repo
    state["repository"] = repo
    state["repo_path"] = "data/repos/supabase_supabase-py"

    # Add 15 path-only/file-path tree files (unrelated)
    for i in range(15):
        state["retrieved_files"].append({
            "path": f"data/repos/supabase_supabase-py/unrelated_{i}.py",
            "evidence_level": "file_path"
        })

    # Add a code read file containing target symbol
    state["retrieved_files"].append({
        "path": "data/repos/supabase_supabase-py/src/postgrest/types.py",
        "content": "class JSONAdapter:\n    pass",
        "symbols_found": ["JSONAdapter"],
        "evidence_level": "code"
    })

    # Add a dependency edge file
    edge = DependencyEdge(
        from_file="data/repos/supabase_supabase-py/src/postgrest/base_request_builder.py",
        to_file="data/repos/supabase_supabase-py/src/postgrest/types.py",
        symbol="JSONAdapter",
        symbols=["JSONAdapter"],
        relationship="imports"
    )
    state["dependency_edges"].append(edge)

    # We also add base_request_builder.py to retrieved_files as a path-only file connected to edge
    state["retrieved_files"].append({
        "path": "data/repos/supabase_supabase-py/src/postgrest/base_request_builder.py",
        "evidence_level": "file_path"
    })

    # Add .gitignore and LICENSE path-only files
    state["retrieved_files"].append({
        "path": "data/repos/supabase_supabase-py/.gitignore",
        "evidence_level": "PATH ONLY"
    })
    state["retrieved_files"].append({
        "path": "data/repos/supabase_supabase-py/LICENSE",
        "evidence_level": "PATH ONLY"
    })

    report = agent.generate_final_answer(state)
    
    # Check item limit
    assert len(state["retrieved_files"]) <= 12
    # Check that unrelated tree files are excluded
    retrieved_paths = [f["path"] for f in state["retrieved_files"]]
    assert "data/repos/supabase_supabase-py/.gitignore" not in retrieved_paths
    assert "data/repos/supabase_supabase-py/LICENSE" not in retrieved_paths
    assert any("unrelated" not in p for p in retrieved_paths)

def test_wording_isolation():
    # 5. Missing-symbol issue reports never contain performance-specific wording.
    # 6. Performance issue reports never contain missing-class-specific wording.
    agent = SupervisorAgent()
    
    # Missing symbol issue report
    state_ms = create_initial_state("Fix missing class ModuleNotFoundError")
    state_ms["selected_issue"] = {
        "title": "ModuleNotFoundError: cannot import name 'RepoBrief'",
        "body": "missing class RepoBrief from exports"
    }
    ms_body = """
## Evidence Gaps
- performance-sensitive usages are unproven.
- benchmark difference.

## Recommended Next Investigation
- Step 1.
"""
    processed_ms = agent._post_process_report(ms_body, state_ms)
    
    assert "performance-sensitive" not in processed_ms
    assert "benchmark difference" not in processed_ms
    assert "JSONAdapter" not in processed_ms
    assert "screenshots is still unknown" in processed_ms
    assert "The exact class referenced by the issue screenshots is still unknown." in processed_ms

    # Performance issue report
    state_perf = create_initial_state("Fix latency and performance in postgrest JSONAdapter")
    state_perf["selected_issue"] = {
        "title": "JSONAdapter is much slower than TypeAdapter",
        "body": "Speed latency benchmark details..."
    }
    perf_body = """
## Evidence Gaps
- screenshots is still unknown.
- cannot import RepoBrief.

## Recommended Next Investigation
- Step 1.
"""
    processed_perf = agent._post_process_report(perf_body, state_perf)
    
    assert "screenshots is still unknown" not in processed_perf
    assert "cannot import" not in processed_perf
    assert "benchmark or regression test is still needed." in processed_perf

def test_missing_symbol_confidence_capping():
    # 7. Missing-symbol issue confidence is capped when exact symbol and reproduction are unproven.
    agent = SupervisorAgent()
    state = create_initial_state("Fix missing class in gfi-bot")
    state["selected_issue"] = {
        "title": "ModuleNotFoundError: cannot import some class",
        "body": "Error class is missing"
    }
    state["selected_repository"] = {
        "full_name": "osslab-pku/gfi-bot",
        "language": "Python"
    }
    state["repository"] = state["selected_repository"]
    state["repo_path"] = "data/repos/osslab-pku_gfi-bot"
    
    # Set evidence records so confidence calculation scores points
    state["retrieved_files"].append({
        "path": "data/repos/osslab-pku_gfi-bot/gfibot/backend/models.py",
        "content": "class GFIResponse:\n    pass",
        "evidence_level": "code"
    })
    edge = DependencyEdge(
        from_file="data/repos/osslab-pku_gfi-bot/gfibot/backend/routes/user.py",
        to_file="data/repos/osslab-pku_gfi-bot/gfibot/backend/models.py",
        symbol="GFIResponse",
        relationship="imports"
    )
    state["dependency_edges"].append(edge)
    state["evidence"].append({
        "claim": "Verified file models.py exists",
        "source_type": "github_file",
        "source_path": "data/repos/osslab-pku_gfi-bot/gfibot/backend/models.py",
        "source_url": "https://github.com/osslab-pku/gfi-bot/blob/main/gfibot/backend/models.py",
        "confidence": 1.0,
        "verified": True
    })

    # Calculate confidence
    confidence = agent._calculate_confidence(state)
    
    # Assert capped at 0.65 or 0.70 because exact symbol and reproduction are unproven
    assert confidence <= 0.70
    
    # Verify description matching Bug 5 requirement
    agent.answer_llm = MockLLM()
    report = agent.generate_final_answer(state)
    assert "repository, issue, model definitions, direct importers, and relevant test references were verified; the screenshot-specific missing class and reproducible root cause remain unproven." in report

def test_language_preservation():
    # 8. Valid repository language is preserved in final state and UI summary.
    agent = SupervisorAgent()
    agent.answer_llm = MockLLM()
    
    state = create_initial_state("test")
    state["selected_repository"] = {
        "full_name": "osslab-pku/gfi-bot",
        "language": "Python"
    }
    state["repository"] = state["selected_repository"]
    state["language"] = "Python"
    
    # Run observation block handler
    repo_data = {
        "full_name": "osslab-pku/gfi-bot",
        "html_url": "https://github.com/osslab-pku/gfi-bot",
        "language": None  # simulating null returned from api
    }
    # This shouldn't overwrite Python with None
    agent._update_state_from_result(state, "get_repository", {}, repo_data)
    
    assert state.get("language") == "Python"
    assert state.get("repository", {}).get("language") is None or state.get("repository", {}).get("language") == "Python"

def test_symbol_accurate_direct_importer():
    # 9. Direct importer claims only appear when the edge explicitly includes the target symbol.
    agent = SupervisorAgent()
    state = create_initial_state("Fix Python classes not found in gfi-bot")
    state["selected_issue"] = {
        "title": "Python classes not found",
        "body": "cannot import GFIResponse"
    }
    state["selected_repository"] = {
        "full_name": "osslab-pku/gfi-bot",
        "language": "Python"
    }
    state["repository"] = state["selected_repository"]
    
    # Add a dependency edge importing only GFIResponse (no JSONAdapter symbol)
    edge = DependencyEdge(
        from_file="gfibot/backend/routes/user.py",
        to_file="gfibot/backend/models.py",
        symbol="GFIResponse",
        symbols=["GFIResponse"],
        relationship="imports"
    )
    state["dependency_edges"].append(edge)
    
    body = """
## Evidence Gaps
- direct importer of GFIResponse was confirmed
- is specifically caused by GFIResponse.
"""
    processed = agent._post_process_report(body, state)
    
    # Should say route modules import model classes, including GFIResponse, but not claim JSONAdapter or root cause specifically
    assert "is specifically caused by GFIResponse" not in processed
    assert "Several route modules directly import model classes from gfibot/backend/models.py, including GFIResponse and related request/response models" in processed

def test_clean_markdown_no_stray_div():
    # 10. Final Markdown contains no raw </div> and table blocks are valid.
    state = create_initial_state("test")
    state["final_answer"] = "# Report\n| A | B |\n|---|---|\n| 1 | 2 |"
    
    report = build_final_markdown(state)
    assert "</div>" not in report
    assert "\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n" in report

def test_general_issue_next_steps():
    agent = SupervisorAgent()
    state = create_initial_state("An empty page problem in the frontend")
    state["selected_issue"] = {
        "title": "An empty page problem in the frontend",
        "body": "Pagination has bugs"
    }
    body = """
## Recommended Next Investigation
- Step 1.
"""
    processed = agent._post_process_report(body, state)
    
    # Should contain generic steps, and NOT contain unresolved class or JSONAdapter wording
    assert "Retrieve the repository code and context related to the issue goal." in processed
    assert "Inspect issue screenshots and comments to identify the exact unresolved class." not in processed
    assert "Retrieve the complete JSONAdapter definition and benchmark details from the issue." not in processed


def test_beginner_suitability_rejection_jsonadapter():
    # 1. JSONAdapter / TypeAdapter / Pydantic performance issue is rejected for beginner users.
    from tools.evidence_tools import evaluate_beginner_suitability
    issue = {
        "title": "JSONAdapter is much slower than TypeAdapter",
        "body": "Using Pydantic performance benchmarks",
        "labels": []
    }
    repo = {"full_name": "supabase/supabase-py"}
    suitability = evaluate_beginner_suitability(
        issue=issue,
        repository=repo,
        retrieved_files=[],
        dependency_edges=[],
        user_goal="I am a beginner in open source."
    )
    assert not suitability.suitable
    assert suitability.score == 0.25
    assert "understanding Pydantic type validation" in "".join(suitability.reasons)

def test_beginner_suitability_acceptance_localized():
    # 2. A localized validation issue with one implementation file and one test file is accepted.
    from tools.evidence_tools import evaluate_beginner_suitability
    issue = {
        "title": "Fix validation error in input check",
        "body": "We should handle null inputs correctly.",
        "labels": [{"name": "beginner"}]
    }
    repo = {"full_name": "some/repo"}
    retrieved = [
        {"path": "src/validator.py", "evidence_level": "code"},
        {"path": "tests/test_validator.py", "evidence_level": "test"}
    ]
    suitability = evaluate_beginner_suitability(
        issue=issue,
        repository=repo,
        retrieved_files=retrieved,
        dependency_edges=[],
        user_goal="I am a beginner in open source."
    )
    assert suitability.suitable
    assert suitability.score >= 0.6

def test_beginner_suitability_acceptance_documentation():
    # 3. A documentation issue is accepted when the user allows documentation work.
    from tools.evidence_tools import evaluate_beginner_suitability
    issue = {
        "title": "Fix typo in README.md",
        "body": "Spelling mistake in installation instructions.",
        "labels": [{"name": "documentation"}]
    }
    repo = {"full_name": "some/repo"}
    suitability = evaluate_beginner_suitability(
        issue=issue,
        repository=repo,
        retrieved_files=[],
        dependency_edges=[],
        user_goal="I am a beginner and want to do documentation work."
    )
    assert suitability.suitable

def test_beginner_suitability_rejection_public_api():
    # 4. An issue requiring public API changes is rejected.
    from tools.evidence_tools import evaluate_beginner_suitability
    issue = {
        "title": "Change public API signature of main client",
        "body": "We need to update deprecation and type alias properties.",
        "labels": []
    }
    repo = {"full_name": "some/repo"}
    suitability = evaluate_beginner_suitability(
        issue=issue,
        repository=repo,
        retrieved_files=[],
        dependency_edges=[],
        user_goal="I am a beginner in open source."
    )
    assert not suitability.suitable
    assert any("public API" in r for r in suitability.reasons)

def test_beginner_suitability_rejection_benchmarking():
    # 5. An issue requiring benchmarking is rejected.
    from tools.evidence_tools import evaluate_beginner_suitability
    issue = {
        "title": "Optimize latency through throughput profiling",
        "body": "Need to run benchmark validation.",
        "labels": []
    }
    repo = {"full_name": "some/repo"}
    suitability = evaluate_beginner_suitability(
        issue=issue,
        repository=repo,
        retrieved_files=[],
        dependency_edges=[],
        user_goal="I am a beginner in open source."
    )
    assert not suitability.suitable
    assert any("benchmark" in r for r in suitability.reasons)

def test_supervisor_search_continuation():
    # 6. The supervisor continues searching after rejecting a candidate.
    agent = SupervisorAgent()
    state = create_initial_state("I am a beginner in open source.")
    state["selected_repository"] = {"full_name": "supabase/supabase-py", "name": "supabase-py"}
    
    # Simulate receiving get_issues result where all are unsuitable
    unsuitable_issues = [
        {"number": 1, "title": "JSONAdapter is slow benchmark", "body": "performance problem", "labels": []}
    ]
    
    agent._update_state_from_result(state, "get_issues", {}, unsuitable_issues)
    
    # Issues list should be empty because candidate was filtered/rejected
    assert len(state["issues"]) == 0
    # The rejected candidate must be in state["rejected_candidates"]
    assert len(state["rejected_candidates"]) == 1
    assert state["rejected_candidates"][0]["number"] == 1

def test_final_recommendation_why_beginner_friendly():
    # 7. Final beginner recommendation includes “Why This Is Beginner-Friendly.”
    agent = SupervisorAgent()
    agent.answer_llm = MockLLM()
    state = create_initial_state("I am a beginner in open source.")
    state["selected_repository"] = {"full_name": "some/repo", "name": "repo"}
    state["selected_issue"] = {
        "title": "Fix small typo in readme",
        "body": "Simple readme edit",
        "labels": [{"name": "good first issue"}]
    }
    state["issue"] = state["selected_issue"]
    
    # Propose evidence so it passes insufficient evidence checks
    state["retrieved_files"].append({
        "path": "README.md",
        "content": "some doc text",
        "evidence_level": "code"
    })
    state["evidence"].append({
        "claim": "Verified README.md exists",
        "source_type": "github_file",
        "source_path": "README.md",
        "source_url": "https://github.com/some/repo/blob/main/README.md",
        "confidence": 1.0,
        "verified": True
    })
    
    report = agent.generate_final_answer(state)
    assert "## Why This Is Beginner-Friendly" in report

def test_no_safe_issue_fallback():
    # 8. If no safe issue exists, the system returns an honest no-recommendation result.
    agent = SupervisorAgent()
    state = create_initial_state("I am a beginner in open source.")
    state["selected_repository"] = {"full_name": "supabase/supabase-py", "name": "supabase-py"}
    state["selected_issue"] = {
        "title": "JSONAdapter is slow",
        "body": "benchmarking pydantic type validation",
        "labels": []
    }
    state["issue"] = state["selected_issue"]
    
    report = agent.generate_final_answer(state)
    assert "No safe beginner-friendly issue was verified in the current candidate set." in report
