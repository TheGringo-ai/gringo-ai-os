# 🤖 GRINGO - Global AI Assistant

**Complete OS Integration for macOS**

GRINGO transforms your entire Mac into an AI-powered development environment. Handle ANY task - creating, editing, reviewing, summarizing, fixing code and files from anywhere on your system.

## 🚀 Quick Installation

```bash
# 1. Install system-wide
./install_gringo.sh

# 2. Set up macOS integration (optional)
./setup_services.sh

# 3. Restart terminal or run:
source ~/.zshrc
```

## 📋 Core Capabilities

### 📁 File Operations
```bash
gringo file create /path/to/file.py "print('hello')"    # Create files
gringo file edit /path/to/file.py "add error handling" # Edit files  
gringo file review /path/to/file.py                    # Review files
gringo file summarize /path/to/file.py                 # Summarize files
gringo file delete /path/to/file.py                    # Delete files
```

### 💻 Code Operations
```bash
gringo code create python "web scraper for news"       # Generate code
gringo code review main.py                             # Review code quality
gringo code fix buggy_script.py                       # Fix code issues
gringo code test my_module.py                         # Generate tests
gringo code edit script.py "optimize performance"     # Refactor code
```

### 🧹 System Cleanup
```bash
gringo duplicates ~/Downloads                         # Find duplicate files
gringo duplicates ~/Documents/projects                # Scan any directory
gringo clean ~/Downloads                              # Delete duplicates (with confirmation)
```

### 🤖 Agent Management
```bash
gringo agents                                         # List all AI agents
```

## 🎯 Real-World Examples

### Development Workflow
```bash
# Create a new Python project
gringo file create ~/projects/web_scraper/main.py "import requests"
gringo code create python "web scraper for Reddit posts"
gringo code review ~/projects/web_scraper/main.py
gringo code test ~/projects/web_scraper/main.py

# Fix and optimize
gringo code fix ~/projects/web_scraper/main.py
gringo code edit ~/projects/web_scraper/main.py "add rate limiting"
```

### File Management
```bash
# Clean up your Downloads folder
gringo duplicates ~/Downloads
gringo clean ~/Downloads

# Review and summarize documents
gringo file summarize ~/Documents/report.md
gringo file review ~/Documents/contract.txt
```

### Code Maintenance
```bash
# Review entire codebase
find . -name "*.py" -exec gringo code review {} \;

# Generate tests for all modules
find . -name "*.py" -exec gringo code test {} \;

# Fix common issues
gringo code fix src/main.py
gringo code fix tests/test_api.py
```

## 🖱️ macOS Integration Features

### Finder Integration
After running `./setup_services.sh`:

1. **Right-click any file** in Finder
2. Look for **Services > GRINGO** menu
3. Choose **"Review File"** or **"Summarize File"**
4. Results appear in terminal/notification

### Keyboard Shortcuts
Set up in **System Preferences > Keyboard > Shortcuts > Services**:
- `⌘⌥R` - Review selected files
- `⌘⌥S` - Summarize selected files

### Quick Actions
```bash
# Review currently selected files in Finder
gringo-quick review

# Summarize currently selected files
gringo-quick summarize

# Find duplicates in current Finder directory
gringo-quick duplicates

# Fix selected code files
gringo-quick fix
```

## 🌐 Web Interface

Your Streamlit command center is running at:
- **Local**: http://localhost:8502
- **Network**: http://192.168.4.47:8502

### Features:
- 📊 **Agent Dashboard** - Monitor all AI agents
- 🎯 **Task Orchestration** - Run multiple agents in parallel
- 📈 **Performance Analytics** - System monitoring
- ⚙️ **Settings** - Configure agent behavior

## 🧠 Available AI Agents

| Agent | Purpose | Usage |
|-------|---------|-------|
| 🧠 **planner** | Task planning and breakdown | Auto-triggered for complex tasks |
| ⚙️ **refactor** | Code refactoring and optimization | `gringo code edit` |
| 🧪 **test_gen** | Automated test generation | `gringo code test` |
| 📚 **doc_gen** | Documentation generation | Auto-triggered |
| 🔍 **reviewer** | Code review and quality check | `gringo code review` |
| ⚡ **performance** | Performance monitoring | `gringo agents` |
| 🤖 **ai_planner** | AI-powered planning with LLaMA | Complex reasoning tasks |
| 🚀 **deploy** | Deployment automation | Production workflows |
| 🔒 **security** | Security analysis | Code security scans |
| 📊 **analytics** | Code analytics | Codebase insights |
| 🌐 **api** | API detection and management | API integration |

## 🔧 Advanced Usage

### Chaining Operations
```bash
# Complete workflow for new project
gringo code create python "REST API with FastAPI" && \
gringo code test api.py && \
gringo code review api.py && \
gringo file create requirements.txt "fastapi uvicorn"
```

### Batch Processing
```bash
# Process multiple files
for file in *.py; do
    gringo code review "$file"
    gringo code test "$file"
done
```

### Integration with Other Tools
```bash
# Combine with git workflow
git status | grep modified | awk '{print $2}' | xargs -I {} gringo code review {}

# Process build outputs
make 2>&1 | grep error | xargs -I {} gringo code fix {}
```

## 🛠️ System Requirements

- **macOS** 10.14+ (Mojave or later)
- **Python** 3.8+
- **Terminal** (zsh or bash)
- **Streamlit** (auto-installed)

## 🔄 Updates and Maintenance

```bash
# Update GRINGO capabilities
cd /path/to/dev_ai
git pull  # if using git
source venv/bin/activate
pip install --upgrade streamlit psutil requests

# Restart services
./install_gringo.sh
```

## 🆘 Troubleshooting

### Command not found
```bash
# Re-run installer
./install_gringo.sh

# Or add to PATH manually
export PATH="/path/to/dev_ai:$PATH"
```

### Permission issues
```bash
# Fix permissions
chmod +x gringo gringo-quick
sudo chown $(whoami) /usr/local/bin/gringo
```

### Virtual environment issues
```bash
# Recreate venv
python3 -m venv venv
source venv/bin/activate
pip install streamlit psutil requests
```

## 🎉 You're All Set!

GRINGO is now integrated into your entire macOS system. You can:

✅ **Use `gringo` command from any terminal**  
✅ **Right-click files in Finder for AI analysis**  
✅ **Access web interface for advanced features**  
✅ **Set keyboard shortcuts for instant AI assistance**

**Start with**: `gringo help` or visit http://localhost:8502

---

**Made with ❤️ by your AI coding assistant**
