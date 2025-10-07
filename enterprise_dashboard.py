#!/usr/bin/env python3
"""
Enterprise Dashboard for CESAR.ai Atlas Final MAIaaS Platform
Provides comprehensive monitoring and management for 25+ enterprise agents
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import json

# Import enterprise components
from .core.enterprise_agent_manager import EnterpriseAgentManager
from .core.multi_tenant_manager import MultiTenantManager

# Create FastAPI app
app = FastAPI(
    title="CESAR.ai Atlas Final - Enterprise MAIaaS Dashboard",
    description="Multi-Agent Infrastructure as a Service - Enterprise Platform",
    version="4.0-Enterprise"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize enterprise components
enterprise_manager = EnterpriseAgentManager()
multi_tenant_manager = MultiTenantManager()
workflow_store = Path(__file__).parent / "generated_assets" / "workflow_events.json"

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Enterprise dashboard with comprehensive agent monitoring."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CESAR.ai Atlas Final - Enterprise MAIaaS Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #0a0a0a 100%);
            background-size: 400% 400%;
            animation: enterpriseGlow 12s ease-in-out infinite;
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        @keyframes enterpriseGlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .header {
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #00ffcc;
            box-shadow: 0 4px 20px rgba(0, 255, 204, 0.3);
        }

        .header h1 {
            font-size: 2.5rem;
            color: #00ffcc;
            text-shadow: 0 0 20px rgba(0, 255, 204, 0.8);
            margin-bottom: 10px;
        }

        .header .subtitle {
            font-size: 1.2rem;
            color: #ffffff;
            opacity: 0.9;
        }

        .platform-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(0, 255, 204, 0.3);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            border-color: #00ffcc;
            box-shadow: 0 8px 25px rgba(0, 255, 204, 0.3);
            transform: translateY(-5px);
        }

        .stat-card h3 {
            color: #00ffcc;
            font-size: 1.5rem;
            margin-bottom: 10px;
        }

        .stat-card .value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 5px;
        }

        .agent-categories {
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .category-section {
            margin-bottom: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(0, 255, 204, 0.2);
        }

        .category-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(0, 255, 204, 0.3);
        }

        .category-header h2 {
            color: #00ffcc;
            font-size: 1.8rem;
            margin-right: 15px;
        }

        .category-badge {
            background: rgba(0, 255, 204, 0.2);
            color: #00ffcc;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
        }

        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }

        .agent-card {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(0, 255, 204, 0.2);
            border-radius: 10px;
            padding: 15px;
            transition: all 0.3s ease;
        }

        .agent-card:hover {
            border-color: #00ffcc;
            box-shadow: 0 5px 15px rgba(0, 255, 204, 0.2);
        }

        .agent-card h4 {
            color: #ffffff;
            margin-bottom: 8px;
            font-size: 1.1rem;
        }

        .agent-card p {
            color: #cccccc;
            font-size: 0.9rem;
            line-height: 1.4;
            margin-bottom: 10px;
        }

        .agent-status {
            display: inline-block;
            background: rgba(0, 255, 0, 0.2);
            color: #00ff00;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
        }

        .security-level {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-left: 5px;
        }

        .security-critical { background: rgba(255, 0, 0, 0.2); color: #ff6666; }
        .security-high { background: rgba(255, 165, 0, 0.2); color: #ffaa66; }
        .security-standard { background: rgba(0, 255, 204, 0.2); color: #00ffcc; }

        .capabilities {
            margin-top: 10px;
        }

        .capability-tag {
            display: inline-block;
            background: rgba(0, 255, 204, 0.1);
            color: #00ffcc;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 0.75rem;
            margin: 2px;
        }

        .footer {
            text-align: center;
            padding: 30px;
            color: #cccccc;
            border-top: 1px solid rgba(0, 255, 204, 0.3);
            margin-top: 40px;
        }

        @media (max-width: 768px) {
            .platform-stats {
                grid-template-columns: 1fr;
                padding: 20px;
            }

            .header h1 {
                font-size: 2rem;
            }

            .agents-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 CESAR.ai Atlas Final</h1>
        <p class="subtitle">Multi-Agent Infrastructure as a Service (MAIaaS) - Enterprise Platform</p>
    </div>

    <div class="platform-stats">
        <div class="stat-card">
            <h3>Total Agents</h3>
            <div class="value" id="total-agents">25</div>
            <p>Enterprise-Grade Agents</p>
        </div>
        <div class="stat-card">
            <h3>Active Agents</h3>
            <div class="value" id="active-agents">25</div>
            <p>Currently Running</p>
        </div>
        <div class="stat-card">
            <h3>Categories</h3>
            <div class="value" id="categories">4</div>
            <p>Specialized Domains</p>
        </div>
        <div class="stat-card">
            <h3>Compliance</h3>
            <div class="value" id="compliance">12</div>
            <p>Standards Covered</p>
        </div>
    </div>

    <div class="agent-categories">
        <div class="category-section">
            <div class="category-header">
                <h2>🏗️ Core Infrastructure</h2>
                <span class="category-badge">8 Agents</span>
            </div>
            <div class="agents-grid" id="core-infrastructure">
                <!-- Core infrastructure agents will be populated here -->
            </div>
        </div>

        <div class="category-section">
            <div class="category-header">
                <h2>💼 Business Automation</h2>
                <span class="category-badge">8 Agents</span>
            </div>
            <div class="agents-grid" id="business-automation">
                <!-- Business automation agents will be populated here -->
            </div>
        </div>

        <div class="category-section">
            <div class="category-header">
                <h2>🔒 Security & Compliance</h2>
                <span class="category-badge">5 Agents</span>
            </div>
            <div class="agents-grid" id="security-compliance">
                <!-- Security & compliance agents will be populated here -->
            </div>
        </div>

        <div class="category-section">
            <div class="category-header">
                <h2>📊 Analytics & Intelligence</h2>
                <span class="category-badge">4 Agents</span>
            </div>
            <div class="agents-grid" id="analytics-intelligence">
                <!-- Analytics & intelligence agents will be populated here -->
            </div>
        </div>
    </div>

    <div class="footer">
        <p>CESAR.ai Atlas Final v4.0-Enterprise | Multi-Agent Infrastructure as a Service</p>
        <p>Providing scalable, secure, and compliant multi-agent solutions for enterprise environments</p>
    </div>

    <script>
        async function loadPlatformData() {
            try {
                const response = await fetch('/api/platform/status');
                const data = await response.json();

                // Update platform stats
                document.getElementById('total-agents').textContent = data.total_agents;
                document.getElementById('active-agents').textContent = data.active_agents;
                document.getElementById('categories').textContent = Object.keys(data.agent_categories).length;
                document.getElementById('compliance').textContent = data.compliance_coverage.length;

                // Load agent specifications
                const specsResponse = await fetch('/api/platform/agents');
                const specs = await specsResponse.json();

                // Populate agent cards by category
                populateAgentCards(specs, data);

            } catch (error) {
                console.error('Error loading platform data:', error);
            }
        }

        function populateAgentCards(specs, platformData) {
            const categories = {
                'core_infrastructure': document.getElementById('core-infrastructure'),
                'business_automation': document.getElementById('business-automation'),
                'security_compliance': document.getElementById('security-compliance'),
                'analytics_intelligence': document.getElementById('analytics-intelligence')
            };

            Object.entries(specs).forEach(([agentId, spec]) => {
                const container = categories[spec.category];
                if (container) {
                    const agentCard = createAgentCard(agentId, spec);
                    container.appendChild(agentCard);
                }
            });
        }

        function createAgentCard(agentId, spec) {
            const card = document.createElement('div');
            card.className = 'agent-card';

            const securityClass = `security-${spec.security_level}`;
            const capabilityTags = spec.capabilities.map(cap =>
                `<span class="capability-tag">${cap}</span>`
            ).join('');

            card.innerHTML = `
                <h4>${spec.name}</h4>
                <p>${spec.description}</p>
                <div>
                    <span class="agent-status">✅ Active</span>
                    <span class="security-level ${securityClass}">${spec.security_level.toUpperCase()}</span>
                </div>
                <div class="capabilities">
                    ${capabilityTags}
                </div>
            `;

            return card;
        }

        // Load data when page loads
        document.addEventListener('DOMContentLoaded', loadPlatformData);

        // Refresh data every 30 seconds
        setInterval(loadPlatformData, 30000);
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)

@app.get("/api/platform/status")
async def get_platform_status():
    """Get comprehensive platform status."""
    try:
        status = enterprise_manager.get_platform_status()
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/platform/agents")
async def get_agent_specifications():
    """Get detailed agent specifications."""
    try:
        specs = enterprise_manager.get_agent_specifications()
        return JSONResponse(content=specs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/platform/health")
async def platform_health():
    """Platform health check endpoint."""
    return {
        "status": "healthy",
        "platform": "CESAR.ai Atlas Final",
        "version": "4.0-Enterprise",
        "timestamp": datetime.now().isoformat(),
        "service": "MAIaaS Platform"
    }


@app.get("/api/platform/workflows")
async def platform_workflows():
    """Expose modernization workflow telemetry captured by Terry orchestrator."""

    if workflow_store.exists():
        try:
            return json.loads(workflow_store.read_text())
        except json.JSONDecodeError:
            return {"workflows": {}, "error": "unparsable_event_store"}
    return {"workflows": {}, "message": "no workflows recorded"}

@app.post("/api/agents/deploy")
async def deploy_agent_cluster(deployment_config: Dict[str, Any]):
    """Deploy a cluster of agents."""
    try:
        agent_ids = deployment_config.get("agent_ids", [])
        cluster_config = deployment_config.get("cluster_config", {})

        success = await enterprise_manager.deploy_agent_cluster(agent_ids, cluster_config)

        if success:
            return {"status": "success", "message": "Agent cluster deployed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Agent cluster deployment failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/{agent_id}/scale")
async def scale_agent(agent_id: str, scale_config: Dict[str, Any]):
    """Scale agent capacity."""
    try:
        target_instances = scale_config.get("target_instances", 1)

        success = await enterprise_manager.scale_agent_capacity(agent_id, target_instances)

        if success:
            return {"status": "success", "message": f"Agent {agent_id} scaled to {target_instances} instances"}
        else:
            raise HTTPException(status_code=500, detail="Agent scaling failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tenants")
async def get_tenants():
    """Get all tenants and their status."""
    try:
        platform_data = multi_tenant_manager.get_platform_dashboard_data()
        return JSONResponse(content=platform_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tenants/{tenant_id}")
async def get_tenant_details(tenant_id: str):
    """Get detailed information for a specific tenant."""
    try:
        tenant_data = multi_tenant_manager.get_tenant_dashboard_data(tenant_id)
        return JSONResponse(content=tenant_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tenants/create")
async def create_tenant(tenant_request: Dict[str, Any]):
    """Create a new tenant."""
    try:
        from .core.multi_tenant_manager import TenantTier

        tenant_name = tenant_request.get("name", "")
        tier_str = tenant_request.get("tier", "starter")
        custom_config = tenant_request.get("custom_config", {})

        # Map tier string to enum
        tier_map = {
            "starter": TenantTier.STARTER,
            "professional": TenantTier.PROFESSIONAL,
            "enterprise": TenantTier.ENTERPRISE,
            "ultimate": TenantTier.ULTIMATE
        }

        tier = tier_map.get(tier_str.lower(), TenantTier.STARTER)

        tenant_id = await multi_tenant_manager.create_tenant(
            tenant_name=tenant_name,
            tier=tier,
            custom_config=custom_config
        )

        return {
            "status": "success",
            "tenant_id": tenant_id,
            "message": f"Tenant '{tenant_name}' created successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tenants/{tenant_id}/agents/deploy")
async def deploy_agent_to_tenant(tenant_id: str, deployment_request: Dict[str, Any]):
    """Deploy an agent to a specific tenant."""
    try:
        agent_type = deployment_request.get("agent_type", "")
        agent_config = deployment_request.get("config", {})

        result = await multi_tenant_manager.allocate_agent_to_tenant(
            tenant_id=tenant_id,
            agent_type=agent_type,
            agent_config=agent_config
        )

        return {
            "status": "success",
            "agent_instance_id": result["agent_instance_id"],
            "message": f"Agent {agent_type} deployed to tenant {tenant_id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/security/dashboard")
async def get_security_dashboard():
    """Get comprehensive security dashboard data."""
    try:
        security_data = enterprise_manager.get_security_dashboard_data()
        return JSONResponse(content=security_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/security/validate-compliance")
async def validate_compliance(validation_request: Dict[str, Any]):
    """Validate compliance for agent operations."""
    try:
        agent_id = validation_request.get("agent_id", "")
        operation_data = validation_request.get("operation_data", {})

        result = await enterprise_manager.validate_agent_compliance(
            agent_id=agent_id,
            operation_data=operation_data
        )

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting CESAR.ai Atlas Final - Enterprise MAIaaS Dashboard")
    print("   Enterprise Platform: http://localhost:9000")
    print("   25+ Enterprise Agents Available")
    print("   Multi-Agent Infrastructure as a Service (MAIaaS)")

    uvicorn.run(app, host="0.0.0.0", port=9000)
