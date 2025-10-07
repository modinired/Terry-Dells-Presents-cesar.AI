#!/usr/bin/env python3
"""
Screen Recorder for Terry Delmonaco Manager Agent
Handles screen activity monitoring and analysis with UI-TARS integration.
"""

import asyncio
import logging
import os
import platform
import shutil
import tempfile
from asyncio.subprocess import PIPE
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from ..utils.metrics import metrics

try:  # Optional dependency for better resolution detection
    import tkinter  # type: ignore
except Exception:  # pragma: no cover - best effort optional import
    tkinter = None

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..utils.config import Config


class ScreenRecorder:
    """
    Manages screen activity monitoring and analysis with UI-TARS integration.
    Enhanced with vision-language model capabilities for advanced screen understanding.
    """

    def __init__(self, config: Optional["Config"] = None, ui_tars_agent=None):
        self.logger = logging.getLogger("screen_recorder")
        self.is_recording = False
        self.config = config
        self.recording_interval = (
            int(getattr(config.screen_recording, "interval_seconds", 20))
            if config
            else 20
        )
        self.last_capture = None
        self.ui_tars_agent = ui_tars_agent
        self.ui_tars_path = self._resolve_ui_tars_path(config)
        self.screenshot_cache = {}
        self.analysis_history = []
        self._platform = platform.system().lower()

    def _resolve_ui_tars_path(self, config: Optional["Config"]) -> Optional[Path]:
        """Resolve the UI-TARS installation directory from config or defaults."""
        candidates = []
        if config and config.ui_tars.install_path:
            candidates.append(Path(config.ui_tars.install_path).expanduser())

        # Common fallback locations
        candidates.extend(
            [
                Path.cwd() / "UI-TARS-desktop",
                Path.home() / "UI-TARS-desktop",
            ]
        )

        for candidate in candidates:
            if candidate and candidate.exists():
                return candidate
        return None

    async def initialize(self, ui_tars_agent=None):
        """Initialize the screen recorder with optional UI-TARS integration."""
        try:
            self.logger.info("Initializing enhanced screen recorder with UI-TARS integration...")

            # Set UI-TARS agent reference if provided
            if ui_tars_agent:
                self.ui_tars_agent = ui_tars_agent

            # Check if screen recording is supported
            await self._check_capabilities()

            # Check UI-TARS availability for enhanced analysis
            await self._check_ui_tars_integration()

            self.logger.info("Enhanced screen recorder initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Screen recorder initialization failed: {e}")
            return False
    
    async def _check_capabilities(self):
        """Check screen recording capabilities."""
        try:
            # Check if screencapture is available (macOS)
            if os.system("which screencapture > /dev/null 2>&1") == 0:
                self.logger.info("macOS screencapture capability detected")
                return True

            # Check other platform capabilities
            self.logger.info("Basic screen recording capabilities verified")
            return True

        except Exception as e:
            self.logger.error(f"Failed to check screen recording capabilities: {e}")
            return False

    async def _check_ui_tars_integration(self):
        """Check UI-TARS integration availability."""
        try:
            if self.ui_tars_agent:
                self.logger.info("UI-TARS agent integration available")
                return True

            # Check if UI-TARS is available in the system
            if self.ui_tars_path and self.ui_tars_path.exists():
                self.logger.info("UI-TARS directory found - enhanced analysis available")
                return True

            self.logger.info("UI-TARS integration not available - using basic analysis")
            return False

        except Exception as e:
            self.logger.error(f"Failed to check UI-TARS integration: {e}")
            return False
    
    async def start_recording(self):
        """Start screen recording."""
        try:
            self.is_recording = True
            self.logger.info("Screen recording started")
            
        except Exception as e:
            self.logger.error(f"Failed to start screen recording: {e}")
    
    async def stop_recording(self):
        """Stop screen recording."""
        try:
            self.is_recording = False
            self.logger.info("Screen recording stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop screen recording: {e}")
    
    async def capture_screen(self) -> Dict:
        """Capture current screen activity with enhanced UI-TARS capabilities."""
        try:
            self.logger.info("Capturing screen activity...")
            await metrics.incr("screen_recorder.capture_requests")

            # Create temporary screenshot file
            temp_dir = tempfile.gettempdir()
            screenshot_path = os.path.join(temp_dir, f"screen_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

            # Capture screenshot
            success = await self._take_screenshot(screenshot_path)

            if success:
                # Store in cache
                timestamp = datetime.now().isoformat()
                self.screenshot_cache[timestamp] = screenshot_path

                capture_data = {
                    "timestamp": timestamp,
                    "activity_type": "screen_capture",
                    "screenshot_path": screenshot_path,
                    "data": {
                        "resolution": await self._get_screen_resolution(),
                        "active_window": await self._get_active_window(),
                        "capture_method": "enhanced_ui_tars" if self.ui_tars_agent else "basic"
                    }
                }

                self.last_capture = capture_data
                await metrics.add_event(
                    "screen_recorder.capture_success",
                    1,
                    metadata={"path": screenshot_path},
                )
                return capture_data
            else:
                return {
                    "status": "error",
                    "message": "Failed to capture screenshot"
                }

        except Exception as e:
            self.logger.error(f"Screen capture failed: {e}")
            await metrics.incr("screen_recorder.capture_errors")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _take_screenshot(self, output_path: str) -> bool:
        """Take a screenshot and save to specified path."""
        try:
            # Use macOS screencapture if available
            if shutil.which("screencapture"):
                process = await asyncio.create_subprocess_exec(
                    "screencapture",
                    "-x",
                    output_path,
                )
                await process.communicate()
                return process.returncode == 0 and Path(output_path).exists()

            # Could add other platform support here
            return False

        except Exception as e:
            self.logger.error(f"Screenshot capture failed: {e}")
            return False

    async def _get_screen_resolution(self) -> str:
        """Get current screen resolution."""
        try:
            if tkinter:
                def _fetch_resolution() -> str:
                    root = tkinter.Tk()
                    root.withdraw()
                    width = root.winfo_screenwidth()
                    height = root.winfo_screenheight()
                    root.destroy()
                    return f"{width}x{height}"

                return await asyncio.to_thread(_fetch_resolution)

            # Fallback to environment variable / default if tkinter unavailable
            return os.getenv("SCREEN_RESOLUTION", "unknown")
        except Exception:
            return "unknown"

    async def _get_active_window(self) -> str:
        """Get active window information."""
        try:
            if self._platform == "darwin" and shutil.which("osascript"):
                script = "tell application \"System Events\" to get name of first application process whose frontmost is true"
                process = await asyncio.create_subprocess_exec(
                    "osascript",
                    "-e",
                    script,
                    stdout=PIPE,
                    stderr=PIPE,
                )
                stdout, _ = await process.communicate()
                if process.returncode == 0:
                    return stdout.decode().strip()

            return "unknown"
        except Exception:
            return "unknown"
    
    async def analyze_activity(self, capture_data: Dict) -> Dict:
        """Analyze captured screen activity using UI-TARS enhanced capabilities."""
        try:
            self.logger.info("Analyzing screen activity with UI-TARS enhancement...")

            screenshot_path = capture_data.get('screenshot_path')
            if not screenshot_path or not os.path.exists(screenshot_path):
                return await self._basic_activity_analysis(capture_data)

            # Enhanced analysis using UI-TARS if available
            if self.ui_tars_agent:
                analysis = await self._ui_tars_enhanced_analysis(screenshot_path, capture_data)
            else:
                analysis = await self._vision_based_analysis(screenshot_path, capture_data)

            # Store analysis in history
            self.analysis_history.append(analysis)
            if len(self.analysis_history) > 50:
                self.analysis_history = self.analysis_history[-50:]
            await metrics.incr("screen_recorder.analysis_runs")

            return analysis

        except Exception as e:
            self.logger.error(f"Activity analysis failed: {e}")
            await metrics.incr("screen_recorder.analysis_errors")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _ui_tars_enhanced_analysis(self, screenshot_path: str, capture_data: Dict) -> Dict:
        """Perform enhanced analysis using UI-TARS agent."""
        try:
            self.logger.info("Performing UI-TARS enhanced screen analysis...")

            # Use UI-TARS agent for advanced screen analysis
            ui_analysis = await self.ui_tars_agent.analyze_screen(screenshot_path)

            analysis = {
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "ui_tars_enhanced",
                "screenshot_path": screenshot_path,
                "ui_tars_analysis": ui_analysis.get('analysis', {}),
                "findings": [],
                "recommendations": [],
                "ui_elements": ui_analysis.get('analysis', {}).get('ui_elements', []),
                "text_content": ui_analysis.get('analysis', {}).get('text_content', []),
                "interactive_elements": ui_analysis.get('analysis', {}).get('interactive_elements', []),
                "confidence": 0.95  # High confidence with UI-TARS
            }

            # Generate insights based on UI-TARS analysis
            analysis["findings"] = await self._generate_insights_from_ui_tars(ui_analysis)
            analysis["recommendations"] = await self._generate_recommendations_from_ui_tars(ui_analysis)

            return analysis

        except Exception as e:
            self.logger.error(f"UI-TARS enhanced analysis failed: {e}")
            return await self._basic_activity_analysis(capture_data)

    async def _vision_based_analysis(self, screenshot_path: str, capture_data: Dict) -> Dict:
        """Perform vision-based analysis without UI-TARS agent."""
        try:
            self.logger.info("Performing vision-based screen analysis...")

            # Basic vision analysis (could integrate with other vision models)
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "vision_based",
                "screenshot_path": screenshot_path,
                "findings": [
                    {
                        "type": "screen_activity",
                        "confidence": 0.7,
                        "description": "Screen activity detected"
                    }
                ],
                "recommendations": [
                    "Consider using UI-TARS for enhanced analysis capabilities"
                ],
                "confidence": 0.7
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Vision-based analysis failed: {e}")
            return await self._basic_activity_analysis(capture_data)

    async def _basic_activity_analysis(self, capture_data: Dict) -> Dict:
        """Perform basic activity analysis as fallback."""
        try:
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "basic",
                "findings": [
                    {
                        "type": "basic_activity",
                        "confidence": 0.5,
                        "description": "Basic screen activity detected"
                    }
                ],
                "recommendations": [
                    "Enable UI-TARS integration for enhanced analysis"
                ],
                "confidence": 0.5
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Basic activity analysis failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _generate_insights_from_ui_tars(self, ui_analysis: Dict) -> List[Dict]:
        """Generate insights from UI-TARS analysis results."""
        try:
            findings = []

            # Analyze UI elements
            ui_elements = ui_analysis.get('analysis', {}).get('ui_elements', [])
            if ui_elements:
                findings.append({
                    "type": "ui_interaction",
                    "confidence": 0.9,
                    "description": f"Detected {len(ui_elements)} interactive UI elements",
                    "details": {"element_count": len(ui_elements)}
                })

            # Analyze text content
            text_content = ui_analysis.get('analysis', {}).get('text_content', [])
            if text_content:
                findings.append({
                    "type": "text_analysis",
                    "confidence": 0.85,
                    "description": f"Identified text content on screen",
                    "details": {"text_elements": len(text_content)}
                })

            return findings

        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return []

    async def _generate_recommendations_from_ui_tars(self, ui_analysis: Dict) -> List[str]:
        """Generate recommendations from UI-TARS analysis results."""
        try:
            recommendations = []

            # Add recommendations based on analysis
            interactive_elements = ui_analysis.get('analysis', {}).get('interactive_elements', [])
            if len(interactive_elements) > 10:
                recommendations.append("Many interactive elements detected - consider using automation for repetitive tasks")

            if not interactive_elements:
                recommendations.append("No interactive elements detected - user may be viewing content")

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Enable detailed logging for better recommendations"]
    
    async def get_status(self) -> Dict:
        """Get enhanced screen recorder status with UI-TARS integration info."""
        return {
            "is_recording": self.is_recording,
            "recording_interval": self.recording_interval,
            "last_capture": self.last_capture["timestamp"] if self.last_capture else None,
            "ui_tars_integration": self.ui_tars_agent is not None,
            "screenshot_cache_count": len(self.screenshot_cache),
            "analysis_history_count": len(self.analysis_history),
            "capabilities": [
                "screen_capture",
                "ui_tars_analysis" if self.ui_tars_agent else "basic_analysis",
                "vision_based_insights",
                "activity_monitoring"
            ]
        }
    
    async def capture_and_analyze(self) -> Dict:
        """Capture screen activity and analyze it with UI-TARS enhancement."""
        try:
            self.logger.info("Starting enhanced capture and analysis cycle...")
            await metrics.incr("screen_recorder.capture_analyze_cycles")

            # Capture screen with enhanced capabilities
            capture_data = await self.capture_screen()

            if capture_data.get("status") == "error":
                return capture_data

            # Analyze the captured data with UI-TARS enhancement
            analysis = await self.analyze_activity(capture_data)

            result = {
                "capture": capture_data,
                "analysis": analysis,
                "enhancement_level": "ui_tars" if self.ui_tars_agent else "basic",
                "timestamp": datetime.now().isoformat()
            }

            # Clean up old cache entries periodically
            await self._cleanup_cache()

            return result

        except Exception as e:
            self.logger.error(f"Enhanced capture and analyze failed: {e}")
            await metrics.incr("screen_recorder.capture_analyze_errors")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _cleanup_cache(self):
        """Clean up old screenshot cache entries."""
        try:
            # Keep only last 10 screenshots to prevent disk space issues
            if len(self.screenshot_cache) > 10:
                # Sort by timestamp and remove oldest
                sorted_cache = sorted(self.screenshot_cache.items())
                for timestamp, screenshot_path in sorted_cache[:-10]:
                    if os.path.exists(screenshot_path):
                        os.unlink(screenshot_path)
                    del self.screenshot_cache[timestamp]

            # Keep only last 50 analysis entries
            if len(self.analysis_history) > 50:
                self.analysis_history = self.analysis_history[-50:]

        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {e}")

    async def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """Get recent analysis history."""
        return self.analysis_history[-limit:] if self.analysis_history else []

    async def set_ui_tars_agent(self, ui_tars_agent):
        """Set or update the UI-TARS agent reference."""
        self.ui_tars_agent = ui_tars_agent
        self.logger.info("UI-TARS agent reference updated")

    async def trigger_enhanced_analysis(self, instruction: str = "Analyze current screen") -> Dict:
        """Trigger an enhanced analysis with specific instruction."""
        try:
            if not self.ui_tars_agent:
                return {
                    "status": "error",
                    "message": "UI-TARS agent not available for enhanced analysis"
                }

            # Capture current screen
            capture_data = await self.capture_screen()
            if capture_data.get("status") == "error":
                return capture_data

            # Use UI-TARS for enhanced task-specific analysis
            screenshot_path = capture_data.get('screenshot_path')
            if screenshot_path:
                task_result = await self.ui_tars_agent.process_task({
                    'instruction': instruction,
                    'screenshot_path': screenshot_path,
                    'task_type': 'screen_analysis'
                })

                return {
                    "status": "completed",
                    "capture": capture_data,
                    "enhanced_analysis": task_result,
                    "instruction": instruction,
                    "timestamp": datetime.now().isoformat()
                }

            return {
                "status": "error",
                "message": "Failed to capture screenshot for enhanced analysis"
            }

        except Exception as e:
            self.logger.error(f"Enhanced analysis failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            } 
    
    async def shutdown(self):
        """Shutdown the enhanced screen recorder with UI-TARS integration."""
        try:
            await self.stop_recording()

            # Clean up screenshot cache
            for timestamp, screenshot_path in self.screenshot_cache.items():
                try:
                    if os.path.exists(screenshot_path):
                        os.unlink(screenshot_path)
                except Exception as e:
                    self.logger.warning(f"Failed to clean up screenshot {screenshot_path}: {e}")

            self.screenshot_cache.clear()
            self.analysis_history.clear()

            self.logger.info("Enhanced screen recorder shutdown complete")

        except Exception as e:
            self.logger.error(f"Screen recorder shutdown error: {e}") 
