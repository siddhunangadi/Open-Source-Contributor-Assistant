# models/evidence.py

from typing import Optional
from pydantic import BaseModel


class Evidence(BaseModel):

    claim: str

    source_type: str

    source_path: str

    source_url: str

    confidence: float

    verified: bool = False

    repository: Optional[str] = None

    issue_number: Optional[int] = None

    file_path: Optional[str] = None

    function_name: Optional[str] = None