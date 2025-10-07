#!/usr/bin/env python3
"""
Simple background agents runner for testing.
This script runs the background agents independently of the main application.
"""

import asyncio
import json
import logging
from pathlib import Path
from .core.background_agent_manager import BackgroundAgentManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Run background agents."""
    print("🚀 Starting background agents...")
    
    # Create background agent manager
    manager = BackgroundAgentManager()
    
    try:
        # Initialize
        if not await manager.initialize():
            print("❌ Failed to initialize background agent manager")
            return
        
        print("✅ Background agent manager initialized")
        
        # Start background agents
        print("🔄 Starting background agents...")
        await manager.start()
        print("✅ Background agents running. Press Ctrl+C to stop.")

        # Keep the event loop alive so periodic audits can execute
        while manager.is_running:
            await asyncio.sleep(30)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down background agents...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await manager.shutdown()
        print("✅ Background agents shutdown complete")

if __name__ == "__main__":
    asyncio.run(main()) 
