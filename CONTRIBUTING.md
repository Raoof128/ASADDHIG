# Contributing to Sovereign AI Gateway

Thank you for your interest in contributing to the Sovereign AI Gateway project! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Environment details (OS, Python version, Docker version)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:
- A clear description of the enhancement
- Use cases and benefits
- Potential implementation approach (if you have ideas)

### Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Follow coding standards** (see below)
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Ensure all tests pass** (`pytest tests/`)
6. **Submit a pull request** with a clear description

## Development Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git

### Local Development

1. Clone your fork:
```bash
git clone https://github.com/your-username/sovereign_ai_gateway.git
cd sovereign_ai_gateway
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

4. Run tests:
```bash
pytest tests/ -v
```

5. Run locally (without Docker):
```bash
# Terminal 1: Start Ollama (if installed locally)
ollama serve

# Terminal 2: Start gateway
cd gateway
uvicorn gateway:app --reload --port 8000

# Terminal 3: Start dashboard
cd dashboard
streamlit run app.py
```

## Coding Standards

### Python Style Guide

- Follow **PEP 8** style guidelines
- Use **type hints** for all function signatures
- Maximum line length: **100 characters**
- Use **black** for code formatting (if configured)
- Use **pylint** or **flake8** for linting

### Code Structure

- **One class per file** (unless closely related)
- **Meaningful names** for variables, functions, and classes
- **Docstrings** for all public functions and classes
- **Comments** for complex logic

### Example Code Style

```python
from typing import List, Optional, Tuple

def process_request(
    prompt: str,
    user_id: Optional[str] = None
) -> Tuple[str, float]:
    """
    Process a gateway request.
    
    Args:
        prompt: User prompt text
        user_id: Optional user identifier
        
    Returns:
        Tuple of (response_text, pii_score)
        
    Raises:
        ValueError: If prompt is empty
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty")
    
    # Implementation here
    return response, score
```

### Testing Standards

- Write **unit tests** for all new functions
- Aim for **>80% code coverage**
- Use **pytest** fixtures for test data
- Mock external dependencies (APIs, databases)

### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

Example:
```
feat(inspector): Add passport number detection

Added regex pattern and validation for Australian passport numbers.
Includes unit tests and documentation updates.

Closes #123
```

## Project Structure

```
sovereign_ai_gateway/
├── gateway/          # Core gateway modules
├── dashboard/        # Streamlit dashboard
├── tests/           # Test suite
├── examples/        # Example requests
└── docs/            # Additional documentation (if added)
```

## Areas for Contribution

### High Priority
- Enhanced PII detection (Presidio integration)
- Additional Australian identifier patterns
- Performance optimizations
- Security enhancements
- Kubernetes deployment manifests

### Medium Priority
- Additional test coverage
- Documentation improvements
- Dashboard enhancements
- Monitoring and observability

### Low Priority
- UI/UX improvements
- Additional language support
- Integration examples

## Questions?

Feel free to:
- Open an issue for questions
- Contact maintainers (if contact info available)
- Check existing issues and discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Sovereign AI Gateway! 🛡️

