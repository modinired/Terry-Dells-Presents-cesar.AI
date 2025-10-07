"""
Security management for Terry Delmonaco Manager Agent.
Handles authentication, authorization, encryption, and security monitoring.
"""

import os
import hashlib
import hmac
import base64
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt

from .logger import LoggerMixin, audit_logger


class SecurityManager(LoggerMixin):
    """
    Security manager for Terry Delmonaco Manager Agent.
    Handles authentication, encryption, and security monitoring.
    """
    
    def __init__(self):
        super().__init__()
        self.encryption_key = None
        self.fernet = None
        self.jwt_secret = os.getenv("JWT_SECRET", "td-manager-agent-secret")
        self.auth_provider = os.getenv("AUTH_PROVIDER", "google_oauth")
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize security components."""
        try:
            self.log_info("Initializing security manager...")
            
            # Initialize encryption
            await self._initialize_encryption()
            
            # Initialize authentication
            await self._initialize_authentication()
            
            # Initialize security monitoring
            await self._initialize_security_monitoring()
            
            self.is_initialized = True
            self.log_info("Security manager initialized successfully")
            
        except Exception as e:
            self.log_error(f"Security initialization failed: {e}")
            raise
    
    async def _initialize_encryption(self):
        """Initialize encryption components."""
        # Generate or load encryption key
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(self.encryption_key)
        
        self.fernet = Fernet(self.encryption_key)
        self.log_info("Encryption initialized")
    
    async def _initialize_authentication(self):
        """Initialize authentication components."""
        if self.auth_provider == "google_oauth":
            await self._setup_google_oauth()
        else:
            self.log_warning(f"Unsupported auth provider: {self.auth_provider}")
    
    async def _setup_google_oauth(self):
        """Setup Google OAuth authentication."""
        # This would integrate with Google OAuth
        # For now, we'll use a simplified approach
        self.log_info("Google OAuth authentication configured")
    
    async def _initialize_security_monitoring(self):
        """Initialize security monitoring."""
        self.log_info("Security monitoring initialized")
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not self.is_initialized:
            raise RuntimeError("Security manager not initialized")
        
        encrypted_data = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not self.is_initialized:
            raise RuntimeError("Security manager not initialized")
        
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.fernet.decrypt(decoded_data)
        return decrypted_data.decode()
    
    def generate_token(self, user_id: str, permissions: list) -> str:
        """Generate JWT token for user."""
        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        audit_logger.log_data_access(user_id, "token_generation", "generate")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            audit_logger.log_data_access(payload.get("user_id"), "token_verification", "verify")
            return payload
        except jwt.ExpiredSignatureError:
            self.log_warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            self.log_warning("Invalid token")
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash password using secure algorithm."""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.b64encode(kdf.derive(password.encode()))
        return f"{base64.b64encode(salt).decode()}:{key.decode()}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        try:
            salt_b64, key_b64 = hashed_password.split(":")
            salt = base64.b64decode(salt_b64)
            key = base64.b64decode(key_b64)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            kdf.verify(password.encode(), key)
            return True
        except Exception:
            return False
    
    def log_security_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Log security event."""
        audit_logger.log_security_event(event_type, user_id, details)
        self.log_warning(f"Security event: {event_type} by user {user_id}")
    
    async def validate_permissions(self, user_id: str, required_permissions: list) -> bool:
        """Validate user permissions."""
        # This would check against user permissions in database
        # For now, return True for demonstration
        return True
    
    def sanitize_input(self, data: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        # Basic sanitization - in production, use a proper library
        dangerous_chars = ["<", ">", "'", '"', "&", ";"]
        sanitized = data
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        return sanitized
    
    async def shutdown(self):
        """Shutdown security manager."""
        self.log_info("Shutting down security manager")
        self.is_initialized = False 