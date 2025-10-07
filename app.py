#!/usr/bin/env python3
"""
Terry Delmonaco Automation Agent - FastAPI Application
Version: 3.2
Provides REST API endpoints for the agent ecosystem.
"""

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager, suppress
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel

PACKAGE_ROOT = Path(__file__).resolve().parent
if __package__ in (None, ""):
    sys.path.insert(0, str(PACKAGE_ROOT.parent))
    __package__ = PACKAGE_ROOT.name
    import importlib

    importlib.import_module(__package__)

from .main_orchestrator import TerryDelmonacoManagerAgent
from .user_question_router import UserQuestionRouter
from .cesar_integration_manager import CESARIntegrationManager
from .utils.config import Config
from .utils.logger import setup_logger


# Global manager agent instance
manager_agent: Optional[TerryDelmonacoManagerAgent] = None
question_router: Optional[UserQuestionRouter] = None
cesar_integration: Optional[CESARIntegrationManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global manager_agent, question_router, cesar_integration

    # Startup
    print("🚀 Starting Terry Delmonaco Automation Agent...")
    periodic_metrics_task: Optional[asyncio.Task] = None

    try:
        manager_agent = TerryDelmonacoManagerAgent()
        init_ok = await manager_agent.initialize()
        if not init_ok:
            raise RuntimeError("Manager agent failed to initialize")

        print("🔗 Initializing question router...")
        question_router = UserQuestionRouter(manager_agent)

        print("🤖 Initializing CESAR integration...")
        cesar_integration = CESARIntegrationManager(manager_agent)

        print("✅ Terry Delmonaco + CESAR Agent Network started successfully")

        if manager.active_connections and hasattr(manager_agent, "get_metrics"):
            initial_metrics = await manager_agent.get_metrics()
            await manager.broadcast(
                json.dumps({"type": "metric_init", "data": initial_metrics})
            )

        periodic_metrics_task = asyncio.create_task(
            send_periodic_metrics(), name="td_agent.metrics_loop"
        )

        yield

    except Exception as exc:
        logger.exception("Startup lifecycle failed", exc_info=exc)
        raise

    finally:
        print("🛑 Shutting down Terry Delmonaco + CESAR Agent Network...")

        if periodic_metrics_task:
            periodic_metrics_task.cancel()
            with suppress(asyncio.CancelledError):
                await periodic_metrics_task

        if manager_agent:
            with suppress(Exception):
                await manager_agent.shutdown()

        manager_agent = None
        question_router = None
        cesar_integration = None

        print("✅ Agent Network shutdown complete")


async def send_periodic_metrics():
    """Periodically sends system metrics and health checks to connected WebSocket clients."""
    while True:
        try:
            await asyncio.sleep(5)

            if not manager.active_connections:
                continue

            if not manager_agent or not getattr(manager_agent, "is_running", False):
                continue

            metrics_payload = await manager_agent.get_metrics()
            await manager.broadcast(
                json.dumps({"type": "metric_update", "data": metrics_payload})
            )

            await manager.broadcast(
                json.dumps(
                    {
                        "type": "thought",
                        "panelId": "system-thoughts",
                        "thoughtType": "analysis",
                        "message": "Periodic health check completed",
                    }
                )
            )

            collective = metrics_payload.get("collective_intelligence", {})
            if collective and not collective.get("error"):
                if collective.get("collective_insights", 0) > 0:
                    await manager.broadcast(
                        json.dumps(
                            {
                                "type": "thought",
                                "panelId": "ci-thoughts",
                                "thoughtType": "insight",
                                "message": "New collective insight generated",
                            }
                        )
                    )
                if collective.get("emergent_behaviors", 0) > 0:
                    await manager.broadcast(
                        json.dumps(
                            {
                                "type": "thought",
                                "panelId": "ci-thoughts",
                                "thoughtType": "insight",
                                "message": "New emergent behavior detected",
                            }
                        )
                    )
        except asyncio.CancelledError:
            logger.info("Periodic metrics task cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in periodic metrics task: {e}")
            await asyncio.sleep(5)  # Wait before retrying


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

# Static asset directory (resolve relative to this file)
STATIC_DIR = PACKAGE_ROOT / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR, check_dir=False), name="static")

# Setup logger
logger = setup_logger("td_agent_api")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        with suppress(ValueError):
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        stale_connections: List[WebSocket] = []
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception as exc:  # pragma: no cover - depends on transport
                logger.warning("WebSocket broadcast failed: %s", exc)
                stale_connections.append(connection)

        for connection in stale_connections:
            self.disconnect(connection)

manager = ConnectionManager()


class WorkflowRequest(BaseModel):
    playbook_id: Optional[str] = None
    workflow_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive, or handle incoming messages if needed
            # For now, we just accept and keep alive.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.get("/")
async def root():
    """Serve the real-time UI."""
    try:
        with open(STATIC_DIR / "index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return {
            "name": "Terry Delmonaco + CESAR Agent Network",
            "version": "3.2",
            "description": "Enhanced multi-agent ecosystem with CESAR SEUC integration",
            "status": "running",
            "ui": "/static/index.html",
            "endpoints": {
                "health": "/health",
                "agents": "/agents",
                "ask": "/ask",
                "seuc": "/ask/seuc",
                "seuc_status": "/seuc/status",
                "nodes": "/nodes/status"
            }
        }


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": "Terry Delmonaco + CESAR Agent Network",
        "version": "3.2",
        "description": "Enhanced multi-agent ecosystem with CESAR SEUC integration",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "agents": "/agents",
            "ask": "/ask",
            "seuc": "/ask/seuc",
            "seuc_status": "/seuc/status",
            "nodes": "/nodes/status"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        if manager_agent and getattr(manager_agent, "is_running", False):
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

        agent_status = await manager_agent.get_all_agent_status()
        return {
            "agents": agent_status,
            "total_agents": len(agent_status),
            "ecosystem_summary": manager_agent.get_ecosystem_summary()
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
        
        result = await manager_agent.delegate_task(task_data)
        return result
    except Exception as e:
        logger.error(f"Task delegation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/communication/send")
async def send_message(
    platform: str,
    recipient: str,
    message: str,
    background_tasks: BackgroundTasks
):
    """Send message via external platform."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        # Add to background tasks for non-blocking operation
        background_tasks.add_task(
            manager_agent.send_user_message,
            recipient,
            message,
            platform
        )
        
        return {
            "success": True,
            "message": "Message queued for sending",
            "platform": platform,
            "recipient": recipient
        }
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/communication/broadcast")
async def broadcast_message(
    message: str,
    background_tasks: BackgroundTasks,
    platforms: List[str] = None
):
    """Broadcast message to all agents via external platforms."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        # Add to background tasks for non-blocking operation
        background_tasks.add_task(
            manager_agent.broadcast_message,
            message,
            platforms[0] if platforms else "google_chat"
        )
        
        return {
            "success": True,
            "message": "Broadcast message queued",
            "platforms": platforms or ["google_chat"]
        }
    except Exception as e:
        logger.error(f"Failed to broadcast message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/communication/status")
async def get_communication_status():
    """Get communication platform status."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        status = {}
        for platform, client in manager_agent.communication_clients.items():
            status[platform] = {
                "connected": client.is_connected,
                "healthy": await client.is_healthy()
            }
        
        return {
            "communication_status": status,
            "total_platforms": len(status)
        }
    except Exception as e:
        logger.error(f"Failed to get communication status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get performance metrics."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")

        metrics_payload = await manager_agent.get_metrics()
        overall = metrics_payload.setdefault("overall_metrics", {})
        overall["active_agents"] = len(
            [
                a
                for a in metrics_payload.get("agent_metrics", {}).values()
                if isinstance(a, dict) and a.get("tasks_completed", 0) > 0
            ]
        )

        return metrics_payload
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/modernization/playbooks")
async def list_playbooks(tags: Optional[str] = None):
    """Expose modernization playbooks for Terry orchestration."""

    if not manager_agent:
        raise HTTPException(status_code=503, detail="Manager agent not initialized")

    tag_filter = [tag.strip() for tag in tags.split(",")] if tags else None
    playbooks = manager_agent.playbook_manager.list_playbooks(tags=tag_filter)
    return {"playbooks": playbooks}


@app.post("/modernization/workflows")
async def start_workflow(request: WorkflowRequest):
    """Kick off assessment→deployment modernization workflow."""

    if not manager_agent:
        raise HTTPException(status_code=503, detail="Manager agent not initialized")

    workflow = await manager_agent.run_modernization_workflow(
        playbook_id=request.playbook_id,
        workflow_name=request.workflow_name,
        metadata=request.metadata,
    )
    return workflow


@app.get("/modernization/workflows")
async def list_workflows():
    """List modernization workflows and statuses."""

    if not manager_agent:
        raise HTTPException(status_code=503, detail="Manager agent not initialized")

    return await manager_agent.list_modernization_workflows()


@app.get("/modernization/workflows/{workflow_id}")
async def get_workflow_events(workflow_id: str, limit: Optional[int] = None):
    """Return recorded workflow events for dashboards."""

    if not manager_agent:
        raise HTTPException(status_code=503, detail="Manager agent not initialized")

    events = await manager_agent.status_reporter.get_workflow_events(
        workflow_id=workflow_id,
        limit=limit,
    )
    if not events.get("events"):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return events


@app.post("/learnings/sync")
async def sync_learnings(background_tasks: BackgroundTasks):
    """Sync learnings with CESAR and agent fleet."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        # Add to background tasks for non-blocking operation
        background_tasks.add_task(manager_agent.sync_learnings)
        
        return {
            "success": True,
            "message": "Learning sync initiated"
        }
    except Exception as e:
        logger.error(f"Failed to sync learnings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screen/record")
async def record_screen_activity(background_tasks: BackgroundTasks):
    """Record and analyze screen activity."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        # Add to background tasks for non-blocking operation
        background_tasks.add_task(manager_agent.record_and_describe)
        
        return {
            "success": True,
            "message": "Screen recording initiated"
        }
    except Exception as e:
        logger.error(f"Failed to record screen activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/report")
async def generate_status_report():
    """Generate comprehensive status report."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        report = await manager_agent.generate_status_report()
        return report
    except Exception as e:
        logger.error(f"Failed to generate status report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cursor/task")
async def process_cursor_task(task_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Process a task from Cursor.ai platform."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")
        
        # Add task to background processing
        background_tasks.add_task(manager_agent.process_cursor_task, task_data)
        
        return {
            "status": "accepted",
            "message": "Task queued for processing",
            "task_id": task_data.get("id", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing Cursor.ai task: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Cursor.ai task")


@app.get("/cursor/status")
async def get_cursor_agent_status():
    """Get Cursor.ai agent status."""
    try:
        if manager_agent and "cursor_agent" in manager_agent.agent_fleet:
            cursor_agent = manager_agent.agent_fleet["cursor_agent"]
            status = await cursor_agent.get_status()
            return status
        else:
            return {
                "status": "unavailable",
                "message": "Cursor.ai agent not found",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error getting Cursor.ai agent status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Cursor.ai agent status")


@app.post("/cursor/webhook")
async def cursor_webhook_handler(webhook_data: Dict[str, Any]):
    """Handle webhook from Cursor.ai platform."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")

        # Process webhook data
        result = await manager_agent.process_cursor_webhook(webhook_data)
        return result
    except Exception as e:
        logger.error(f"Error processing Cursor.ai webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Cursor.ai webhook")


@app.post("/ask")
async def ask_question(question_data: Dict[str, Any]):
    """Route user question through all agent nodes with CESAR SEUC enhancement."""
    try:
        if not manager_agent or not question_router or not cesar_integration:
            raise HTTPException(status_code=503, detail="Agent systems not fully initialized")

        question = question_data.get("question", "")
        context = question_data.get("context", {})
        use_seuc = question_data.get("use_seuc", True)

        if not question:
            raise HTTPException(status_code=400, detail="Question is required")

        await manager.broadcast(json.dumps({"type": "thought", "panelId": "agent-thoughts", "thoughtType": "analysis", "message": f"Processing question: \"{question[:50]}...\""}))
        await manager.broadcast(json.dumps({"type": "thought", "panelId": "ci-thoughts", "thoughtType": "insight", "message": "Analyzing question complexity and routing to relevant agents"}))
        await manager.broadcast(json.dumps({"type": "thought", "panelId": "system-thoughts", "thoughtType": "analysis", "message": "Question received, initiating multi-agent processing"}))

        if use_seuc:
            # Enhanced processing with CESAR SEUC
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            await manager.broadcast(json.dumps({"type": "thought", "panelId": "agent-thoughts", "thoughtType": "decision", "message": "Initializing SEUC processing..."}))
            seuc_context = await cesar_integration.initialize_seuc_processing(question, session_id)
            await manager.broadcast(json.dumps({"type": "thought", "panelId": "agent-thoughts", "thoughtType": "insight", "message": "SEUC processing initialized."}))

            await manager.broadcast(json.dumps({"type": "thought", "panelId": "ci-thoughts", "thoughtType": "analysis", "message": "Gathering multi-layer intelligence..."}))
            intelligence_layers = await cesar_integration.gather_multi_layer_intelligence(question, seuc_context)
            await manager.broadcast(json.dumps({"type": "thought", "panelId": "ci-thoughts", "thoughtType": "insight", "message": "Multi-layer intelligence gathered."}))

            await manager.broadcast(json.dumps({"type": "thought", "panelId": "agent-thoughts", "thoughtType": "decision", "message": "Analyzing symbiotic ecosystem..."}))
            ecosystem_insights = await cesar_integration.analyze_symbiotic_ecosystem(question, intelligence_layers)
            await manager.broadcast(json.dumps({"type": "thought", "panelId": "agent-thoughts", "thoughtType": "insight", "message": "Symbiotic ecosystem analyzed."}))

            await manager.broadcast(json.dumps({"type": "thought", "panelId": "ci-thoughts", "thoughtType": "analysis", "message": "Processing with recursive cognition..."}))
            recursive_result = await cesar_integration.process_with_recursive_cognition(question, seuc_context)
            await manager.broadcast(json.dumps({"type": "thought", "panelId": "ci-thoughts", "thoughtType": "insight", "message": "Recursive cognition complete."}))

            await manager.broadcast(json.dumps({"type": "thought", "panelId": "agent-thoughts", "thoughtType": "decision", "message": "Applying SEUC enhancements..."}))
            enhanced_result = await cesar_integration.apply_seuc_enhancements(recursive_result, seuc_context)
            await manager.broadcast(json.dumps({"type": "thought", "panelId": "agent-thoughts", "thoughtType": "insight", "message": "SEUC enhancements applied."}))

            await manager.broadcast(json.dumps({"type": "thought", "panelId": "system-thoughts", "thoughtType": "decision", "message": "Updating ecosystem learning..."}))
            await cesar_integration.update_ecosystem_learning(question, enhanced_result, seuc_context)
            await manager.broadcast(json.dumps({"type": "thought", "panelId": "system-thoughts", "thoughtType": "insight", "message": "Ecosystem learning updated."}))

            await manager.broadcast(json.dumps({"type": "thought", "panelId": "agent-thoughts", "thoughtType": "decision", "message": f"Successfully processed through {len(manager_agent.agent_fleet)} agents"}))
            await manager.broadcast(json.dumps({"type": "thought", "panelId": "ci-thoughts", "thoughtType": "insight", "message": "Collective intelligence synthesis complete"}))
            await manager.broadcast(json.dumps({"type": "thought", "panelId": "system-thoughts", "thoughtType": "decision", "message": "Question processing completed successfully"}))

            return enhanced_result
        else:
            # Standard processing
            result = await question_router.route_user_question(question, context)
            return result

    except Exception as e:
        logger.error(f"Error processing user question: {e}")
        await manager.broadcast(json.dumps({"type": "thought", "panelId": "system-thoughts", "thoughtType": "warning", "message": f"Error processing question: {str(e)}"}))
        raise HTTPException(status_code=500, detail="Failed to process user question")


@app.post("/ask/seuc")
async def ask_question_seuc_enhanced(question_data: Dict[str, Any]):
    """Route user question through CESAR SEUC enhanced processing."""
    try:
        if not cesar_integration:
            raise HTTPException(status_code=503, detail="CESAR integration not initialized")

        question = question_data.get("question", "")
        session_id = question_data.get("session_id", f"seuc_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        if not question:
            raise HTTPException(status_code=400, detail="Question is required")

        # Full SEUC processing pipeline
        seuc_context = await cesar_integration.initialize_seuc_processing(question, session_id)
        intelligence_layers = await cesar_integration.gather_multi_layer_intelligence(question, seuc_context)
        ecosystem_insights = await cesar_integration.analyze_symbiotic_ecosystem(question, intelligence_layers)
        recursive_result = await cesar_integration.process_with_recursive_cognition(question, seuc_context)
        enhanced_result = await cesar_integration.apply_seuc_enhancements(recursive_result, seuc_context)
        await cesar_integration.update_ecosystem_learning(question, enhanced_result, seuc_context)

        return enhanced_result

    except Exception as e:
        logger.error(f"Error processing SEUC question: {e}")
        raise HTTPException(status_code=500, detail="Failed to process SEUC question")


@app.get("/seuc/status")
async def get_seuc_status():
    """Get CESAR SEUC system status."""
    try:
        if not cesar_integration:
            raise HTTPException(status_code=503, detail="CESAR integration not initialized")

        status = await cesar_integration.get_seuc_status()
        return status

    except Exception as e:
        logger.error(f"Error getting SEUC status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SEUC status")


@app.get("/nodes/status")
async def get_all_nodes_status():
    """Get status of all nodes in the agent network."""
    try:
        if not manager_agent:
            raise HTTPException(status_code=503, detail="Manager agent not initialized")

        # Get comprehensive status from all nodes
        agent_status = await manager_agent.get_all_agent_status()
        ci_status = await manager_agent.get_recursive_cognition_status()
        ecosystem = await manager_agent.get_ecosystem_summary()

        return {
            "ecosystem_summary": ecosystem,
            "agent_fleet": agent_status,
            "collective_intelligence": ci_status,
            "total_nodes": len(agent_status),
            "active_nodes": len([a for a in agent_status.values() if a.get('is_running', False)]),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting nodes status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get nodes status")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    # Get configuration
    config = Config()
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Terry Delmonaco Automation Agent API on {host}:{port}")
    
    # Run the application
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False,
        log_level=config.log_level.lower()
    ) 
