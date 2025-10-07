#!/usr/bin/env python3
"""
Terry Delmonaco Automation Agent - Simple FastAPI Application
Version: 3.2
Provides REST API endpoints for the agent ecosystem.
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

PACKAGE_ROOT = Path(__file__).resolve().parent
if __package__ in (None, ""):
    sys.path.insert(0, str(PACKAGE_ROOT.parent))
    __package__ = PACKAGE_ROOT.name
    import importlib

    importlib.import_module(__package__)

from .main_orchestrator import CESARAIOrchestrator
from .utils.config import Config
from .utils.logger import setup_logger


# Global manager agent instance
manager_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global manager_agent
    
    # Startup
    print("🚀 Starting Atlas CESAR.ai Orchestrator...")
    try:
        manager_agent = CESARAIOrchestrator()
        success = await manager_agent.initialize()
        if success:
            print("✅ Atlas CESAR.ai Orchestrator started successfully")
        else:
            print("❌ Atlas CESAR.ai Orchestrator failed to initialize")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Atlas CESAR.ai Orchestrator...")
    if manager_agent:
        try:
            await manager_agent.shutdown()
            print("✅ Atlas CESAR.ai Orchestrator shutdown complete")
        except Exception as e:
            print(f"❌ Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="Terry Delmonaco Automation Agent API",
    description="REST API for Terry Delmonaco Automation Agent Ecosystem",
    version="3.2",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logger
logger = setup_logger("td_agent_api")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Terry Delmonaco Automation Agent",
        "version": "3.2",
        "description": "Central orchestrator for automation agent fleet",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "agents": "/agents",
            "tasks": "/tasks",
            "communication": "/communication",
            "metrics": "/metrics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        if manager_agent and hasattr(manager_agent, 'is_running') and manager_agent.is_running:
            return {
                "status": "healthy",
                "agent_count": len(manager_agent.agent_fleet) if hasattr(manager_agent, 'agent_fleet') else 0,
                "ecosystem_status": "operational"
            }
        elif manager_agent:
            return {
                "status": "initializing",
                "message": "Manager agent is initialized but not yet running"
            }
        else:
            return {
                "status": "degraded",
                "message": "Manager agent not initialized"
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "message": f"Health check error: {str(e)}"
        }


@app.get("/agents")
async def get_agents():
    """Get all agent status."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        if hasattr(manager_agent, 'get_all_agent_status'):
            agent_status = await manager_agent.get_all_agent_status()
            return {
                "agents": agent_status,
                "total_agents": len(agent_status),
                "ecosystem_summary": manager_agent.get_ecosystem_summary() if hasattr(manager_agent, 'get_ecosystem_summary') else {}
            }
        else:
            return {
                "agents": {},
                "total_agents": 0,
                "message": "Agent status method not available"
            }
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks/delegate")
async def delegate_task(task_data: Dict[str, Any]):
    """Delegate a task to the appropriate agent."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        if hasattr(manager_agent, 'delegate_task'):
            result = await manager_agent.delegate_task(task_data)
            return result
        else:
            return {
                "status": "error",
                "message": "Task delegation not available"
            }
    except Exception as e:
        logger.error(f"Task delegation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cursor/task")
async def process_cursor_task(task_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Process a task from Cursor.ai platform."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        if hasattr(manager_agent, 'process_cursor_task'):
            # Add to background tasks for non-blocking operation
            background_tasks.add_task(manager_agent.process_cursor_task, task_data)
            
            return {
                "status": "accepted",
                "message": "Task queued for processing",
                "task_id": task_data.get("id", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": "Cursor task processing not available"
            }
    except Exception as e:
        logger.error(f"Cursor task processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cursor/status")
async def get_cursor_agent_status():
    """Get Cursor agent status."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        if hasattr(manager_agent, 'agent_fleet') and 'cursor_agent' in manager_agent.agent_fleet:
            cursor_agent = manager_agent.agent_fleet['cursor_agent']
            if hasattr(cursor_agent, 'get_status'):
                status = await cursor_agent.get_status()
                return status
            else:
                return {
                    "status": "unknown",
                    "message": "Cursor agent status method not available"
                }
        else:
            return {
                "status": "not_found",
                "message": "Cursor agent not found in fleet"
            }
    except Exception as e:
        logger.error(f"Failed to get cursor agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screen/record")
async def record_screen_activity(background_tasks: BackgroundTasks):
    """Trigger screen activity recording."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        if hasattr(manager_agent, 'record_and_describe'):
            # Add to background tasks for non-blocking operation
            background_tasks.add_task(manager_agent.record_and_describe)
            
            return {
                "success": True,
                "message": "Screen recording initiated"
            }
        else:
            return {
                "success": False,
                "message": "Screen recording not available"
            }
    except Exception as e:
        logger.error(f"Screen recording failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/learnings/sync")
async def sync_learnings(background_tasks: BackgroundTasks):
    """Sync learnings with CESAR ecosystem."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        if hasattr(manager_agent, 'sync_learnings'):
            # Add to background tasks for non-blocking operation
            background_tasks.add_task(manager_agent.sync_learnings)
            
            return {
                "success": True,
                "message": "Learning sync initiated"
            }
        else:
            return {
                "success": False,
                "message": "Learning sync not available"
            }
    except Exception as e:
        logger.error(f"Learning sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/report")
async def generate_status_report():
    """Generate comprehensive status report."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        if hasattr(manager_agent, 'generate_status_report'):
            report = await manager_agent.generate_status_report()
            return report
        else:
            return {
                "status": "error",
                "message": "Status report generation not available"
            }
    except Exception as e:
        logger.error(f"Status report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    print("🚀 Starting Terry Delmonaco Automation Agent API on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
