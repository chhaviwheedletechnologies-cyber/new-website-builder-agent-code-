import operator
from typing import List, Dict, Any, Annotated
from typing_extensions import TypedDict
from models import CampaignGoal

def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    if not a: a = {}
    if not b: b = {}
    return {**a, **b}

class OrchestratorState(TypedDict):
    client_goal: CampaignGoal
    brand_context: str
    brand_color: str
    secondary_color: str
    logo_data: str
    target_pages: List[str]
    messages: Annotated[List[str], operator.add]
    execution_results: Annotated[Dict[str, Any], merge_dicts]
