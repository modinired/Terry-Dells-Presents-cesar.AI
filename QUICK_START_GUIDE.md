# 🚀 Terry Delmonaco + CESAR Agent Network - Quick Start Guide

## 📍 AGENT SYSTEM LOCATIONS

### **Main Directory:**
```
/Users/modini_red/td_manager_agent/
```

### **Updated UI Location:**
```
/Users/modini_red/td_manager_agent/static/index.html
```

### **Enhanced Features:**
- **Real-time 4-panel thinking UI**
- **CESAR SEUC integration**
- **Multi-agent ecosystem**
- **Recursive cognition**
- **Collective intelligence**

---

## 🎯 3 WAYS TO ACCESS YOUR AGENTS

### **1. 🖥️ WEB UI (Recommended)**
```bash
# Double-click this file on Desktop:
Terry Delmonaco Agents.command

# OR run manually:
cd /Users/modini_red/td_manager_agent
./start_agents.sh

# Then open: http://localhost:8000
```

### **2. 💻 Enhanced CLI**
```bash
cd /Users/modini_red/td_manager_agent
./launch_cli.sh
```

### **3. 🔧 Direct Python**
```bash
cd /Users/modini_red/td_manager_agent
python3 app.py                    # Web UI + API
python3 enhanced_interact.py      # Interactive CLI
python3 test_merged_system.py     # System test
```

---

## ⚡ AUTO-START ON LOGIN

### **Enable Auto-Start:**
```bash
# Load the launch agent
launchctl load /Users/modini_red/Library/LaunchAgents/com.terrydelmonaco.agents.plist

# Enable auto-start
launchctl enable gui/$(id -u)/com.terrydelmonaco.agents
```

### **Disable Auto-Start:**
```bash
# Disable auto-start
launchctl disable gui/$(id -u)/com.terrydelmonaco.agents

# Unload the launch agent
launchctl unload /Users/modini_red/Library/LaunchAgents/com.terrydelmonaco.agents.plist
```

### **Check Status:**
```bash
# Check if auto-start is running
launchctl list | grep terrydelmonaco
```

---

## 🌐 WEB UI FEATURES

### **Real-Time 4-Panel Interface:**
1. **💬 Question Panel** - Ask questions to all agents
2. **⚡ Agent Processing** - See agents thinking in real-time
3. **🧠 Collective Intelligence** - Emergent behaviors & insights
4. **📊 System Monitor** - Performance & health metrics

### **Access URL:**
```
http://localhost:8000
```

### **API Endpoints:**
- `POST /ask` - SEUC-enhanced question processing
- `POST /ask/seuc` - Full CESAR recursive cognition
- `GET /seuc/status` - CESAR system status
- `GET /nodes/status` - All agent network status

---

## 🔧 SYSTEM CAPABILITIES

### **Agent Fleet:**
- `automated_reporting` - System metrics and reports
- `inbox_calendar` - Email and calendar management
- `spreadsheet_processor` - Data analysis and processing
- `crm_sync` - Customer relationship management
- `screen_activity` - Screen monitoring and analysis
- `cursor_agent` - Code development assistance

### **CESAR SEUC Features:**
- **Recursive Cognition** - Multi-depth analysis
- **Collective Intelligence** - Cross-agent insights
- **Symbiotic Learning** - Continuous evolution
- **Financial Intelligence** - Atlas Capital focus
- **Predictive Analytics** - Future trend analysis
- **Emergent Behaviors** - Automatic adaptation

---

## 🚀 QUICK START COMMANDS

### **Start Everything:**
```bash
# Desktop launcher (easiest)
double-click "Terry Delmonaco Agents.command"

# Command line
cd /Users/modini_red/td_manager_agent && ./start_agents.sh
```

### **Test System:**
```bash
cd /Users/modini_red/td_manager_agent
python3 test_merged_system.py
```

### **Check Logs:**
```bash
tail -f /Users/modini_red/td_manager_agent/logs/startup.log
```

---

## 🆘 TROUBLESHOOTING

### **If agents won't start:**
```bash
cd /Users/modini_red/td_manager_agent
python3 -m pip install --upgrade fastapi uvicorn
./start_agents.sh
```

### **If UI doesn't load:**
```bash
# Check if server is running
curl http://localhost:8000/api

# Check logs
tail /Users/modini_red/td_manager_agent/logs/startup.log
```

### **Reset everything:**
```bash
# Stop auto-start
launchctl unload /Users/modini_red/Library/LaunchAgents/com.terrydelmonaco.agents.plist

# Manual start
cd /Users/modini_red/td_manager_agent
./start_agents.sh
```

---

## 🎉 YOU'RE READY!

Your enhanced agent network is configured with:
- ✅ Real-time thinking UI
- ✅ CESAR SEUC integration
- ✅ Auto-start capability
- ✅ Desktop launcher
- ✅ Multiple access methods

**Start your agents and open http://localhost:8000 to see them thinking in real-time!**