#!/usr/bin/env python3
"""
User Question Router for Terry Delmonaco Manager Agent
Version: 1.0
Description: Routes user questions to all relevant nodes in the agent ecosystem
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

PACKAGE_ROOT = Path(__file__).resolve().parent
if __package__ in (None, ""):
    sys.path.insert(0, str(PACKAGE_ROOT.parent))
    __package__ = PACKAGE_ROOT.name
    import importlib

    importlib.import_module(__package__)

from .main_orchestrator import TerryDelmonacoManagerAgent
from .utils.logger import setup_logger


class UserQuestionRouter:
    """
    Routes user questions through the entire agent ecosystem.
    Ensures all relevant nodes process and contribute to answers.
    """

    def __init__(self, manager_agent: TerryDelmonacoManagerAgent):
        self.manager_agent = manager_agent
        self.logger = setup_logger("user_question_router")

        # Question processing configuration
        self.processing_config = {
            'broadcast_to_all': True,
            'collect_responses': True,
            'aggregate_insights': True,
            'enable_collective_intelligence': True,
            'timeout_seconds': 30
        }

    async def route_user_question(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route user question to all relevant nodes and aggregate responses.

        Args:
            question: User's question
            context: Additional context for the question

        Returns:
            Aggregated response from all nodes
        """
        try:
            self.logger.info(f"Routing user question: {question[:100]}...")

            # Prepare question data
            question_data = {
                'question': question,
                'context': context or {},
                'timestamp': datetime.now().isoformat(),
                'question_id': f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }

            # Step 1: Analyze question to determine relevant agents
            relevant_agents = await self._identify_relevant_agents(question, context)

            # Step 2: Broadcast to all agent nodes
            agent_responses = await self._broadcast_to_agents(question_data, relevant_agents)

            # Step 3: Use collective intelligence to generate insights
            collective_insights = await self._generate_collective_insights(question_data, agent_responses)

            # Step 4: Aggregate all responses
            aggregated_response = await self._aggregate_responses(
                question_data, agent_responses, collective_insights
            )

            # Step 5: Store interaction for learning
            await self._store_interaction(question_data, aggregated_response)

            return aggregated_response

        except Exception as e:
            self.logger.error(f"Failed to route user question: {e}")
            return {
                'success': False,
                'error': str(e),
                'question': question,
                'timestamp': datetime.now().isoformat()
            }

    async def _identify_relevant_agents(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Identify which agents are most relevant to the question."""
        try:
            relevant_agents = []
            question_lower = question.lower()

            # Get all available agents
            available_agents = list(self.manager_agent.agent_fleet.keys())

            # Always include these core agents for any question
            core_agents = ['automated_reporting', 'screen_activity']
            relevant_agents.extend([agent for agent in core_agents if agent in available_agents])

            # Add specific agents based on question content
            if any(keyword in question_lower for keyword in ['email', 'calendar', 'schedule', 'meeting']):
                if 'inbox_calendar' in available_agents:
                    relevant_agents.append('inbox_calendar')

            if any(keyword in question_lower for keyword in ['spreadsheet', 'excel', 'data', 'calculate']):
                if 'spreadsheet_processor' in available_agents:
                    relevant_agents.append('spreadsheet_processor')

            if any(keyword in question_lower for keyword in ['crm', 'customer', 'sales', 'contact']):
                if 'crm_sync' in available_agents:
                    relevant_agents.append('crm_sync')

            if any(keyword in question_lower for keyword in ['code', 'programming', 'development', 'cursor']):
                if 'cursor_agent' in available_agents:
                    relevant_agents.append('cursor_agent')

            # If no specific matches, include all agents
            if len(relevant_agents) <= 2:
                relevant_agents = available_agents

            # Remove duplicates while preserving order
            relevant_agents = list(dict.fromkeys(relevant_agents))

            self.logger.info(f"Identified {len(relevant_agents)} relevant agents: {relevant_agents}")
            return relevant_agents

        except Exception as e:
            self.logger.error(f"Failed to identify relevant agents: {e}")
            return list(self.manager_agent.agent_fleet.keys())

    async def _broadcast_to_agents(self, question_data: Dict[str, Any], agent_ids: List[str]) -> Dict[str, Any]:
        """Broadcast question to all relevant agents and collect responses."""
        try:
            responses = {}

            # Create tasks for parallel processing
            tasks = []
            for agent_id in agent_ids:
                if agent_id in self.manager_agent.agent_fleet:
                    task = asyncio.create_task(
                        self._query_agent(agent_id, question_data),
                        name=f"query_{agent_id}"
                    )
                    tasks.append(task)

            # Wait for all responses or timeout
            if tasks:
                completed, pending = await asyncio.wait(
                    tasks,
                    timeout=self.processing_config['timeout_seconds'],
                    return_when=asyncio.ALL_COMPLETED
                )

                # Process completed tasks
                for task in completed:
                    try:
                        agent_id, response = await task
                        responses[agent_id] = response
                    except Exception as e:
                        self.logger.error(f"Agent task failed: {e}")

                # Cancel pending tasks
                for task in pending:
                    task.cancel()

            self.logger.info(f"Collected responses from {len(responses)} agents")
            return responses

        except Exception as e:
            self.logger.error(f"Failed to broadcast to agents: {e}")
            return {}

    async def _query_agent(self, agent_id: str, question_data: Dict[str, Any]) -> tuple:
        """Query a specific agent with the question."""
        try:
            agent = self.manager_agent.agent_fleet[agent_id]

            # Create task data for the agent
            task_data = {
                'task_type': 'user_question',
                'question': question_data['question'],
                'context': question_data['context'],
                'question_id': question_data['question_id'],
                'priority': 'high'
            }

            # Execute task on agent
            result = await agent.execute_task(task_data)

            return agent_id, {
                'success': result.success,
                'response': result.data,
                'agent_type': agent_id,
                'duration_ms': result.duration_ms,
                'timestamp': result.timestamp.isoformat() if result.timestamp else None
            }

        except Exception as e:
            self.logger.error(f"Failed to query agent {agent_id}: {e}")
            return agent_id, {
                'success': False,
                'error': str(e),
                'agent_type': agent_id,
                'timestamp': datetime.now().isoformat()
            }

    async def _generate_collective_insights(self, question_data: Dict[str, Any], agent_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate collective insights from agent responses."""
        try:
            if not self.processing_config['enable_collective_intelligence']:
                return {}

            # Extract successful responses
            successful_responses = [
                response for response in agent_responses.values()
                if response.get('success', False)
            ]

            if len(successful_responses) < 2:
                return {'message': 'Insufficient responses for collective intelligence'}

            # Use collective intelligence framework
            participating_agents = [
                self.manager_agent.agent_fleet[agent_id]
                for agent_id in agent_responses.keys()
                if agent_id in self.manager_agent.agent_fleet and agent_responses[agent_id].get('success', False)
            ]

            if len(participating_agents) >= 2:
                collective_insight = await self.manager_agent.generate_collective_insight(
                    question_data['question'],
                    [agent.agent_id for agent in participating_agents]
                )
                return collective_insight

            return {}

        except Exception as e:
            self.logger.error(f"Failed to generate collective insights: {e}")
            return {'error': str(e)}

    async def _aggregate_responses(self, question_data: Dict[str, Any], agent_responses: Dict[str, Any], collective_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate all responses into a comprehensive answer."""
        try:
            # Count successful responses
            successful_responses = [r for r in agent_responses.values() if r.get('success', False)]

            # Compile comprehensive response
            aggregated = {
                'question': question_data['question'],
                'question_id': question_data['question_id'],
                'timestamp': datetime.now().isoformat(),
                'processing_summary': {
                    'total_agents_queried': len(agent_responses),
                    'successful_responses': len(successful_responses),
                    'collective_intelligence_generated': bool(collective_insights.get('insight_generated', False))
                },
                'agent_responses': agent_responses,
                'collective_insights': collective_insights,
                'comprehensive_answer': self._synthesize_answer(question_data, agent_responses, collective_insights)
            }

            return aggregated

        except Exception as e:
            self.logger.error(f"Failed to aggregate responses: {e}")
            return {
                'question': question_data['question'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _synthesize_answer(self, question_data: Dict[str, Any], agent_responses: Dict[str, Any], collective_insights: Dict[str, Any]) -> str:
        """Synthesize a comprehensive answer from all responses."""
        try:
            answer_parts = []

            # Add introduction
            answer_parts.append(f"Based on analysis from {len(agent_responses)} specialized agents:")

            # Add individual agent insights
            for agent_id, response in agent_responses.items():
                if response.get('success', False) and response.get('response'):
                    agent_data = response.get('response', {})
                    if isinstance(agent_data, dict) and agent_data.get('insight'):
                        answer_parts.append(f"\n• {agent_id.replace('_', ' ').title()}: {agent_data['insight']}")
                    elif isinstance(agent_data, str):
                        answer_parts.append(f"\n• {agent_id.replace('_', ' ').title()}: {agent_data}")

            # Add collective insights
            if collective_insights.get('insight_generated', False):
                insight_content = collective_insights.get('insight_content', {})
                if insight_content:
                    answer_parts.append(f"\n\nCollective Intelligence Synthesis:")
                    if isinstance(insight_content, dict):
                        for key, value in insight_content.items():
                            answer_parts.append(f"• {key.replace('_', ' ').title()}: {value}")
                    else:
                        answer_parts.append(f"• {insight_content}")

            # Fallback if no useful responses
            if len(answer_parts) <= 1:
                answer_parts.append("\nNo specific insights were generated by the agent network for this question. Please try rephrasing or providing more context.")

            return "\n".join(answer_parts)

        except Exception as e:
            self.logger.error(f"Failed to synthesize answer: {e}")
            return f"Error synthesizing response: {str(e)}"

    async def _store_interaction(self, question_data: Dict[str, Any], response: Dict[str, Any]):
        """Store the question-response interaction for learning."""
        try:
            # Store in memory system for future learning
            if hasattr(self.manager_agent, 'sheets_memory_manager'):
                await self.manager_agent.sheets_memory_manager.store_learning_data(
                    agent_id='user_question_router',
                    learning_type='user_interaction',
                    learning_content={
                        'question': question_data['question'],
                        'response_quality': len(response.get('agent_responses', {})),
                        'collective_intelligence_used': bool(response.get('collective_insights', {}).get('insight_generated', False))
                    },
                    effectiveness=0.8  # Default effectiveness score
                )

        except Exception as e:
            self.logger.error(f"Failed to store interaction: {e}")


async def main():
    """Example usage of the UserQuestionRouter."""
    # Initialize manager agent
    manager = TerryDelmonacoManagerAgent()
    await manager.initialize()

    # Create router
    router = UserQuestionRouter(manager)

    # Example questions
    test_questions = [
        "What's my schedule for today?",
        "Can you analyze my recent email activity?",
        "How is the system performing?",
        "Review the code in my latest project"
    ]

    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Processing: {question}")
        print('='*60)

        response = await router.route_user_question(question)
        print(json.dumps(response.get('comprehensive_answer', ''), indent=2))

    await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
