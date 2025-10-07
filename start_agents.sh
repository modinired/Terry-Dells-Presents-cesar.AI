#!/bin/bash
# Terry Delmonaco + CESAR Agent Network Startup Script
# Auto-starts the complete agent ecosystem

echo "🚀 Starting Terry Delmonaco + CESAR Agent Network..."

# Change to agent directory
cd /Users/modini_red/td_manager_agent

# Check if virtual environment exists, create if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
echo "📚 Installing/updating requirements..."
pip install -q fastapi uvicorn websockets

# Start the web interface (this includes all agents + UI)
echo "🌐 Starting web interface with real-time UI..."
echo "   ✅ Agent Network will be available at: http://localhost:8000"
echo "   ✅ Real-time UI with 4 thinking panels"
echo "   ✅ CESAR SEUC integration active"
echo ""
echo "🔄 Starting server..."

python3 app.py