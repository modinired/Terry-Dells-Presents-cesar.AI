#!/usr/bin/env python3
"""
Task Orchestrator for Terry Delmonaco Manager Agent
Handles task delegation and coordination between agents.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..agents.base_agent import TaskResult
from ..utils.metrics import metrics

class TaskOrchestrator:
    """
    Orchestrates task delegation and coordination between agents.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("task_orchestrator")
        self.agent_fleet: Dict[str, Any] = {}
        self.task_queue = []
        self.is_running = False
        self.playbook_manager = None
        self.workflow_engine = None
        self._capability_index: Dict[str, List[Tuple[str, Any]]] = {}
        
    async def initialize(self, agent_fleet: Dict):
        """Initialize the task orchestrator with agent fleet."""
        try:
            self.logger.info("Initializing task orchestrator...")
            self.agent_fleet = agent_fleet
            self._refresh_capability_index()
            self.logger.info(f"Task orchestrator initialized with {len(agent_fleet)} agents")
            return True
        except Exception as e:
            self.logger.error(f"Task orchestrator initialization failed: {e}")
            return False
    
    async def delegate_task(self, task_data: Dict) -> Dict:
        """Delegate a task to the appropriate agent."""
        try:
            task_type = task_data.get("task_type", "unknown")
            self._refresh_capability_index()
            self.logger.info(f"Delegating task: {task_type}")
            
            if task_type == "modernization_workflow" and self.workflow_engine:
                workflow_result = await self.workflow_engine.run_workflow(
                    playbook_id=task_data.get("playbook_id"),
                    workflow_name=task_data.get("workflow_name"),
                    metadata=task_data,
                )
                return {
                    "status": workflow_result.get("status", "unknown"),
                    "agent": "workflow_engine",
                    "result": workflow_result,
                }

            # Find appropriate agent for task type
            agent_key = self._find_agent_for_task(task_type)
            resolved_key, agent = self._resolve_agent(agent_key, task_type)
            if agent:
                result = await self._execute_task(resolved_key, agent, task_data)
                await metrics.add_event(
                    "task_orchestrator.delegated",
                    1,
                    metadata={"agent": resolved_key, "task_type": task_type}
                )
                return result
            else:
                await metrics.add_event(
                    "task_orchestrator.unrouted",
                    1,
                    metadata={"task_type": task_type}
                )
                return {
                    "status": "error",
                    "message": f"No agent found for task type: {task_type}"
                }
                
        except Exception as e:
            self.logger.error(f"Task delegation failed: {e}")
            await metrics.add_event(
                "task_orchestrator.error",
                1,
                metadata={"message": str(e)}
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _find_agent_for_task(self, task_type: str) -> Optional[str]:
        """Find the appropriate agent for a given task type."""
        task_agent_mapping = {
            "email_processing": "inbox_calendar",
            "calendar_management": "inbox_calendar",
            "data_analysis": "spreadsheet_processor",
            "report_generation": "automated_reporting",
            "crm_sync": "crm_sync",
            "screen_analysis": "screen_activity",
            "terry_personal_assist": "terry_delmonaco",
            "local_coding_assist": "terry_delmonaco",
        }

        direct_match = task_agent_mapping.get(task_type)
        if direct_match:
            return direct_match

        candidate_agents = self._capability_index.get(task_type)
        if candidate_agents:
            return candidate_agents[0][0]

        return None

    async def _execute_task(self, agent_name: str, agent: Any, task_data: Dict) -> Dict:
        """Execute a task with the specified agent."""
        try:
            self.logger.info(f"Executing task with agent: {agent_name}")
            if hasattr(agent, "is_running") and not getattr(agent, "is_running"):
                start_callable = getattr(agent, "start", None)
                if callable(start_callable):
                    maybe_coro = start_callable()
                    if asyncio.iscoroutine(maybe_coro):
                        await maybe_coro

            start_time = datetime.utcnow()

            if hasattr(agent, "execute_task"):
                result = await agent.execute_task(task_data)
            elif hasattr(agent, "delegate_task"):
                result = await agent.delegate_task(task_data)
            else:
                raise RuntimeError(f"Agent {agent_name} cannot accept tasks")

            return self._normalize_task_result(agent_name, result, start_time)
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _resolve_agent(self, agent_key: Optional[str], task_type: Optional[str]) -> Tuple[Optional[str], Optional[Any]]:
        """Find the best available agent instance for the provided key or capability."""

        if agent_key and agent_key in self.agent_fleet:
            return agent_key, self.agent_fleet[agent_key]

        if agent_key:
            for name, agent in self.agent_fleet.items():
                if getattr(agent, "agent_id", None) == agent_key or getattr(agent, "name", None) == agent_key:
                    return name, agent

        if task_type:
            candidates = self._capability_index.get(task_type, [])
            if candidates:
                name, agent = candidates[0]
                return name, agent

        return None, None

    def _refresh_capability_index(self) -> None:
        """Rebuild capability index so new agents are routable immediately."""

        index: Dict[str, List[Tuple[str, Any]]] = {}
        for name, agent in self.agent_fleet.items():
            capabilities = []
            if hasattr(agent, "get_capabilities"):
                try:
                    capabilities = list(agent.get_capabilities() or [])
                except Exception as exc:
                    self.logger.warning(
                        "Failed to read capabilities from agent %s: %s",
                        name,
                        exc,
                    )

            for capability in capabilities:
                index.setdefault(capability, []).append((name, agent))

        self._capability_index = index

    def _normalize_task_result(self, agent_name: str, result: Any, started_at: datetime) -> Dict[str, Any]:
        """Standardize agent results into a consistent payload for downstream consumers."""

        completed_at = datetime.utcnow()
        base_payload = {
            "agent": agent_name,
            "started_at": started_at.isoformat() + "Z",
            "completed_at": completed_at.isoformat() + "Z",
        }

        if isinstance(result, TaskResult):
            payload = {
                **base_payload,
                "status": "success" if result.success else "error",
                "data": result.data,
                "duration_ms": result.duration_ms,
            }
            if result.error_message:
                payload["error"] = result.error_message
            return payload

        if isinstance(result, dict):
            return {**base_payload, **result}

        return {
            **base_payload,
            "status": "success",
            "data": result,
        }
    
    async def start(self):
        """Start the task orchestrator."""
        self.is_running = True
        self.logger.info("Task orchestrator started")
    
    async def stop(self):
        """Stop the task orchestrator."""
        self.is_running = False
        self.logger.info("Task orchestrator stopped")
    
    async def process_pending_tasks(self):
        """Process any pending tasks in the queue."""
        try:
            if not self.is_running:
                return
            
            # Process any pending tasks
            if self.task_queue:
                task = self.task_queue.pop(0)
                await self.delegate_task(task)
                
        except Exception as e:
            self.logger.error(f"Error processing pending tasks: {e}") 

    def set_playbook_manager(self, manager):
        """Attach playbook manager for reuse in tasks."""
        self.playbook_manager = manager

    def set_workflow_engine(self, engine):
        """Attach modernization workflow engine."""
        self.workflow_engine = engine
