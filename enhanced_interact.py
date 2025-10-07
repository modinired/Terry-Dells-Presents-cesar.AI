#!/usr/bin/env python3
"""
Enhanced Interactive Interface with User Question Routing
Version: 1.0
Description: Interactive CLI that routes user questions through all agent nodes
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

PACKAGE_ROOT = Path(__file__).resolve().parent
if __package__ in (None, ""):
    sys.path.insert(0, str(PACKAGE_ROOT.parent))
    __package__ = PACKAGE_ROOT.name
    import importlib

    importlib.import_module(__package__)

from .main_orchestrator import TerryDelmonacoManagerAgent
from .user_question_router import UserQuestionRouter
from .utils.logger import setup_logger


class EnhancedAgentInterface:
    """Enhanced interface with intelligent question routing."""

    def __init__(self):
        self.manager_agent = None
        self.question_router = None
        self.logger = setup_logger("enhanced_interface")
        self.is_running = False

    async def initialize(self):
        """Initialize the manager agent and question router."""
        try:
            print("🚀 Initializing Terry Delmonaco Manager Agent...")

            self.manager_agent = TerryDelmonacoManagerAgent()
            success = await self.manager_agent.initialize()

            if not success:
                print("❌ Failed to initialize manager agent")
                return False

            print("🔗 Setting up question router...")
            self.question_router = UserQuestionRouter(self.manager_agent)

            self.is_running = True
            print("✅ Enhanced Agent Interface ready!")
            return True

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False

    async def start_interactive_session(self):
        """Start the interactive session."""
        if not await self.initialize():
            return

        print("\n" + "="*80)
        print("🤖 TERRY DELMONACO ENHANCED AGENT INTERFACE")
        print("   All user questions are routed through the entire agent network")
        print("="*80)

        try:
            while self.is_running:
                await self.show_menu()
                choice = input("\nEnter your choice: ").strip()
                await self.handle_choice(choice)

        except KeyboardInterrupt:
            print("\n👋 Shutting down gracefully...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await self.shutdown()

    async def show_menu(self):
        """Display the interactive menu."""
        print("\n" + "-"*60)
        print("🔥 AGENT NETWORK ACTIONS")
        print("-"*60)
        print("1.  Ask Any Question (Routes to All Agents)")
        print("2.  System Status & Health")
        print("3.  Agent Fleet Overview")
        print("4.  Performance Metrics")
        print("5.  Collective Intelligence Status")
        print("6.  Screen Activity Analysis")
        print("7.  Learning Sync with CESAR")
        print("8.  Generate Status Report")
        print("9.  Trigger Agent Evolution")
        print("10. Spawn Specialized Agent")
        print("11. Quick Code Review")
        print("12. Emergency System Check")
        print("0.  Exit")
        print("-"*60)

    async def handle_choice(self, choice: str):
        """Handle user menu choice."""
        try:
            if choice == "1":
                await self.ask_question()
            elif choice == "2":
                await self.system_status()
            elif choice == "3":
                await self.agent_fleet_overview()
            elif choice == "4":
                await self.performance_metrics()
            elif choice == "5":
                await self.collective_intelligence_status()
            elif choice == "6":
                await self.screen_activity_analysis()
            elif choice == "7":
                await self.learning_sync()
            elif choice == "8":
                await self.generate_status_report()
            elif choice == "9":
                await self.trigger_agent_evolution()
            elif choice == "10":
                await self.spawn_specialized_agent()
            elif choice == "11":
                await self.quick_code_review()
            elif choice == "12":
                await self.emergency_system_check()
            elif choice == "0":
                self.is_running = False
            else:
                print("❌ Invalid choice. Please try again.")

        except Exception as e:
            print(f"❌ Error processing choice: {e}")

    async def ask_question(self):
        """Route user question through all agents."""
        print("\n🤔 ASK A QUESTION - All Agents Will Contribute")
        print("-" * 50)

        question = input("Your question: ").strip()
        if not question:
            print("❌ Please enter a question.")
            return

        context_input = input("Additional context (optional): ").strip()
        context = {"user_provided_context": context_input} if context_input else {}

        print(f"\n🔄 Routing question through {len(self.manager_agent.agent_fleet)} agents...")

        # Route question through all agents
        response = await self.question_router.route_user_question(question, context)

        # Display comprehensive results
        self.display_question_response(response)

    def display_question_response(self, response: Dict[str, Any]):
        """Display the comprehensive question response."""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE AGENT NETWORK RESPONSE")
        print("="*80)

        # Processing Summary
        summary = response.get('processing_summary', {})
        print(f"🔍 Agents Queried: {summary.get('total_agents_queried', 0)}")
        print(f"✅ Successful Responses: {summary.get('successful_responses', 0)}")
        print(f"🧠 Collective Intelligence: {'Yes' if summary.get('collective_intelligence_generated', False) else 'No'}")

        # Main Answer
        print(f"\n📝 SYNTHESIZED ANSWER:")
        print("-" * 40)
        answer = response.get('comprehensive_answer', 'No answer generated')
        print(answer)

        # Individual Agent Responses
        agent_responses = response.get('agent_responses', {})
        if agent_responses:
            print(f"\n🤖 INDIVIDUAL AGENT CONTRIBUTIONS:")
            print("-" * 40)
            for agent_id, agent_response in agent_responses.items():
                status = "✅" if agent_response.get('success', False) else "❌"
                print(f"{status} {agent_id.replace('_', ' ').title()}")
                if agent_response.get('success', False):
                    duration = agent_response.get('duration_ms', 0)
                    print(f"   Duration: {duration}ms")

        # Collective Insights
        collective = response.get('collective_insights', {})
        if collective.get('insight_generated', False):
            print(f"\n🌐 COLLECTIVE INTELLIGENCE INSIGHTS:")
            print("-" * 40)
            print(f"Confidence: {collective.get('confidence_score', 0):.2%}")
            print(f"Source Agents: {len(collective.get('source_agents', []))}")

        print("="*80)

    async def system_status(self):
        """Get system status and health."""
        print("\n🏥 SYSTEM STATUS & HEALTH CHECK")
        print("-" * 40)

        try:
            # Get ecosystem summary
            ecosystem = await self.manager_agent.get_ecosystem_summary()
            print(f"Total Agents: {ecosystem.get('total_agents', 0)}")
            print(f"Active Agents: {ecosystem.get('active_agents', 0)}")
            print(f"Ecosystem Status: {ecosystem.get('ecosystem_status', 'unknown').upper()}")
            print(f"Manager Status: {ecosystem.get('manager_status', 'unknown').upper()}")

            # Get individual agent health
            agent_status = await self.manager_agent.get_all_agent_status()
            print(f"\n🤖 AGENT HEALTH:")
            for agent_id, status in agent_status.items():
                health = "🟢" if status.get('is_running', False) else "🔴"
                print(f"{health} {agent_id.replace('_', ' ').title()}")

        except Exception as e:
            print(f"❌ Failed to get system status: {e}")

    async def agent_fleet_overview(self):
        """Get detailed agent fleet overview."""
        print("\n🚁 AGENT FLEET OVERVIEW")
        print("-" * 40)

        try:
            agent_status = await self.manager_agent.get_all_agent_status()

            for agent_id, status in agent_status.items():
                print(f"\n📋 {agent_id.replace('_', ' ').title()}")
                print(f"   Status: {'Running' if status.get('is_running', False) else 'Stopped'}")
                print(f"   Initialized: {'Yes' if status.get('is_initialized', False) else 'No'}")

                # Performance metrics if available
                if 'performance_metrics' in status:
                    metrics = status['performance_metrics']
                    print(f"   Tasks Completed: {metrics.get('tasks_completed', 0)}")
                    print(f"   Success Rate: {metrics.get('success_rate', 0):.1%}")

        except Exception as e:
            print(f"❌ Failed to get fleet overview: {e}")

    async def performance_metrics(self):
        """Get performance metrics."""
        print("\n📊 PERFORMANCE METRICS")
        print("-" * 40)

        try:
            total_completed = 0
            total_failed = 0

            for agent_id, agent in self.manager_agent.agent_fleet.items():
                metrics = await agent.get_performance_metrics()
                completed = metrics.get('tasks_completed', 0)
                failed = metrics.get('tasks_failed', 0)
                success_rate = metrics.get('success_rate', 0)

                total_completed += completed
                total_failed += failed

                print(f"🤖 {agent_id.replace('_', ' ').title()}")
                print(f"   Completed: {completed}, Failed: {failed}")
                print(f"   Success Rate: {success_rate:.1%}")

            overall_rate = total_completed / max(total_completed + total_failed, 1)
            print(f"\n🎯 OVERALL PERFORMANCE")
            print(f"   Total Tasks: {total_completed + total_failed}")
            print(f"   Success Rate: {overall_rate:.1%}")

        except Exception as e:
            print(f"❌ Failed to get performance metrics: {e}")

    async def collective_intelligence_status(self):
        """Get collective intelligence status."""
        print("\n🧠 COLLECTIVE INTELLIGENCE STATUS")
        print("-" * 40)

        try:
            ci_status = await self.manager_agent.get_recursive_cognition_status()

            collective = ci_status.get('collective_intelligence', {})
            ecosystem = ci_status.get('ecosystem_overview', {})

            print(f"Network Connections: {ecosystem.get('network_connections', 0)}")
            print(f"Collective Insights: {ecosystem.get('collective_insights_generated', 0)}")
            print(f"Emergent Behaviors: {ecosystem.get('emergent_behaviors_detected', 0)}")
            print(f"Specialized Agents: {ecosystem.get('specialized_agents', 0)}")

        except Exception as e:
            print(f"❌ Failed to get collective intelligence status: {e}")

    async def screen_activity_analysis(self):
        """Trigger screen activity analysis."""
        print("\n📱 SCREEN ACTIVITY ANALYSIS")
        print("-" * 40)

        try:
            result = await self.manager_agent.record_and_describe()
            if result.get('success', False):
                print("✅ Screen activity captured and analyzed")
                print(f"Analysis: {result.get('description', 'No description available')}")
            else:
                print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Failed to analyze screen activity: {e}")

    async def learning_sync(self):
        """Sync learnings with CESAR."""
        print("\n🔄 LEARNING SYNC WITH CESAR")
        print("-" * 40)

        try:
            result = await self.manager_agent.sync_with_cesar_ecosystem()
            if result.get('knowledge_sync'):
                print("✅ Knowledge sync completed")
            if result.get('memory_sync'):
                print("✅ Memory sync completed")
            if result.get('intelligence_sync'):
                print("✅ Intelligence sync completed")

        except Exception as e:
            print(f"❌ Failed to sync learnings: {e}")

    async def generate_status_report(self):
        """Generate comprehensive status report."""
        print("\n📊 COMPREHENSIVE STATUS REPORT")
        print("-" * 40)

        try:
            report = await self.manager_agent.generate_status_report()
            print(json.dumps(report, indent=2))

        except Exception as e:
            print(f"❌ Failed to generate status report: {e}")

    async def trigger_agent_evolution(self):
        """Trigger agent evolution."""
        print("\n🧬 TRIGGER AGENT EVOLUTION")
        print("-" * 40)

        agent_id = input("Enter agent ID to evolve: ").strip()
        if agent_id not in self.manager_agent.agent_fleet:
            print(f"❌ Agent '{agent_id}' not found")
            return

        try:
            performance_data = {
                'task_pattern': {'specialization': 'user_requested_evolution'},
                'success_rate': 0.6,  # Trigger evolution
                'optimization_suggestion': {
                    'type': 'capability_expansion',
                    'new_capabilities': ['enhanced_processing']
                }
            }

            result = await self.manager_agent.trigger_agent_evolution(agent_id, performance_data)
            if result.get('evolution_triggered', False):
                print(f"✅ Agent {agent_id} evolution triggered")
            else:
                print(f"❌ Evolution failed for {agent_id}")

        except Exception as e:
            print(f"❌ Failed to trigger evolution: {e}")

    async def spawn_specialized_agent(self):
        """Spawn a specialized agent."""
        print("\n🐣 SPAWN SPECIALIZED AGENT")
        print("-" * 40)

        task_type = input("Enter task type for specialization: ").strip()
        if not task_type:
            print("❌ Please enter a task type")
            return

        try:
            pattern_data = {
                'pattern_id': f'user_requested_{task_type}',
                'task_type': task_type,
                'frequency': 15,  # High frequency to trigger spawning
                'complexity': 0.8,
                'success_rate': 0.7,
                'avg_duration_ms': 25000
            }

            result = await self.manager_agent.spawn_specialized_agent(pattern_data)
            if result.get('success', False):
                print(f"✅ Specialized agent spawned: {result.get('new_agent_id')}")
            else:
                print(f"❌ Failed to spawn agent: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Failed to spawn specialized agent: {e}")

    async def quick_code_review(self):
        """Quick code review through cursor agent."""
        print("\n💻 QUICK CODE REVIEW")
        print("-" * 40)

        code = input("Enter code to review: ").strip()
        if not code:
            print("❌ Please enter code to review")
            return

        # Route through question system for comprehensive analysis
        question = f"Please review this code for issues, improvements, and best practices: {code}"
        response = await self.question_router.route_user_question(question)
        self.display_question_response(response)

    async def emergency_system_check(self):
        """Emergency system check."""
        print("\n🚨 EMERGENCY SYSTEM CHECK")
        print("-" * 40)

        question = "Perform an emergency system health check. Report any issues, failures, or degraded performance."
        response = await self.question_router.route_user_question(question)
        self.display_question_response(response)

    async def shutdown(self):
        """Shutdown the interface and manager agent."""
        try:
            print("\n🛑 Shutting down Terry Delmonaco Manager Agent...")
            if self.manager_agent:
                await self.manager_agent.shutdown()
            print("✅ Shutdown complete")
        except Exception as e:
            print(f"❌ Shutdown error: {e}")


async def main():
    """Main entry point."""
    interface = EnhancedAgentInterface()
    await interface.start_interactive_session()


if __name__ == "__main__":
    asyncio.run(main())
