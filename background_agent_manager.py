#!/usr/bin/env python3
"""
Background Agent Manager for Terry Delmonaco Manager Agent
Handles the execution and coordination of background agents for code auditing and monitoring.
"""

import asyncio
import json
import logging
import os
from asyncio.subprocess import PIPE
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..utils.metrics import metrics


class BackgroundAgentManager:
    """
    Manages background agents for continuous code auditing and monitoring.
    """
    
    def __init__(self):
        self.config_file = str(Path(__file__).resolve().parent.parent / "background_agents_config.json")
        data_dir = Path(os.getenv("CESAR_DATA_DIR", Path.cwd()))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = data_dir / ".memory.json"
        self.audit_findings_file = data_dir / ".audit_findings.json"
        self.background_agents = {}
        self.is_running = False
        self._tasks: List[asyncio.Task] = []
        self._repo_root = Path(os.getenv("CESAR_REPO_ROOT", Path.cwd()))
        self._intervals = {
            "super_audit_seconds": 300,
            "agent_cycle_seconds": 600,
        }
        self._safety = {
            "allow_git_mutations": False,
            "dry_run": True,
            "max_parallel_analyses": 2,
        }
        self.logger = logging.getLogger("background_agent_manager")
        
    async def initialize(self):
        """Initialize the background agent manager."""
        try:
            self.logger.info("Initializing background agent manager...")
            
            # Load configuration
            if not await self._load_config():
                self.logger.error("Failed to load background agent configuration")
                return False
            
            # Initialize background agents
            await self._initialize_background_agents()
            
            self.logger.info("Background agent manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Background agent manager initialization failed: {e}")
            return False
    
    async def _load_config(self) -> bool:
        """Load background agent configuration."""
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                self.logger.error(f"Configuration file not found: {self.config_file}")
                return False
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if "backgroundAgents" not in config:
                self.logger.error("Invalid configuration: missing backgroundAgents section")
                return False
            
            self.config = config["backgroundAgents"]
            self._intervals.update(self.config.get("intervals", {}))
            self._safety.update(self.config.get("safety", {}))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    async def _initialize_background_agents(self):
        """Initialize all background agents."""
        if not self.config.get("enabled", False):
            self.logger.info("Background agents are disabled")
            return
        
        agents_config = self.config.get("agents", {})
        
        for agent_name, agent_config in agents_config.items():
            if agent_config.get("enabled", False):
                self.background_agents[agent_name] = {
                    "config": agent_config,
                    "status": "initialized",
                    "last_run": None,
                    "findings_count": 0
                }
                self.logger.info(f"Initialized background agent: {agent_name}")
    
    async def start(self):
        """Start the background agent manager."""
        if not self.config.get("enabled", False):
            self.logger.info("Background agents are disabled")
            return

        if self.is_running:
            self.logger.debug("Background agent manager already running")
            return

        self.is_running = True
        self.logger.info("Starting background agent manager...")
        self._tasks = [
            asyncio.create_task(self._super_audit_coordinator_loop(), name="super_audit_coordinator"),
            asyncio.create_task(self._background_agents_loop(), name="background_agents_runner"),
        ]
        await metrics.incr("background_agents.started")

    async def _super_audit_coordinator_loop(self):
        """Run the SuperAuditCoordinator agent."""
        interval = max(30, int(self._intervals.get("super_audit_seconds", 300)))

        while self.is_running:
            try:
                if "SuperAuditCoordinator" in self.background_agents:
                    await self._run_audit_coordinator()
                    await metrics.incr("background_agents.super_audit_runs")
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"SuperAuditCoordinator error: {e}")
                await asyncio.sleep(min(60, interval))

    async def _background_agents_loop(self):
        """Run other background agents."""
        interval = max(60, int(self._intervals.get("agent_cycle_seconds", 600)))

        while self.is_running:
            try:
                changed_files = await self._get_changed_files()
                if not changed_files:
                    await asyncio.sleep(interval)
                    continue

                for agent_name, agent_info in self.background_agents.items():
                    if agent_name != "SuperAuditCoordinator":
                        await self._run_background_agent(agent_name, agent_info, changed_files)
                        await metrics.incr("background_agents.agent_runs")

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Background agents error: {e}")
                await asyncio.sleep(min(60, interval))

    async def stop(self):
        """Stop background agents and cancel running tasks."""
        if not self.is_running:
            return

        self.is_running = False
        for task in list(self._tasks):
            task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        self._tasks.clear()
        await metrics.incr("background_agents.stopped")
    
    async def _run_audit_coordinator(self):
        """Run the SuperAuditCoordinator agent."""
        try:
            self.logger.info("Running SuperAuditCoordinator audit...")
            
            # Check git repository status
            git_status = await self._run_git_command("git status")
            
            # Get changed files
            changed_files = await self._get_changed_files()
            
            if changed_files:
                self.logger.info(f"Found {len(changed_files)} changed files")
                
                # Delegate to specialized agents
                await self._delegate_to_agents(changed_files)
                
                # Compile findings
                await self._compile_findings()
                await metrics.incr("background_agents.audit_cycles")
            
            # Update agent status
            self.background_agents["SuperAuditCoordinator"]["last_run"] = datetime.now()
            self.background_agents["SuperAuditCoordinator"]["findings_count"] += 1
            
        except Exception as e:
            self.logger.error(f"SuperAuditCoordinator audit failed: {e}")
    
    async def _run_background_agent(self, agent_name: str, agent_info: Dict, files: List[str]):
        """Run a specific background agent."""
        try:
            self.logger.info(f"Running {agent_name}...")
            limited_files = files[: int(self._safety.get("max_parallel_analyses", len(files)))]

            if limited_files:
                findings = await self._run_agent_analysis(agent_name, limited_files)
                if findings:
                    await self._log_findings(agent_name, findings)

            # Update agent status
            agent_info["last_run"] = datetime.now()
            agent_info["findings_count"] += 1
            
        except Exception as e:
            self.logger.error(f"{agent_name} failed: {e}")
    
    async def _run_git_command(self, command: str) -> str:
        """Run a git command asynchronously with safety checks."""
        command = command.strip()

        if not self._is_git_command_allowed(command):
            self.logger.warning(f"Blocked git command due to safety policy: {command}")
            await metrics.incr("background_agents.git_command_blocked")
            return ""

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=PIPE,
                stderr=PIPE,
                cwd=str(self._repo_root),
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                self.logger.error(
                    "Git command failed: %s | stderr=%s",
                    command,
                    stderr.decode().strip(),
                )
                await metrics.incr("background_agents.git_command_error")
                return ""

            return stdout.decode().strip()
        except Exception as e:
            self.logger.error(f"Git command failed: {e}")
            await metrics.incr("background_agents.git_command_exception")
            return ""

    def _is_git_command_allowed(self, command: str) -> bool:
        safe_prefixes = (
            "git status",
            "git status --porcelain",
            "git remote -v",
        )

        if any(command.startswith(prefix) for prefix in safe_prefixes):
            return True

        return bool(self._safety.get("allow_git_mutations"))
    
    async def _get_changed_files(self) -> List[str]:
        """Get list of changed files."""
        try:
            # Use git status --porcelain for changed files
            output = await self._run_git_command("git status --porcelain")
            
            if not output:
                return []
            
            files = []
            for line in output.split('\n'):
                if line.strip():
                    # Extract filename from git status output
                    parts = line.split()
                    if len(parts) >= 2:
                        filename = parts[1]
                        if filename and not filename.startswith('.'):
                            # Only include files in the current directory (not parent directories)
                            if '/' not in filename or filename.startswith('./'):
                                # Remove ./ prefix if present
                                if filename.startswith('./'):
                                    filename = filename[2:]
                                files.append(filename)
            
            self.logger.info(f"Found changed files: {files}")
            await metrics.set_gauge("background_agents.changed_files", len(files))
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to get changed files: {e}")
            return []
    
    async def _delegate_to_agents(self, files: List[str]):
        """Delegate files to specialized agents."""
        for agent_name in ["BugHunter", "DocChecker", "SecuritySentinel"]:
            if agent_name in self.background_agents:
                findings = await self._run_agent_analysis(agent_name, files)
                if findings:
                    await self._log_findings(agent_name, findings)
    
    async def _run_agent_analysis(self, agent_name: str, files: List[str]) -> List[Dict]:
        """Run analysis for a specific agent."""
        findings = []
        
        self.logger.info(f"{agent_name} analyzing {len(files)} files")
        
        for file_path in files:
            if file_path.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c")):
                source_path = (self._repo_root / file_path).resolve()

                if not source_path.exists():
                    self.logger.error(f"File not found: {source_path}")
                    continue
                    
                try:
                    self.logger.info(f"{agent_name} analyzing: {file_path}")
                    # Read file content
                    content = await asyncio.to_thread(source_path.read_text)
                    
                    # Agent-specific analysis
                    if agent_name == "BugHunter":
                        findings.extend(await self._analyze_bugs(file_path, content))
                    elif agent_name == "DocChecker":
                        findings.extend(await self._analyze_documentation(file_path, content))
                    elif agent_name == "SecuritySentinel":
                        findings.extend(await self._analyze_security(file_path, content))
                        
                except Exception as e:
                    self.logger.error(f"Failed to analyze {file_path}: {e}")
        
        return findings
    
    async def _analyze_bugs(self, file_path: str, content: str) -> List[Dict]:
        """Analyze file for bugs and code smells."""
        findings = []
        
        # Enhanced bug detection patterns
        bug_patterns = [
            ("print statement", "print("),
            ("TODO comment", "TODO"),
            ("FIXME comment", "FIXME"),
            ("hardcoded localhost", "localhost"),
            ("hardcoded port", ":8000"),
            ("hardcoded database", "postgresql://"),
            ("unused import", "import json"),
            ("debug statement", "print("),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for issue_type, pattern in bug_patterns:
                if pattern.lower() in line.lower():
                    findings.append({
                        "type": "bug",
                        "severity": "medium",
                        "file": file_path,
                        "line": line_num,
                        "issue": issue_type,
                        "description": f"Found {issue_type} on line {line_num}: {line.strip()}",
                        "agent": "BugHunter",
                        "timestamp": datetime.now().isoformat()
                    })
        
        self.logger.info(f"BugHunter found {len(findings)} issues in {file_path}")
        return findings
    
    async def _analyze_documentation(self, file_path: str, content: str) -> List[Dict]:
        """Analyze file for documentation issues."""
        findings = []
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Check for functions without docstrings
            if line.strip().startswith('def ') and line_num < len(lines):
                # Check if next line has docstring
                next_line = lines[line_num] if line_num < len(lines) else ""
                if not next_line.strip().startswith('"""') and not next_line.strip().startswith("'''"):
                    findings.append({
                        "type": "doc",
                        "severity": "low",
                        "file": file_path,
                        "line": line_num,
                        "issue": "missing_docstring",
                        "description": f"Function on line {line_num} missing docstring",
                        "agent": "DocChecker",
                        "timestamp": datetime.now().isoformat()
                    })
        
        return findings
    
    async def _analyze_security(self, file_path: str, content: str) -> List[Dict]:
        """Analyze file for security issues."""
        findings = []
        
        # Enhanced security patterns to check
        security_patterns = [
            ("hardcoded_api_key", "sk-"),
            ("hardcoded_password", "password"),
            ("hardcoded_secret", "secret"),
            ("dangerous_eval", "eval("),
            ("dangerous_exec", "exec("),
            ("sql_injection", "SELECT *"),
            ("hardcoded_credentials", "postgresql://"),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for issue_type, pattern in security_patterns:
                if pattern.lower() in line.lower():
                    findings.append({
                        "type": "security",
                        "severity": "high",
                        "file": file_path,
                        "line": line_num,
                        "issue": issue_type,
                        "description": f"Security issue found on line {line_num}: {line.strip()}",
                        "agent": "SecuritySentinel",
                        "timestamp": datetime.now().isoformat()
                    })
        
        self.logger.info(f"SecuritySentinel found {len(findings)} security issues in {file_path}")
        return findings
    
    async def _log_findings(self, agent_name: str, findings: List[Dict]):
        """Log findings to memory file."""
        try:
            memory_path = Path(self.memory_file)

            def load_memory() -> Dict[str, Any]:
                if memory_path.exists():
                    return json.loads(memory_path.read_text())
                return {"findings": []}

            memory_data = await asyncio.to_thread(load_memory)
            memory_data.setdefault("findings", []).extend(findings)
            memory_data["last_updated"] = datetime.now().isoformat()

            await asyncio.to_thread(
                lambda: memory_path.write_text(json.dumps(memory_data, indent=2))
            )

            self.logger.info(f"{agent_name} logged {len(findings)} findings")
            await metrics.incr("background_agents.findings_logged", len(findings))
            await metrics.set_gauge("memory_manager.findings", len(memory_data.get("findings", [])))
            
        except Exception as e:
            self.logger.error(f"Failed to log findings: {e}")
    
    async def _compile_findings(self):
        """Compile findings into audit report."""
        try:
            memory_path = Path(self.memory_file)
            if not memory_path.exists():
                return

            def load_memory() -> Dict[str, Any]:
                return json.loads(memory_path.read_text())

            memory_data = await asyncio.to_thread(load_memory)
            findings = memory_data.get("findings", [])
            
            # Compile summary
            summary = {
                "total_findings": len(findings),
                "by_type": {},
                "by_severity": {},
                "by_agent": {},
                "readiness_score": 0
            }
            
            for finding in findings:
                # Count by type
                finding_type = finding.get("type", "unknown")
                summary["by_type"][finding_type] = summary["by_type"].get(finding_type, 0) + 1
                
                # Count by severity
                severity = finding.get("severity", "unknown")
                summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
                
                # Count by agent
                agent = finding.get("agent", "unknown")
                summary["by_agent"][agent] = summary["by_agent"].get(agent, 0) + 1
            
            # Calculate readiness score (0-100)
            high_severity = summary["by_severity"].get("high", 0)
            medium_severity = summary["by_severity"].get("medium", 0)
            low_severity = summary["by_severity"].get("low", 0)
            
            # Penalize high severity issues heavily
            readiness_score = 100 - (high_severity * 20) - (medium_severity * 10) - (low_severity * 5)
            readiness_score = max(0, min(100, readiness_score))
            
            summary["readiness_score"] = readiness_score
            
            audit_path = Path(self.audit_findings_file)
            audit_data = {
                "audit_date": datetime.now().isoformat(),
                "findings": findings,
                "summary": summary
            }

            await asyncio.to_thread(
                lambda: audit_path.write_text(json.dumps(audit_data, indent=2))
            )

            self.logger.info(
                "Compiled audit findings: %s findings, readiness score: %s",
                summary['total_findings'],
                readiness_score,
            )
            await metrics.set_gauge("background_agents.audit_readiness", readiness_score)
            
        except Exception as e:
            self.logger.error(f"Failed to compile findings: {e}")
    
    async def shutdown(self):
        """Shutdown the background agent manager."""
        await self.stop()
        self.logger.info("Background agent manager shutdown complete")

    def get_status(self) -> Dict[str, Any]:
        """Get status of background agents."""
        return {
            "enabled": self.config.get("enabled", False),
            "agents": self.background_agents,
            "memory_file": self.memory_file,
            "audit_findings_file": self.audit_findings_file
        }
