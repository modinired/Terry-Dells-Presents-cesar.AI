"""
Logging system for Terry Delmonaco Manager Agent.
Provides structured logging with different levels and output formats.
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


class SecurityFilter(logging.Filter):
    """Filter to redact sensitive information from logs."""
    
    def __init__(self):
        super().__init__()
        self.sensitive_patterns = [
            "password",
            "api_key", 
            "token",
            "secret",
            "credential",
            "auth"
        ]
    
    def filter(self, record):
        """Filter and redact sensitive information."""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            for pattern in self.sensitive_patterns:
                if pattern.lower() in record.msg.lower():
                    record.msg = f"[REDACTED - {pattern.upper()}]"
                    record.args = ()
                    
        return True


def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup a logger with structured formatting and security filtering.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set log level
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = StructuredFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(SecurityFilter())
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(SecurityFilter())
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance by name."""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)
    
    def log_info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log info message with optional extra fields."""
        if extra_fields:
            self.logger.info(message, extra={"extra_fields": extra_fields})
        else:
            self.logger.info(message)
    
    def log_warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log warning message with optional extra fields."""
        if extra_fields:
            self.logger.warning(message, extra={"extra_fields": extra_fields})
        else:
            self.logger.warning(message)
    
    def log_error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log error message with optional extra fields."""
        if extra_fields:
            self.logger.error(message, extra={"extra_fields": extra_fields})
        else:
            self.logger.error(message)
    
    def log_debug(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log debug message with optional extra fields."""
        if extra_fields:
            self.logger.debug(message, extra={"extra_fields": extra_fields})
        else:
            self.logger.debug(message)


class PerformanceLogger:
    """Specialized logger for performance metrics."""
    
    def __init__(self, name: str = "performance"):
        self.logger = get_logger(name)
    
    def log_task_start(self, task_id: str, task_type: str, agent_id: str):
        """Log task start with performance tracking."""
        self.logger.info(
            "Task started",
            extra={
                "extra_fields": {
                    "event": "task_start",
                    "task_id": task_id,
                    "task_type": task_type,
                    "agent_id": agent_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    def log_task_complete(self, task_id: str, duration_ms: float, success: bool):
        """Log task completion with performance metrics."""
        self.logger.info(
            "Task completed",
            extra={
                "extra_fields": {
                    "event": "task_complete",
                    "task_id": task_id,
                    "duration_ms": duration_ms,
                    "success": success,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    def log_agent_performance(self, agent_id: str, metrics: Dict[str, Any]):
        """Log agent performance metrics."""
        self.logger.info(
            "Agent performance metrics",
            extra={
                "extra_fields": {
                    "event": "agent_performance",
                    "agent_id": agent_id,
                    "metrics": metrics,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )


class AuditLogger:
    """Specialized logger for audit events."""
    
    def __init__(self, name: str = "audit"):
        self.logger = get_logger(name)
    
    def log_security_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Log security-related events."""
        self.logger.warning(
            "Security event",
            extra={
                "extra_fields": {
                    "event": "security_event",
                    "event_type": event_type,
                    "user_id": user_id,
                    "details": details,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    def log_data_access(self, user_id: str, resource: str, action: str):
        """Log data access events."""
        self.logger.info(
            "Data access",
            extra={
                "extra_fields": {
                    "event": "data_access",
                    "user_id": user_id,
                    "resource": resource,
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    def log_config_change(self, user_id: str, config_key: str, old_value: Any, new_value: Any):
        """Log configuration changes."""
        self.logger.info(
            "Configuration change",
            extra={
                "extra_fields": {
                    "event": "config_change",
                    "user_id": user_id,
                    "config_key": config_key,
                    "old_value": str(old_value),
                    "new_value": str(new_value),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )


# Initialize default loggers
main_logger = setup_logger("td_manager_agent")
performance_logger = PerformanceLogger()
audit_logger = AuditLogger() 
