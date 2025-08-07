# 🚀 GRINGO AI OS - Startup Guide

## Quick Start (After Computer Restart)

### Method 1: One-Click Startup (Recommended)
```bash
./start_gringo.sh
```

### Method 2: Desktop App (macOS)
1. Double-click the **GRINGO AI OS.app** (with your company logo)
2. The app will automatically start everything for you

### Method 3: Manual Startup

#### Step 1: Start Ollama (AI Engine)
```bash
# Start Ollama service
ollama serve
```
*Keep this terminal open - Ollama runs in the background*

#### Step 2: Start GRINGO AI OS (New Terminal)
```bash
# Navigate to your project
cd "/Users/fredtaylor/Build myassistant_2025-05-02T23-25-33.xcresult/dev_ai"

# Start the main application
streamlit run ultimate_gringo.py --server.port 8507
```

#### Step 3: Open in Browser
Open: http://localhost:8507

---

## 🔧 Troubleshooting

### If Ollama is not installed:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Install a model (choose one)
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

### If Python packages are missing:
```bash
pip install -r requirements.txt
```

### If port 8507 is busy:
```bash
# Kill any existing Streamlit processes
pkill -f streamlit

# Or use a different port
streamlit run ultimate_gringo.py --server.port 8508
```

---

## 🎯 What Each Method Does

### `start_gringo.sh` Script
- ✅ Checks if Ollama is running
- ✅ Starts Ollama if needed
- ✅ Installs missing Python packages
- ✅ Starts GRINGO AI OS
- ✅ Opens browser automatically

### Desktop App
- ✅ Professional app icon (your company logo)
- ✅ One-click launch
- ✅ Handles all startup automatically
- ✅ Integrates with macOS

### Manual Method
- ✅ Full control over each step
- ✅ Best for debugging
- ✅ See all logs and outputs

---

## 📱 First Time Setup (One Time Only)

### 1. Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Install AI Models
```bash
# Choose your preferred model
ollama pull llama2        # General purpose
ollama pull codellama     # Code assistance
ollama pull mistral       # Fast and efficient
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Test Everything
```bash
./start_gringo.sh
```

---

## 🌟 Pro Tips

### Auto-Start on Login (macOS)
1. Create the app: `./install_gringo_app.sh`
2. Move `GRINGO AI OS.app` to Applications
3. System Preferences → Users & Groups → Login Items
4. Add `GRINGO AI OS.app`

### Bookmark Your Interface
- Main Interface: http://localhost:8507
- Save this as a bookmark for quick access

### Multiple Projects
You can run multiple instances on different ports:
```bash
streamlit run ultimate_gringo.py --server.port 8508
streamlit run ultimate_gringo.py --server.port 8509
```

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Ollama not found" | Install Ollama: `curl -fsSL https://ollama.ai/install.sh \| sh` |
| "No module named streamlit" | Install packages: `pip install -r requirements.txt` |
| "Port already in use" | Kill processes: `pkill -f streamlit` |
| "Browser doesn't open" | Manually go to http://localhost:8507 |
| App won't start | Check logs in terminal for specific error |

---

## 🎮 Ready to Go!

After following any of the startup methods above, you'll have:
- ✅ GRINGO AI OS running at http://localhost:8507
- ✅ Ollama AI engine ready for queries
- ✅ All agents and tools available
- ✅ Project management, file upload, terminal access
- ✅ Multi-agent orchestration system

**Happy coding! 🚀**
