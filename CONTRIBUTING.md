# Contributing to GRINGO AI OS

We're thrilled that you're interested in contributing to GRINGO! This document provides guidelines and information about contributing to this project.

## 🚀 Quick Start for Contributors

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/yourusername/gringo-ai-os.git`
3. **Create a branch**: `git checkout -b feature/your-feature`
4. **Make changes** following our guidelines below
5. **Test** your changes thoroughly
6. **Submit** a Pull Request

## 📋 Types of Contributions

### 🐛 Bug Reports
- Use the GitHub issue template
- Include reproduction steps
- Provide environment details (OS, Python version, etc.)
- Include error messages and logs

### ✨ Feature Requests
- Describe the problem you're solving
- Explain your proposed solution
- Consider backwards compatibility
- Discuss potential alternatives

### 🔧 Code Contributions
- Follow the coding standards below
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 📖 Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Update API documentation
- Improve README and guides

## 🏗️ Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/gringo-ai-os.git
cd gringo-ai-os

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black isort flake8

# Install Ollama for AI features (optional)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3
```

## 📝 Coding Standards

### Python Style
- Follow **PEP 8** style guidelines
- Use **Black** for code formatting: `black .`
- Sort imports with **isort**: `isort .`
- Lint with **flake8**: `flake8 .`

### Code Organization
- Keep functions focused and single-purpose
- Use descriptive variable and function names
- Add docstrings for classes and functions
- Include type hints where helpful

### Example Code Style
```python
def create_custom_tool(description: str, ai_model: str = "llama3") -> dict:
    """
    Create a custom tool using AI generation.
    
    Args:
        description: Natural language description of the tool
        ai_model: AI model to use for generation
        
    Returns:
        Dictionary containing tool code and metadata
        
    Raises:
        ValueError: If description is empty
        ConnectionError: If AI service is unavailable
    """
    if not description.strip():
        raise ValueError("Tool description cannot be empty")
    
    # Implementation here...
    return {"code": generated_code, "metadata": tool_info}
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_agents.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests
- Write tests for all new functionality
- Use descriptive test names
- Include edge cases and error conditions
- Mock external dependencies (AI services, file system)

### Test Example
```python
import pytest
from unittest.mock import patch, MagicMock
from custom_tools_manager import CustomToolsManager

def test_create_tool_success():
    """Test successful tool creation with valid description."""
    manager = CustomToolsManager()
    
    with patch('custom_tools_manager.call_llama_api') as mock_ai:
        mock_ai.return_value = "def hello(): return 'Hello World'"
        
        result = manager.create_tool("greeting function")
        
        assert "def hello()" in result["code"]
        assert result["metadata"]["description"] == "greeting function"
        mock_ai.assert_called_once()

def test_create_tool_empty_description():
    """Test tool creation fails with empty description."""
    manager = CustomToolsManager()
    
    with pytest.raises(ValueError, match="Description cannot be empty"):
        manager.create_tool("")
```

## 🏷️ Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commit messages are clear

### PR Description Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (existing functionality changes)
- [ ] Documentation update

## Testing
- [ ] Added/updated tests
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 🏗️ Architecture Guidelines

### Adding New Agents
```python
# agents/your_agent.py
class YourAgent:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.name = "Your Agent"
        self.description = "What this agent does"
    
    def run(self, task_description: str) -> dict:
        """Execute the agent's main functionality."""
        # Implementation
        return {
            "success": True,
            "message": "Task completed",
            "output": "Agent results"
        }
    
    def health_check(self) -> bool:
        """Check if agent is ready to run."""
        return True
```

### Adding New Tool Categories
1. Update `custom_tools_manager.py`
2. Add category to the UI in `ultimate_gringo.py`
3. Create example tools for the category
4. Add tests for the new category

### File Organization
- **Main app**: `ultimate_gringo.py`
- **Agents**: `agents/` directory
- **Utilities**: Keep in root or create `utils/` directory
- **Tests**: `tests/` directory (mirror main structure)
- **Docs**: `docs/` directory for additional documentation

## 🔄 Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Release Checklist
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Test all features thoroughly
- [ ] Update documentation
- [ ] Create GitHub release with notes

## 🆘 Getting Help

### Community Resources
- **GitHub Discussions**: Ask questions and share ideas
- **GitHub Issues**: Report bugs and request features
- **Wiki**: Additional documentation and guides

### Code Review Process
1. Maintainers review all PRs
2. At least one approval required
3. All checks must pass
4. Squash and merge preferred

### Response Times
- **Bug reports**: Within 2-3 days
- **Feature requests**: Within 1 week
- **Pull requests**: Within 3-5 days

## 🎯 Roadmap Contributions

High-priority areas where contributions are especially welcome:

### Immediate Needs (v2.0)
- [ ] Web-based code editor integration
- [ ] Plugin system architecture
- [ ] More language support (Go, Rust, TypeScript)
- [ ] Performance optimizations

### Future Features (v2.1+)
- [ ] Cloud sync capabilities
- [ ] Mobile-responsive interface
- [ ] Advanced CI/CD integration
- [ ] Team collaboration features

## 📜 Code of Conduct

### Our Standards
- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Focus on what's best** for the community
- **Show empathy** towards other contributors

### Unacceptable Behavior
- Harassment or discriminatory language
- Personal attacks or trolling
- Spam or off-topic content
- Publishing private information

### Enforcement
Violations may result in temporary or permanent ban from the project.

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- GitHub releases
- Special thanks in major version announcements

Thank you for helping make GRINGO better! 🚀
