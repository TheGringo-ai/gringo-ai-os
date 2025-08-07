# 🤖 GRINGO - Ultimate AI Development OS

**Your Complete Local AI-Powered Development Environment**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AI](https://img.shields.io/badge/AI-LLaMA3-purple.svg)](https://ollama.ai)

> Transform ideas into working code through natural language. Create, manage, and orchestrate development tools with AI assistance. 100% local and private.

## ✨ Features

### 🚀 **AI Project Creator**
- **Natural Language → Working Code**: Describe any project and get complete, runnable applications
- **Multi-Language Support**: Python, JavaScript, with smart framework detection
- **Instant Deployment**: One-click project execution and testing
- **Smart Templates**: AI generates appropriate project structures

### 🤖 **Multi-Agent Orchestration**
- **10 Specialized Agents**: Planning, refactoring, testing, documentation, security, performance
- **Parallel Execution**: Run multiple agents simultaneously for complex tasks
- **Feature Pipelines**: Complete development workflows from planning to deployment
- **Agent Status Monitoring**: Real-time health checks and performance metrics

### 🛠️ **AI-Powered Custom Tools**
- **Tool Creator**: Describe any tool and AI builds it for you
- **Smart Execution**: AI runs tools with optimal parameters
- **Test-then-Save**: Execute tools before adding to your library
- **Usage Analytics**: Track and optimize your toolkit

### 💬 **Local AI Chat**
- **LLaMA3 Integration**: Complete privacy with local AI processing
- **Code Review**: Get expert-level code analysis and suggestions
- **Architecture Planning**: AI-assisted project design and roadmaps
- **Problem Solving**: Debug issues with AI assistance

### 📊 **Integrated Development Environment**
- **In-Browser Terminal**: Full command-line access
- **File Management**: Upload, organize, and manage project files
- **Project Database**: SQLite-backed project tracking and history
- **System Monitoring**: Resource usage and performance metrics

### 🏢 **Enterprise Features**
- **Branded Desktop App**: Custom logo integration for professional deployment
- **Service Management**: Automated startup/shutdown with health monitoring
- **Project Folder Learning**: AI learns from existing codebases
- **External Folder Linking**: Connect and analyze external projects
- **One-Command Deployment**: Complete automation from clone to running

### 🔧 **System Integration**
- **macOS App Bundle**: Native application with custom icon
- **Service Scripts**: Professional startup/shutdown automation
- **Desktop Launcher**: Branded GUI launcher with system integration
- **Auto-Recovery**: Smart error handling and service restoration

## 🎯 Quick Start

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai) for local AI (optional but recommended)

### One-Command Installation & Startup

```bash
# Clone the repository
git clone https://github.com/TheGringo-ai/gringo-ai-os.git
cd gringo-ai-os

# One-command startup (handles everything automatically)
./start_gringo.sh
```

**That's it!** The script will:
- ✅ Install all Python dependencies
- ✅ Start Ollama AI service
- ✅ Launch GRINGO AI OS
- ✅ Open your browser automatically

### Manual Installation (Alternative)

```bash
# Install dependencies
pip install -r requirements.txt

# Install Ollama for AI features
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2

# Launch GRINGO manually
streamlit run ultimate_gringo.py --server.port 8507
```

Open [http://localhost:8507](http://localhost:8507) in your browser.

## 🚀 Service Management

### Starting After Computer Restart
```bash
cd gringo-ai-os
./start_gringo.sh
```

### Desktop App (macOS)
```bash
# Create branded app with your logo
./install_gringo_app.sh

# Then double-click "GRINGO AI OS.app"
```

### Stop Services
```bash
./stop_gringo.sh
```

### Service Status
- **Main Interface**: http://localhost:8507
- **Ollama AI**: http://localhost:11434
- **Check Status**: Script shows real-time monitoring

## 🚀 Usage Examples

### Create a Web Application
```
Prompt: "Create a todo list app with categories and due dates"
Result: Complete Streamlit application with database, UI, and functionality
```

### Build Custom Tools
```
Prompt: "Make a file organizer that sorts by date and file type"
Result: Production-ready Python script with error handling and documentation
```

### Orchestrate Development Workflow
```
Task: "Add user authentication to my project"
Agents: Planner → Security → Refactor → Test → Document
Result: Complete feature implementation with tests and docs
```

## 📁 Project Structure

```
gringo-ai-os/
├── ultimate_gringo.py          # Main GRINGO application
├── multi_agent_orchestrator.py # Agent coordination system
├── custom_tools_manager.py     # Tool creation and management
├── start_gringo.sh            # One-command startup script
├── stop_gringo.sh             # Service stop script
├── install_gringo_app.sh      # macOS app creator
├── gringo_launcher.py         # Desktop launcher
├── create_app_bundle.sh       # App bundle creator
├── agents/                    # Specialized AI agents
│   ├── planner_agent.py
│   ├── refactor_agent.py
│   ├── test_generator_agent.py
│   ├── doc_generator_agent.py
│   ├── review_agent.py
│   ├── security_agent.py
│   ├── performance_agent.py
│   ├── api_agent.py
│   ├── deploy_agent.py
│   └── analytics_agent.py
├── assets/                    # Branding and logos
│   └── company_logo.png       # Your company logo
├── call_llama.py              # Local AI integration
├── memory.json                # Persistent memory storage
├── STARTUP_GUIDE.md           # Complete startup instructions
└── README.md                  # This file
```

## 🤖 Available Agents

| Agent | Purpose | Capabilities |
|-------|---------|-------------|
| 🧠 **Planner** | Task breakdown and architecture | Analyzes requirements, creates development roadmaps |
| 🔧 **Refactor** | Code optimization | Improves code quality, performance, maintainability |
| 🧪 **Test Generator** | Automated testing | Creates comprehensive test suites |
| 📖 **Doc Generator** | Documentation | Generates README files, API docs, user guides |
| 👥 **Reviewer** | Code review | Quality assurance, best practices enforcement |
| 🔒 **Security** | Security analysis | Vulnerability scanning, security hardening |
| ⚡ **Performance** | Optimization | Performance profiling and improvements |
| 🌐 **API** | API development | REST API creation and testing |
| 🚀 **Deploy** | Deployment | DevOps automation and deployment strategies |
| 📊 **Analytics** | Data analysis | Metrics collection and analysis |

## Development

### Service Architecture
- **Main Interface**: Streamlit web application on port 8507
- **AI Engine**: Ollama local AI service on port 11434
- **Process Management**: Automated startup/shutdown scripts
- **Desktop Integration**: Native macOS app bundle support

### Running Tests

```bash
python3 -m pytest
# or run individual test files:
python3 test_basic.py
python3 test_death_server.py
python3 test_fredfix_agent.py
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama not found" | `curl -fsSL https://ollama.ai/install.sh \| sh` |
| "No module named streamlit" | `pip install -r requirements.txt` |
| "Port already in use" | `./stop_gringo.sh` then restart |
| Service won't start | Check `STARTUP_GUIDE.md` for details |

## Documentation

- **Files:** 21 Python modules
- **Tests:** 6 test files
- **Directories:** 1 subdirectories

*Generated automatically by Doc Generator Agent*
