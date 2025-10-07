#!/usr/bin/env python3
"""
Main Entry Point for Terry Delmonaco Manager Agent
Version: 3.2
Description: Main application entry point for the automation ecosystem
"""

import asyncio
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
if __package__ in (None, ""):
    sys.path.insert(0, str(PACKAGE_ROOT.parent))
    __package__ = PACKAGE_ROOT.name
    import importlib

    importlib.import_module(__package__)

from .main_orchestrator import TerryDelmonacoManagerAgent
from .utils.logger import setup_logger


async def main():
    """Main entry point for the Terry Delmonaco Manager Agent."""
    logger = setup_logger("main")
    
    try:
        logger.info("🚀 Starting Terry Delmonaco Manager Agent...")
        
        # Create and initialize manager agent
        manager = TerryDelmonacoManagerAgent()
        
        # Initialize the system
        success = await manager.initialize()
        if not success:
            logger.error("❌ Failed to initialize manager agent")
            sys.exit(1)
        
        # Start the manager agent
        await manager.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal, shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("✅ Terry Delmonaco Manager Agent shutdown complete")


if __name__ == "__main__":
    asyncio.run(main()) 
