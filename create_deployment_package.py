#!/usr/bin/env python3
"""
Create Deployment Package for Terry Delmonaco Manager Agent
Version: 3.2
Description: Creates deployment packages for various platforms
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class DeploymentPackageCreator:
    """Creates deployment packages for different platforms."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.package_dir = self.project_root / "deployment_packages"
        self.package_dir.mkdir(exist_ok=True)
    
    def create_docker_package(self) -> str:
        """Create Docker deployment package."""
        package_name = f"td-manager-agent-docker-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        package_path = self.package_dir / package_name
        
        # Create package structure
        package_path.mkdir(exist_ok=True)
        
        # Copy essential files
        essential_files = [
            "Dockerfile",
            "docker-compose.yml",
            "requirements.txt",
            "main_orchestrator.py",
            "app.py",
            "cursor_config.json",
            "background_agents_config.json"
        ]
        
        for file_name in essential_files:
            src = self.project_root / file_name
            if src.exists():
                shutil.copy2(src, package_path)
        
        # Copy directories
        directories = ["agents", "core", "utils", "communication"]
        for dir_name in directories:
            src_dir = self.project_root / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, package_path / dir_name, dirs_exist_ok=True)
        
        # Create deployment script
        deploy_script = package_path / "deploy.sh"
        with open(deploy_script, 'w') as f:
            f.write("""#!/bin/bash
echo "🚀 Deploying Terry Delmonaco Manager Agent..."
docker-compose up -d
echo "✅ Deployment complete!"
""")
        os.chmod(deploy_script, 0o755)
        
        return str(package_path)
    
    def create_vertex_ai_package(self) -> str:
        """Create Vertex AI deployment package."""
        package_name = f"td-manager-agent-vertex-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        package_path = self.package_dir / package_name
        
        # Create package structure
        package_path.mkdir(exist_ok=True)
        
        # Copy Vertex AI specific files
        vertex_files = [
            "vertex-ai-deployment.yaml",
            "deploy-vertex-ai.sh",
            "requirements.txt",
            "main_orchestrator.py",
            "app.py"
        ]
        
        for file_name in vertex_files:
            src = self.project_root / file_name
            if src.exists():
                shutil.copy2(src, package_path)
        
        # Copy directories
        directories = ["agents", "core", "utils", "communication"]
        for dir_name in directories:
            src_dir = self.project_root / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, package_path / dir_name, dirs_exist_ok=True)
        
        return str(package_path)
    
    def create_kubernetes_package(self) -> str:
        """Create Kubernetes deployment package."""
        package_name = f"td-manager-agent-k8s-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        package_path = self.package_dir / package_name
        
        # Create package structure
        package_path.mkdir(exist_ok=True)
        
        # Copy Kubernetes specific files
        k8s_files = [
            "vertex-ai-deployment.yaml",
            "requirements.txt",
            "main_orchestrator.py",
            "app.py"
        ]
        
        for file_name in k8s_files:
            src = self.project_root / file_name
            if src.exists():
                shutil.copy2(src, package_path)
        
        # Copy directories
        directories = ["agents", "core", "utils", "communication"]
        for dir_name in directories:
            src_dir = self.project_root / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, package_path / dir_name, dirs_exist_ok=True)
        
        return str(package_path)
    
    def create_zip_package(self, package_path: str) -> str:
        """Create a zip file from the package directory."""
        zip_path = Path(package_path).with_suffix('.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, package_path)
                    zipf.write(file_path, arcname)
        
        return str(zip_path)


def main():
    """Main function to create deployment packages."""
    creator = DeploymentPackageCreator()
    
    print("🚀 Creating deployment packages for Terry Delmonaco Manager Agent...")
    
    # Create Docker package
    docker_package = creator.create_docker_package()
    print(f"✅ Docker package created: {docker_package}")
    
    # Create Vertex AI package
    vertex_package = creator.create_vertex_ai_package()
    print(f"✅ Vertex AI package created: {vertex_package}")
    
    # Create Kubernetes package
    k8s_package = creator.create_kubernetes_package()
    print(f"✅ Kubernetes package created: {k8s_package}")
    
    # Create zip files
    docker_zip = creator.create_zip_package(docker_package)
    vertex_zip = creator.create_zip_package(vertex_package)
    k8s_zip = creator.create_zip_package(k8s_package)
    
    print(f"✅ Zip packages created:")
    print(f"   - Docker: {docker_zip}")
    print(f"   - Vertex AI: {vertex_zip}")
    print(f"   - Kubernetes: {k8s_zip}")
    
    print("🎉 Deployment package creation complete!")


if __name__ == "__main__":
    main() 