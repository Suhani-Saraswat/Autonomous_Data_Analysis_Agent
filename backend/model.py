from dataclasses import dataclass, field
from typing import Any

@dataclass
class AnalysisContext:
    query: str
    dataframe: Any
    dataset_name: str
    profile: dict[str, Any] = field(default_factory=dict)
    plan: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    chart: dict[str, Any] = field(default_factory=dict)
    insights: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
