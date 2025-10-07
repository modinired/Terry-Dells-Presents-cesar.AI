#!/usr/bin/env python3
"""
Setup script for background agents with proper git repository initialization.
This script ensures the git repository is properly configured before running background agents.
"""

import subprocess
import json
import os
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def setup_git_repository():
    """Initialize and configure git repository for background agents."""
    print("🔧 Setting up git repository for background agents...")
    
    # Check if we're in a git repository
    success, stdout, stderr = run_command("git status")
    
    if not success:
        print("📁 Initializing git repository...")
        success, stdout, stderr = run_command("git init")
        if not success:
            print(f"❌ Failed to initialize git repository: {stderr}")
            return False
    
    # Check for remotes
    success, stdout, stderr = run_command("git remote -v")
    if not stdout.strip():
        print("🌐 No git remotes found. Creating a default remote...")
        # Create a default remote (you can modify this URL)
        remote_url = "https://github.com/your-username/td_manager_agent.git"
        success, stdout, stderr = run_command(f'git remote add origin "{remote_url}"')
        if not success:
            print(f"⚠️  Warning: Could not add remote origin: {stderr}")
            print("   Background agents will work without remote tracking")
    
    # Create initial commit if no commits exist
    success, stdout, stderr = run_command("git log --oneline -1")
    if not stdout.strip():
        print("📝 Creating initial commit...")
        run_command("git add .")
        success, stdout, stderr = run_command('git commit -m "Initial commit for background agents"')
        if not success:
            print(f"⚠️  Warning: Could not create initial commit: {stderr}")
    
    print("✅ Git repository setup complete")
    return True

def create_background_agent_files():
    """Create necessary files for background agents."""
    print("📄 Creating background agent files...")
    
    # Create .gitignore entries for background agent files
    gitignore_entries = [
        "# Background agent files",
        ".audit_findings.json",
        ".memory.json",
        "*.fixed",
        ".background_agents/"
    ]
    
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            content = f.read()
        
        # Add entries if they don't exist
        for entry in gitignore_entries:
            if entry not in content:
                with open(gitignore_path, "a") as f:
                    f.write(f"\n{entry}")
    else:
        with open(gitignore_path, "w") as f:
            f.write("\n".join(gitignore_entries))
    
    # Create initial memory file
    initial_memory = {
        "findings": [],
        "last_audit": None,
        "session_id": "initial"
    }
    
    with open(".memory.json", "w") as f:
        json.dump(initial_memory, f, indent=2)
    
    # Create initial audit findings file
    initial_findings = {
        "audit_date": None,
        "findings": [],
        "summary": {},
        "readiness_score": 0
    }
    
    with open(".audit_findings.json", "w") as f:
        json.dump(initial_findings, f, indent=2)
    
    print("✅ Background agent files created")

def validate_background_agent_config():
    """Validate the background agent configuration."""
    print("🔍 Validating background agent configuration...")
    
    config_path = Path("background_agents_config.json")
    if not config_path.exists():
        print("❌ Background agents configuration file not found")
        return False
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Validate required fields
        if "backgroundAgents" not in config:
            print("❌ Missing required field: backgroundAgents")
            return False
        
        background_agents = config["backgroundAgents"]
        if "agents" not in background_agents:
            print("❌ Missing required field: agents")
            return False
        
        agents = background_agents["agents"]
        required_agent_fields = ["enabled", "prompt", "tools"]
        
        for agent_name, agent_config in agents.items():
            for field in required_agent_fields:
                if field not in agent_config:
                    print(f"❌ Agent {agent_name} missing required field: {field}")
                    return False
        
        print("✅ Background agent configuration is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating configuration: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up background agents for Terry Delmonaco Manager Agent...")
    
    # Setup git repository
    if not setup_git_repository():
        print("❌ Failed to setup git repository")
        sys.exit(1)
    
    # Create background agent files
    create_background_agent_files()
    
    # Validate configuration
    if not validate_background_agent_config():
        print("❌ Background agent configuration validation failed")
        sys.exit(1)
    
    print("\n🎉 Background agents setup complete!")
    print("\n📋 Next steps:")
    print("1. Review and modify background_agents_config.json if needed")
    print("2. Add your git remote origin if desired")
    print("3. Start your application to begin using background agents")
    print("\n⚠️  Note: Background agents will now handle git operations safely")

if __name__ == "__main__":
    main() 