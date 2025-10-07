"""
Agent Manager for Terry Delmonaco Automation Agent Ecosystem.
Manages hyper-specialized automation agents with external communication capabilities.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from ..utils.logger import LoggerMixin, performance_logger
from ..utils.config import Config

from ..communication.external_platforms import GoogleChatClient, SignalClient
from ..agents.base_agent import BaseAgent, TaskResult
from ..agents.automated_reporting_agent import AutomatedReportingAgent
from ..agents.inbox_calendar_agent import InboxCalendarAgent
from ..agents.spreadsheet_processor_agent import SpreadsheetProcessorAgent
from ..agents.crm_sync_agent import CRMSyncAgent
from ..agents.screen_activity_agent import ScreenActivityAgent
from ..agents.cursor_agent import CursorAgent
from ..agents.ui_tars_agent import UITarsAgent


class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentInfo:
    """Information about an automation agent."""
    agent_id: str
    agent_type: str
    status: AgentStatus
    capabilities: List[str]
    current_task: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    last_activity: Optional[datetime] = None


class AgentManager(LoggerMixin):
    """
    Manager for Terry Delmonaco Automation Agent fleet.
    Handles agent creation, monitoring, and communication coordination.
    """
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_info: Dict[str, AgentInfo] = {}
        self.communication_clients = {}
        self.is_running = False
        
        # Initialize communication clients
        self._initialize_communication_clients()
    
    def _initialize_communication_clients(self):
        """Initialize external communication platforms."""
        try:
            # Google Chat client for team communication
            self.communication_clients['google_chat'] = GoogleChatClient()
            
            # Signal client for secure messaging
            self.communication_clients['signal'] = SignalClient()
            
            self.log_info("External communication clients initialized")
            
        except Exception as e:
            self.log_error(f"Failed to initialize communication clients: {e}")
    
    async def create_agent(self, agent_type: str) -> BaseAgent:
        """Create a hyper-specialized automation agent."""
        agent_config = self.config.get_agent_config(agent_type)
        
        if not agent_config.get('enabled', True):
            raise ValueError(f"Agent type {agent_type} is disabled")
        
        # Create agent based on type
        agent_map = {
            "automated_reporting": AutomatedReportingAgent,
            "inbox_calendar": InboxCalendarAgent,
            "spreadsheet_processor": SpreadsheetProcessorAgent,
            "crm_sync": CRMSyncAgent,
            "screen_activity": ScreenActivityAgent,
            "cursor_agent": CursorAgent,
            "ui_tars_agent": UITarsAgent,
        }
        
        if agent_type not in agent_map:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        try:
            # Create agent instance
            agent_class = agent_map[agent_type]
            
            # Handle special agent types with different constructors
            if agent_type == "cursor_agent":
                agent = agent_class()
            elif agent_type == "ui_tars_agent":
                agent = agent_class(config=agent_config)
            elif agent_type == "terry_delmonaco":
                agent = agent_class(
                    agent_type=agent_type,
                    config=agent_config,
                    communication_clients=self.communication_clients,
                )
            else:
                agent = agent_class(
                    agent_type=agent_type,
                    config=agent_config,
                    communication_clients=self.communication_clients,
                )
            
            # Initialize agent
            await agent.initialize()
            
            # Register agent
            agent_id = f"{agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.agents[agent_id] = agent
            
            # Create agent info
            self.agent_info[agent_id] = AgentInfo(
                agent_id=agent_id,
                agent_type=agent_type,
                status=AgentStatus.IDLE,
                capabilities=agent.get_capabilities(),
                performance_metrics={},
                last_activity=datetime.now()
            )
            
            self.log_info(f"Created {agent_type} agent: {agent_id}")
            return agent
            
        except Exception as e:
            self.log_error(f"Failed to create {agent_type} agent: {e}")
            raise
    
    async def delegate_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Delegate task to the most appropriate agent."""
        try:
            task_type = task_data.get('task_type')
            priority = task_data.get('priority', 'routine')
            
            # Find best agent for task
            best_agent = await self._find_best_agent(task_type, priority)
            
            if not best_agent:
                return TaskResult(
                    success=False,
                    data={},
                    error_message=f"No suitable agent found for task type: {task_type}"
                )
            
            # Delegate task
            result = await best_agent.execute_task(task_data)
            
            # Update agent info
            agent_id = best_agent.agent_id
            self.agent_info[agent_id].current_task = task_data.get('task_id')
            self.agent_info[agent_id].last_activity = datetime.now()
            
            # Log performance
            performance_logger.log_task_complete(
                task_data.get('task_id'),
                result.duration_ms,
                result.success
            )
            
            return result
            
        except Exception as e:
            self.log_error(f"Task delegation failed: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
    
    async def _find_best_agent(self, task_type: Optional[str], priority: str) -> Optional[BaseAgent]:
        """Find the best agent for a given task."""
        suitable_agents = []
        
        if not task_type:
            return None
        
        for agent_id, agent in self.agents.items():
            agent_info = self.agent_info[agent_id]
            
            # Check if agent can handle this task type
            if task_type in agent_info.capabilities:
                # Check if agent is available
                if agent_info.status == AgentStatus.IDLE:
                    suitable_agents.append((agent, agent_info))
        
        if not suitable_agents:
            return None
        
        # Select best agent based on priority and performance
        if priority == "urgent":
            # For urgent tasks, prefer agents with better performance
            suitable_agents.sort(
                key=lambda x: x[1].performance_metrics.get('success_rate', 0),
                reverse=True
            )
        else:
            # For routine tasks, use round-robin
            suitable_agents.sort(
                key=lambda x: x[1].last_activity or datetime.min
            )
        
        return suitable_agents[0][0]
    
    async def broadcast_message(self, message: str, platform: str = "google_chat") -> bool:
        """Broadcast message to all agents via external platform."""
        try:
            if platform not in self.communication_clients:
                self.log_error(f"Unsupported platform: {platform}")
                return False
            
            client = self.communication_clients[platform]
            
            # Send to all agents
            for agent_id, agent in self.agents.items():
                await client.send_message(
                    recipient=agent.get_communication_id(),
                    message=message
                )
            
            self.log_info(f"Broadcast message sent via {platform}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to broadcast message: {e}")
            return False
    
    async def send_user_message(self, user_id: str, message: str, platform: str = "signal") -> bool:
        """Send message to user via external platform."""
        try:
            if platform not in self.communication_clients:
                self.log_error(f"Unsupported platform: {platform}")
                return False
            
            client = self.communication_clients[platform]
            await client.send_message(recipient=user_id, message=message)
            
            self.log_info(f"Message sent to user {user_id} via {platform}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to send user message: {e}")
            return False
    
    async def get_agent_status(self, agent_id: str) -> Optional[AgentInfo]:
        """Get status of a specific agent."""
        return self.agent_info.get(agent_id)
    
    async def get_all_agent_status(self) -> Dict[str, AgentInfo]:
        """Get status of all agents."""
        return self.agent_info.copy()
    
    async def update_agent_performance(self, agent_id: str, metrics: Dict[str, Any]):
        """Update performance metrics for an agent."""
        if agent_id in self.agent_info:
            self.agent_info[agent_id].performance_metrics.update(metrics)
            self.agent_info[agent_id].last_activity = datetime.now()
            
            performance_logger.log_agent_performance(agent_id, metrics)
    
    async def restart_agent(self, agent_id: str) -> bool:
        """Restart a specific agent."""
        try:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            await agent.shutdown()
            await agent.initialize()
            
            self.agent_info[agent_id].status = AgentStatus.IDLE
            self.agent_info[agent_id].current_task = None
            
            self.log_info(f"Restarted agent: {agent_id}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to restart agent {agent_id}: {e}")
            return False
    
    async def shutdown_agent(self, agent_id: str) -> bool:
        """Shutdown a specific agent."""
        try:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            await agent.shutdown()
            
            self.agent_info[agent_id].status = AgentStatus.OFFLINE
            
            self.log_info(f"Shutdown agent: {agent_id}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to shutdown agent {agent_id}: {e}")
            return False
    
    async def shutdown_all_agents(self):
        """Shutdown all agents."""
        self.log_info("Shutting down all agents...")
        
        for agent_id, agent in self.agents.items():
            try:
                await agent.shutdown()
                self.agent_info[agent_id].status = AgentStatus.OFFLINE
            except Exception as e:
                self.log_error(f"Failed to shutdown agent {agent_id}: {e}")
        
        self.is_running = False
        self.log_info("All agents shutdown complete")
    
    async def monitor_agents(self):
        """Monitor agent health and performance."""
        while self.is_running:
            try:
                for agent_id, agent in self.agents.items():
                    agent_info = self.agent_info[agent_id]
                    
                    # Check agent health
                    if not await agent.is_healthy():
                        agent_info.status = AgentStatus.ERROR
                        self.log_warning(f"Agent {agent_id} is unhealthy")
                        
                        # Attempt restart
                        await self.restart_agent(agent_id)
                    
                    # Update performance metrics
                    metrics = await agent.get_performance_metrics()
                    await self.update_agent_performance(agent_id, metrics)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.log_error(f"Agent monitoring error: {e}")
                await asyncio.sleep(30)
    
    def get_ecosystem_summary(self) -> Dict[str, Any]:
        """Get summary of the agent ecosystem."""
        total_agents = len(self.agents)
        active_agents = sum(1 for info in self.agent_info.values() 
                          if info.status == AgentStatus.IDLE or info.status == AgentStatus.BUSY)
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "agent_types": list(set(info.agent_type for info in self.agent_info.values())),
            "communication_platforms": list(self.communication_clients.keys()),
            "ecosystem_status": "healthy" if active_agents > 0 else "degraded"
        } 
