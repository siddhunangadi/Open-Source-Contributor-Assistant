# models/state.py
from models.evidence import Evidence
from models.schemas import DependencyEdge
from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):

    user_goal: str

    thoughts: List[str]

    actions: List[str]

    observations: List[str]

    repositories: List[Dict[str, Any]]

    selected_repository: Optional[Dict[str, Any]]

    issues: List[Dict[str, Any]]

    selected_issue: Optional[Dict[str, Any]]

    retrieved_context: List[str]

    dependencies: List[str]

    verification_result: Dict[str, Any]

    current_action: str

    current_action_input: Dict[str, Any]

    final_answer: str

    iteration_count: int

    evidence: List[Any]

    repository_url: str

    issue_url: str

    repo_path: str

    ingestion_attempted: bool

    ingestion_error: Optional[str]

    # Evidence-grounded research architecture fields
    iterations: int
    repository: Optional[Dict[str, Any]]
    issue: Optional[Dict[str, Any]]
    repository_tree: List[str]
    retrieved_files: List[Dict[str, Any]]
    dependency_edges: List[DependencyEdge]
    failed_tool_calls: List[Dict[str, Any]]
    root_cause_status: str
    confidence: float
    goal: str
    language: Optional[str]
    test_files: List[str]
    executed_tool_calls: List[Dict[str, Any]]