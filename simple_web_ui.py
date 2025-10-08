#!/usr/bin/env python3
"""
Simple Web UI for Terry Delmonaco Agents
Quick-start version that works immediately
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

PACKAGE_ROOT = Path(__file__).resolve().parent
if __package__ in (None, ""):
    sys.path.insert(0, str(PACKAGE_ROOT.parent))
    __package__ = PACKAGE_ROOT.name
    import importlib

    importlib.import_module(__package__)

from .main_orchestrator import CESARAIOrchestrator
from .utils.metrics import metrics


class TerryChatRequest(BaseModel):
    prompt: str
    tags: Optional[list[str]] = None


class TerryTaskRequest(BaseModel):
    title: str
    description: Optional[str] = ""


class MobileRequest(BaseModel):
    prompt: str


def infer_task_type(question: str) -> str:
    """Infer task type based on user question heuristics."""
    lowered = question.lower()
    if any(keyword in lowered for keyword in ["email", "inbox", "message"]):
        return "email_processing"
    if any(keyword in lowered for keyword in ["calendar", "meeting", "schedule"]):
        return "calendar_management"
    if any(keyword in lowered for keyword in ["spreadsheet", "data", "analysis", "calculate"]):
        return "data_analysis"
    if any(keyword in lowered for keyword in ["report", "summary", "presentation"]):
        return "report_generation"
    if "crm" in lowered:
        return "crm_sync"
    if any(keyword in lowered for keyword in ["screen", "ui", "monitor"]):
        return "screen_analysis"
    return "report_generation"

# Create FastAPI app
app = FastAPI(
    title="Terry Delmonaco Agent Network - Simple UI",
    description="Quick-start agent interface",
    version="1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass


@app.on_event("startup")
async def startup_event():
    orchestrator = CESARAIOrchestrator()
    app.state.orchestrator = orchestrator
    try:
        await orchestrator.ensure_started()
    except Exception as exc:  # pragma: no cover - startup guard
        print(f"Failed to start CESAR orchestrator: {exc}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    orchestrator: CESARAIOrchestrator = getattr(app.state, "orchestrator", None)
    if orchestrator:
        await orchestrator.shutdown()

@app.get("/")
async def root():
    """Serve the UI or fallback interface."""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Fallback HTML interface
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Terry Delmonaco Agent Network</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            position: relative;
            background: none;
        }
        body::before {
            content: "";
            position: fixed;
            inset: 0;
            background: url('/static/images/dashboard-photo.png') center/cover no-repeat;
            z-index: -2;
            filter: brightness(1.12) contrast(1.05);
        }
        body::after {
            content: "";
            position: fixed;
            inset: 0;
            background: linear-gradient(135deg, rgba(6, 15, 40, 0.25) 0%, rgba(12, 24, 60, 0.35) 35%, rgba(8, 12, 30, 0.5) 100%);
            z-index: -1;
            pointer-events: none;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .panel { background: rgba(255,255,255,0.1); border-radius: 10px; padding: 20px; margin: 20px 0; }
        .button { background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .button:hover { background: #45a049; }
        .status { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 5px; margin: 10px 0; }
        #response { background: rgba(0,0,0,0.3); padding: 15px; border-radius: 5px; min-height: 100px; margin-top: 20px; }
        input[type="text"] { width: 100%; padding: 15px; border-radius: 5px; border: none; font-size: 16px; }
        textarea { width: 100%; padding: 15px; border-radius: 8px; border: none; font-size: 16px; margin-top: 10px; background: rgba(0,0,0,0.25); color: white; }
        .assistant-output { background: rgba(0,0,0,0.35); border-radius: 8px; padding: 15px; min-height: 90px; margin-top: 12px; white-space: pre-wrap; }
        .actions-row { display: flex; gap: 12px; margin-top: 12px; }
        .button.subtle { background: rgba(255,255,255,0.15); }
        .button.subtle:hover { background: rgba(255,255,255,0.25); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Terry Delmonaco Agent Network</h1>
            <h2>Multi-Agent System Interface</h2>
        </div>

        <div class="panel">
            <h3>💬 Ask Your Agents</h3>
            <input type="text" id="question" placeholder="Type your question here..." />
            <br><br>
            <button class="button" onclick="askQuestion()">🚀 Ask All Agents</button>
            <div id="response">Ready to process your questions...</div>
        </div>

        <div class="panel">
            <h3>📊 System Status</h3>
            <div class="status">
                <strong>Manager:</strong> <span id="network-status">Initializing...</span><br>
                <strong>Agents Online:</strong> <span id="agent-count">--</span><br>
                <strong>Background Agents:</strong> <span id="background-status">--</span><br>
                <strong>Screen Recorder:</strong> <span id="recorder-status">--</span>
            </div>
            <button class="button" onclick="checkStatus()">🔄 Refresh Status</button>
        </div>

        <div class="panel">
            <h3>📈 Live Metrics</h3>
            <div class="status" id="metrics-output">Loading metrics...</div>
        </div>

        <div class="panel">
            <h3>🎯 Quick Actions</h3>
            <button class="button" onclick="quickAction('status')">System Status</button>
            <button class="button" onclick="quickAction('performance')">Performance Report</button>
            <button class="button" onclick="quickAction('health')">Health Check</button>
        </div>

        <div class="panel">
            <h3>🧑‍💻 Terry Delmonaco Assistant</h3>
            <textarea id="terry-prompt" placeholder="Ask Terry for localized help, coding tips, or workstation automations..."></textarea>
            <div class="actions-row">
                <button class="button" onclick="askTerry()">Ask Terry</button>
                <button class="button subtle" onclick="createTerryTask()">Log Task</button>
            </div>
            <div class="assistant-output" id="terry-output">Standing by...</div>
        </div>
    </div>

    <script>
        async function askQuestion() {
            const question = document.getElementById('question').value;
            if (!question) return;

            document.getElementById('response').innerHTML = '🔄 Processing question through agent network...';

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question })
                });

                const data = await response.json();
                document.getElementById('response').innerHTML =
                    '<h4>Agent Response:</h4><pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('response').innerHTML =
                    '❌ Error: ' + error.message + '<br><br>The full agent system may still be loading. Try again in a moment.';
            }
        }

        async function checkStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                const ecosystem = data.ecosystem || {};
                document.getElementById('network-status').textContent = ecosystem.manager_status || 'unknown';
                document.getElementById('agent-count').textContent = `${ecosystem.active_agents || 0}/${ecosystem.total_agents || 0}`;

                const background = data.background_agents || {};
                document.getElementById('background-status').textContent = background.enabled ? 'enabled' : 'disabled';

                const recorder = data.screen_recorder || {};
                document.getElementById('recorder-status').textContent = recorder.is_recording ? `recording every ${recorder.recording_interval}s` : 'idle';

                const metrics = data.metrics || {};
                const agentsResponse = await fetch('/agents');
                const agentData = await agentsResponse.json();
                document.getElementById('metrics-output').innerHTML = `<pre>${JSON.stringify({ metrics, agents: agentData }, null, 2)}</pre>`;

                const terryStatusResponse = await fetch('/terry/status');
                const terryStatus = await terryStatusResponse.json();
                document.getElementById('terry-output').textContent = terryStatus.status.connected ? 'Terry is online and ready.' : 'Terry assistant offline. Launch AgentC bridge.';
            } catch (error) {
                document.getElementById('network-status').textContent = 'Loading...';
            }
        }

        async function quickAction(action) {
            await askQuestion();
            document.getElementById('question').value = 'System ' + action + ' report';
        }

        async function askTerry() {
            const prompt = document.getElementById('terry-prompt').value;
            if (!prompt) return;
            document.getElementById('terry-output').textContent = 'Thinking locally...';
            try {
                const response = await fetch('/terry/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt })
                });
                if (!response.ok) {
                    throw new Error(await response.text());
                }
                const data = await response.json();
                document.getElementById('terry-output').textContent = data.response || JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('terry-output').textContent = 'Error contacting Terry: ' + error;
            }
        }

        async function createTerryTask() {
            const prompt = document.getElementById('terry-prompt').value;
            if (!prompt) return;
            try {
                const response = await fetch('/terry/tasks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: prompt.slice(0, 80), description: prompt })
                });
                if (!response.ok) {
                    throw new Error(await response.text());
                }
                document.getElementById('terry-output').textContent = 'Task logged for Terry to follow-up.';
            } catch (error) {
                document.getElementById('terry-output').textContent = 'Unable to log task: ' + error;
            }
        }

        // Update status every 5 seconds
        setInterval(checkStatus, 5000);
        checkStatus();
    </script>
</body>
</html>"""
        return HTMLResponse(content=html_content)

@app.get("/status")
async def get_status():
    """Get live system status from the orchestrator."""
    orchestrator: CESARAIOrchestrator = app.state.orchestrator
    ecosystem = await orchestrator.get_ecosystem_summary()
    background = orchestrator.background_agent_manager.get_status()
    recorder_status = await orchestrator.screen_recorder.get_status()
    metrics_snapshot = await metrics.snapshot()

    return {
        "ecosystem": ecosystem,
        "background_agents": background,
        "screen_recorder": recorder_status,
        "metrics": metrics_snapshot,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/ask")
async def ask_question(question_data: Dict[str, Any]):
    """Delegate a question to the orchestrator's task network."""
    question = question_data.get("question", "").strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    orchestrator: CESARAIOrchestrator = app.state.orchestrator
    task_type = infer_task_type(question)
    task_payload = {
        "task_id": f"ui-{uuid4()}",
        "task_type": task_type,
        "task_description": question,
        "priority": question_data.get("priority", "routine"),
        "source": "desktop_ui",
        "created_at": datetime.now().isoformat()
    }

    result = await orchestrator.delegate_task(task_payload)
    await metrics.add_event(
        "desktop_ui.ask",
        1,
        metadata={"task_type": task_type, "status": result.get("status")}
    )

    return {
        "question": question,
        "task_type": task_type,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    orchestrator: CESARAIOrchestrator = app.state.orchestrator
    return {
        "status": "healthy" if orchestrator.is_running else "initializing",
        "initialized": getattr(orchestrator, "_initialized", False),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/metrics")
async def metrics_snapshot():
    """Expose the live metrics snapshot."""
    return await metrics.snapshot()


@app.get("/agents")
async def agent_statuses():
    """Return the status of all orchestrator-managed agents."""
    orchestrator: CESARAIOrchestrator = app.state.orchestrator
    return await orchestrator.get_all_agent_status()


@app.post("/terry/chat")
async def terry_chat(chat_request: TerryChatRequest):
    orchestrator: CESARAIOrchestrator = app.state.orchestrator
    result = await orchestrator.request_terry_assistance(
        chat_request.prompt,
        tags=chat_request.tags or [],
    )
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error") or "Terry assistant error")
    return result["data"]


@app.post("/terry/tasks")
async def terry_create_task(task_request: TerryTaskRequest):
    orchestrator: CESARAIOrchestrator = app.state.orchestrator
    result = await orchestrator.create_terry_task(task_request.title, task_request.description or "")
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@app.get("/terry/status")
async def terry_status():
    orchestrator: CESARAIOrchestrator = app.state.orchestrator
    status = await orchestrator.get_terry_status()
    tasks = await orchestrator.list_terry_tasks(status="open")
    open_tasks = tasks.get("tasks", [])
    return {"status": status, "open_tasks": open_tasks}


@app.post("/mobile/ask", tags=["Mobile"])
async def mobile_ask(request: MobileRequest):
    """
    Endpoint for mobile clients to submit tasks.
    Leverages the same core logic as the main 'ask' endpoint but is optimized
    for simple, prompt-based interactions from a mobile-first UI.
    """
    question = request.prompt.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    orchestrator: CESARAIOrchestrator = app.state.orchestrator
    task_type = infer_task_type(question)
    task_payload = {
        "task_id": f"mobile-ui-{uuid4()}",
        "task_type": task_type,
        "task_description": question,
        "priority": "routine",
        "source": "mobile_ui",
        "created_at": datetime.now().isoformat(),
    }

    result = await orchestrator.delegate_task(task_payload)
    await metrics.add_event(
        "mobile_ui.ask",
        1,
        metadata={"task_type": task_type, "status": result.get("status", "unknown")},
    )

    return {
        "question": question,
        "task_type": task_type,
        "result": result,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/mobile", response_class=HTMLResponse, tags=["Mobile"])
async def serve_mobile_ui():
    """Serves the mobile-optimized HTML interface."""
    try:
        with open("static/mobile.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Mobile UI not found.")


if __name__ == "__main__":
    print("🚀 Starting CESAR.ai Atlas Final - User Dashboard")
    print("   Interface will be available at: http://localhost:8080")
    print("   The full enhanced UI will load automatically")

    uvicorn.run(app, host="0.0.0.0", port=8080)
