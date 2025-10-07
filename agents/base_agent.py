"""
Base Agent class for Terry Delmonaco Automation Agent Ecosystem.
Provides common functionality for all automation agents.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from ..utils.logger import LoggerMixin
    from ..utils.config import Config
except ImportError:  # pragma: no cover - support direct package execution
    from utils.logger import LoggerMixin
    from utils.config import Config


# Configuration constants
DEFAULT_SUCCESS_THRESHOLD = 0.7
DEFAULT_MIN_SPAWN_FREQUENCY = 10
DEFAULT_MIN_SPAWN_COMPLEXITY = 0.7
DEFAULT_MIN_INSIGHT_RELEVANCE = 0.6
DEFAULT_FAILURE_THRESHOLD = 0.3
DEFAULT_OPTIMIZATION_THRESHOLD = 0.8
DEFAULT_MAX_AVG_DURATION_MS = 30000


@dataclass
class TaskResult:
    """Result of a task execution."""
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None
    duration_ms: int = 0
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseAgent(LoggerMixin, ABC):
    """
    Base class for all automation agents.
    Provides common functionality for agent lifecycle and task execution.
    Enhanced with recursive self-improvement and collective intelligence.
    """

    def __init__(self, agent_type: str, config: Dict[str, Any], communication_clients: Dict[str, Any]):
        super().__init__()
        self.agent_type = agent_type
        self.config = config
        self.communication_clients = communication_clients
        self.agent_id = f"{agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.is_initialized = False
        self.is_running = False
        self.current_task = None
        self.performance_metrics = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_duration_ms': 0,
            'success_rate': 0.0,
            'last_task_time': None
        }

        # Recursive cognition attributes
        self.learning_patterns = {}
        self.capability_evolution = {}
        self.network_connections = set()
        self.knowledge_fragments = []
        self.meta_cognition_data = {
            'self_modifications': [],
            'spawned_agents': [],
            'learned_behaviors': [],
            'optimization_history': []
        }
        self.collective_memory_access = None
    
    async def initialize(self):
        """Initialize the agent."""
        try:
            self.log_info(f"Initializing {self.agent_type} agent: {self.agent_id}")
            
            # Initialize agent-specific components
            await self._initialize_agent()
            
            self.is_initialized = True
            self.is_running = True
            
            self.log_info(f"{self.agent_type} agent initialized successfully")
            
        except Exception as e:
            self.log_error(f"Failed to initialize {self.agent_type} agent: {e}")
            raise
    
    @abstractmethod
    async def _initialize_agent(self):
        """Initialize agent-specific components. Override in subclasses."""
        pass
    
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute a task and return the result."""
        start_time = datetime.now()
        task_id = task_data.get('task_id', 'unknown')
        
        try:
            self.log_info(f"Executing task {task_id} on {self.agent_type} agent")
            self.current_task = task_id
            
            # Execute the task
            result = await self._execute_task(task_data)
            
            # Update performance metrics
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self._update_performance_metrics(result.success, duration_ms)
            
            self.log_info(f"Task {task_id} completed successfully")
            return result
            
        except Exception as e:
            self.log_error(f"Task {task_id} failed: {e}")
            
            # Update performance metrics for failure
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self._update_performance_metrics(False, duration_ms)
            
            return TaskResult(
                success=False,
                data={},
                error_message=str(e),
                duration_ms=duration_ms
            )
        finally:
            self.current_task = None
    
    @abstractmethod
    async def _execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute agent-specific task. Override in subclasses."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get list of task types this agent can handle."""
        return self.config.get('capabilities', [])
    
    def get_communication_id(self) -> str:
        """Get communication identifier for this agent."""
        return f"{self.agent_type}_{self.agent_id}"
    
    async def is_healthy(self) -> bool:
        """Check if the agent is healthy."""
        return self.is_initialized and self.is_running
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_metrics.copy()
    
    def _update_performance_metrics(self, success: bool, duration_ms: int):
        """Update performance metrics after task execution."""
        if success:
            self.performance_metrics['tasks_completed'] += 1
        else:
            self.performance_metrics['tasks_failed'] += 1
        
        self.performance_metrics['total_duration_ms'] += duration_ms
        self.performance_metrics['last_task_time'] = datetime.now()
        
        total_tasks = self.performance_metrics['tasks_completed'] + self.performance_metrics['tasks_failed']
        if total_tasks > 0:
            self.performance_metrics['success_rate'] = (
                self.performance_metrics['tasks_completed'] / total_tasks
            )
    
    async def shutdown(self):
        """Shutdown the agent."""
        try:
            self.log_info(f"Shutting down {self.agent_type} agent: {self.agent_id}")
            
            # Shutdown agent-specific components
            await self._shutdown_agent()
            
            self.is_running = False
            self.is_initialized = False
            
            self.log_info(f"{self.agent_type} agent shutdown complete")
            
        except Exception as e:
            self.log_error(f"Failed to shutdown {self.agent_type} agent: {e}")
            raise
    
    @abstractmethod
    async def _shutdown_agent(self):
        """Shutdown agent-specific components. Override in subclasses."""
        pass

    # Recursive Self-Improvement Methods
    async def evolve_capabilities(self, learning_data: Dict[str, Any]) -> bool:
        """Allow agents to modify their own capabilities based on learnings."""
        try:
            task_pattern = learning_data.get('task_pattern')
            success_rate = learning_data.get('success_rate', 0)
            optimization_suggestion = learning_data.get('optimization')

            success_threshold = self.config.get('success_threshold', 0.7)
            if success_rate < success_threshold and optimization_suggestion:
                # Self-modify based on poor performance
                await self._apply_optimization(optimization_suggestion)

                # Record the modification
                self.meta_cognition_data['self_modifications'].append({
                    'timestamp': datetime.now().isoformat(),
                    'trigger': f"Low success rate: {success_rate}",
                    'modification': optimization_suggestion,
                    'previous_config': self.config.copy()
                })

                self.log_info(f"Agent {self.agent_id} evolved capabilities based on learning data")
                return True

        except Exception as e:
            self.log_error(f"Capability evolution failed: {e}")

        return False

    async def _apply_optimization(self, optimization: Dict[str, Any]):
        """Apply optimization to agent configuration or behavior."""
        optimization_type = optimization.get('type')

        if optimization_type == 'config_update':
            # Update configuration parameters
            config_updates = optimization.get('config_changes', {})
            self.config.update(config_updates)

        elif optimization_type == 'capability_expansion':
            # Add new capabilities
            new_capabilities = optimization.get('new_capabilities', [])
            current_capabilities = self.config.get('capabilities', [])
            self.config['capabilities'] = list(set(current_capabilities + new_capabilities))

        elif optimization_type == 'behavior_modification':
            # Modify behavior patterns
            behavior_changes = optimization.get('behavior_changes', {})
            self.learning_patterns.update(behavior_changes)

    async def spawn_specialized_agent(self, task_pattern: Dict[str, Any]) -> Optional[str]:
        """Create new specialized agents based on recurring patterns."""
        try:
            pattern_frequency = task_pattern.get('frequency', 0)
            task_complexity = task_pattern.get('complexity', 0)

            # Only spawn if pattern is frequent and complex enough
            min_frequency = self.config.get('min_spawn_frequency', 10)
            min_complexity = self.config.get('min_spawn_complexity', 0.7)
            if pattern_frequency > min_frequency and task_complexity > min_complexity:
                new_agent_type = f"{self.agent_type}_specialized_{len(self.meta_cognition_data['spawned_agents'])}"

                # Create specialized configuration
                specialized_config = self.config.copy()
                specialized_config.update({
                    'specialization': task_pattern.get('specialization'),
                    'parent_agent': self.agent_id,
                    'spawned_for_pattern': task_pattern
                })

                # Record spawning
                spawn_record = {
                    'timestamp': datetime.now().isoformat(),
                    'new_agent_type': new_agent_type,
                    'trigger_pattern': task_pattern,
                    'parent_performance': await self.get_performance_metrics()
                }

                self.meta_cognition_data['spawned_agents'].append(spawn_record)

                self.log_info(f"Agent {self.agent_id} spawned specialized agent: {new_agent_type}")
                return new_agent_type

        except Exception as e:
            self.log_error(f"Agent spawning failed: {e}")

        return None

    # Cross-Agent Learning Networks
    async def connect_to_agent_network(self, other_agents: List['BaseAgent']):
        """Create direct learning connections with other agents."""
        for agent in other_agents:
            if agent.agent_id != self.agent_id:
                self.network_connections.add(agent.agent_id)
                agent.network_connections.add(self.agent_id)

        self.log_info(f"Agent {self.agent_id} connected to {len(other_agents)} agents")

    async def share_insight(self, insight: Dict[str, Any], target_agents: List[str] = None):
        """Share insights with connected agents."""
        if target_agents is None:
            target_agents = list(self.network_connections)

        shared_insight = {
            'source_agent': self.agent_id,
            'timestamp': datetime.now().isoformat(),
            'insight_type': insight.get('type'),
            'data': insight.get('data'),
            'confidence': insight.get('confidence', 0.5)
        }

        # Add to knowledge fragments for collective intelligence
        self.knowledge_fragments.append(shared_insight)

        self.log_info(f"Agent {self.agent_id} shared insight with {len(target_agents)} agents")

    async def receive_insight(self, insight: Dict[str, Any]) -> bool:
        """Receive and integrate insight from another agent."""
        try:
            # Evaluate insight relevance and quality
            relevance_score = await self._evaluate_insight_relevance(insight)

            min_relevance = self.config.get('min_insight_relevance', 0.6)
            if relevance_score > min_relevance:
                # Integrate insight into learning patterns
                insight_type = insight.get('insight_type')
                if insight_type not in self.learning_patterns:
                    self.learning_patterns[insight_type] = []

                self.learning_patterns[insight_type].append(insight)

                # Record learned behavior
                self.meta_cognition_data['learned_behaviors'].append({
                    'timestamp': datetime.now().isoformat(),
                    'source_agent': insight.get('source_agent'),
                    'insight_type': insight_type,
                    'relevance_score': relevance_score
                })

                return True

        except Exception as e:
            self.log_error(f"Insight integration failed: {e}")

        return False

    async def _evaluate_insight_relevance(self, insight: Dict[str, Any]) -> float:
        """Evaluate how relevant an insight is to this agent."""
        # Simple relevance scoring based on agent type and capabilities
        insight_type = insight.get('insight_type', '')
        agent_capabilities = self.get_capabilities()

        relevance = 0.0

        # Check if insight type matches any capabilities
        for capability in agent_capabilities:
            if capability.lower() in insight_type.lower():
                relevance += 0.3

        # Check confidence of the insight
        confidence = insight.get('confidence', 0)
        relevance += confidence * 0.4

        # Check recency (newer insights are more relevant)
        try:
            insight_time = datetime.fromisoformat(insight.get('timestamp', ''))
            time_diff = (datetime.now() - insight_time).total_seconds()
            recency_score = max(0, 1 - (time_diff / 86400))  # Decay over 24 hours
            relevance += recency_score * 0.3
        except (ValueError, TypeError) as e:
            # Handle cases where timestamp is missing or malformed
            pass

        return min(1.0, relevance)

    # Meta-Cognition Layer
    async def analyze_self_performance(self) -> Dict[str, Any]:
        """Analyze own performance patterns and identify optimization opportunities."""
        try:
            performance = await self.get_performance_metrics()

            analysis = {
                'performance_trend': self._calculate_performance_trend(),
                'capability_gaps': self._identify_capability_gaps(),
                'optimization_opportunities': self._identify_optimizations(),
                'learning_effectiveness': self._evaluate_learning_effectiveness()
            }

            # Record analysis
            self.meta_cognition_data['optimization_history'].append({
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis,
                'current_performance': performance
            })

            return analysis

        except Exception as e:
            self.log_error(f"Self-performance analysis failed: {e}")
            return {}

    def _calculate_performance_trend(self) -> str:
        """Calculate if performance is improving, declining, or stable."""
        optimization_history = self.meta_cognition_data['optimization_history']

        if len(optimization_history) < 2:
            return "insufficient_data"

        recent_performance = optimization_history[-1]['current_performance']['success_rate']
        previous_performance = optimization_history[-2]['current_performance']['success_rate']

        if recent_performance > previous_performance + 0.05:
            return "improving"
        elif recent_performance < previous_performance - 0.05:
            return "declining"
        else:
            return "stable"

    def _identify_capability_gaps(self) -> List[str]:
        """Identify missing capabilities based on failed tasks."""
        gaps = []

        # Analyze failed task patterns
        for pattern_type, patterns in self.learning_patterns.items():
            failure_rate = sum(1 for p in patterns if not p.get('success', True)) / max(len(patterns), 1)

            failure_threshold = self.config.get('failure_threshold', 0.3)
            if failure_rate > failure_threshold:  # High failure rate indicates capability gap
                gaps.append(pattern_type)

        return gaps

    def _identify_optimizations(self) -> List[Dict[str, Any]]:
        """Identify potential optimizations based on performance data."""
        optimizations = []

        # Low success rate optimization
        optimization_threshold = self.config.get('optimization_threshold', 0.8)
        if self.performance_metrics['success_rate'] < optimization_threshold:
            optimizations.append({
                'type': 'capability_expansion',
                'priority': 'high',
                'description': 'Expand capabilities to improve success rate',
                'suggested_action': 'Add specialized training or tools'
            })

        # High task duration optimization
        avg_duration = (self.performance_metrics['total_duration_ms'] /
                       max(self.performance_metrics['tasks_completed'], 1))

        max_avg_duration = self.config.get('max_avg_duration_ms', 30000)
        if avg_duration > max_avg_duration:  # Configurable duration threshold
            optimizations.append({
                'type': 'performance_optimization',
                'priority': 'medium',
                'description': 'Reduce task execution time',
                'suggested_action': 'Optimize algorithms or add caching'
            })

        return optimizations

    def _evaluate_learning_effectiveness(self) -> float:
        """Evaluate how well the agent is learning from experiences."""
        learned_behaviors = self.meta_cognition_data['learned_behaviors']

        if not learned_behaviors:
            return 0.0

        # Calculate learning rate (behaviors learned per time unit)
        recent_learnings = [
            b for b in learned_behaviors
            if (datetime.now() - datetime.fromisoformat(b['timestamp'])).days <= 7
        ]

        return min(1.0, len(recent_learnings) / 10)  # Normalize to 0-1

    # Collective Intelligence
    async def contribute_to_collective_intelligence(self, insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Contribute insights to the collective intelligence pool."""
        collective_contribution = {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'timestamp': datetime.now().isoformat(),
            'insights': insights,
            'performance_context': await self.get_performance_metrics(),
            'network_connections': len(self.network_connections)
        }

        # Store in knowledge fragments for collective access
        self.knowledge_fragments.extend(insights)

        return collective_contribution

    async def access_collective_intelligence(self, query_pattern: str) -> List[Dict[str, Any]]:
        """Access relevant insights from the collective intelligence pool."""
        relevant_insights = []

        # Search through knowledge fragments with structured search
        for fragment in self.knowledge_fragments:
            insight_type = fragment.get('insight_type', '')
            insight_data = str(fragment.get('data', ''))
            source_agent = fragment.get('source_agent', '')

            if (query_pattern.lower() in insight_type.lower() or
                query_pattern.lower() in insight_data.lower() or
                query_pattern.lower() in source_agent.lower()):
                relevant_insights.append(fragment)

        # Sort by relevance and recency
        relevant_insights.sort(
            key=lambda x: (
                x.get('confidence', 0),
                datetime.fromisoformat(x.get('timestamp', '2000-01-01'))
            ),
            reverse=True
        )

        return relevant_insights[:10]  # Return top 10 relevant insights
    
