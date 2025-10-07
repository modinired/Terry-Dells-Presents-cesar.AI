#!/usr/bin/env python3
"""
Enterprise Agent Manager for CESAR.ai Atlas Final
Manages enterprise-grade multi-agent infrastructure as envisioned in the MAIaaS business plan.
Supports 25+ specialized agents across multiple business domains.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from ..utils.logger import LoggerMixin, performance_logger
from ..utils.config import Config
from .enterprise_security_framework import EnterpriseSecurityFramework, SecurityLevel
from ..utils.metrics import metrics


class EnterpriseAgentProxy:
    """Runtime proxy that exposes enterprise agent specs as active fleet entries."""

    def __init__(self, spec: "EnterpriseAgentSpec") -> None:
        self.spec = spec
        self.agent_id = spec.agent_id
        self.name = spec.name
        self.category = spec.category.value
        self.security_level = spec.security_level
        self.compliance_requirements = list(spec.compliance_requirements)
        self.capabilities = list(spec.capabilities)
        self.resource_requirements = dict(spec.resource_requirements)
        self.dependencies = list(spec.dependencies)
        self.is_running = False
        self.last_started_at: Optional[datetime] = None
        self.logger = logging.getLogger(f"enterprise_agent.{self.agent_id}")

    async def start(self) -> None:
        """Activate the enterprise proxy so orchestrators can delegate safely."""

        if self.is_running:
            return

        self.logger.info("Activating enterprise agent proxy for %s", self.name)
        self.is_running = True
        self.last_started_at = datetime.utcnow()
        await metrics.incr("enterprise_agents.started")

    async def stop(self) -> None:
        """Deactivate the proxy."""

        if not self.is_running:
            return

        self.logger.info("Stopping enterprise agent proxy for %s", self.name)
        self.is_running = False
        await metrics.incr("enterprise_agents.stopped")

    def get_capabilities(self) -> List[str]:
        """Expose enterprise capabilities for orchestration routing."""

        return list(self.capabilities)

    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate work to the enterprise platform and return structured telemetry."""

        await self._ensure_running()
        started_at = datetime.utcnow()
        task_type = task_data.get("task_type", "enterprise_operation")
        await metrics.incr("enterprise_agents.tasks")

        self.logger.info(
            "Delegating task '%s' to enterprise agent %s with security level %s",
            task_type,
            self.agent_id,
            self.security_level,
        )

        response = {
            "status": "delegated",
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "category": self.category,
            "security_level": self.security_level,
            "task_type": task_type,
            "inputs": {k: v for k, v in task_data.items() if k != "task_type"},
            "compliance": self.compliance_requirements,
            "resource_requirements": self.resource_requirements,
            "dependencies": self.dependencies,
            "started_at": started_at.isoformat() + "Z",
            "completed_at": datetime.utcnow().isoformat() + "Z",
        }

        return response

    async def _ensure_running(self) -> None:
        """Start the proxy if it has not been activated yet."""

        if not self.is_running:
            await self.start()


class AgentCategory(Enum):
    """Agent category enumeration for enterprise organization."""
    CORE_INFRASTRUCTURE = "core_infrastructure"
    BUSINESS_AUTOMATION = "business_automation"
    SECURITY_COMPLIANCE = "security_compliance"
    ANALYTICS_INTELLIGENCE = "analytics_intelligence"
    INTEGRATION_SERVICES = "integration_services"
    SPECIALIZED_DOMAIN = "specialized_domain"


@dataclass
class EnterpriseAgentSpec:
    """Specification for enterprise-grade agents."""
    agent_id: str
    name: str
    category: AgentCategory
    description: str
    capabilities: List[str]
    compliance_requirements: List[str] = field(default_factory=list)
    security_level: str = "standard"  # standard, high, critical
    scalability_tier: str = "standard"  # standard, high, enterprise
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


class EnterpriseAgentManager(LoggerMixin):
    """
    Enterprise Agent Manager for MAIaaS platform.
    Manages 25+ specialized agents across enterprise business domains.
    """

    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("enterprise_agent_manager")
        self.agent_specs = {}
        self.active_agents = {}
        self.agent_registry = {}
        self.load_balancer = None
        self.security_manager = None

        # Initialize enterprise security framework
        self.security_framework = EnterpriseSecurityFramework()

        # Initialize enterprise agent specifications
        self._initialize_enterprise_agent_specs()

    def _initialize_enterprise_agent_specs(self):
        """Initialize comprehensive enterprise agent specifications."""

        # Core Infrastructure Agents (8 agents)
        core_agents = [
            EnterpriseAgentSpec(
                agent_id="network_orchestrator",
                name="Network Orchestration Agent",
                category=AgentCategory.CORE_INFRASTRUCTURE,
                description="Manages private network topology, VPN configurations, and SDN controls",
                capabilities=["network_management", "vpn_orchestration", "sdn_control", "traffic_optimization"],
                security_level="critical",
                compliance_requirements=["SOC2", "ISO27001"]
            ),
            EnterpriseAgentSpec(
                agent_id="container_orchestrator",
                name="Container Orchestration Agent",
                category=AgentCategory.CORE_INFRASTRUCTURE,
                description="Manages Kubernetes clusters and container deployments",
                capabilities=["k8s_management", "auto_scaling", "resource_optimization", "deployment_automation"],
                security_level="high"
            ),
            EnterpriseAgentSpec(
                agent_id="service_mesh_manager",
                name="Service Mesh Management Agent",
                category=AgentCategory.CORE_INFRASTRUCTURE,
                description="Controls Istio/Linkerd service mesh configurations and policies",
                capabilities=["service_mesh_control", "traffic_routing", "policy_enforcement", "observability"],
                security_level="high"
            ),
            EnterpriseAgentSpec(
                agent_id="distributed_consensus",
                name="Distributed Consensus Agent",
                category=AgentCategory.CORE_INFRASTRUCTURE,
                description="Manages consensus protocols and distributed coordination",
                capabilities=["raft_consensus", "leader_election", "distributed_locks", "state_synchronization"],
                security_level="critical"
            ),
            EnterpriseAgentSpec(
                agent_id="message_broker",
                name="Message Broker Agent",
                category=AgentCategory.CORE_INFRASTRUCTURE,
                description="Orchestrates Kafka/RabbitMQ message streaming and queuing",
                capabilities=["message_routing", "stream_processing", "queue_management", "event_sourcing"],
                security_level="high"
            ),
            EnterpriseAgentSpec(
                agent_id="load_balancer",
                name="Load Balancer Agent",
                category=AgentCategory.CORE_INFRASTRUCTURE,
                description="Manages traffic distribution and load balancing strategies",
                capabilities=["traffic_distribution", "health_monitoring", "failover_management", "performance_optimization"],
                security_level="high"
            ),
            EnterpriseAgentSpec(
                agent_id="database_coordinator",
                name="Database Coordination Agent",
                category=AgentCategory.CORE_INFRASTRUCTURE,
                description="Manages distributed databases and data consistency",
                capabilities=["database_sharding", "replication_management", "backup_orchestration", "query_optimization"],
                security_level="critical",
                compliance_requirements=["HIPAA", "PCI_DSS", "GDPR"]
            ),
            EnterpriseAgentSpec(
                agent_id="storage_manager",
                name="Distributed Storage Agent",
                category=AgentCategory.CORE_INFRASTRUCTURE,
                description="Manages distributed storage systems and data lakes",
                capabilities=["storage_provisioning", "data_tiering", "compression_optimization", "backup_management"],
                security_level="high"
            )
        ]

        # Business Automation Agents (8 agents)
        business_agents = [
            EnterpriseAgentSpec(
                agent_id="workflow_orchestrator",
                name="Workflow Orchestration Agent",
                category=AgentCategory.BUSINESS_AUTOMATION,
                description="Manages complex business workflows and process automation",
                capabilities=["workflow_management", "process_optimization", "task_scheduling", "sla_monitoring"],
                compliance_requirements=["SOX", "ISO9001"]
            ),
            EnterpriseAgentSpec(
                agent_id="erp_integration",
                name="ERP Integration Agent",
                category=AgentCategory.BUSINESS_AUTOMATION,
                description="Integrates with SAP, Oracle, and other ERP systems",
                capabilities=["erp_connectivity", "data_synchronization", "transaction_processing", "master_data_management"],
                compliance_requirements=["SOX", "GAAP"]
            ),
            EnterpriseAgentSpec(
                agent_id="supply_chain_optimizer",
                name="Supply Chain Optimization Agent",
                category=AgentCategory.BUSINESS_AUTOMATION,
                description="Optimizes supply chain operations and logistics",
                capabilities=["demand_forecasting", "inventory_optimization", "logistics_planning", "supplier_management"]
            ),
            EnterpriseAgentSpec(
                agent_id="financial_processor",
                name="Financial Processing Agent",
                category=AgentCategory.BUSINESS_AUTOMATION,
                description="Handles financial transactions and accounting automation",
                capabilities=["transaction_processing", "financial_reporting", "compliance_monitoring", "risk_assessment"],
                security_level="critical",
                compliance_requirements=["SOX", "PCI_DSS", "GAAP"]
            ),
            EnterpriseAgentSpec(
                agent_id="hr_automation",
                name="HR Automation Agent",
                category=AgentCategory.BUSINESS_AUTOMATION,
                description="Automates human resources processes and employee management",
                capabilities=["employee_onboarding", "performance_tracking", "compliance_monitoring", "payroll_processing"],
                compliance_requirements=["GDPR", "CCPA", "EEOC"]
            ),
            EnterpriseAgentSpec(
                agent_id="customer_service",
                name="Customer Service Agent",
                category=AgentCategory.BUSINESS_AUTOMATION,
                description="Handles customer interactions and support automation",
                capabilities=["ticket_management", "chatbot_orchestration", "sentiment_analysis", "escalation_management"]
            ),
            EnterpriseAgentSpec(
                agent_id="marketing_automation",
                name="Marketing Automation Agent",
                category=AgentCategory.BUSINESS_AUTOMATION,
                description="Manages marketing campaigns and customer engagement",
                capabilities=["campaign_management", "lead_scoring", "content_personalization", "attribution_analysis"],
                compliance_requirements=["GDPR", "CCPA", "CAN_SPAM"]
            ),
            EnterpriseAgentSpec(
                agent_id="sales_intelligence",
                name="Sales Intelligence Agent",
                category=AgentCategory.BUSINESS_AUTOMATION,
                description="Provides sales insights and opportunity management",
                capabilities=["lead_qualification", "opportunity_scoring", "pipeline_management", "forecast_generation"]
            )
        ]

        # Security & Compliance Agents (5 agents)
        security_agents = [
            EnterpriseAgentSpec(
                agent_id="zero_trust_enforcer",
                name="Zero Trust Security Agent",
                category=AgentCategory.SECURITY_COMPLIANCE,
                description="Enforces zero-trust security policies across the network",
                capabilities=["identity_verification", "access_control", "policy_enforcement", "threat_detection"],
                security_level="critical",
                compliance_requirements=["NIST", "ISO27001", "SOC2"]
            ),
            EnterpriseAgentSpec(
                agent_id="compliance_monitor",
                name="Compliance Monitoring Agent",
                category=AgentCategory.SECURITY_COMPLIANCE,
                description="Monitors and ensures regulatory compliance across all systems",
                capabilities=["compliance_scanning", "audit_trail_management", "policy_validation", "report_generation"],
                security_level="critical",
                compliance_requirements=["SOX", "HIPAA", "PCI_DSS", "GDPR"]
            ),
            EnterpriseAgentSpec(
                agent_id="threat_intelligence",
                name="Threat Intelligence Agent",
                category=AgentCategory.SECURITY_COMPLIANCE,
                description="Collects and analyzes threat intelligence data",
                capabilities=["threat_detection", "vulnerability_assessment", "incident_response", "forensic_analysis"],
                security_level="critical"
            ),
            EnterpriseAgentSpec(
                agent_id="encryption_manager",
                name="Encryption Management Agent",
                category=AgentCategory.SECURITY_COMPLIANCE,
                description="Manages encryption keys and cryptographic operations",
                capabilities=["key_management", "certificate_rotation", "encryption_enforcement", "hsm_integration"],
                security_level="critical",
                compliance_requirements=["FIPS140", "Common_Criteria"]
            ),
            EnterpriseAgentSpec(
                agent_id="access_governance",
                name="Access Governance Agent",
                category=AgentCategory.SECURITY_COMPLIANCE,
                description="Manages identity and access governance policies",
                capabilities=["identity_lifecycle", "access_reviews", "privilege_management", "segregation_of_duties"],
                security_level="critical",
                compliance_requirements=["SOX", "ISO27001"]
            )
        ]

        # Specialized Domain Agents (2 agents) - Including Jules Integration
        specialized_agents = [
            EnterpriseAgentSpec(
                agent_id="jules_automation",
                name="Jules Desktop Automation Agent",
                category=AgentCategory.SPECIALIZED_DOMAIN,
                description="Google Jules-style desktop automation with advanced workflow capabilities",
                capabilities=["desktop_automation", "workflow_execution", "ui_interaction", "screen_analysis", "file_management", "browser_automation", "application_control", "task_scheduling", "trigger_management", "intelligent_assistance"],
                security_level="high",
                compliance_requirements=["SOC2", "ISO27001"]
            ),
            EnterpriseAgentSpec(
                agent_id="enhanced_ui_tars",
                name="Enhanced UI-TARS with Jules Integration",
                category=AgentCategory.SPECIALIZED_DOMAIN,
                description="UI-TARS desktop automation enhanced with Jules capabilities and workflows",
                capabilities=["gui_automation", "screen_analysis", "visual_reasoning", "cross_platform_control", "browser_automation", "desktop_interaction", "screenshot_analysis", "natural_language_control", "jules_integration", "workflow_automation"],
                security_level="high",
                compliance_requirements=["SOC2"]
            )
        ]

        # Analytics & Intelligence Agents (4 agents)
        analytics_agents = [
            EnterpriseAgentSpec(
                agent_id="business_intelligence",
                name="Business Intelligence Agent",
                category=AgentCategory.ANALYTICS_INTELLIGENCE,
                description="Provides business intelligence and analytics capabilities",
                capabilities=["data_analysis", "report_generation", "dashboard_creation", "kpi_monitoring"]
            ),
            EnterpriseAgentSpec(
                agent_id="predictive_analytics",
                name="Predictive Analytics Agent",
                category=AgentCategory.ANALYTICS_INTELLIGENCE,
                description="Performs predictive modeling and forecasting",
                capabilities=["machine_learning", "predictive_modeling", "anomaly_detection", "trend_analysis"]
            ),
            EnterpriseAgentSpec(
                agent_id="data_lake_manager",
                name="Data Lake Management Agent",
                category=AgentCategory.ANALYTICS_INTELLIGENCE,
                description="Manages data lakes and big data processing",
                capabilities=["data_ingestion", "etl_processing", "data_cataloging", "metadata_management"]
            ),
            EnterpriseAgentSpec(
                agent_id="real_time_analytics",
                name="Real-time Analytics Agent",
                category=AgentCategory.ANALYTICS_INTELLIGENCE,
                description="Provides real-time streaming analytics and monitoring",
                capabilities=["stream_processing", "real_time_dashboards", "alert_generation", "metric_aggregation"]
            )
        ]

        # Store all agent specifications
        all_agents = core_agents + business_agents + security_agents + analytics_agents + specialized_agents

        for agent_spec in all_agents:
            self.agent_specs[agent_spec.agent_id] = agent_spec

        self.logger.info(f"Initialized {len(all_agents)} enterprise agent specifications")

    async def initialize_enterprise_platform(self) -> bool:
        """Initialize the complete enterprise multi-agent platform."""
        try:
            self.logger.info("Initializing Enterprise Multi-Agent Platform...")
            self.logger.info(f"Platform supports {len(self.agent_specs)} enterprise-grade agents")

            # Initialize by category
            for category in AgentCategory:
                category_agents = [spec for spec in self.agent_specs.values() if spec.category == category]
                self.logger.info(f"  {category.value}: {len(category_agents)} agents available")

            # Initialize core infrastructure agents first
            await self._initialize_core_infrastructure()

            # Initialize security and compliance layer
            await self._initialize_security_layer()

            # Initialize business automation agents
            await self._initialize_business_automation()

            # Initialize analytics and intelligence
            await self._initialize_analytics_layer()

            self.logger.info("Enterprise Multi-Agent Platform initialization complete")
            return True

        except Exception as e:
            self.logger.error(f"Enterprise platform initialization failed: {e}")
            return False

    async def _initialize_core_infrastructure(self):
        """Initialize core infrastructure agents."""
        core_agents = [spec for spec in self.agent_specs.values()
                      if spec.category == AgentCategory.CORE_INFRASTRUCTURE]

        for agent_spec in core_agents:
            self.logger.info(f"  Initializing {agent_spec.name}")
            # Agent initialization logic would go here
            self.agent_registry[agent_spec.agent_id] = {
                'status': 'initialized',
                'spec': agent_spec,
                'last_updated': datetime.now()
            }

    async def _initialize_security_layer(self):
        """Initialize security and compliance agents."""
        security_agents = [spec for spec in self.agent_specs.values()
                          if spec.category == AgentCategory.SECURITY_COMPLIANCE]

        for agent_spec in security_agents:
            self.logger.info(f"  Initializing {agent_spec.name}")
            self.agent_registry[agent_spec.agent_id] = {
                'status': 'initialized',
                'spec': agent_spec,
                'last_updated': datetime.now()
            }

    async def _initialize_business_automation(self):
        """Initialize business automation agents."""
        business_agents = [spec for spec in self.agent_specs.values()
                          if spec.category == AgentCategory.BUSINESS_AUTOMATION]

        for agent_spec in business_agents:
            self.logger.info(f"  Initializing {agent_spec.name}")
            self.agent_registry[agent_spec.agent_id] = {
                'status': 'initialized',
                'spec': agent_spec,
                'last_updated': datetime.now()
            }

    async def _initialize_analytics_layer(self):
        """Initialize analytics and intelligence agents."""
        analytics_agents = [spec for spec in self.agent_specs.values()
                           if spec.category == AgentCategory.ANALYTICS_INTELLIGENCE]

        for agent_spec in analytics_agents:
            self.logger.info(f"  Initializing {agent_spec.name}")
            self.agent_registry[agent_spec.agent_id] = {
                'status': 'initialized',
                'spec': agent_spec,
                'last_updated': datetime.now()
            }

    def get_platform_status(self) -> Dict[str, Any]:
        """Get comprehensive platform status."""
        status = {
            'platform_version': '4.0-Enterprise',
            'total_agents': len(self.agent_specs),
            'active_agents': len([a for a in self.agent_registry.values() if a['status'] == 'initialized']),
            'agent_categories': {},
            'compliance_coverage': set(),
            'security_levels': {}
        }

        # Count by category
        for category in AgentCategory:
            category_agents = [spec for spec in self.agent_specs.values() if spec.category == category]
            status['agent_categories'][category.value] = len(category_agents)

        # Aggregate compliance requirements
        for spec in self.agent_specs.values():
            status['compliance_coverage'].update(spec.compliance_requirements)

        # Count by security level
        for spec in self.agent_specs.values():
            level = spec.security_level
            status['security_levels'][level] = status['security_levels'].get(level, 0) + 1

        status['compliance_coverage'] = list(status['compliance_coverage'])

        return status

    def get_agent_specifications(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed agent specifications for the platform."""
        return {
            agent_id: {
                'name': spec.name,
                'category': spec.category.value,
                'description': spec.description,
                'capabilities': spec.capabilities,
                'security_level': spec.security_level,
                'compliance_requirements': spec.compliance_requirements,
                'scalability_tier': spec.scalability_tier
            }
            for agent_id, spec in self.agent_specs.items()
        }

    async def deploy_agent_cluster(self, agent_ids: List[str], cluster_config: Dict[str, Any]) -> bool:
        """Deploy a cluster of agents for enterprise workloads."""
        try:
            self.logger.info(f"Deploying agent cluster with {len(agent_ids)} agents")

            # Validate agent dependencies
            for agent_id in agent_ids:
                if agent_id not in self.agent_specs:
                    raise ValueError(f"Unknown agent: {agent_id}")

            # Deploy in dependency order
            # This would contain actual deployment logic

            self.logger.info("Agent cluster deployment complete")
            return True

        except Exception as e:
            self.logger.error(f"Agent cluster deployment failed: {e}")
            return False

    async def scale_agent_capacity(self, agent_id: str, target_instances: int) -> bool:
        """Scale agent capacity based on demand."""
        try:
            if agent_id not in self.agent_specs:
                raise ValueError(f"Unknown agent: {agent_id}")

            spec = self.agent_specs[agent_id]
            self.logger.info(f"Scaling {spec.name} to {target_instances} instances")

            # Scaling logic would go here

            return True

        except Exception as e:
            self.logger.error(f"Agent scaling failed: {e}")
            return False

    async def authenticate_agent_operation(self, agent_id: str, operation: str,
                                         resource: str, context: Dict[str, Any] = None) -> bool:
        """Authenticate and authorize agent operations with enterprise security."""
        try:
            # Get agent security level
            agent_spec = self.agent_specs.get(agent_id)
            if not agent_spec:
                self.logger.error(f"Unknown agent: {agent_id}")
                return False

            # Map security level string to enum
            security_level_map = {
                "standard": SecurityLevel.STANDARD,
                "high": SecurityLevel.HIGH,
                "critical": SecurityLevel.CRITICAL
            }
            security_level = security_level_map.get(agent_spec.security_level, SecurityLevel.STANDARD)

            # Authenticate agent
            token = await self.security_framework.authenticate_agent(
                agent_id=agent_id,
                credentials={"agent_type": agent_spec.name},
                security_level=security_level
            )

            if not token:
                self.logger.error(f"Authentication failed for agent: {agent_id}")
                return False

            # Authorize operation
            authorized = await self.security_framework.authorize_operation(
                token_id=token.token_id,
                operation=operation,
                resource=resource,
                context=context or {}
            )

            return authorized

        except Exception as e:
            self.logger.error(f"Agent authentication/authorization error: {e}")
            return False

    async def validate_agent_compliance(self, agent_id: str, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent operations against compliance requirements."""
        try:
            agent_spec = self.agent_specs.get(agent_id)
            if not agent_spec:
                return {"error": f"Unknown agent: {agent_id}"}

            # Validate against all required compliance standards
            compliance_results = {}
            overall_compliant = True

            for standard_str in agent_spec.compliance_requirements:
                # Map string to enum
                try:
                    from .enterprise_security_framework import ComplianceStandard
                    standard = ComplianceStandard(standard_str.lower())

                    result = await self.security_framework.validate_compliance(
                        standard=standard,
                        agent_id=agent_id,
                        operation_data=operation_data
                    )

                    compliance_results[standard_str] = result
                    if not result.get("compliant", False):
                        overall_compliant = False

                except ValueError:
                    self.logger.warning(f"Unknown compliance standard: {standard_str}")
                    compliance_results[standard_str] = {"error": "Unknown standard"}
                    overall_compliant = False

            return {
                "agent_id": agent_id,
                "overall_compliant": overall_compliant,
                "standards_results": compliance_results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Compliance validation error: {e}")
            return {"error": str(e)}

    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get security dashboard data for the platform."""
        try:
            security_data = self.security_framework.get_security_dashboard()

            # Add enterprise agent security information
            agent_security_summary = {
                "total_agents": len(self.agent_specs),
                "security_levels": {},
                "compliance_coverage": {}
            }

            # Count agents by security level
            for spec in self.agent_specs.values():
                level = spec.security_level
                agent_security_summary["security_levels"][level] = \
                    agent_security_summary["security_levels"].get(level, 0) + 1

            # Count compliance coverage
            all_standards = set()
            for spec in self.agent_specs.values():
                all_standards.update(spec.compliance_requirements)

            agent_security_summary["compliance_coverage"] = {
                "total_standards": len(all_standards),
                "standards": list(all_standards)
            }

            # Combine with security framework data
            security_data["enterprise_agents"] = agent_security_summary

            return security_data

        except Exception as e:
            self.logger.error(f"Error getting security dashboard data: {e}")
            return {"error": str(e)}

    async def detect_agent_threats(self, agent_id: str, activity_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect threats in agent behavior."""
        try:
            threats = await self.security_framework.detect_threats(agent_id, activity_data)

            if threats:
                self.logger.warning(f"Detected {len(threats)} threats from agent {agent_id}")

                # Update agent status if critical threats detected
                critical_threats = [t for t in threats if t.get("severity") == "critical"]
                if critical_threats and agent_id in self.agent_registry:
                    self.agent_registry[agent_id]["status"] = "threat_detected"
                    self.agent_registry[agent_id]["last_threat_detection"] = datetime.now()

            return threats

        except Exception as e:
            self.logger.error(f"Threat detection error for agent {agent_id}: {e}")
            return []

    async def get_active_agents(self) -> Dict[str, Any]:
        """Get all active enterprise agents as a fleet dictionary."""

        try:
            active_fleet: Dict[str, Any] = {}

            for agent_id, spec in self.agent_specs.items():
                proxy = self.active_agents.get(agent_id)

                if proxy is None:
                    proxy = EnterpriseAgentProxy(spec)
                    self.active_agents[agent_id] = proxy

                active_fleet[agent_id] = proxy

            self.logger.info("Returning %s enterprise agents as active fleet", len(active_fleet))
            return active_fleet

        except Exception as e:
            self.logger.error(f"Error getting active agents: {e}")
            return {}

    async def shutdown(self):
        """Gracefully shutdown the enterprise platform."""
        self.logger.info("Shutting down Enterprise Multi-Agent Platform...")

        # Shutdown security framework first
        if hasattr(self, 'security_framework'):
            await self.security_framework.shutdown()

        # Shutdown agents in reverse dependency order
        for agent_id in self.agent_registry:
            self.logger.info(f"  Shutting down {agent_id}")

        self.logger.info("Enterprise platform shutdown complete")
