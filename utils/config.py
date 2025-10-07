"""
Configuration management for Terry Delmonaco Manager Agent.
Handles all configuration settings, environment variables, and system parameters.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, fields
from datetime import datetime


@dataclass
class ScreenRecordingConfig:
    """Screen recording configuration."""
    enabled: bool = True
    capture_mode: str = "interval"
    interval_seconds: int = 20
    ocr_model: str = "tesserocr"
    vision_model: str = "openai/clip-vit-base-patch32"
    language_model: str = "gpt-4"
    output_format: str = "JSON + Natural Language"
    description_style: str = "precise, business-aligned, task-contextual"


@dataclass
class TaskManagementConfig:
    """Task management configuration."""
    scheduling: bool = True
    priority_levels: List[str] = field(default_factory=lambda: ["urgent", "routine", "backlog"])
    delegation_strategy: str = "Round-robin with specialization match and performance heuristics"


@dataclass
class MemoryConfig:
    """Memory system configuration."""
    enabled: bool = True
    mode: str = "semantic + episodic"
    storage: str = "PostgreSQL + Redis"
    learning_sync: Dict[str, Any] = field(default_factory=lambda: {
        "targets": ["CESAR-core", "Automation-Agent-Fleet"],
        "frequency": "on-event + hourly sync",
        "format": "vector embeddings + natural language summaries"
    })


@dataclass
class AgentFleetConfig:
    """Agent fleet configuration."""
    structure: str = "Hub-and-Spoke"
    types: List[str] = field(default_factory=lambda: [
        "Automated Reporting Agent",
        "Inbox + Calendar Agent", 
        "Spreadsheet Processor",
        "CRM Sync Agent",
        "Screen Activity Agent"
    ])
    specialization_policy: str = "Each agent focuses exclusively on a single work-related vertical with deep task automation"


@dataclass
class SecurityConfig:
    """Security configuration."""
    auth_required: bool = True
    auth_provider: str = "Google OAuth"
    logging: str = "secure + redacted"
    data_encryption: str = "AES-256"


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    on_task_complete: str = "https://your-webhook/complete"
    on_agent_feedback: str = "https://your-webhook/feedback"


@dataclass
class PermissionsConfig:
    """Permissions configuration."""
    file_read: bool = True
    file_write: bool = True
    network_access: bool = True
    subprocess_control: bool = True
    database_access: bool = True


@dataclass
class InteractionPolicyConfig:
    """Interaction policy configuration."""
    with_CESAR: str = "Bi-directional learning exchange only"
    with_AgentFleet: str = "Full orchestration, task delegation, and performance oversight"


@dataclass
class UITarsConfig:
    """UI-TARS desktop operator configuration."""
    enabled: bool = True
    install_path: Optional[str] = None
    operator_mode: str = "local"
    auto_start: bool = False
    model_provider: str = "huggingface"
    model_name: str = "UI-TARS-1.5-7B"


class Config:
    """
    Main configuration class for Terry Delmonaco Manager Agent.
    Manages all system configuration including environment variables,
    default settings, and runtime parameters.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config.json"
        self.project_root = Path(__file__).parent.parent
        
        # Load configuration
        self._load_config()
        
        # Initialize sub-configurations
        self.screen_recording = self._build_dataclass(ScreenRecordingConfig, self._config_data.get("screen_recording"))
        self.task_management = self._build_dataclass(TaskManagementConfig, self._config_data.get("task_management"))
        self.memory = self._build_dataclass(MemoryConfig, self._config_data.get("memory"))
        self.agent_fleet = self._build_dataclass(AgentFleetConfig, self._config_data.get("agent_fleet"))
        self.security = self._build_dataclass(SecurityConfig, self._config_data.get("security"))
        self.webhooks = self._build_dataclass(WebhookConfig, self._config_data.get("webhooks"))
        self.permissions = self._build_dataclass(PermissionsConfig, self._config_data.get("permissions"))
        self.interaction_policy = self._build_dataclass(InteractionPolicyConfig, self._config_data.get("interaction_policy"))
        self.ui_tars = self._build_dataclass(UITarsConfig, self._config_data.get("ui_tars"))

        # Override with environment variables
        self._load_from_env()

        # Capture validation feedback
        self._validation_errors: List[str] = []
        self._run_basic_validation()
    
    def _load_config(self):
        """Load configuration from file."""
        config_path = self.project_root / self.config_file
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self._config_data = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                self._config_data = {}
        else:
            self._config_data = {}

    def _build_dataclass(self, dataclass_type, values: Optional[Dict[str, Any]]):
        """Safely instantiate dataclasses with optional overrides."""
        values = values or {}
        allowed_fields = {f.name for f in fields(dataclass_type)}
        filtered = {k: v for k, v in values.items() if k in allowed_fields}
        return dataclass_type(**filtered)

    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Screen recording
        self._maybe_set_bool("SCREEN_RECORDING_ENABLED", self.screen_recording, "enabled")

        if os.getenv("SCREEN_RECORDING_INTERVAL"):
            self.screen_recording.interval_seconds = int(os.getenv("SCREEN_RECORDING_INTERVAL"))

        # Memory
        self._maybe_set_bool("MEMORY_ENABLED", self.memory, "enabled")

        # Security
        self._maybe_set_bool("AUTH_REQUIRED", self.security, "auth_required")

        # Webhooks
        if os.getenv("WEBHOOK_TASK_COMPLETE"):
            self.webhooks.on_task_complete = os.getenv("WEBHOOK_TASK_COMPLETE")

        if os.getenv("WEBHOOK_AGENT_FEEDBACK"):
            self.webhooks.on_agent_feedback = os.getenv("WEBHOOK_AGENT_FEEDBACK")

        # UI-TARS overrides
        if os.getenv("UITARS_INSTALL_PATH"):
            self.ui_tars.install_path = os.getenv("UITARS_INSTALL_PATH")
        self._maybe_set_bool("UITARS_ENABLED", self.ui_tars, "enabled")
        self._maybe_set_bool("UITARS_AUTO_START", self.ui_tars, "auto_start")
        if os.getenv("UITARS_OPERATOR_MODE"):
            self.ui_tars.operator_mode = os.getenv("UITARS_OPERATOR_MODE")
        if os.getenv("UITARS_MODEL_PROVIDER"):
            self.ui_tars.model_provider = os.getenv("UITARS_MODEL_PROVIDER")
        if os.getenv("UITARS_MODEL_NAME"):
            self.ui_tars.model_name = os.getenv("UITARS_MODEL_NAME")

    def _maybe_set_bool(self, env_var: str, target: Any, attribute: str) -> None:
        value = os.getenv(env_var)
        if value is None:
            return
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            setattr(target, attribute, True)
        elif normalized in {"false", "0", "no", "off"}:
            setattr(target, attribute, False)

    def _run_basic_validation(self) -> None:
        if self.screen_recording.interval_seconds <= 0:
            self._validation_errors.append("screen_recording.interval_seconds must be positive")

        if self.ui_tars.install_path:
            expanded = Path(self.ui_tars.install_path).expanduser()
            if not expanded.exists():
                self._validation_errors.append(f"ui_tars.install_path not found: {expanded}")

    @property
    def validation_errors(self) -> List[str]:
        return list(self._validation_errors)

    def ensure_valid(self) -> None:
        if self._validation_errors:
            raise ValueError("; ".join(self._validation_errors))
    
    @property
    def agent_name(self) -> str:
        """Get the agent name."""
        return os.getenv("AGENT_NAME", "Terry Delmonaco Manager Agent")
    
    @property
    def version(self) -> str:
        """Get the agent version."""
        return os.getenv("AGENT_VERSION", "3.1")
    
    @property
    def timezone(self) -> str:
        """Get the timezone setting."""
        return os.getenv("TIMEZONE", "UTC")
    
    @property
    def log_level(self) -> str:
        """Get the log level."""
        return os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def database_url(self) -> str:
        """Get the database URL."""
        return os.getenv("DATABASE_URL", "postgresql://localhost/td_manager_agent")
    
    @property
    def redis_url(self) -> str:
        """Get the Redis URL."""
        return os.getenv("REDIS_URL", "redis://localhost:6379")
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get the OpenAI API key."""
        return os.getenv("OPENAI_API_KEY")
    
    @property
    def google_credentials_file(self) -> str:
        """Get the Google credentials file path."""
        return os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    
    @property
    def cesar_api_url(self) -> str:
        """Get the CESAR API URL."""
        return os.getenv("CESAR_API_URL", "http://localhost:8000")
    
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """Get configuration for a specific agent type."""
        agent_configs = {
            "automated_reporting": {
                "enabled": True,
                "report_types": ["daily", "weekly", "monthly"],
                "output_formats": ["pdf", "excel", "google_sheets"],
                "schedule": "0 9 * * *"  # Daily at 9 AM
            },
            "inbox_calendar": {
                "enabled": True,
                "email_providers": ["gmail", "outlook"],
                "calendar_providers": ["google_calendar", "outlook_calendar"],
                "auto_respond": False,
                "priority_filtering": True
            },
            "spreadsheet_processor": {
                "enabled": True,
                "supported_formats": ["xlsx", "csv", "google_sheets"],
                "auto_processing": True,
                "template_matching": True
            },
            "crm_sync": {
                "enabled": True,
                "crm_providers": ["salesforce", "hubspot", "pipedrive"],
                "sync_frequency": "hourly",
                "data_mapping": "auto"
            },
            "screen_activity": {
                "enabled": True,
                "capture_interval": 20,
                "analysis_depth": "detailed",
                "privacy_mode": True
            },
            "terry_delmonaco": {
                "enabled": os.getenv("ENABLE_TERRY_ASSISTANT", "false").lower() in {"1", "true", "yes"},
                "api_base": os.getenv("TERRY_BRIDGE_URL", "http://127.0.0.1:8899"),
                "timeout_seconds": int(os.getenv("TERRY_BRIDGE_TIMEOUT", "90")),
                "capabilities": ["terry_personal_assist", "local_coding_assist"],
                "system_prompt": os.getenv(
                    "TERRY_SYSTEM_PROMPT",
                    "You are Terry Delmonaco, a diligent local assistant who enhances CESAR workflows.",
                ),
            }
        }

        return agent_configs.get(agent_type, {})
    
    def save_config(self):
        """Save current configuration to file."""
        config_data = {
            "agent_name": self.agent_name,
            "version": self.version,
            "timezone": self.timezone,
            "screen_recording": {
                "enabled": self.screen_recording.enabled,
                "interval_seconds": self.screen_recording.interval_seconds,
                "capture_mode": self.screen_recording.capture_mode
            },
            "task_management": {
                "scheduling": self.task_management.scheduling,
                "priority_levels": self.task_management.priority_levels
            },
            "memory": {
                "enabled": self.memory.enabled,
                "mode": self.memory.mode,
                "storage": self.memory.storage
            },
            "security": {
                "auth_required": self.security.auth_required,
                "auth_provider": self.security.auth_provider
            },
            "webhooks": {
                "on_task_complete": self.webhooks.on_task_complete,
                "on_agent_feedback": self.webhooks.on_agent_feedback
            }
        }
        
        config_path = self.project_root / self.config_file
        try:
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def validate(self) -> bool:
        """Validate the configuration."""
        required_env_vars = [
            "OPENAI_API_KEY",
            "DATABASE_URL",
            "REDIS_URL"
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Warning: Missing required environment variables: {missing_vars}")
            return False
        
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            "agent_name": self.agent_name,
            "version": self.version,
            "timezone": self.timezone,
            "screen_recording_enabled": self.screen_recording.enabled,
            "memory_enabled": self.memory.enabled,
            "security_auth_required": self.security.auth_required,
            "agent_fleet_types": self.agent_fleet.types,
            "task_management_scheduling": self.task_management.scheduling
        } 
