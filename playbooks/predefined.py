"""Predefined modernization playbooks for Terry Super Ecosystem."""

from __future__ import annotations

from typing import Any, Dict, List

PREDEFINED_PLAYBOOKS: List[Dict[str, Any]] = [
    {
        "identifier": "secret_regeneration",
        "name": "Rotate secrets and adopt managed identity",
        "description": (
            "Replace embedded credentials with managed identities across application layers "
            "and update configuration to source secrets from secure vaults."
        ),
        "tags": ["security", "secrets", "azure"],
        "steps": [
            {
                "action": "scan",
                "name": "Find embedded credentials",
                "details": "Search codebase for static keys, passwords, or connection strings.",
            },
            {
                "action": "plan",
                "name": "Map replacements",
                "details": "Generate mapping to Azure Key Vault or managed identity endpoints.",
            },
            {
                "action": "transform",
                "name": "Patch configuration",
                "details": "Replace secrets with vault references and identity bindings.",
            },
            {
                "action": "verify",
                "name": "Validate connection flows",
                "details": "Run smoke tests against staging using rotated credentials.",
            },
        ],
        "metadata": {
            "compliance": ["SOC2", "ISO27001"],
            "estimated_runtime_minutes": 35,
            "requires_approval": True,
        },
    },
    {
        "identifier": "queue_integration",
        "name": "Modernize messaging with Azure Service Bus",
        "description": (
            "Introduce resilient messaging primitives, migrating legacy queue integrations to "
            "Azure Service Bus with telemetry hooks."
        ),
        "tags": ["integration", "messaging", "resilience"],
        "steps": [
            {
                "action": "assess",
                "name": "Inventory publishers and consumers",
                "details": "Map queue usage patterns and throughput across services.",
            },
            {
                "action": "transform",
                "name": "Generate Service Bus clients",
                "details": "Create idiomatic client wrappers and connection policies.",
            },
            {
                "action": "configure",
                "name": "Provision infrastructure",
                "details": "Emit IaC templates for queues, topics, subscriptions, and alerts.",
            },
            {
                "action": "validate",
                "name": "Load-test critical paths",
                "details": "Execute reliability scenarios with chaos-friendly retry policies.",
            },
        ],
        "metadata": {
            "observability_hooks": ["OpenTelemetry", "AppInsights"],
            "estimated_runtime_minutes": 55,
            "requires_approval": True,
        },
    },
    {
        "identifier": "identity_unification",
        "name": "Adopt Azure AD based identity",
        "description": (
            "Migrate authentication flows to Azure Active Directory with token hardening, "
            "MFA enforcement, and least-privilege role assignments."
        ),
        "tags": ["security", "identity", "governance"],
        "steps": [
            {
                "action": "assess",
                "name": "Catalog identity flows",
                "details": "Identify login endpoints, token issuers, and session policies.",
            },
            {
                "action": "plan",
                "name": "Design Azure AD integration",
                "details": "Define app registrations, scopes, and redirect URIs.",
            },
            {
                "action": "transform",
                "name": "Implement MSAL-based flows",
                "details": "Refactor services to use MSAL libraries with refresh token handling.",
            },
            {
                "action": "verify",
                "name": "Enforce MFA and conditional access",
                "details": "Run integration tests to confirm policy coverage and fallback paths.",
            },
        ],
        "metadata": {
            "security_controls": ["MFA", "ConditionalAccess"],
            "estimated_runtime_minutes": 65,
            "requires_approval": True,
        },
    },
]

