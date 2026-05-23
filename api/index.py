"""
Vercel serverless function entrypoint.
Self-contained FastAPI app for the Multi-Agent Real Estate Intelligence API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI(title="Multi-Agent Real Estate Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchInput(BaseModel):
    target_location: str = Field(..., description="Target location for property search")
    search_radius_miles: str = Field(default="5")
    min_price: str = Field(default="")
    max_price: str = Field(default="")
    zoning_type: str = Field(default="")
    minimum_acres: str = Field(default="")
    source_agents: str = Field(
        default="Real Estate Data Researcher, Property Development Analyst, API Response Manager"
    )
    client_type: str = Field(default="developer")


@app.get("/api/status")
async def health_check():
    return {"status": "ok", "mode": "demo", "timestamp": datetime.now().isoformat()}


@app.get("/api/agents")
async def get_agents():
    return {
        "agents": [
            {
                "id": "real_estate_data_researcher",
                "name": "Data Researcher",
                "role": "Real Estate Data Researcher",
                "tools": ["RealEstateApiTool", "99acresIndiaTool", "MagicBricksIndiaTool"],
                "color": "#3b82f6",
            },
            {
                "id": "property_development_analyst",
                "name": "Dev Analyst",
                "role": "Property Development Analyst",
                "tools": ["PropertyScoringTool", "SarvamAnalysisTool"],
                "color": "#10b981",
            },
            {
                "id": "api_response_manager",
                "name": "API Manager",
                "role": "API Response Manager",
                "tools": ["SarvamResponseGenerator"],
                "color": "#f59e0b",
            },
            {
                "id": "information_collector",
                "name": "Info Collector",
                "role": "Information Collector",
                "tools": ["FileReadTool"],
                "color": "#8b5cf6",
            },
            {
                "id": "client_presentation_specialist",
                "name": "Presentation",
                "role": "Client Presentation Specialist",
                "tools": ["FileReadTool"],
                "color": "#f43f5e",
            },
            {
                "id": "workflow_supervisor",
                "name": "Supervisor",
                "role": "Workflow Supervisor",
                "tools": ["FileReadTool"],
                "color": "#06b6d4",
            },
        ]
    }


@app.post("/api/run")
async def start_run(inputs: SearchInput):
    return {
        "run_id": "demo",
        "status": "started",
        "message": "CrewAI execution is available in local mode. Use demo mode in the UI for deployed version.",
    }
