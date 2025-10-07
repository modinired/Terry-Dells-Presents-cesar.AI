#!/bin/bash
# Quick CLI Launcher for Terry Delmonaco Agents
# For when you want the enhanced interactive CLI instead of web UI

echo "🤖 Terry Delmonaco + CESAR Agent CLI Launcher"
echo "=============================================="

cd /Users/modini_red/td_manager_agent

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🚀 Starting Enhanced Interactive CLI..."
echo "   Features:"
echo "   ✅ Direct agent interaction"
echo "   ✅ Real-time status monitoring"
echo "   ✅ CESAR SEUC integration"
echo "   ✅ Emergency system checks"
echo ""

python3 enhanced_interact.py