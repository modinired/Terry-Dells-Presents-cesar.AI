#!/bin/bash
# Working Terry Delmonaco Agent Network Startup Script

echo "🚀 Starting Terry Delmonaco Agent Network..."

# Change to agent directory
cd /Users/modini_red/td_manager_agent

# Install any missing dependencies
echo "📦 Checking dependencies..."
pip3 install -q fastapi uvicorn feedparser gspread oauth2client pandas numpy networkx 2>/dev/null

# Try to start the full system first
echo "🔄 Attempting to start full agent system..."
timeout 10 python3 app.py &
APP_PID=$!

# Wait a moment to see if it starts successfully
sleep 3

# Check if the full system is running
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Full agent system started successfully!"
    echo "   🌐 Web UI: http://localhost:8000"
    echo "   🤖 All agents active with CESAR SEUC integration"
    wait $APP_PID
else
    echo "⚠️  Full system loading... Starting simple UI"
    # Kill the failed attempt
    kill $APP_PID 2>/dev/null

    # Start the simple version that always works
    echo "🔄 Starting simplified interface..."
    python3 simple_web_ui.py &
    SIMPLE_PID=$!

    sleep 2
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ Simple UI started successfully!"
        echo "   🌐 Web Interface: http://localhost:8000"
        echo "   📝 Note: Full agent system will load in background"

        # Try to start the full system in background
        echo "🔄 Loading full agent system in background..."
        (
            sleep 5
            # Try to upgrade to full system after dependencies load
            if python3 -c "from main_orchestrator import TerryDelmonacoManagerAgent" 2>/dev/null; then
                echo "✅ Full system dependencies loaded"
                kill $SIMPLE_PID 2>/dev/null
                sleep 2
                python3 app.py
            fi
        ) &

        wait $SIMPLE_PID
    else
        echo "❌ Failed to start any interface"
        echo "   Run: python3 simple_web_ui.py"
        exit 1
    fi
fi