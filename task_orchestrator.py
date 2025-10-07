#!/usr/bin/env python3
"""
Task Orchestrator for Terry Delmonaco Manager Agent
Handles task delegation and coordination between agents.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.metrics import metrics

class TaskOrchestrator:
    """
    Orchestrates task delegation and coordination between agents.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("task_orchestrator")
        self.agent_fleet = {}
        self.task_queue = []
        self.is_running = False
        self.playbook_manager = None
        self.workflow_engine = None
        
    async def initialize(self, agent_fleet: Dict):
        """Initialize the task orchestrator with agent fleet."""
        try:
            self.logger.info("Initializing task orchestrator...")
            self.agent_fleet = agent_fleet
            self.logger.info(f"Task orchestrator initialized with {len(agent_fleet)} agents")
            return True
        except Exception as e:
            self.logger.error(f"Task orchestrator initialization failed: {e}")
            return False
    
    async def delegate_task(self, task_data: Dict) -> Dict:
        """Delegate a task to the appropriate agent."""
        try:
            task_type = task_data.get("task_type", "unknown")
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
            agent = self._find_agent_for_task(task_type)
            if agent:
                result = await self._execute_task(agent, task_data)
                await metrics.add_event(
                    "task_orchestrator.delegated",
                    1,
                    metadata={"agent": agent, "task_type": task_type}
                )
                return {
                    "status": "success",
                    "agent": agent,
                    "result": result
                }
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

        return task_agent_mapping.get(task_type)
    
    async def _execute_task(self, agent_name: str, task_data: Dict) -> Dict:
        """Execute a task with the specified agent."""
        try:
            self.logger.info(f"Executing task with agent: {agent_name}")
            # Placeholder for actual task execution
            return {
                "agent": agent_name,
                "task_id": task_data.get("task_id", "unknown"),
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return {
                "status": "error",
                "message": str(e)
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
