"""Main entry point for the Stadium Commander FastAPI Application.

This module initializes the FastAPI app, registers exception handlers for HTTP 400
and 500 statuses, injects orchestrator and agent state variables, and mounts routes.
"""

import os
import logging
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from google import genai

from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from analyzers.crowd_analyzer import CrowdAnalyzer
from analyzers.transport_analyzer import TransportAnalyzer
from analyzers.medical_analyzer import MedicalAnalyzer
from analyzers.weather_analyzer import WeatherAnalyzer
from analyzers.volunteer_analyzer import VolunteerAnalyzer
from orchestrator.stadium_orchestrator import StadiumOrchestrator
from agents.commander_agent import CommanderAgent

# Setup system logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stadium_commander.app")

app = FastAPI(
    title="Stadium Commander API",
    version="1.0",
    description="AI-powered FIFA Stadium Operations Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend client accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register Exception Handlers without exposing stack traces
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Gracefully catches Pydantic validation errors and returns HTTP 400."""
    logger.warning("Request validation failed: %s", str(exc))
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid input"}
    )




@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Gracefully catches all unhandled exceptions and returns HTTP 500."""
    logger.exception("An unhandled exception occurred: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Unexpected errors"}
    )


# Dependency Injection Setup
def initialize_dependencies():
    """Wires up all analyzer modules, orchestrator, and reasoning agents."""
    logger.info("Initializing application dependencies.")
    
    # 1. Instantiate analyzers
    crowd = CrowdAnalyzer()
    transport = TransportAnalyzer()
    medical = MedicalAnalyzer()
    weather = WeatherAnalyzer()
    volunteer = VolunteerAnalyzer()
    
    # 2. Instantiate orchestrator
    orchestrator = StadiumOrchestrator(
        crowd_analyzer=crowd,
        transport_analyzer=transport,
        medical_analyzer=medical,
        weather_analyzer=weather,
        volunteer_analyzer=volunteer
    )
    
    # 3. Instantiate Gemini Client
        # 3. Instantiate Gemini Client
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Check backend/.env")

    client = genai.Client(api_key=api_key)

    # 4. Load System Prompt
    try:
        from pathlib import Path
        prompt_path = Path("prompts") / "commander_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt_content = file.read()
    except Exception:
        logger.warning(
            "Could not find prompts/commander_prompt.txt. Falling back to default system prompt."
        )
        prompt_content = "You are Stadium Commander."
        
    # 5. Instantiate Commander Agent
    commander = CommanderAgent(client=client, system_prompt=prompt_content)
    
    # 6. Inject into app.state
    app.state.orchestrator = orchestrator
    app.state.commander = commander


initialize_dependencies()

# Register Router
app.include_router(router)