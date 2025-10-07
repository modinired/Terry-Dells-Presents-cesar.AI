#!/usr/bin/env python3
"""
CESAR.ai - Cognitive Enterprise System for Autonomous Reasoning
Main entry point for the Atlas Final ecosystem.
"""

import asyncio
import logging
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
if __package__ in (None, ""):
    sys.path.insert(0, str(PACKAGE_ROOT.parent))
    __package__ = PACKAGE_ROOT.name
    import importlib

    importlib.import_module(__package__)

from .main_orchestrator import CESARAIOrchestrator


async def main():
    """Main entry point for CESAR.ai Atlas Final."""
    print("🚀 CESAR.ai Atlas Final - Starting...")
    print("=" * 50)
    print("Cognitive Enterprise System for Autonomous Reasoning")
    print("Version 4.0 Atlas Final")
    print("=" * 50)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        # Initialize CESAR.ai
        cesar_ai = CESARAIOrchestrator()
        print("\n🔧 Initializing CESAR.ai system...")

        success = await cesar_ai.initialize()

        if success:
            print("✅ CESAR.ai initialized successfully!")

            # Check for Atlas CESAR AI enhancements
            if hasattr(cesar_ai, 'atlas_cesar_integration'):
                print("🎯 Atlas CESAR AI enhancements active")
                status = await cesar_ai.atlas_cesar_integration.get_atlas_cesar_status()
                if status.get('atlas_cesar_active'):
                    improvements = status.get('performance_improvements', {})
                    print(f"   • Token Reduction: {improvements.get('token_reduction_pct', 0):.1f}%")
                    print(f"   • Latency Improvement: {improvements.get('latency_improvement_pct', 0):.1f}%")
                    print(f"   • Accuracy Enhancement: {improvements.get('accuracy_improvement_pct', 0):.1f}%")

            print("\n🌟 CESAR.ai is ready for operation!")
            print("   Agent fleet initialized and standing by")
            print("   Enhanced memory system active")
            print("   UI automation capabilities enabled")
            print("   Collective intelligence framework running")

            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 Shutting down CESAR.ai...")
                await cesar_ai.shutdown()
                print("✅ CESAR.ai shutdown complete")

        else:
            print("❌ Failed to initialize CESAR.ai")
            return 1

    except Exception as e:
        print(f"❌ CESAR.ai startup failed: {e}")
        logging.error(f"CESAR.ai startup error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
