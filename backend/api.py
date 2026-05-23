"""
FastAPI backend for the Multi-Agent Real Estate Intelligence Dashboard.
Wraps the CrewAI crew with SSE streaming for real-time progress updates.
"""

import asyncio
import json
import uuid
import sys
import os
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional

# Add project src to path so we can import the crew
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass


# ─── Models ────────────────────────────────────────────────────

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


# ─── State ─────────────────────────────────────────────────────

runs: Dict[str, Dict[str, Any]] = {}


# ─── App ───────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Cleanup on shutdown
    runs.clear()

app = FastAPI(
    title="Multi-Agent Real Estate Intelligence API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Endpoints ─────────────────────────────────────────────────

@app.get("/api/status")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.post("/api/run")
async def start_run(inputs: SearchInput):
    """Start a new crew execution."""
    run_id = str(uuid.uuid4())[:8]

    runs[run_id] = {
        "status": "starting",
        "inputs": inputs.model_dump(),
        "queue": asyncio.Queue(),
        "results": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
    }

    # Start crew in background
    asyncio.create_task(_run_crew(run_id, inputs.model_dump()))

    return {"run_id": run_id, "status": "started"}


@app.get("/api/stream/{run_id}")
async def stream_events(run_id: str):
    """SSE endpoint for real-time crew progress updates."""
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")

    async def event_generator():
        queue = runs[run_id]["queue"]
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=120.0)
                yield f"data: {json.dumps(event)}\n\n"

                if event.get("type") in ("complete", "error"):
                    break
            except asyncio.TimeoutError:
                # Send heartbeat
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/agents")
async def get_agents():
    """Return agent metadata for pipeline visualization."""
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


# ─── Crew Runner ───────────────────────────────────────────────

AGENT_ORDER = [
    "real_estate_data_researcher",
    "property_development_analyst",
    "api_response_manager",
    "information_collector",
    "client_presentation_specialist",
    "workflow_supervisor",
]

AGENT_NAMES = {
    "real_estate_data_researcher": "Data Researcher",
    "property_development_analyst": "Dev Analyst",
    "api_response_manager": "API Manager",
    "information_collector": "Info Collector",
    "client_presentation_specialist": "Presentation",
    "workflow_supervisor": "Supervisor",
}


async def _run_crew(run_id: str, inputs: dict):
    """Execute the CrewAI crew and stream progress events."""
    queue = runs[run_id]["queue"]

    try:
        await queue.put({
            "type": "log",
            "agent": "System",
            "message": "Initializing crew with sequential process...",
        })

        # Try to import and run the actual crew
        try:
            from multi_agent_information_management_system_with_crew_supervision.crew import (
                MultiAgentInformationManagementSystemWithCrewSupervisionCrew,
            )

            crew_instance = MultiAgentInformationManagementSystemWithCrewSupervisionCrew()
            crew = crew_instance.crew()

            # Set up step callback for progress tracking
            current_task_index = 0

            def step_callback(step_output):
                nonlocal current_task_index
                agent_id = AGENT_ORDER[min(current_task_index, len(AGENT_ORDER) - 1)]
                agent_name = AGENT_NAMES.get(agent_id, "System")

                # Queue events (synchronous, but queue is thread-safe)
                asyncio.get_event_loop().call_soon_threadsafe(
                    queue.put_nowait,
                    {
                        "type": "log",
                        "agent": agent_name,
                        "message": str(step_output)[:200],
                    },
                )

            # Set step callback on crew tasks
            for i, task in enumerate(crew.tasks):
                original_callback = task.callback

                def make_task_callback(task_idx):
                    def task_done(output):
                        nonlocal current_task_index
                        current_task_index = task_idx + 1
                        agent_id = AGENT_ORDER[task_idx]
                        agent_name = AGENT_NAMES.get(agent_id, "System")

                        asyncio.get_event_loop().call_soon_threadsafe(
                            queue.put_nowait,
                            {
                                "type": "agent_status",
                                "agent_id": agent_id,
                                "status": "complete",
                                "task_index": task_idx,
                            },
                        )
                        asyncio.get_event_loop().call_soon_threadsafe(
                            queue.put_nowait,
                            {
                                "type": "log",
                                "agent": agent_name,
                                "message": f"Task complete: {output.description[:80] if output.description else 'done'}",
                            },
                        )

                        # Mark next agent as working
                        if task_idx + 1 < len(AGENT_ORDER):
                            next_id = AGENT_ORDER[task_idx + 1]
                            asyncio.get_event_loop().call_soon_threadsafe(
                                queue.put_nowait,
                                {
                                    "type": "agent_status",
                                    "agent_id": next_id,
                                    "status": "working",
                                },
                            )
                    return task_done

                task.callback = make_task_callback(i)

            # Mark first agent as working
            await queue.put({
                "type": "agent_status",
                "agent_id": AGENT_ORDER[0],
                "status": "working",
            })

            await queue.put({
                "type": "log",
                "agent": "System",
                "message": f"Starting crew execution for {inputs.get('target_location', 'unknown location')}",
            })

            # Run crew in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: crew.kickoff(inputs=inputs),
            )

            # Parse results
            results_data = {
                "properties": [],
                "metadata": {
                    "location": inputs.get("target_location", ""),
                    "api_sources": "CrewAI",
                },
                "presentation": "",
                "supervisor_report": "",
            }

            if result.tasks_output:
                for i, task_output in enumerate(result.tasks_output):
                    raw = task_output.raw if hasattr(task_output, 'raw') else str(task_output)
                    if i == 4:  # Presentation task
                        results_data["presentation"] = raw
                    elif i == 5:  # Supervisor task
                        results_data["supervisor_report"] = raw

                    # Try to parse properties from task outputs
                    if i <= 2:
                        try:
                            parsed = json.loads(raw) if isinstance(raw, str) else raw
                            if isinstance(parsed, dict) and "properties" in parsed:
                                results_data["properties"] = parsed["properties"]
                        except (json.JSONDecodeError, TypeError):
                            pass

            runs[run_id]["results"] = results_data

            await queue.put({
                "type": "complete",
                "results": results_data,
            })

        except ImportError as e:
            await queue.put({
                "type": "log",
                "agent": "System",
                "message": f"Could not import crew module: {e}. Running in demo mode.",
            })
            await queue.put({
                "type": "error",
                "message": f"Crew import failed: {e}",
            })

    except Exception as e:
        runs[run_id]["error"] = str(e)
        await queue.put({
            "type": "error",
            "message": str(e),
        })


# ─── Main ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True)
