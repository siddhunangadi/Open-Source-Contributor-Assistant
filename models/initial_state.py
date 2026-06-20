# models/initial_state.py

from models.state import AgentState


def create_initial_state(goal: str) -> AgentState:
    return {
        "user_goal": goal,
        "goal": goal,
        "thoughts": [],
        "actions": [],
        "observations": [],
        "repositories": [],
        "selected_repository": None,
        "issues": [],
        "selected_issue": None,
        "retrieved_context": [],
        "dependencies": [],
        "current_action": "",
        "current_action_input": {},
        "verification_result": {},
        "final_answer": "",
        "iteration_count": 0,
        # Evidence-grounded fields
        "iterations": 0,
        "repository": None,
        "issue": None,
        "repository_tree": [],
        "retrieved_files": [],
        "dependency_edges": [],
        "failed_tool_calls": [],
        "root_cause_status": "unproven",
        "confidence": 0.0,
        "repo_path": None,
        "language": None,
        "test_files": [],
        "evidence": [],
        "executed_tool_calls": [],
    }