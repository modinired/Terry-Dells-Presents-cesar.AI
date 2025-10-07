#!/usr/bin/env python3
"""
Memory Manager for Terry Delmonaco Manager Agent
Handles episodic and semantic memory storage and retrieval.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from ..utils.metrics import metrics


class MemoryManager:
    """
    Manages episodic and semantic memory for the agent system.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("memory_manager")
        data_dir = Path(os.getenv("CESAR_DATA_DIR", Path.cwd()))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = data_dir / ".memory.json"
        self.audit_findings_file = data_dir / ".audit_findings.json"
        self.memory_data = {}
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the memory manager."""
        try:
            self.logger.info("Initializing memory manager...")
            
            # Load existing memory data
            await self._load_memory()
            
            self.is_initialized = True
            self.logger.info("Memory manager initialized successfully")
            await metrics.incr("memory_manager.initialize")
            return True
            
        except Exception as e:
            self.logger.error(f"Memory manager initialization failed: {e}")
            return False
    
    async def _load_memory(self):
        """Load memory data from files."""
        try:
            # Load main memory file
            memory_path = Path(self.memory_file)

            def load_memory() -> Dict[str, Any]:
                if memory_path.exists():
                    return json.loads(memory_path.read_text())
                return {
                    "findings": [],
                    "last_audit": None,
                    "session_id": "initial"
                }

            self.memory_data = await asyncio.to_thread(load_memory)

            if not memory_path.exists():
                await self._save_memory()

            await metrics.set_gauge(
                "memory_manager.findings",
                len(self.memory_data.get("findings", []))
            )
            
            # Load audit findings
            audit_path = Path(self.audit_findings_file)

            def load_audit() -> Dict[str, Any]:
                if audit_path.exists():
                    return json.loads(audit_path.read_text())
                return {
                    "audit_date": None,
                    "findings": [],
                    "summary": {},
                    "readiness_score": 0
                }

            self.audit_findings = await asyncio.to_thread(load_audit)

            if not audit_path.exists():
                await self._save_audit_findings()

            await metrics.set_gauge(
                "memory_manager.audit_findings",
                len(self.audit_findings.get("findings", []))
            )
        except Exception as e:
            self.logger.error(f"Failed to load memory: {e}")
            raise

    async def _save_memory(self):
        """Save memory data to file."""
        try:
            await asyncio.to_thread(
                lambda: Path(self.memory_file).write_text(
                    json.dumps(self.memory_data, indent=2)
                )
            )
            await metrics.incr("memory_manager.save_memory")
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")

    async def _save_audit_findings(self):
        """Save audit findings to file."""
        try:
            await asyncio.to_thread(
                lambda: Path(self.audit_findings_file).write_text(
                    json.dumps(self.audit_findings, indent=2)
                )
            )
            await metrics.incr("memory_manager.save_audit_findings")
        except Exception as e:
            self.logger.error(f"Failed to save audit findings: {e}")

    async def add_finding(self, agent_name: str, finding: Dict):
        """Add a finding to memory."""
        try:
            finding["timestamp"] = datetime.now().isoformat()
            finding["agent"] = agent_name
            
            self.memory_data["findings"].append(finding)
            await self._save_memory()
            await metrics.incr("memory_manager.findings_added")
            
            self.logger.info(f"Added finding from {agent_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to add finding: {e}")
    
    async def get_findings(self, agent_name: Optional[str] = None) -> List[Dict]:
        """Get findings from memory, optionally filtered by agent."""
        try:
            findings = self.memory_data.get("findings", [])
            
            if agent_name:
                findings = [f for f in findings if f.get("agent") == agent_name]
            
            return findings
            
        except Exception as e:
            self.logger.error(f"Failed to get findings: {e}")
            return []
    
    async def update_audit_findings(self, findings: List[Dict], summary: Dict):
        """Update audit findings with new data."""
        try:
            self.audit_findings["audit_date"] = datetime.now().isoformat()
            self.audit_findings["findings"] = findings
            self.audit_findings["summary"] = summary
            
            await self._save_audit_findings()
            
            self.logger.info("Updated audit findings")
            
        except Exception as e:
            self.logger.error(f"Failed to update audit findings: {e}")
    
    async def get_memory_status(self) -> Dict:
        """Get memory status information."""
        return {
            "findings_count": len(self.memory_data.get("findings", [])),
            "last_audit": self.memory_data.get("last_audit"),
            "session_id": self.memory_data.get("session_id"),
            "is_initialized": self.is_initialized
        }
    
    async def shutdown(self):
        """Shutdown the memory manager."""
        try:
            # Save any pending data
            await self._save_memory()
            await self._save_audit_findings()
            
            self.is_initialized = False
            self.logger.info("Memory manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Memory manager shutdown error: {e}") 
