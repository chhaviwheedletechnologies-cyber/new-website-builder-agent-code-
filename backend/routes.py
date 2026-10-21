from fastapi import APIRouter, HTTPException
from models import CampaignGoal
from state import OrchestratorState
from workflow import app_workflow
import os
import shutil
import traceback
from fastapi.responses import FileResponse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATES_DIR = OUTPUT_DIR / "templates"

router = APIRouter()

@router.post("/run-campaign", response_model=OrchestratorState)
def run_campaign(goal: CampaignGoal):
    initial_state = OrchestratorState(
        client_goal=goal,
        brand_context=goal.brand_context or "Premium, high-conversion modern branding.",
        brand_color=goal.brand_color or "#6C63FF",
        secondary_color=goal.secondary_color or "#FF6584",
        logo_data=goal.logo_data or "",
        target_pages=goal.target_pages or [],
        messages=["Starting UI generation workflow"],
        execution_results={}
    )
    
    try:
        result = app_workflow.invoke(initial_state)
        return result
    except Exception as e:
        with open("error.log", "w") as f:
            traceback.print_exc(file=f)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{run_id}.zip")
async def download_template(run_id: str):
    template_dir = TEMPLATES_DIR / f"template_{run_id}"
    if not template_dir.exists():
        raise HTTPException(status_code=404, detail="Template not found")
        
    zip_path = OUTPUT_DIR / f"website_{run_id}.zip"
    
    if not os.path.exists(zip_path):
        shutil.make_archive(
            str(zip_path.with_suffix("")),
            "zip",
            str(template_dir)
        )
        
    return FileResponse(
        str(zip_path),
        media_type="application/zip",
        filename=f"ai_website_{run_id}.zip"
    )
