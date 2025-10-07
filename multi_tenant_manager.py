#!/usr/bin/env python3
"""
Multi-Tenant Infrastructure Manager for CESAR.ai Atlas Final MAIaaS Platform
Enables enterprise-grade multi-tenancy with isolation, resource allocation, and governance.
"""

import asyncio
import logging
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib

from ..utils.logger import LoggerMixin, performance_logger
from ..utils.config import Config


class TenantTier(Enum):
    """Tenant subscription tiers."""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ULTIMATE = "ultimate"


class ResourceType(Enum):
    """Resource types for tenant allocation."""
    CPU_CORES = "cpu_cores"
    MEMORY_GB = "memory_gb"
    STORAGE_GB = "storage_gb"
    NETWORK_BANDWIDTH = "network_bandwidth_mbps"
    AGENT_INSTANCES = "agent_instances"
    API_CALLS_PER_HOUR = "api_calls_per_hour"
    CONCURRENT_SESSIONS = "concurrent_sessions"


class IsolationLevel(Enum):
    """Data and compute isolation levels."""
    SHARED = "shared"
    NAMESPACE = "namespace"
    DEDICATED_VM = "dedicated_vm"
    DEDICATED_HARDWARE = "dedicated_hardware"


@dataclass
class ResourceQuota:
    """Resource quota definition for a tenant."""
    resource_type: ResourceType
    allocated: float
    used: float = 0.0
    reserved: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TenantConfiguration:
    """Comprehensive tenant configuration."""
    tenant_id: str
    tenant_name: str
    tier: TenantTier
    isolation_level: IsolationLevel
    resource_quotas: Dict[ResourceType, ResourceQuota]
    allowed_agent_types: List[str]
    security_policies: List[str]
    compliance_requirements: List[str]
    custom_configurations: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    active: bool = True


@dataclass
class TenantNamespace:
    """Isolated namespace for tenant resources."""
    namespace_id: str
    tenant_id: str
    name: str
    agent_instances: Dict[str, Any] = field(default_factory=dict)
    network_config: Dict[str, Any] = field(default_factory=dict)
    storage_config: Dict[str, Any] = field(default_factory=dict)
    security_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantMetrics:
    """Real-time tenant metrics and usage."""
    tenant_id: str
    resource_utilization: Dict[ResourceType, float]
    agent_performance: Dict[str, Dict[str, Any]]
    api_usage: Dict[str, int]
    error_rates: Dict[str, float]
    cost_tracking: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


class MultiTenantManager(LoggerMixin):
    """
    Multi-tenant infrastructure manager for MAIaaS platform.
    Provides enterprise-grade isolation, resource management, and governance.
    """

    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("multi_tenant_manager")

        # Tenant management
        self.tenants: Dict[str, TenantConfiguration] = {}
        self.namespaces: Dict[str, TenantNamespace] = {}
        self.tenant_metrics: Dict[str, TenantMetrics] = {}

        # Resource management
        self.global_resource_pool = {
            ResourceType.CPU_CORES: 1000.0,
            ResourceType.MEMORY_GB: 2048.0,
            ResourceType.STORAGE_GB: 10240.0,
            ResourceType.NETWORK_BANDWIDTH: 10000.0,
            ResourceType.AGENT_INSTANCES: 500,
            ResourceType.API_CALLS_PER_HOUR: 1000000,
            ResourceType.CONCURRENT_SESSIONS: 10000
        }

        # Tier configurations
        self.tier_configurations = self._initialize_tier_configurations()

        # Monitoring and governance
        self.usage_monitor = None
        self.governance_policies = {}

        self.logger.info("Multi-Tenant Manager initialized")

    def _initialize_tier_configurations(self) -> Dict[TenantTier, Dict[str, Any]]:
        """Initialize tenant tier configurations with resource allocations."""
        return {
            TenantTier.STARTER: {
                "max_agents": 3,
                "resource_limits": {
                    ResourceType.CPU_CORES: 4.0,
                    ResourceType.MEMORY_GB: 8.0,
                    ResourceType.STORAGE_GB: 100.0,
                    ResourceType.AGENT_INSTANCES: 5,
                    ResourceType.API_CALLS_PER_HOUR: 1000,
                    ResourceType.CONCURRENT_SESSIONS: 10
                },
                "isolation_level": IsolationLevel.SHARED,
                "allowed_agent_types": ["basic_automation", "customer_service", "data_analysis"],
                "support_level": "community",
                "sla_uptime": 99.0
            },
            TenantTier.PROFESSIONAL: {
                "max_agents": 10,
                "resource_limits": {
                    ResourceType.CPU_CORES: 16.0,
                    ResourceType.MEMORY_GB: 32.0,
                    ResourceType.STORAGE_GB: 500.0,
                    ResourceType.AGENT_INSTANCES: 20,
                    ResourceType.API_CALLS_PER_HOUR: 10000,
                    ResourceType.CONCURRENT_SESSIONS: 50
                },
                "isolation_level": IsolationLevel.NAMESPACE,
                "allowed_agent_types": ["*"],  # All agent types
                "support_level": "business",
                "sla_uptime": 99.5
            },
            TenantTier.ENTERPRISE: {
                "max_agents": 25,
                "resource_limits": {
                    ResourceType.CPU_CORES: 64.0,
                    ResourceType.MEMORY_GB: 128.0,
                    ResourceType.STORAGE_GB: 2048.0,
                    ResourceType.AGENT_INSTANCES: 100,
                    ResourceType.API_CALLS_PER_HOUR: 100000,
                    ResourceType.CONCURRENT_SESSIONS: 500
                },
                "isolation_level": IsolationLevel.DEDICATED_VM,
                "allowed_agent_types": ["*"],
                "support_level": "enterprise",
                "sla_uptime": 99.9,
                "compliance_included": ["SOC2", "ISO27001", "GDPR"]
            },
            TenantTier.ULTIMATE: {
                "max_agents": -1,  # Unlimited
                "resource_limits": {
                    ResourceType.CPU_CORES: 256.0,
                    ResourceType.MEMORY_GB: 512.0,
                    ResourceType.STORAGE_GB: 10240.0,
                    ResourceType.AGENT_INSTANCES: -1,  # Unlimited
                    ResourceType.API_CALLS_PER_HOUR: -1,  # Unlimited
                    ResourceType.CONCURRENT_SESSIONS: -1  # Unlimited
                },
                "isolation_level": IsolationLevel.DEDICATED_HARDWARE,
                "allowed_agent_types": ["*"],
                "support_level": "white_glove",
                "sla_uptime": 99.99,
                "compliance_included": ["ALL"],
                "custom_integrations": True,
                "dedicated_support_team": True
            }
        }

    async def create_tenant(self, tenant_name: str, tier: TenantTier,
                           custom_config: Dict[str, Any] = None) -> str:
        """Create a new tenant with specified tier and configuration."""
        try:
            # Generate unique tenant ID
            tenant_id = f"tenant_{secrets.token_urlsafe(16)}"

            # Get tier configuration
            tier_config = self.tier_configurations[tier]

            # Create resource quotas based on tier
            resource_quotas = {}
            for resource_type, limit in tier_config["resource_limits"].items():
                if limit == -1:  # Unlimited
                    limit = self.global_resource_pool[resource_type]

                resource_quotas[resource_type] = ResourceQuota(
                    resource_type=resource_type,
                    allocated=limit
                )

            # Create tenant configuration
            tenant_config = TenantConfiguration(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                tier=tier,
                isolation_level=tier_config["isolation_level"],
                resource_quotas=resource_quotas,
                allowed_agent_types=tier_config["allowed_agent_types"],
                security_policies=self._get_default_security_policies(tier),
                compliance_requirements=tier_config.get("compliance_included", []),
                custom_configurations=custom_config or {}
            )

            # Create tenant namespace
            namespace = await self._create_tenant_namespace(tenant_id, tenant_name, tier_config)

            # Store tenant configuration
            self.tenants[tenant_id] = tenant_config
            self.namespaces[namespace.namespace_id] = namespace

            # Initialize tenant metrics
            self.tenant_metrics[tenant_id] = TenantMetrics(
                tenant_id=tenant_id,
                resource_utilization={rt: 0.0 for rt in ResourceType},
                agent_performance={},
                api_usage={},
                error_rates={},
                cost_tracking={}
            )

            self.logger.info(f"Created tenant: {tenant_name} ({tenant_id}) with tier: {tier.value}")

            return tenant_id

        except Exception as e:
            self.logger.error(f"Failed to create tenant {tenant_name}: {e}")
            raise

    async def _create_tenant_namespace(self, tenant_id: str, tenant_name: str,
                                     tier_config: Dict[str, Any]) -> TenantNamespace:
        """Create isolated namespace for tenant."""
        namespace_id = f"ns_{tenant_id}"

        # Configure network isolation
        network_config = {
            "vlan_id": hash(tenant_id) % 4096,  # Simple VLAN assignment
            "subnet": f"10.{(hash(tenant_id) % 254) + 1}.0.0/24",
            "firewall_rules": self._generate_firewall_rules(tier_config),
            "load_balancer": f"lb-{namespace_id}"
        }

        # Configure storage isolation
        storage_config = {
            "volume_prefix": f"vol-{namespace_id}",
            "encryption": tier_config["isolation_level"] != IsolationLevel.SHARED,
            "backup_retention": 30 if tier_config.get("support_level") == "enterprise" else 7,
            "replication_factor": 3 if tier_config.get("sla_uptime", 0) > 99.5 else 1
        }

        # Configure security context
        security_context = {
            "service_account": f"sa-{namespace_id}",
            "rbac_policies": self._generate_rbac_policies(tier_config),
            "pod_security_policy": self._get_pod_security_policy(tier_config["isolation_level"]),
            "network_policies": self._generate_network_policies(tier_config)
        }

        namespace = TenantNamespace(
            namespace_id=namespace_id,
            tenant_id=tenant_id,
            name=f"{tenant_name.lower().replace(' ', '-')}-{namespace_id}",
            network_config=network_config,
            storage_config=storage_config,
            security_context=security_context
        )

        return namespace

    def _get_default_security_policies(self, tier: TenantTier) -> List[str]:
        """Get default security policies for tenant tier."""
        base_policies = ["authentication_required", "audit_logging", "data_encryption"]

        if tier in [TenantTier.ENTERPRISE, TenantTier.ULTIMATE]:
            base_policies.extend([
                "zero_trust_network",
                "advanced_threat_protection",
                "compliance_monitoring",
                "privileged_access_management"
            ])

        if tier == TenantTier.ULTIMATE:
            base_policies.extend([
                "hardware_security_module",
                "dedicated_security_team",
                "custom_security_controls"
            ])

        return base_policies

    def _generate_firewall_rules(self, tier_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate firewall rules based on tenant tier."""
        base_rules = [
            {"action": "allow", "source": "tenant_network", "destination": "agent_services", "ports": [8080, 8443]},
            {"action": "allow", "source": "tenant_network", "destination": "api_gateway", "ports": [443]},
            {"action": "deny", "source": "*", "destination": "management_network", "ports": ["*"]}
        ]

        if tier_config["isolation_level"] == IsolationLevel.DEDICATED_HARDWARE:
            base_rules.append({
                "action": "allow",
                "source": "tenant_network",
                "destination": "dedicated_infrastructure",
                "ports": ["*"]
            })

        return base_rules

    def _generate_rbac_policies(self, tier_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RBAC policies for tenant."""
        return {
            "roles": [
                {
                    "name": "tenant-admin",
                    "permissions": ["create_agents", "manage_configs", "view_metrics", "manage_users"]
                },
                {
                    "name": "tenant-user",
                    "permissions": ["use_agents", "view_basic_metrics"]
                },
                {
                    "name": "tenant-viewer",
                    "permissions": ["view_basic_metrics"]
                }
            ],
            "default_role": "tenant-user",
            "admin_approval_required": tier_config.get("support_level") in ["enterprise", "white_glove"]
        }

    def _get_pod_security_policy(self, isolation_level: IsolationLevel) -> Dict[str, Any]:
        """Get pod security policy based on isolation level."""
        base_policy = {
            "privileged": False,
            "allowPrivilegeEscalation": False,
            "runAsNonRoot": True,
            "readOnlyRootFilesystem": True
        }

        if isolation_level in [IsolationLevel.DEDICATED_VM, IsolationLevel.DEDICATED_HARDWARE]:
            base_policy.update({
                "seLinux": {"rule": "RunAsAny"},
                "fsGroup": {"rule": "RunAsAny"},
                "volumes": ["configMap", "emptyDir", "projected", "secret", "downwardAPI", "persistentVolumeClaim"]
            })

        return base_policy

    def _generate_network_policies(self, tier_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Kubernetes network policies."""
        return [
            {
                "name": "default-deny-all",
                "spec": {
                    "podSelector": {},
                    "policyTypes": ["Ingress", "Egress"]
                }
            },
            {
                "name": "allow-tenant-communication",
                "spec": {
                    "podSelector": {"matchLabels": {"tenant": "current"}},
                    "ingress": [{"from": [{"podSelector": {"matchLabels": {"tenant": "current"}}}]}],
                    "egress": [{"to": [{"podSelector": {"matchLabels": {"tenant": "current"}}}]}]
                }
            }
        ]

    async def allocate_agent_to_tenant(self, tenant_id: str, agent_type: str,
                                     agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate agent instance to tenant with resource checking."""
        try:
            tenant = self.tenants.get(tenant_id)
            if not tenant:
                raise ValueError(f"Tenant not found: {tenant_id}")

            # Check if agent type is allowed
            if tenant.allowed_agent_types != ["*"] and agent_type not in tenant.allowed_agent_types:
                raise ValueError(f"Agent type {agent_type} not allowed for tenant {tenant_id}")

            # Check resource availability
            required_resources = self._get_agent_resource_requirements(agent_type)
            if not await self._check_resource_availability(tenant_id, required_resources):
                raise ValueError("Insufficient resources for agent allocation")

            # Generate agent instance ID
            agent_instance_id = f"agent_{secrets.token_urlsafe(12)}"

            # Get tenant namespace
            namespace = self._get_tenant_namespace(tenant_id)
            if not namespace:
                raise ValueError(f"Namespace not found for tenant {tenant_id}")

            # Create agent deployment configuration
            deployment_config = {
                "agent_instance_id": agent_instance_id,
                "agent_type": agent_type,
                "tenant_id": tenant_id,
                "namespace": namespace.name,
                "resource_allocation": required_resources,
                "security_context": namespace.security_context,
                "network_config": namespace.network_config,
                "storage_config": namespace.storage_config,
                "custom_config": agent_config
            }

            # Update tenant resource usage
            await self._update_resource_usage(tenant_id, required_resources, "allocate")

            # Store agent instance in namespace
            namespace.agent_instances[agent_instance_id] = deployment_config

            self.logger.info(f"Allocated agent {agent_type} to tenant {tenant_id}: {agent_instance_id}")

            return {
                "agent_instance_id": agent_instance_id,
                "deployment_config": deployment_config,
                "status": "allocated"
            }

        except Exception as e:
            self.logger.error(f"Failed to allocate agent to tenant {tenant_id}: {e}")
            raise

    def _get_agent_resource_requirements(self, agent_type: str) -> Dict[ResourceType, float]:
        """Get resource requirements for agent type."""
        # Default resource requirements
        base_requirements = {
            ResourceType.CPU_CORES: 0.5,
            ResourceType.MEMORY_GB: 1.0,
            ResourceType.STORAGE_GB: 5.0,
            ResourceType.AGENT_INSTANCES: 1
        }

        # Agent-specific requirements
        agent_requirements = {
            "network_orchestrator": {
                ResourceType.CPU_CORES: 2.0,
                ResourceType.MEMORY_GB: 4.0,
                ResourceType.STORAGE_GB: 20.0
            },
            "container_orchestrator": {
                ResourceType.CPU_CORES: 1.5,
                ResourceType.MEMORY_GB: 3.0,
                ResourceType.STORAGE_GB: 15.0
            },
            "database_coordinator": {
                ResourceType.CPU_CORES: 3.0,
                ResourceType.MEMORY_GB: 8.0,
                ResourceType.STORAGE_GB: 100.0
            },
            "financial_processor": {
                ResourceType.CPU_CORES: 2.0,
                ResourceType.MEMORY_GB: 4.0,
                ResourceType.STORAGE_GB: 50.0
            }
        }

        # Merge base requirements with agent-specific requirements
        requirements = base_requirements.copy()
        if agent_type in agent_requirements:
            requirements.update(agent_requirements[agent_type])

        return requirements

    async def _check_resource_availability(self, tenant_id: str,
                                         required_resources: Dict[ResourceType, float]) -> bool:
        """Check if tenant has sufficient resources for allocation."""
        tenant = self.tenants[tenant_id]

        for resource_type, required_amount in required_resources.items():
            quota = tenant.resource_quotas.get(resource_type)
            if not quota:
                continue

            available = quota.allocated - quota.used - quota.reserved
            if available < required_amount:
                self.logger.warning(
                    f"Insufficient {resource_type.value} for tenant {tenant_id}: "
                    f"required={required_amount}, available={available}"
                )
                return False

        return True

    async def _update_resource_usage(self, tenant_id: str,
                                   resources: Dict[ResourceType, float], operation: str):
        """Update tenant resource usage."""
        tenant = self.tenants[tenant_id]

        for resource_type, amount in resources.items():
            quota = tenant.resource_quotas.get(resource_type)
            if not quota:
                continue

            if operation == "allocate":
                quota.used += amount
            elif operation == "deallocate":
                quota.used = max(0, quota.used - amount)

            quota.last_updated = datetime.now()

        # Update tenant metrics
        if tenant_id in self.tenant_metrics:
            metrics = self.tenant_metrics[tenant_id]
            for resource_type in ResourceType:
                quota = tenant.resource_quotas.get(resource_type)
                if quota and quota.allocated > 0:
                    metrics.resource_utilization[resource_type] = (quota.used / quota.allocated) * 100

            metrics.timestamp = datetime.now()

    def _get_tenant_namespace(self, tenant_id: str) -> Optional[TenantNamespace]:
        """Get tenant namespace by tenant ID."""
        for namespace in self.namespaces.values():
            if namespace.tenant_id == tenant_id:
                return namespace
        return None

    async def scale_tenant_resources(self, tenant_id: str, resource_changes: Dict[ResourceType, float]) -> bool:
        """Scale tenant resources up or down."""
        try:
            tenant = self.tenants.get(tenant_id)
            if not tenant:
                raise ValueError(f"Tenant not found: {tenant_id}")

            # Validate scaling request
            for resource_type, change in resource_changes.items():
                quota = tenant.resource_quotas.get(resource_type)
                if not quota:
                    continue

                new_allocation = quota.allocated + change
                if new_allocation < quota.used:
                    raise ValueError(
                        f"Cannot scale down {resource_type.value} below current usage: "
                        f"used={quota.used}, new_allocation={new_allocation}"
                    )

                # Check global resource limits
                global_limit = self.global_resource_pool.get(resource_type, float('inf'))
                if new_allocation > global_limit:
                    raise ValueError(
                        f"Scaling request exceeds global limit for {resource_type.value}: "
                        f"requested={new_allocation}, limit={global_limit}"
                    )

            # Apply scaling changes
            for resource_type, change in resource_changes.items():
                quota = tenant.resource_quotas.get(resource_type)
                if quota:
                    quota.allocated += change
                    quota.last_updated = datetime.now()

            tenant.updated_at = datetime.now()

            self.logger.info(f"Scaled resources for tenant {tenant_id}: {resource_changes}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to scale tenant resources: {e}")
            return False

    def get_tenant_dashboard_data(self, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a specific tenant."""
        try:
            tenant = self.tenants.get(tenant_id)
            if not tenant:
                return {"error": f"Tenant not found: {tenant_id}"}

            namespace = self._get_tenant_namespace(tenant_id)
            metrics = self.tenant_metrics.get(tenant_id)

            # Resource utilization
            resource_status = {}
            for resource_type, quota in tenant.resource_quotas.items():
                resource_key = resource_type.value if hasattr(resource_type, 'value') else str(resource_type)
                resource_status[resource_key] = {
                    "allocated": quota.allocated,
                    "used": quota.used,
                    "available": quota.allocated - quota.used - quota.reserved,
                    "utilization_percent": (quota.used / quota.allocated * 100) if quota.allocated > 0 else 0
                }

            # Agent instances
            agent_instances = []
            if namespace:
                for instance_id, config in namespace.agent_instances.items():
                    agent_instances.append({
                        "instance_id": instance_id,
                        "agent_type": config["agent_type"],
                        "status": "running",  # Would be determined by actual deployment
                        "resource_usage": config["resource_allocation"]
                    })

            dashboard_data = {
                "tenant_info": {
                    "tenant_id": tenant_id,
                    "name": tenant.tenant_name,
                    "tier": tenant.tier.value,
                    "isolation_level": tenant.isolation_level.value,
                    "created_at": tenant.created_at.isoformat(),
                    "active": tenant.active
                },
                "resource_status": resource_status,
                "agent_instances": agent_instances,
                "compliance_status": {
                    "requirements": tenant.compliance_requirements,
                    "current_status": "compliant"  # Would be determined by compliance checks
                },
                "metrics": {
                    "resource_utilization": metrics.resource_utilization if metrics else {},
                    "api_usage": metrics.api_usage if metrics else {},
                    "error_rates": metrics.error_rates if metrics else {}
                } if metrics else {},
                "security": {
                    "policies": tenant.security_policies,
                    "namespace": namespace.name if namespace else None,
                    "isolation_level": tenant.isolation_level.value
                }
            }

            return dashboard_data

        except Exception as e:
            self.logger.error(f"Error getting tenant dashboard data: {e}")
            return {"error": str(e)}

    def get_platform_dashboard_data(self) -> Dict[str, Any]:
        """Get platform-wide multi-tenant dashboard data."""
        try:
            # Tenant statistics
            tenant_stats = {
                "total_tenants": len(self.tenants),
                "active_tenants": len([t for t in self.tenants.values() if t.active]),
                "tier_distribution": {},
                "total_agent_instances": 0
            }

            # Count tenants by tier
            for tenant in self.tenants.values():
                tier = tenant.tier.value
                tenant_stats["tier_distribution"][tier] = tenant_stats["tier_distribution"].get(tier, 0) + 1

            # Count total agent instances
            for namespace in self.namespaces.values():
                tenant_stats["total_agent_instances"] += len(namespace.agent_instances)

            # Resource utilization across all tenants
            global_utilization = {}
            for resource_type in ResourceType:
                total_allocated = 0
                total_used = 0

                for tenant in self.tenants.values():
                    quota = tenant.resource_quotas.get(resource_type)
                    if quota:
                        total_allocated += quota.allocated
                        total_used += quota.used

                global_utilization[resource_type.value] = {
                    "total_allocated": total_allocated,
                    "total_used": total_used,
                    "utilization_percent": (total_used / total_allocated * 100) if total_allocated > 0 else 0,
                    "available_in_pool": self.global_resource_pool.get(resource_type, 0) - total_allocated
                }

            # Recent tenant activities
            recent_tenants = sorted(self.tenants.values(), key=lambda x: x.updated_at, reverse=True)[:10]
            recent_activities = [
                {
                    "tenant_id": t.tenant_id,
                    "name": t.tenant_name,
                    "tier": t.tier.value,
                    "last_activity": t.updated_at.isoformat()
                }
                for t in recent_tenants
            ]

            return {
                "tenant_statistics": tenant_stats,
                "global_resource_utilization": global_utilization,
                "recent_activities": recent_activities,
                "platform_health": {
                    "total_namespaces": len(self.namespaces),
                    "isolation_levels": list(set(t.isolation_level.value for t in self.tenants.values())),
                    "compliance_coverage": list(set(
                        req for tenant in self.tenants.values()
                        for req in tenant.compliance_requirements
                    ))
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting platform dashboard data: {e}")
            return {"error": str(e)}

    async def delete_tenant(self, tenant_id: str) -> bool:
        """Delete tenant and clean up all resources."""
        try:
            tenant = self.tenants.get(tenant_id)
            if not tenant:
                raise ValueError(f"Tenant not found: {tenant_id}")

            # Find and clean up namespace
            namespace = self._get_tenant_namespace(tenant_id)
            if namespace:
                # Deallocate all agent instances
                for instance_id, config in namespace.agent_instances.items():
                    await self._update_resource_usage(
                        tenant_id,
                        config["resource_allocation"],
                        "deallocate"
                    )

                # Remove namespace
                del self.namespaces[namespace.namespace_id]

            # Remove tenant and metrics
            del self.tenants[tenant_id]
            if tenant_id in self.tenant_metrics:
                del self.tenant_metrics[tenant_id]

            self.logger.info(f"Deleted tenant: {tenant_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete tenant {tenant_id}: {e}")
            return False

    async def shutdown(self):
        """Gracefully shutdown the multi-tenant manager."""
        try:
            self.logger.info("Shutting down Multi-Tenant Manager...")

            # Gracefully stop all tenant workloads
            for tenant_id in list(self.tenants.keys()):
                self.logger.info(f"  Stopping tenant workloads: {tenant_id}")
                # In production, this would gracefully stop agent instances

            self.logger.info("Multi-Tenant Manager shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during multi-tenant manager shutdown: {e}")


# Factory function for creating multi-tenant manager instance
def create_multi_tenant_manager() -> MultiTenantManager:
    """Create a new multi-tenant manager instance."""
    return MultiTenantManager()
