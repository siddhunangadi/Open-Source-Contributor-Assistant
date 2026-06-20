# tests/test_state_regression.py

from agents.supervisor import SupervisorAgent
from models.initial_state import create_initial_state
from models.schemas import DependencyEdge

def test_state_regression_preserves_repository_and_issue():
    # 1. Initialize state
    goal = "Fix postgrest JSONAdapter performance"
    state = create_initial_state(goal)
    
    # 2. Simulate repository retrieved
    repo = {
        "name": "supabase-py",
        "full_name": "supabase/supabase-py",
        "html_url": "https://github.com/supabase/supabase-py",
        "stars": 1000,
        "language": "Python"
    }
    state["selected_repository"] = repo
    state["repository"] = repo
    state["repository_url"] = repo["html_url"]
    
    # 3. Simulate issue retrieved
    issue = {
        "number": 123,
        "title": "postgrest JSONAdapter issue",
        "body": "postgrest.types.JSONAdapter is slow",
        "url": "https://github.com/supabase/supabase-py/issues/123"
    }
    state["selected_issue"] = issue
    state["issue"] = issue
    state["issue_url"] = issue["url"]
    
    # 4. Simulate file retrieved
    file_record = {
        "path": "src/postgrest/types.py",
        "github_url": "https://github.com/supabase/supabase-py/blob/main/src/postgrest/types.py",
        "content": "class JSONAdapter:\n    pass",
        "symbols_found": ["JSONAdapter"],
        "evidence_level": "code"
    }
    state["retrieved_files"].append(file_record)

    # Simulate dependency edge
    edge = DependencyEdge(
        from_file="src/postgrest/base_request_builder.py",
        to_file="src/postgrest/types.py",
        symbol="JSONAdapter",
        relationship="imports",
        evidence="from postgrest.types import JSONAdapter",
        github_url="https://github.com/supabase/supabase-py/blob/main/src/postgrest/base_request_builder.py"
    )
    state["dependency_edges"].append(edge)
    
    # 5. Instantiate agent and generate final answer
    agent = SupervisorAgent()
    final_answer = agent.generate_final_answer(state)
    
    # 6. Asserts
    assert final_answer is not None
    assert len(final_answer) > 0
    assert state.get("repository") == repo
    assert state.get("issue") == issue
    assert state.get("confidence") is not None
    assert state.get("confidence") > 0.0
