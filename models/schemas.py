# models/schemas.py

from pydantic import BaseModel
from typing import List

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Repository(BaseModel):
    name: str
    full_name: str
    description: Optional[str] = ""
    stars: int
    language: Optional[str] = "Unknown"   # GitHub returns null for some repos
    html_url: str


class DependencyEdge(BaseModel):
    from_file: str
    to_file: str
    symbol: Optional[str] = None
    symbols: Optional[List[str]] = None
    relationship: str
    evidence: Optional[str] = None
    github_url: Optional[str] = None



class Issue(BaseModel):
    number: int
    title: str
    body: Optional[str] = ""              # GitHub returns null for issues with no body
    url: str
    labels: Optional[List[Any]] = None


class CodeChunk(BaseModel):
    file_path: str
    content: str


class ContributionPlan(BaseModel):
    summary: str
    files_to_modify: List[str]
    implementation_steps: List[str]
    risks: List[str]


class VerificationResult(BaseModel):
    passed: bool
    evidence_found: List[str]
    missing_evidence: List[str]


class AgentDecision(BaseModel):
    """
    Supervisor output.
    """
    thought: str
    action: str
    action_input: Dict[str, Any] = Field(
        default_factory=dict
    )


class ToolObservation(BaseModel):
    """
    Tool execution result.
    """
    tool_name: str
    success: bool
    result: Any


class AgentFinalAnswer(BaseModel):
    """
    Final agent response.
    """
    summary: str
    contribution_plan: str
    confidence_score: float


class RepositoryContext(BaseModel):
    repository_name: str
    relevant_files: List[str]
    retrieved_chunks: List[str]


class BeginnerSuitability(BaseModel):
    score: float
    suitable: bool
    reasons: List[str]
    risks: List[str]
    estimated_files_to_change: Optional[int] = None
    requires_public_api_change: bool = False
    requires_performance_benchmarking: bool = False
    requires_deep_framework_knowledge: bool = False
    requires_multi_package_changes: bool = False
    has_nearby_tests: bool = False
    root_cause_clarity: str