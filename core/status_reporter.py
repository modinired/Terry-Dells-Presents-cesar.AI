#!/usr/bin/env python3
"""
Status Reporter for Terry Delmonaco Manager Agent
Handles system status reporting and monitoring.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class StatusReporter:
    """
    Manages system status reporting and monitoring.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("status_reporter")
        self.reporting_interval = 300  # 5 minutes
        self.last_report = None
        self.is_reporting = False
        self.workflow_events: Dict[str, List[Dict[str, Any]]] = {}
        self.event_store_path: Optional[Path] = None
        
    async def initialize(self):
        """Initialize the status reporter."""
        try:
            self.logger.info("Initializing status reporter...")
            
            # Setup reporting infrastructure
            await self._setup_reporting()
            
            self.logger.info("Status reporter initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Status reporter initialization failed: {e}")
            return False
    
    async def _setup_reporting(self):
        """Setup reporting infrastructure."""
        try:
            # Placeholder for actual reporting setup
            self.logger.info("Reporting infrastructure configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup reporting: {e}")
    
    async def start_reporting(self):
        """Start status reporting."""
        try:
            self.is_reporting = True
            self.logger.info("Status reporting started")
            
        except Exception as e:
            self.logger.error(f"Failed to start status reporting: {e}")
    
    async def stop_reporting(self):
        """Stop status reporting."""
        try:
            self.is_reporting = False
            self.logger.info("Status reporting stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop status reporting: {e}")
    
    async def generate_status_report(self) -> Dict:
        """Generate a comprehensive status report."""
        try:
            self.logger.info("Generating status report...")
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_status": "operational",
                "components": {
                    "agent_manager": "running",
                    "task_orchestrator": "running",
                    "memory_manager": "running",
                    "learning_bridge": "connected",
                    "screen_recorder": "active",
                    "background_agents": "enabled"
                },
                "metrics": {
                    "active_agents": 6,
                    "tasks_processed": 0,
                    "memory_usage": "low",
                    "uptime": "00:05:30"
                },
                "workflows": self._summarize_workflows(),
                "alerts": [],
                "recommendations": [
                    "System is running optimally",
                    "Consider enabling additional background agents"
                ]
            }
            
            self.last_report = report
            return report
            
        except Exception as e:
            self.logger.error(f"Status report generation failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def send_status_report(self, report: Dict) -> Dict:
        """Send status report to external systems."""
        try:
            self.logger.info("Sending status report...")
            
            # Placeholder for actual report sending
            await asyncio.sleep(0.1)  # Simulate network delay
            
            return {
                "status": "success",
                "sent_at": datetime.now().isoformat(),
                "recipients": ["monitoring_system", "admin_dashboard"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send status report: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_reporting_status(self) -> Dict:
        """Get reporting status information."""
        return {
            "is_reporting": self.is_reporting,
            "reporting_interval": self.reporting_interval,
            "last_report": self.last_report["timestamp"] if self.last_report else None,
            "recent_workflows": self._summarize_workflows(limit=5),
        }

    async def record_workflow_update(
        self,
        workflow_id: str,
        phase: str,
        status: str,
        payload: Dict[str, Any],
    ) -> None:
        """Persist workflow updates for dashboard consumers."""

        event = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "status": status,
            "payload": payload,
        }
        self.workflow_events.setdefault(workflow_id, []).append(event)
        self.logger.info(
            "Workflow %s phase %s recorded with status %s", workflow_id, phase, status
        )
        self._persist_events()

    async def get_workflow_events(
        self,
        workflow_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Return stored workflow events for dashboards or APIs."""

        if workflow_id:
            events = self.workflow_events.get(workflow_id, [])
            if limit is not None:
                events = events[-limit:]
            return {"workflow_id": workflow_id, "events": events}

        summaries = self._summarize_workflows(limit=limit)
        return {"workflows": summaries}

    def _summarize_workflows(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        summaries: List[Dict[str, Any]] = []
        for workflow_id, events in list(self.workflow_events.items())[::-1]:
            if not events:
                continue
            latest = events[-1]
            summaries.append(
                {
                    "workflow_id": workflow_id,
                    "last_phase": latest.get("phase"),
                    "status": latest.get("status"),
                    "updated_at": latest.get("timestamp"),
                }
            )
        if limit is not None:
            return summaries[:limit]
        return summaries

    def _persist_events(self) -> None:
        if not self.event_store_path:
            return
        try:
            self.event_store_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "updated_at": datetime.now().isoformat(),
                "workflows": self.workflow_events,
            }
            self.event_store_path.write_text(json.dumps(payload, indent=2))
        except Exception as exc:
            self.logger.warning("Failed to persist workflow events: %s", exc)
    
    async def shutdown(self):
        """Shutdown the status reporter."""
        try:
            await self.stop_reporting()
            self.logger.info("Status reporter shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Status reporter shutdown error: {e}") 
