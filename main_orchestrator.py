#!/usr/bin/env python3
"""
CESAR.ai - Cognitive Enterprise System for Autonomous Reasoning
Version: 4.0 Atlas Final
Description: Advanced multi-agent orchestrator with enhanced memory, UI automation,
and collective intelligence capabilities for comprehensive business automation.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json

# Ensure the package root is importable when executed directly
PACKAGE_ROOT = Path(__file__).resolve().parent
if __package__ in (None, ""):
    sys.path.insert(0, str(PACKAGE_ROOT.parent))
    __package__ = PACKAGE_ROOT.name
    import importlib

    importlib.import_module(__package__)

PROJECT_ROOT = PACKAGE_ROOT
project_root = PROJECT_ROOT

from .core.agent_manager import AgentManager
from .core.task_orchestrator import TaskOrchestrator
from .core.memory_manager import MemoryManager
from .core.learning_bridge import LearningBridge
from .core.screen_recorder import ScreenRecorder
from .core.status_reporter import StatusReporter
from .core.background_agent_manager import BackgroundAgentManager
from .core.agent_breeding_manager import AgentBreedingManager
from .core.google_sheets_knowledge_brain import GoogleSheetsKnowledgeBrain
from .core.google_sheets_memory_manager import GoogleSheetsMemoryManager
from .core.collective_intelligence_framework import CollectiveIntelligenceFramework
from .core.enterprise_agent_manager import EnterpriseAgentManager
from .core.playbook_manager import PlaybookManager
from .core.workflow_engine import ModernizationWorkflowEngine
from .core.cesar_multi_agent_network import (
    CESARMultiAgentNetwork,
    create_cesar_multi_agent_network,
)
from .utils.config import Config
from .utils.logger import setup_logger
from .utils.security import SecurityManager
from .utils.metrics import metrics
from .utils.security_scanner import SecurityScanner
from .utils.iac_generator import IaCGenerator


class CESARAIOrchestrator:
    """
    Main orchestrator class for the CESAR.ai Atlas Final ecosystem.
    Advanced multi-agent system with enhanced memory, UI automation, and collective
    intelligence capabilities for comprehensive enterprise automation.
    """
    
    def __init__(self):
        self.config = Config()
        try:
            self.config.ensure_valid()
        except ValueError as config_error:
            raise RuntimeError(f"Invalid CESAR configuration: {config_error}")
        self.logger = setup_logger("td_manager_agent")
        self.security_manager = SecurityManager()
        self.project_root = project_root
        
        # Core components
        self.agent_manager = AgentManager()
        self.task_orchestrator = TaskOrchestrator()
        self.memory_manager = MemoryManager()
        self.learning_bridge = LearningBridge()
        self.screen_recorder = ScreenRecorder(self.config)
        self.status_reporter = StatusReporter()
        self.status_reporter.event_store_path = self.project_root / "generated_assets" / "workflow_events.json"
        self.background_agent_manager = BackgroundAgentManager()

        # Advanced recursive cognition components
        self.agent_breeding_manager = AgentBreedingManager()
        self.knowledge_brain = GoogleSheetsKnowledgeBrain(getattr(self.config, '_config_data', {}).get('knowledge_brain', {}))
        self.sheets_memory_manager = GoogleSheetsMemoryManager(getattr(self.config, '_config_data', {}).get('sheets_memory', {}))
        self.collective_intelligence = CollectiveIntelligenceFramework(getattr(self.config, '_config_data', {}).get('collective_intelligence', {}))

        # Modernization playbooks and workflow orchestration
        self.playbook_manager = PlaybookManager(self.project_root)
        self.security_scanner = SecurityScanner()
        self.iac_generator = IaCGenerator(self.project_root / "generated_assets")
        self.workflow_engine = ModernizationWorkflowEngine(
            self.project_root,
            self.playbook_manager,
            self.status_reporter,
            self.security_scanner,
            self.iac_generator,
        )
        self.task_orchestrator.set_playbook_manager(self.playbook_manager)
        self.task_orchestrator.set_workflow_engine(self.workflow_engine)

        # Enterprise Multi-Agent Platform Manager
        self.enterprise_agent_manager = EnterpriseAgentManager()

        # CESAR Multi-Agent Network (2025 Enhanced)
        self.cesar_network = create_cesar_multi_agent_network()
        self.logger.info("CESAR Multi-Agent Network initialized with 6 specialized agents")

        # Agent fleet
        self.agent_fleet = {}
        self.is_running = False
        self._background_tasks: List[asyncio.Task] = []
        self._initialized = False
        
        self.logger.info("Terry Delmonaco Manager Agent initialized")

    async def _ensure_initialized(self, awaitable, component_name: str) -> Any:
        """Await a component initializer and raise if it reports failure."""

        result = await awaitable
        if result is False:
            raise RuntimeError(f"{component_name} failed to initialize")
        return result

    async def initialize(self):
        """Initialize all components and start the agent fleet."""
        try:
            self.logger.info("Initializing Terry Delmonaco Manager Agent...")

            # Initialize security
            await self._ensure_initialized(
                self.security_manager.initialize(), "Security manager"
            )

            # Initialize memory systems
            await self._ensure_initialized(
                self.memory_manager.initialize(), "Memory manager"
            )
            await self._ensure_initialized(
                self.sheets_memory_manager.initialize(), "Sheets memory manager"
            )

            # Initialize knowledge brain
            await self._ensure_initialized(
                self.knowledge_brain.initialize(), "Knowledge brain"
            )

            # Initialize learning bridge with CESAR
            await self._ensure_initialized(
                self.learning_bridge.initialize(), "Learning bridge"
            )

            # Initialize agent breeding manager
            await self._ensure_initialized(
                self.agent_breeding_manager.initialize(), "Agent breeding manager"
            )

            # Initialize collective intelligence framework
            await self._ensure_initialized(
                self.collective_intelligence.initialize(
                    self.knowledge_brain, self.sheets_memory_manager
                ),
                "Collective intelligence framework",
            )

            # Initialize enterprise multi-agent platform FIRST
            await self._ensure_initialized(
                self.enterprise_agent_manager.initialize_enterprise_platform(),
                "Enterprise agent platform",
            )

            # Get enterprise agents as primary fleet
            self.agent_fleet = await self.enterprise_agent_manager.get_active_agents()

            # Initialize basic agents as supplementary (if needed)
            await self._initialize_supplementary_agents()

            # Initialize task orchestrator with enterprise fleet
            await self._ensure_initialized(
                self.task_orchestrator.initialize(self.agent_fleet),
                "Task orchestrator",
            )

            # Initialize screen recorder with UI-TARS integration
            ui_tars_agent = self.agent_fleet.get("ui_tars_agent")
            await self.screen_recorder.initialize(ui_tars_agent)

            # Initialize status reporter
            await self.status_reporter.initialize()

            # Initialize background agent manager
            await self._ensure_initialized(
                self.background_agent_manager.initialize(),
                "Background agent manager",
            )
            await self.background_agent_manager.start()

            # Set running flag
            self.is_running = True
            self._initialized = True

            self.logger.info("Terry Delmonaco Manager Agent initialization complete")
            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    async def _initialize_supplementary_agents(self):
        """Initialize supplementary agents to work alongside enterprise fleet."""
        agent_types = [
            "automated_reporting",
            "inbox_calendar",
            "spreadsheet_processor",
            "crm_sync",
            "screen_activity",
            "cursor_agent",
            "ui_tars_agent",
            "terry_delmonaco",
        ]
        
        for agent_type in agent_types:
            try:
                # Only add if not already in enterprise fleet
                if agent_type not in self.agent_fleet:
                    agent_config = self.config.get_agent_config(agent_type)
                    if not agent_config.get("enabled", True):
                        self.logger.info(f"Skipping disabled agent: {agent_type}")
                        continue

                    agent = await self.agent_manager.create_agent(agent_type)
                    self.agent_fleet[agent_type] = agent
                    self.logger.info(f"Added supplementary {agent_type} agent")
                else:
                    self.logger.info(f"Enterprise agent {agent_type} already available")
            except Exception as e:
                self.logger.error(f"Failed to initialize {agent_type} agent: {e}")
    
    async def start(self):
        """Start the manager agent and all subordinate agents."""
        if not await self.initialize():
            self.logger.error("Failed to initialize manager agent")
            return False
        
        self.is_running = True
        self.logger.info("Starting Terry Delmonaco Manager Agent...")
        self._ensure_background_tasks()

        try:
            await asyncio.gather(*self._background_tasks)
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error(f"Runtime error: {e}")
        finally:
            await self.shutdown()

    def _ensure_background_tasks(self):
        """Create background tasks if they are not already running."""
        if self._background_tasks:
            return

        loop = asyncio.get_running_loop()
        self._background_tasks = [
            loop.create_task(self._run_agent_fleet(), name="orchestrator.agent_fleet"),
            loop.create_task(self._run_task_orchestration(), name="orchestrator.task_orchestration"),
            loop.create_task(self._run_screen_recording(), name="orchestrator.screen_recording"),
            loop.create_task(self._run_learning_sync(), name="orchestrator.learning_sync"),
            loop.create_task(self._run_status_reporting(), name="orchestrator.status_reporting"),
            loop.create_task(self._monitor_background_agents(), name="orchestrator.background_monitor"),
        ]

    async def ensure_started(self) -> None:
        """Ensure the orchestrator is initialized and background loops are running."""
        if not self._initialized:
            success = await self.initialize()
            if not success:
                raise RuntimeError("Failed to initialize CESAR orchestrator")
        if not self.is_running:
            self.is_running = True
        self._ensure_background_tasks()

    async def _run_agent_fleet(self):
        """Run the agent fleet with continuous monitoring."""
        while self.is_running:
            try:
                for agent_type, agent in self.agent_fleet.items():
                    if not agent.is_running:
                        await agent.start()
                        self.logger.info(f"Started {agent_type} agent")
                await metrics.incr("orchestrator.agent_fleet.tick")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Agent fleet error: {e}")
                await asyncio.sleep(10)
    
    async def _run_task_orchestration(self):
        """Run continuous task orchestration."""
        while self.is_running:
            try:
                await self.task_orchestrator.process_pending_tasks()
                await metrics.incr("orchestrator.task_orchestration.tick")
                await asyncio.sleep(10)  # Process tasks every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Task orchestration error: {e}")
                await asyncio.sleep(10)
    
    async def _run_screen_recording(self):
        """Run continuous screen recording and analysis."""
        while self.is_running:
            try:
                await self.screen_recorder.capture_and_analyze()
                await asyncio.sleep(self.screen_recorder.recording_interval)

            except Exception as e:
                self.logger.error(f"Screen recording error: {e}")
                await asyncio.sleep(10)
    
    async def _run_learning_sync(self):
        """Run bidirectional learning sync with CESAR."""
        while self.is_running:
            try:
                learning_sync_result = await self.learning_bridge.sync_learnings()
                if learning_sync_result.get("status") == "success":
                    await self._share_learnings_with_terry(learning_sync_result)
                await metrics.incr("orchestrator.learning_sync.runs")
                await asyncio.sleep(3600)  # Sync every hour
                
            except Exception as e:
                self.logger.error(f"Learning sync error: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes
    
    async def _run_status_reporting(self):
        """Run periodic status reporting."""
        while self.is_running:
            try:
                await self.status_reporter.generate_status_report()
                await metrics.incr("orchestrator.status_reports.generated")
                await asyncio.sleep(1800)  # Report every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Status reporting error: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_background_agents(self):
        """Monitor background agents for code auditing and monitoring."""
        while self.is_running:
            try:
                status = self.background_agent_manager.get_status()
                await metrics.set_gauge(
                    "background_agents.enabled",
                    1 if status.get("enabled") else 0,
                )
                agents = status.get("agents", {})
                await metrics.set_gauge("background_agents.count", len(agents))
                await asyncio.sleep(60)
            except Exception as e:
                self.logger.error(f"Background agents error: {e}")
                await asyncio.sleep(60)
    
    async def delegate_task(self, task_data: Dict) -> Dict:
        """Delegate a task to the most appropriate agent."""
        try:
            terry_task_types = {"terry_personal_assist", "local_coding_assist"}
            if task_data.get("task_type") in terry_task_types:
                result = await self.agent_manager.delegate_task(task_data)
                return {
                    "status": "success" if result.success else "error",
                    "result": result.data,
                    "error": result.error_message,
                }

            result = await self.task_orchestrator.delegate_task(task_data)
            self.logger.info(f"Task delegated successfully: {task_data.get('task_id')}")
            return result
        except Exception as e:
            self.logger.error(f"Task delegation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def sync_learnings(self) -> Dict:
        """Sync learnings with CESAR and agent fleet."""
        try:
            result = await self.learning_bridge.sync_learnings()
            self.logger.info("Learning sync completed")
            return result
        except Exception as e:
            self.logger.error(f"Learning sync failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def record_and_describe(self) -> Dict:
        """Capture and describe current screen activity."""
        try:
            result = await self.screen_recorder.capture_and_analyze()
            self.logger.info("Screen activity captured and analyzed")
            return result
        except Exception as e:
            self.logger.error(f"Screen recording failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_status_report(self) -> Dict:
        """Generate comprehensive status report."""
        try:
            report = await self.status_reporter.generate_status_report()
            self.logger.info("Status report generated")
            return report
        except Exception as e:
            self.logger.error(f"Status report generation failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_metrics(self) -> Dict[str, Any]:
        """Aggregate orchestrator, agent, and telemetry metrics for dashboards."""

        process_metrics = await metrics.snapshot()

        agent_metrics: Dict[str, Any] = {}
        for agent_type, agent in self.agent_fleet.items():
            if not hasattr(agent, "get_performance_metrics"):
                continue

            try:
                agent_metrics[agent_type] = await agent.get_performance_metrics()
            except Exception as exc:  # pragma: no cover - defensive logging path
                agent_metrics[agent_type] = {"error": str(exc)}
                self.logger.warning(
                    "Failed to gather metrics for %s", agent_type, exc_info=exc
                )

        total_tasks = sum(
            (
                metrics_data.get("tasks_completed", 0)
                + metrics_data.get("tasks_failed", 0)
            )
            for metrics_data in agent_metrics.values()
            if isinstance(metrics_data, dict)
        )
        total_completed = sum(
            metrics_data.get("tasks_completed", 0)
            for metrics_data in agent_metrics.values()
            if isinstance(metrics_data, dict)
        )
        overall_success_rate = (
            (total_completed / total_tasks) * 100 if total_tasks else 0.0
        )

        ecosystem_summary = await self.get_ecosystem_summary()
        collective_status = {}
        if hasattr(self, "collective_intelligence") and self.collective_intelligence:
            try:
                collective_status = (
                    await self.collective_intelligence.get_collective_intelligence_status()
                )
            except Exception as exc:  # pragma: no cover - defensive logging path
                collective_status = {"error": str(exc)}
                self.logger.warning(
                    "Collective intelligence status unavailable", exc_info=exc
                )

        workflow_status = await self.status_reporter.get_workflow_events(limit=5)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "orchestrator": {
                "is_running": self.is_running,
                "initialized": self._initialized,
                "background_tasks": len(self._background_tasks),
            },
            "agent_metrics": agent_metrics,
            "overall_metrics": {
                "total_tasks": total_tasks,
                "total_completed": total_completed,
                "success_rate": overall_success_rate,
            },
            "ecosystem_summary": ecosystem_summary,
            "collective_intelligence": collective_status,
            "process_metrics": process_metrics,
            "workflow_status": workflow_status,
        }

    async def run_modernization_workflow(
        self,
        playbook_id: Optional[str] = None,
        workflow_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self.workflow_engine.run_workflow(
            playbook_id=playbook_id,
            workflow_name=workflow_name,
            metadata=metadata,
        )

    async def list_modernization_workflows(self) -> Dict[str, Any]:
        return {"workflows": self.workflow_engine.list_workflows()}

    async def get_all_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents in the fleet."""
        try:
            agent_status = {}
            for agent_type, agent in self.agent_fleet.items():
                if hasattr(agent, 'get_status'):
                    status = await agent.get_status()
                    agent_status[agent_type] = status
                else:
                    agent_status[agent_type] = {
                        "agent_type": agent_type,
                        "status": "unknown",
                        "is_initialized": getattr(agent, 'is_initialized', False),
                        "is_running": getattr(agent, 'is_running', False)
                    }
            
            return agent_status
        except Exception as e:
            self.logger.error(f"Failed to get agent status: {e}")
            return {"error": str(e)}
    
    async def get_ecosystem_summary(self) -> Dict[str, Any]:
        """Get summary of the agent ecosystem."""
        try:
            total_agents = len(self.agent_fleet)
            active_agents = sum(1 for agent in self.agent_fleet.values() 
                              if getattr(agent, 'is_running', False))
            
            return {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "ecosystem_status": "operational" if active_agents > 0 else "degraded",
                "manager_status": "running" if self.is_running else "stopped"
            }
        except Exception as e:
            self.logger.error(f"Failed to get ecosystem summary: {e}")
            return {"error": str(e)}

    async def request_terry_assistance(
        self,
        prompt: str,
        tags: Optional[List[str]] = None,
        task_type: str = "terry_personal_assist",
    ) -> Dict[str, Any]:
        """Convenience helper to route prompts to Terry Delmonaco assistant."""
        task_payload = {
            "task_id": f"terry-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "task_type": task_type,
            "prompt": prompt,
            "tags": tags or [],
            "priority": "routine",
        }
        result = await self.agent_manager.delegate_task(task_payload)
        return {
            "success": result.success,
            "data": result.data,
            "error": result.error_message,
        }

    async def get_terry_status(self) -> Dict[str, Any]:
        for agent in self.agent_manager.agents.values():
            if getattr(agent, "agent_type", "") == "terry_delmonaco" and hasattr(agent, "get_status"):
                return await agent.get_status()
        return {"connected": False, "message": "Terry assistant not running"}

    async def _share_learnings_with_terry(self, sync_payload: Dict[str, Any]) -> None:
        terry_config = self.config.get_agent_config("terry_delmonaco")
        if not terry_config.get("enabled", False):
            return

        local_learnings = sync_payload.get("local_learnings", []) or []
        cesar_learnings = sync_payload.get("cesar_learnings", []) or []

        if not local_learnings and not cesar_learnings:
            return

        lines = [
            "CESAR learning sync summary:",
            f"- Local learnings shared: {len(local_learnings)}",
            f"- CESAR insights received: {len(cesar_learnings)}",
        ]

        for item in local_learnings[:3]:
            lines.append(
                f"  • Local {item.get('type', 'learning')} — context: {item.get('data', {}).get('task_type', item.get('data'))}"
            )

        for item in cesar_learnings[:3]:
            lines.append(
                f"  • CESAR {item.get('type', 'learning')} — confidence: {item.get('data', {}).get('confidence', 'n/a')}"
            )

        lines.append("Please assimilate these updates into your ongoing routines.")

        await self.request_terry_assistance(
            "\n".join(lines),
            tags=["cesar_sync", "learning_update"],
        )

    async def create_terry_task(self, title: str, description: str = "") -> Dict[str, Any]:
        for agent in self.agent_manager.agents.values():
            if getattr(agent, "agent_type", "") == "terry_delmonaco" and hasattr(agent, "create_task"):
                return await agent.create_task(title, description)  # type: ignore[attr-defined]
        return {"error": "Terry assistant not running"}

    async def list_terry_tasks(self, status: Optional[str] = None) -> Dict[str, Any]:
        for agent in self.agent_manager.agents.values():
            if getattr(agent, "agent_type", "") == "terry_delmonaco" and hasattr(agent, "list_tasks"):
                return await agent.list_tasks(status=status)  # type: ignore[attr-defined]
        return {"tasks": [], "error": "Terry assistant not running"}

    async def process_cursor_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task from Cursor.ai platform."""
        try:
            if "cursor_agent" in self.agent_fleet:
                cursor_agent = self.agent_fleet["cursor_agent"]
                result = await cursor_agent.process_task(task_data)
                return result
            else:
                self.logger.error("Cursor.ai agent not found in fleet")
                return {
                    "status": "failed",
                    "error": "Cursor.ai agent not available",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error processing Cursor.ai task: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def process_cursor_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook from Cursor.ai platform."""
        try:
            # Extract task data from webhook
            task_data = webhook_data.get("data", {})
            event_type = webhook_data.get("event_type", "unknown")

            self.logger.info(f"Processing Cursor.ai webhook: {event_type}")

            if event_type == "task_created":
                return await self.process_cursor_task(task_data)
            elif event_type == "task_updated":
                return await self.process_cursor_task(task_data)
            elif event_type == "ping":
                return {"status": "pong", "timestamp": datetime.now().isoformat()}
            else:
                return {
                    "status": "ignored",
                    "message": f"Unknown event type: {event_type}",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Error processing Cursor.ai webhook: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    # Advanced Recursive Cognition Methods

    async def trigger_agent_evolution(self, agent_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger evolution of a specific agent based on performance data."""
        try:
            if agent_id in self.agent_fleet:
                agent = self.agent_fleet[agent_id]

                # Trigger self-improvement
                evolution_result = await agent.evolve_capabilities({
                    'task_pattern': performance_data.get('task_pattern', {}),
                    'success_rate': performance_data.get('success_rate', 0),
                    'optimization': performance_data.get('optimization_suggestion', {})
                })

                # Check if breeding is needed
                if performance_data.get('pattern_frequency', 0) > 15:
                    breeding_result = await self.agent_breeding_manager.evolve_existing_agent(
                        agent, performance_data
                    )

                    return {
                        'agent_id': agent_id,
                        'evolution_triggered': evolution_result,
                        'breeding_triggered': breeding_result,
                        'timestamp': datetime.now().isoformat()
                    }

                return {
                    'agent_id': agent_id,
                    'evolution_triggered': evolution_result,
                    'breeding_triggered': False,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Agent evolution failed for {agent_id}: {e}")
            return {'error': str(e)}

    async def spawn_specialized_agent(self, pattern_data: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn a new specialized agent based on observed patterns."""
        try:
            # Use breeding manager to create specialized agent
            parent_agents = list(self.agent_fleet.values())

            if len(parent_agents) < 2:
                return {'error': 'Insufficient parent agents for breeding'}

            # Create breeding pattern
            breeding_pattern = self.agent_breeding_manager.BreedingPattern(
                pattern_id=pattern_data.get('pattern_id', 'unknown'),
                task_type=pattern_data.get('task_type', 'general'),
                frequency=pattern_data.get('frequency', 0),
                complexity=pattern_data.get('complexity', 0.5),
                success_rate=pattern_data.get('success_rate', 0.5),
                avg_duration_ms=pattern_data.get('avg_duration_ms', 30000),
                agents_involved=[agent.agent_id for agent in parent_agents[:3]],
                first_observed=datetime.now(),
                last_observed=datetime.now()
            )

            # Breed new specialized agent
            breeding_result = await self.agent_breeding_manager.breed_specialized_agent(
                breeding_pattern, parent_agents[:3]
            )

            if breeding_result:
                # Create and initialize the new agent
                new_agent_config = breeding_result['config']
                new_agent = await self.agent_manager.create_agent(breeding_result['agent_type'], new_agent_config)

                # Add to fleet
                self.agent_fleet[breeding_result['agent_type']] = new_agent

                # Register with collective intelligence
                await self.collective_intelligence.register_agent(new_agent)

                return {
                    'success': True,
                    'new_agent_id': breeding_result['agent_type'],
                    'breeding_record': breeding_result['breeding_record'],
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Agent spawning failed: {e}")
            return {'error': str(e)}

    async def detect_emergent_behaviors(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect and analyze emergent behaviors in agent interactions."""
        try:
            participating_agents = [
                self.agent_fleet[agent_id] for agent_id in interaction_data.get('agent_ids', [])
                if agent_id in self.agent_fleet
            ]

            if len(participating_agents) < 2:
                return {'error': 'Insufficient agents for emergence detection'}

            # Detect emergent behavior
            emergent_behavior = await self.collective_intelligence.detect_emergent_behavior(
                participating_agents, interaction_data
            )

            if emergent_behavior:
                # Store in memory systems
                await self.sheets_memory_manager.store_collective_intelligence(
                    intelligence_type='emergent_behavior',
                    insights=[{
                        'behavior_id': emergent_behavior.behavior_id,
                        'behavior_type': emergent_behavior.behavior_type,
                        'emergence_strength': emergent_behavior.emergence_strength,
                        'participating_agents': emergent_behavior.participating_agents
                    }],
                    confidence=emergent_behavior.emergence_strength
                )

                return {
                    'emergence_detected': True,
                    'behavior_id': emergent_behavior.behavior_id,
                    'behavior_type': emergent_behavior.behavior_type,
                    'emergence_strength': emergent_behavior.emergence_strength,
                    'participating_agents': emergent_behavior.participating_agents,
                    'timestamp': datetime.now().isoformat()
                }

            return {
                'emergence_detected': False,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Emergence detection failed: {e}")
            return {'error': str(e)}

    async def generate_collective_insight(self, problem_domain: str, agent_ids: List[str] = None) -> Dict[str, Any]:
        """Generate collective insights from distributed agent knowledge."""
        try:
            if agent_ids is None:
                # Use all available agents
                participating_agents = list(self.agent_fleet.values())
            else:
                # Use specified agents
                participating_agents = [
                    self.agent_fleet[agent_id] for agent_id in agent_ids
                    if agent_id in self.agent_fleet
                ]

            if len(participating_agents) < 2:
                return {'error': 'Insufficient agents for collective insight generation'}

            # Generate collective insight
            collective_insight = await self.collective_intelligence.generate_collective_insight(
                problem_domain, participating_agents
            )

            if collective_insight:
                # Store insight in knowledge brain
                insight_data = {
                    'title': f"Collective Insight: {problem_domain}",
                    'content': json.dumps(collective_insight.insight_content),
                    'category': 'collective_intelligence',
                    'confidence_score': collective_insight.confidence_score,
                    'source_agents': collective_insight.source_agents,
                    'application_areas': collective_insight.application_areas
                }

                return {
                    'insight_generated': True,
                    'insight_id': collective_insight.insight_id,
                    'problem_domain': problem_domain,
                    'confidence_score': collective_insight.confidence_score,
                    'source_agents': collective_insight.source_agents,
                    'insight_content': collective_insight.insight_content,
                    'application_areas': collective_insight.application_areas,
                    'timestamp': datetime.now().isoformat()
                }

            return {
                'insight_generated': False,
                'problem_domain': problem_domain,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Collective insight generation failed: {e}")
            return {'error': str(e)}

    async def optimize_agent_swarm(self, objective: str, agent_pool: List[str] = None) -> Dict[str, Any]:
        """Optimize agent swarm behavior for a specific objective."""
        try:
            if agent_pool is None:
                # Use all available agents
                agents_to_optimize = list(self.agent_fleet.values())
            else:
                # Use specified agents
                agents_to_optimize = [
                    self.agent_fleet[agent_id] for agent_id in agent_pool
                    if agent_id in self.agent_fleet
                ]

            if len(agents_to_optimize) < 3:
                return {'error': 'Insufficient agents for swarm optimization'}

            # Perform swarm optimization
            optimization_result = await self.collective_intelligence.optimize_swarm_behavior(
                objective, agents_to_optimize
            )

            # Store optimization results
            await self.sheets_memory_manager.store_performance_metrics(
                agent_id='swarm_optimization',
                metrics={
                    'objective': objective,
                    'performance_improvement': optimization_result.get('performance_improvement', 0),
                    'participating_agents': len(agents_to_optimize),
                    'optimization_steps': len(optimization_result.get('optimization_steps', []))
                }
            )

            return optimization_result

        except Exception as e:
            self.logger.error(f"Swarm optimization failed: {e}")
            return {'error': str(e)}

    async def facilitate_agent_learning(self, learning_domain: str, participant_ids: List[str] = None) -> Dict[str, Any]:
        """Facilitate collaborative learning between agents."""
        try:
            if participant_ids is None:
                # Select agents based on domain relevance
                participants = [
                    agent for agent in self.agent_fleet.values()
                    if any(learning_domain.lower() in cap.lower() for cap in agent.get_capabilities())
                ]
            else:
                # Use specified agents
                participants = [
                    self.agent_fleet[agent_id] for agent_id in participant_ids
                    if agent_id in self.agent_fleet
                ]

            if len(participants) < 2:
                return {'error': 'Insufficient agents for collaborative learning'}

            # Facilitate learning session
            learning_result = await self.collective_intelligence.facilitate_collaborative_learning(
                learning_domain, participants
            )

            # Store learning outcomes
            for agent_id, outcomes in learning_result.get('learning_outcomes', {}).items():
                await self.sheets_memory_manager.store_learning_data(
                    agent_id=agent_id,
                    learning_type='collaborative_learning',
                    learning_content={
                        'domain': learning_domain,
                        'session_id': learning_result['session_id'],
                        'outcomes': outcomes
                    },
                    effectiveness=outcomes.get('effectiveness_score', 0.5)
                )

            return learning_result

        except Exception as e:
            self.logger.error(f"Collaborative learning failed: {e}")
            return {'error': str(e)}

    async def get_recursive_cognition_status(self) -> Dict[str, Any]:
        """Get comprehensive status of recursive cognition capabilities."""
        try:
            # Get status from all recursive cognition components
            status = {
                'timestamp': datetime.now().isoformat(),
                'agent_breeding': await self.agent_breeding_manager.get_breeding_status(),
                'knowledge_brain': await self.knowledge_brain.get_knowledge_summary(),
                'collective_intelligence': await self.collective_intelligence.get_collective_intelligence_status(),
                'memory_system': await self.sheets_memory_manager.get_memory_status(),
                'ecosystem_overview': {
                    'total_agents': len(self.agent_fleet),
                    'specialized_agents': len([
                        agent for agent in self.agent_fleet.values()
                        if hasattr(agent, 'specialization')
                    ]),
                    'network_connections': sum(
                        len(getattr(agent, 'network_connections', set()))
                        for agent in self.agent_fleet.values()
                    ),
                    'collective_insights_generated': len(
                        self.collective_intelligence.collective_insights
                    ),
                    'emergent_behaviors_detected': len(
                        self.collective_intelligence.emergent_behaviors
                    )
                }
            }

            return status

        except Exception as e:
            self.logger.error(f"Failed to get recursive cognition status: {e}")
            return {'error': str(e)}

    async def sync_with_cesar_ecosystem(self) -> Dict[str, Any]:
        """Sync all learning and intelligence data with CESAR ecosystem."""
        try:
            sync_results = {
                'timestamp': datetime.now().isoformat(),
                'knowledge_sync': None,
                'memory_sync': None,
                'intelligence_sync': None
            }

            # Sync knowledge brain data
            knowledge_collection = await self.knowledge_brain.collect_daily_knowledge()
            sync_results['knowledge_sync'] = knowledge_collection

            # Export memory for CESAR
            memory_export = await self.sheets_memory_manager.export_memory_for_cesar([
                self.sheets_memory_manager.MemoryType.LEARNING_DATA,
                self.sheets_memory_manager.MemoryType.COLLECTIVE_INTELLIGENCE,
                self.sheets_memory_manager.MemoryType.AGENT_COMMUNICATION
            ])
            sync_results['memory_sync'] = memory_export

            # Export collective intelligence insights
            ci_status = await self.collective_intelligence.get_collective_intelligence_status()
            sync_results['intelligence_sync'] = ci_status

            # Sync with traditional learning bridge
            learning_sync = await self.learning_bridge.sync_learnings()
            sync_results['learning_bridge_sync'] = learning_sync

            return sync_results

        except Exception as e:
            self.logger.error(f"CESAR ecosystem sync failed: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown all components."""
        self.logger.info("Shutting down Terry Delmonaco Manager Agent...")
        self.is_running = False
        
        try:
            for task in list(self._background_tasks):
                task.cancel()
            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)
            self._background_tasks.clear()

            # Shutdown all agents
            for agent_type, agent in self.agent_fleet.items():
                await agent.shutdown()
                self.logger.info(f"Shutdown {agent_type} agent")
            
            # Shutdown components
            await self.memory_manager.shutdown()
            await self.sheets_memory_manager.shutdown()
            await self.knowledge_brain.shutdown()
            await self.learning_bridge.shutdown()
            await self.screen_recorder.shutdown()
            await self.status_reporter.shutdown()
            await self.background_agent_manager.shutdown()
            await self.agent_breeding_manager.shutdown()
            await self.collective_intelligence.shutdown()

            self.logger.info("Terry Delmonaco Manager Agent shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


class TerryDelmonacoManagerAgent(CESARAIOrchestrator):
    """Backward-compatible alias for legacy Terry Delmonaco naming."""

    pass


async def main():
    """Main entry point for the Terry Delmonaco Manager Agent."""
    manager = TerryDelmonacoManagerAgent()
    
    try:
        await manager.start()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 
