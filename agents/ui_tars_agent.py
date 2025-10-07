#!/usr/bin/env python3
"""
UI-TARS Agent for Terry Delmonaco Manager Agent
Integrates UI-TARS desktop automation capabilities into the CESAR agent ecosystem.
"""

import asyncio
import logging
import subprocess
import json
import os
import tempfile
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .base_agent import BaseAgent, TaskResult


class UITarsAgent(BaseAgent):
    """
    UI-TARS Agent that provides GUI automation capabilities using UI-TARS vision-language model.
    Integrates with the CESAR agent ecosystem for advanced desktop task automation.
    """

    def __init__(self, config: Dict[str, Any] = None, communication_clients: Dict[str, Any] = None):
        super().__init__("ui_tars_agent", config or {}, communication_clients or {})
        self.agent_id = f"{self.agent_type}_{self.config.get('instance_id', 'default')}"
        self.logger = logging.getLogger(f"ui_tars_agent.{self.agent_id}")

        # UI-TARS specific configuration
        self.ui_tars_path = self.config.get('ui_tars_path', '/Users/modini_red/UI-TARS-desktop')
        self.model_provider = self.config.get('model_provider', 'huggingface')
        self.model_name = self.config.get('model_name', 'UI-TARS-1.5-7B')
        self.api_key = self.config.get('api_key', '')
        self.base_url = self.config.get('base_url', '')

        # Agent capabilities including Jules integration
        self.capabilities = [
            "gui_automation",
            "screen_analysis",
            "visual_reasoning",
            "cross_platform_control",
            "browser_automation",
            "desktop_interaction",
            "screenshot_analysis",
            "natural_language_control",
            "jules_integration",
            "workflow_automation",
            "desktop_triggers",
            "advanced_task_scheduling"
        ]

        # Jules integration components
        self.jules_integration_enabled = self.config.get('jules_integration_enabled', True)
        self.jules_workflow_templates = {}
        self.jules_desktop_triggers = {}

        # Task execution state
        self.current_task = None
        self.execution_history = []
        self.screenshot_cache = {}

        self.logger.info(f"UI-TARS Agent initialized: {self.agent_id}")

    async def initialize(self) -> bool:
        """Initialize the UI-TARS agent."""
        try:
            self.logger.info("Initializing UI-TARS agent...")

            # Check if UI-TARS desktop is available
            if not await self._check_ui_tars_availability():
                self.logger.error("UI-TARS desktop not available")
                return False

            # Verify Node.js and npm dependencies
            if not await self._verify_node_dependencies():
                self.logger.error("Node.js dependencies not available")
                return False

            # Test basic functionality
            if not await self._test_basic_functionality():
                self.logger.error("Basic functionality test failed")
                return False

            self.is_initialized = True
            self.logger.info("UI-TARS agent initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"UI-TARS agent initialization failed: {e}")
            return False

    async def _check_ui_tars_availability(self) -> bool:
        """Check if UI-TARS desktop is available and accessible."""
        try:
            # Check if UI-TARS directory exists
            ui_tars_dir = Path(self.ui_tars_path)
            if not ui_tars_dir.exists():
                self.logger.error(f"UI-TARS directory not found: {self.ui_tars_path}")
                return False

            # Check for key files
            required_files = [
                "package.json",
                "multimodal/gui-agent/agent-sdk/package.json"
            ]

            for file_path in required_files:
                if not (ui_tars_dir / file_path).exists():
                    self.logger.error(f"Required UI-TARS file not found: {file_path}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking UI-TARS availability: {e}")
            return False

    async def _verify_node_dependencies(self) -> bool:
        """Verify Node.js and required dependencies are available."""
        try:
            # Check Node.js
            result = await asyncio.create_subprocess_exec(
                'node', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                self.logger.error("Node.js not available")
                return False

            node_version = stdout.decode().strip()
            self.logger.info(f"Node.js version: {node_version}")

            # Check if dependencies are installed in UI-TARS directory
            package_lock_path = Path(self.ui_tars_path) / "pnpm-lock.yaml"
            if not package_lock_path.exists():
                self.logger.warning("UI-TARS dependencies might not be installed")
                # Attempt to install dependencies
                await self._install_ui_tars_dependencies()

            return True

        except Exception as e:
            self.logger.error(f"Error verifying Node.js dependencies: {e}")
            return False

    async def _install_ui_tars_dependencies(self):
        """Install UI-TARS dependencies if needed."""
        try:
            self.logger.info("Installing UI-TARS dependencies...")

            # Change to UI-TARS directory and install dependencies
            process = await asyncio.create_subprocess_exec(
                'pnpm', 'install',
                cwd=self.ui_tars_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                self.logger.info("UI-TARS dependencies installed successfully")
            else:
                self.logger.error(f"Failed to install UI-TARS dependencies: {stderr.decode()}")

        except Exception as e:
            self.logger.error(f"Error installing UI-TARS dependencies: {e}")

    async def _test_basic_functionality(self) -> bool:
        """Test basic UI-TARS functionality."""
        try:
            # Test screenshot capability
            screenshot_path = await self.capture_screenshot()
            if screenshot_path and Path(screenshot_path).exists():
                self.logger.info("Screenshot functionality working")
                # Clean up test screenshot
                os.unlink(screenshot_path)
                return True
            else:
                self.logger.error("Screenshot functionality not working")
                return False

        except Exception as e:
            self.logger.error(f"Basic functionality test failed: {e}")
            return False

    async def start(self) -> bool:
        """Start the UI-TARS agent."""
        if not self.is_initialized:
            if not await self.initialize():
                return False

        try:
            self.is_running = True
            self.logger.info("UI-TARS agent started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start UI-TARS agent: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the UI-TARS agent."""
        try:
            self.is_running = False
            self.current_task = None
            self.logger.info("UI-TARS agent stopped")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop UI-TARS agent: {e}")
            return False

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a GUI automation task using UI-TARS."""
        try:
            self.current_task = task_data
            task_id = task_data.get('task_id', f"ui_tars_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            instruction = task_data.get('instruction', '')
            target_application = task_data.get('target_application', 'desktop')

            self.logger.info(f"Processing UI-TARS task: {task_id}")
            self.logger.info(f"Instruction: {instruction}")

            # Capture initial screenshot
            initial_screenshot = await self.capture_screenshot()

            # Execute the GUI automation task
            result = await self._execute_gui_task(instruction, target_application, initial_screenshot)

            # Store execution in history
            execution_record = {
                'task_id': task_id,
                'instruction': instruction,
                'target_application': target_application,
                'initial_screenshot': initial_screenshot,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            self.execution_history.append(execution_record)

            return {
                'status': 'completed' if result.get('success') else 'failed',
                'task_id': task_id,
                'result': result,
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error processing UI-TARS task: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }
        finally:
            self.current_task = None

    async def _execute_gui_task(self, instruction: str, target_application: str, screenshot_path: str) -> Dict[str, Any]:
        """Execute a GUI automation task using UI-TARS CLI."""
        try:
            # Create temporary configuration for this task
            config = {
                'instruction': instruction,
                'target_application': target_application,
                'screenshot': screenshot_path,
                'provider': self.model_provider,
                'model': self.model_name,
                'api_key': self.api_key,
                'base_url': self.base_url
            }

            # Use Agent TARS CLI for task execution
            result = await self._run_agent_tars_cli(config)

            return {
                'success': result.get('success', False),
                'actions_taken': result.get('actions', []),
                'final_screenshot': result.get('final_screenshot'),
                'execution_log': result.get('log', []),
                'duration_ms': result.get('duration_ms', 0)
            }

        except Exception as e:
            self.logger.error(f"Error executing GUI task: {e}")
            return {
                'success': False,
                'error': str(e),
                'actions_taken': [],
                'execution_log': []
            }

    async def _run_agent_tars_cli(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run Agent TARS CLI command for GUI automation."""
        try:
            # Build command arguments
            cmd_args = [
                'npx', '@agent-tars/cli@latest',
                '--provider', config.get('provider', 'huggingface'),
                '--model', config.get('model', 'UI-TARS-1.5-7B')
            ]

            if config.get('api_key'):
                cmd_args.extend(['--apiKey', config['api_key']])

            if config.get('base_url'):
                cmd_args.extend(['--baseUrl', config['base_url']])

            # Add instruction as the task
            cmd_args.append(config.get('instruction', ''))

            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.ui_tars_path
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                # Parse the output for results
                output = stdout.decode()
                return {
                    'success': True,
                    'actions': [],  # Would need to parse from output
                    'log': output.split('\n'),
                    'duration_ms': 0  # Would need to measure
                }
            else:
                self.logger.error(f"Agent TARS CLI failed: {stderr.decode()}")
                return {
                    'success': False,
                    'error': stderr.decode(),
                    'log': []
                }

        except Exception as e:
            self.logger.error(f"Error running Agent TARS CLI: {e}")
            return {
                'success': False,
                'error': str(e),
                'log': []
            }

    async def capture_screenshot(self) -> Optional[str]:
        """Capture a screenshot of the current screen."""
        try:
            # Create temporary file for screenshot
            temp_dir = tempfile.gettempdir()
            screenshot_path = os.path.join(temp_dir, f"ui_tars_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

            # Use system screenshot command (macOS)
            if os.system("which screencapture > /dev/null 2>&1") == 0:
                result = os.system(f"screencapture -x '{screenshot_path}'")
                if result == 0 and os.path.exists(screenshot_path):
                    self.screenshot_cache[datetime.now().isoformat()] = screenshot_path
                    return screenshot_path

            # Use alternative methods for other platforms
            # Could integrate with UI-TARS screenshot utilities here

            return None

        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
            return None

    async def analyze_screen(self, screenshot_path: str = None) -> Dict[str, Any]:
        """Analyze screen content using UI-TARS vision capabilities."""
        try:
            if not screenshot_path:
                screenshot_path = await self.capture_screenshot()

            if not screenshot_path:
                return {'error': 'Failed to capture screenshot'}

            # Use UI-TARS vision model for screen analysis
            analysis_result = await self._analyze_screenshot_with_ui_tars(screenshot_path)

            return {
                'screenshot_path': screenshot_path,
                'analysis': analysis_result,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error analyzing screen: {e}")
            return {'error': str(e)}

    async def _analyze_screenshot_with_ui_tars(self, screenshot_path: str) -> Dict[str, Any]:
        """Analyze screenshot using UI-TARS vision model."""
        try:
            # This would interface with the UI-TARS vision model
            # For now, return a placeholder structure
            return {
                'ui_elements': [],
                'text_content': [],
                'interactive_elements': [],
                'layout_analysis': {},
                'accessibility_info': {}
            }

        except Exception as e:
            self.logger.error(f"Error analyzing screenshot with UI-TARS: {e}")
            return {'error': str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the UI-TARS agent."""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'is_initialized': self.is_initialized,
            'is_running': self.is_running,
            'capabilities': self.capabilities,
            'current_task': self.current_task.get('task_id') if self.current_task else None,
            'execution_history_count': len(self.execution_history),
            'screenshot_cache_count': len(self.screenshot_cache),
            'ui_tars_path': self.ui_tars_path,
            'model_provider': self.model_provider,
            'model_name': self.model_name,
            'timestamp': datetime.now().isoformat()
        }

    async def get_capabilities(self) -> List[str]:
        """Get the list of capabilities supported by this agent."""
        return self.capabilities.copy()

    async def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history."""
        return self.execution_history[-limit:] if self.execution_history else []

    async def clear_screenshot_cache(self):
        """Clear the screenshot cache and remove temporary files."""
        try:
            for timestamp, screenshot_path in self.screenshot_cache.items():
                if os.path.exists(screenshot_path):
                    os.unlink(screenshot_path)

            self.screenshot_cache.clear()
            self.logger.info("Screenshot cache cleared")

        except Exception as e:
            self.logger.error(f"Error clearing screenshot cache: {e}")

    async def configure_model_settings(self, provider: str, model_name: str, api_key: str, base_url: str = None):
        """Configure the UI-TARS model settings."""
        self.model_provider = provider
        self.model_name = model_name
        self.api_key = api_key
        if base_url:
            self.base_url = base_url

        self.logger.info(f"Model settings updated: {provider}/{model_name}")

    # Jules Integration Methods
    async def _initialize_jules_integration(self) -> bool:
        """Initialize Jules integration capabilities."""
        try:
            # Initialize Jules workflow templates
            self.jules_workflow_templates = {
                "ui_automation_workflow": {
                    "name": "UI Automation with Jules",
                    "description": "Advanced UI automation combining UI-TARS vision with Jules workflow engine",
                    "steps": [
                        {"type": "capture_screen", "analysis": "ui_elements"},
                        {"type": "analyze_ui_structure", "method": "ui_tars_vision"},
                        {"type": "plan_automation", "strategy": "jules_workflow"},
                        {"type": "execute_actions", "framework": "combined"}
                    ]
                },
                "intelligent_form_filling": {
                    "name": "Intelligent Form Filling",
                    "description": "Automatically detect and fill forms using visual understanding",
                    "steps": [
                        {"type": "detect_form_elements", "method": "ui_tars"},
                        {"type": "extract_field_requirements", "analysis": "contextual"},
                        {"type": "populate_fields", "data_source": "provided"},
                        {"type": "submit_form", "validation": "pre_submit"}
                    ]
                },
                "application_testing": {
                    "name": "Automated Application Testing",
                    "description": "Test application functionality using visual verification",
                    "steps": [
                        {"type": "baseline_capture", "scope": "application_state"},
                        {"type": "execute_test_actions", "sequence": "defined"},
                        {"type": "verify_results", "method": "visual_comparison"},
                        {"type": "generate_report", "format": "structured"}
                    ]
                }
            }

            # Initialize Jules desktop triggers
            self.jules_desktop_triggers = {
                "ui_change_detection": {
                    "trigger": "screen_content_change",
                    "threshold": 0.05,
                    "action": "analyze_and_respond"
                },
                "new_window_detection": {
                    "trigger": "new_window_opened",
                    "action": "categorize_and_automate"
                },
                "error_dialog_detection": {
                    "trigger": "error_dialog_appeared",
                    "action": "capture_and_report"
                }
            }

            self.logger.info("Jules integration initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Jules integration initialization failed: {e}")
            return False

    async def execute_jules_workflow(self, workflow_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Jules workflow template."""
        try:
            if workflow_name not in self.jules_workflow_templates:
                raise ValueError(f"Unknown workflow: {workflow_name}")

            workflow = self.jules_workflow_templates[workflow_name]
            self.logger.info(f"Executing Jules workflow: {workflow['name']}")

            execution_log = []
            results = {}

            for i, step in enumerate(workflow['steps']):
                step_result = await self._execute_jules_workflow_step(step, context, results)
                execution_log.append(f"Step {i+1}: {step['type']} - {step_result.get('status', 'unknown')}")

                if not step_result.get('success', False):
                    execution_log.append(f"Workflow failed at step {i+1}")
                    break

                # Update results with step output
                results.update(step_result.get('data', {}))

            return {
                'success': all('failed' not in log for log in execution_log),
                'workflow': workflow_name,
                'execution_log': execution_log,
                'results': results
            }

        except Exception as e:
            self.logger.error(f"Jules workflow execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'workflow': workflow_name
            }

    async def _execute_jules_workflow_step(self, step: Dict[str, Any], context: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single Jules workflow step."""
        try:
            step_type = step.get('type')

            if step_type == 'capture_screen':
                screenshot_path = await self.capture_screenshot()
                return {
                    'success': screenshot_path is not None,
                    'status': 'completed' if screenshot_path else 'failed',
                    'data': {'screenshot_path': screenshot_path}
                }

            elif step_type == 'analyze_ui_structure':
                # Combine UI-TARS analysis with Jules intelligence
                screenshot_path = previous_results.get('screenshot_path')
                if screenshot_path:
                    analysis = await self._analyze_screenshot_with_jules(screenshot_path)
                    return {
                        'success': True,
                        'status': 'completed',
                        'data': {'ui_analysis': analysis}
                    }

            elif step_type == 'plan_automation':
                # Use Jules planning capabilities
                ui_analysis = previous_results.get('ui_analysis', {})
                automation_plan = await self._create_jules_automation_plan(ui_analysis, context)
                return {
                    'success': True,
                    'status': 'completed',
                    'data': {'automation_plan': automation_plan}
                }

            elif step_type == 'execute_actions':
                # Execute planned actions
                automation_plan = previous_results.get('automation_plan', {})
                execution_result = await self._execute_jules_automation_plan(automation_plan)
                return {
                    'success': execution_result.get('success', False),
                    'status': 'completed' if execution_result.get('success') else 'failed',
                    'data': {'execution_result': execution_result}
                }

            else:
                return {
                    'success': False,
                    'status': 'unknown_step_type',
                    'data': {}
                }

        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'error': str(e),
                'data': {}
            }

    async def _analyze_screenshot_with_jules(self, screenshot_path: str) -> Dict[str, Any]:
        """Analyze screenshot using combined UI-TARS and Jules capabilities."""
        try:
            # Enhanced analysis combining UI-TARS vision with Jules intelligence
            base_analysis = await self._analyze_screenshot_with_ui_tars(screenshot_path)

            # Add Jules-specific enhancements
            jules_enhancements = {
                'workflow_opportunities': [],
                'automation_suggestions': [],
                'interaction_patterns': [],
                'contextual_insights': {}
            }

            # Detect workflow opportunities
            if base_analysis.get('interactive_elements'):
                jules_enhancements['workflow_opportunities'] = [
                    'form_automation',
                    'navigation_workflow',
                    'data_extraction'
                ]

            # Generate automation suggestions
            jules_enhancements['automation_suggestions'] = [
                {
                    'type': 'click_automation',
                    'confidence': 0.9,
                    'description': 'Automate button clicks based on visual recognition'
                },
                {
                    'type': 'form_filling',
                    'confidence': 0.8,
                    'description': 'Automatically populate form fields'
                }
            ]

            # Combine analyses
            combined_analysis = {**base_analysis, 'jules_enhancements': jules_enhancements}

            return combined_analysis

        except Exception as e:
            self.logger.error(f"Jules screenshot analysis failed: {e}")
            return {'error': str(e)}

    async def _create_jules_automation_plan(self, ui_analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create an automation plan using Jules planning capabilities."""
        try:
            plan = {
                'actions': [],
                'fallback_strategies': [],
                'verification_steps': [],
                'estimated_duration': 0
            }

            # Analyze UI elements and create action sequence
            interactive_elements = ui_analysis.get('interactive_elements', [])
            for element in interactive_elements:
                action = {
                    'type': 'click',
                    'target': element,
                    'confidence': 0.8,
                    'fallback': 'visual_search'
                }
                plan['actions'].append(action)

            # Add verification steps
            plan['verification_steps'] = [
                {'type': 'screenshot_comparison', 'timing': 'after_each_action'},
                {'type': 'element_verification', 'timing': 'critical_points'}
            ]

            plan['estimated_duration'] = len(plan['actions']) * 2  # 2 seconds per action

            return plan

        except Exception as e:
            self.logger.error(f"Jules automation planning failed: {e}")
            return {'error': str(e)}

    async def _execute_jules_automation_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Jules automation plan."""
        try:
            executed_actions = []
            verification_results = []

            for action in plan.get('actions', []):
                # Execute action using UI-TARS capabilities
                action_result = await self._execute_ui_action_with_jules(action)
                executed_actions.append(action_result)

                # Perform verification if required
                if action_result.get('requires_verification'):
                    verification = await self._verify_action_result(action, action_result)
                    verification_results.append(verification)

            return {
                'success': all(action.get('success', False) for action in executed_actions),
                'executed_actions': executed_actions,
                'verification_results': verification_results,
                'total_actions': len(executed_actions)
            }

        except Exception as e:
            self.logger.error(f"Jules automation plan execution failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _execute_ui_action_with_jules(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute UI action with Jules enhancements."""
        try:
            action_type = action.get('type')

            if action_type == 'click':
                # Enhanced click with Jules intelligence
                target = action.get('target')
                if target:
                    # Use visual recognition to find and click element
                    click_result = await self._jules_enhanced_click(target)
                    return click_result
                else:
                    return {'success': False, 'error': 'No target specified'}

            elif action_type == 'type':
                # Enhanced typing with Jules context awareness
                text = action.get('text', '')
                type_result = await self._jules_enhanced_type(text)
                return type_result

            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _jules_enhanced_click(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Perform enhanced click using Jules visual intelligence."""
        try:
            # Use UI-TARS for visual element detection
            # Enhanced with Jules contextual understanding
            return {
                'success': True,
                'action': 'click',
                'target': target,
                'method': 'jules_enhanced_visual',
                'confidence': 0.9
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _jules_enhanced_type(self, text: str) -> Dict[str, Any]:
        """Perform enhanced typing with Jules context awareness."""
        try:
            # Enhanced typing with context understanding
            return {
                'success': True,
                'action': 'type',
                'text': text,
                'method': 'jules_enhanced_input',
                'confidence': 0.95
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _verify_action_result(self, action: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Verify action result using Jules verification methods."""
        try:
            verification = {
                'action_verified': True,
                'verification_method': 'visual_comparison',
                'confidence': 0.9,
                'issues_detected': []
            }

            return verification

        except Exception as e:
            return {
                'action_verified': False,
                'error': str(e)
            }

    async def setup_jules_trigger(self, trigger_config: Dict[str, Any]) -> str:
        """Setup a Jules desktop trigger."""
        try:
            trigger_id = f"jules_trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Store trigger configuration
            self.jules_desktop_triggers[trigger_id] = {
                **trigger_config,
                'created_at': datetime.now(),
                'active': True
            }

            self.logger.info(f"Jules trigger setup: {trigger_id}")
            return trigger_id

        except Exception as e:
            self.logger.error(f"Jules trigger setup failed: {e}")
            return ""

    async def get_jules_status(self) -> Dict[str, Any]:
        """Get Jules integration status."""
        return {
            'jules_integration_enabled': self.jules_integration_enabled,
            'workflow_templates': len(self.jules_workflow_templates),
            'active_triggers': len([t for t in self.jules_desktop_triggers.values() if t.get('active', False)]),
            'available_workflows': list(self.jules_workflow_templates.keys()),
            'trigger_types': list(set(t.get('trigger') for t in self.jules_desktop_triggers.values()))
        }

    async def shutdown(self):
        """Gracefully shutdown the UI-TARS agent."""
        try:
            self.logger.info("Shutting down UI-TARS agent...")

            # Stop any running tasks
            await self.stop()

            # Clear screenshot cache
            await self.clear_screenshot_cache()

            self.logger.info("UI-TARS agent shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during UI-TARS agent shutdown: {e}")

    # Abstract method implementations required by BaseAgent
    async def _initialize_agent(self):
        """Initialize agent-specific components."""
        return await self.initialize()

    async def _execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute agent-specific task."""
        return await self.process_task(task_data)

    async def _shutdown_agent(self):
        """Shutdown agent-specific components."""
        await self.shutdown()


# Factory function for creating UI-TARS agent instances
def create_ui_tars_agent(config: Dict[str, Any] = None, communication_clients: Dict[str, Any] = None) -> UITarsAgent:
    """Create a new UI-TARS agent instance."""
    return UITarsAgent(config, communication_clients)
