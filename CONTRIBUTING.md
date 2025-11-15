# Contributing to Website Monitor

Thank you for your interest in contributing to Website Monitor! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Adding New Checks](#adding-new-checks)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

1. **Fork the Repository**: Click the "Fork" button on the GitHub repository page.

2. **Clone Your Fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/websites-monitor.git
   cd websites-monitor
   ```

3. **Add Upstream Remote**:
   ```bash
   git remote add upstream https://github.com/fabriziosalmi/websites-monitor.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- Docker (optional, for containerized development)

### Local Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install fastapi uvicorn[standard] pydantic
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the Application**:
   ```bash
   # Start the API server
   python api.py
   
   # Or run checks directly
   python main.py
   ```

### Docker Setup

```bash
# Build the Docker image
docker build -t websites-monitor .

# Run the container
docker run -p 8000:8000 websites-monitor

# Or use docker-compose
docker-compose up
```

## How to Contribute

### Reporting Bugs

1. **Check Existing Issues**: Search existing issues to avoid duplicates
2. **Create New Issue**: Use the bug report template
3. **Provide Details**: Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)
   - Error messages or logs

### Suggesting Enhancements

1. **Check Existing Issues**: Look for similar feature requests
2. **Create Feature Request**: Use the feature request template
3. **Describe the Feature**: Include:
   - Use case and motivation
   - Proposed solution
   - Alternative approaches considered
   - Impact on existing features

### Contributing Code

1. **Choose an Issue**: Pick an issue to work on or create a new one
2. **Assign Yourself**: Comment on the issue to let others know you're working on it
3. **Create a Branch**: Use descriptive branch names
   ```bash
   git checkout -b feature/add-new-check
   git checkout -b fix/ssl-validation-bug
   git checkout -b docs/update-readme
   ```

## Pull Request Process

### Branch Naming Convention

- `feature/` - New features or enhancements
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or updates
- `chore/` - Maintenance tasks

### Before Submitting

1. **Update Your Branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run Tests** (if applicable):
   ```bash
   python -m pytest tests/
   ```

3. **Format Code**: Ensure code follows project standards
   ```bash
   # Format Python code
   black *.py checks/*.py
   ```

4. **Update Documentation**: Update relevant documentation for your changes

### Submitting the PR

1. **Push Your Branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**:
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template completely

3. **PR Title Format**:
   - `feat: Add SSL certificate expiration check`
   - `fix: Correct DNS blacklist validation`
   - `docs: Update API endpoint documentation`
   - `refactor: Improve check error handling`

4. **PR Description Should Include**:
   - Summary of changes
   - Related issue number (e.g., "Fixes #123")
   - Testing performed
   - Screenshots (for UI changes)
   - Breaking changes (if any)

### Review Process

1. Wait for maintainer review
2. Address review comments promptly
3. Keep the conversation focused and professional
4. Make requested changes in new commits
5. Once approved, maintainers will merge your PR

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use meaningful variable and function names
- Write docstrings for functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 88 characters (Black default)

### Example Function Format

```python
def check_ssl_cert(url: str, timeout: int = 30) -> str:
    """
    Check SSL certificate validity for a given URL.
    
    Args:
        url: The website URL to check
        timeout: Request timeout in seconds (default: 30)
    
    Returns:
        Status emoji: 🟢 (valid), 🔴 (invalid), or ⚪ (error)
    
    Example:
        >>> check_ssl_cert("https://example.com")
        '🟢 Valid until 2025-12-31'
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"SSL check failed: {e}")
        return "⚪ Error"
```

## Adding New Checks

### Step 1: Create Check File

Create a new file in the `checks/` directory:

```bash
touch checks/check_your_feature.py
```

### Step 2: Implement Check Function

```python
# checks/check_your_feature.py
import logging

logger = logging.getLogger(__name__)

def check_your_feature(url: str, timeout: int = 30) -> str:
    """
    Brief description of what this check does.
    
    Args:
        url: The website URL to check
        timeout: Request timeout in seconds
    
    Returns:
        Status emoji with description
    """
    try:
        # Your check logic here
        # Return status emoji:
        # 🟢 for success/passed
        # 🔴 for failure/issue found
        # 🟡 for warning
        # ⚪ for error/unable to check
        
        return "🟢 Feature is working correctly"
    except Exception as e:
        logger.error(f"Check failed for {url}: {e}")
        return f"⚪ Error: {str(e)}"
```

### Step 3: Register the Check

1. Import in `main.py`:
   ```python
   from checks.check_your_feature import check_your_feature
   ```

2. Add to `api.py` CHECK_MODULES dictionary:
   ```python
   CHECK_MODULES = {
       # ... existing checks ...
       'your_feature': 'checks.check_your_feature',
   }
   ```

3. Update the check list in `WebsiteMonitor` class if needed

### Step 4: Update Documentation

- Add the check to README.md in the appropriate category
- Update the check count if necessary
- Document any special requirements or API keys needed

### Step 5: Test Your Check

```python
# Test manually
from checks.check_your_feature import check_your_feature
result = check_your_feature("https://example.com")
print(result)
```

## Testing

### Manual Testing

1. **Test Individual Checks**:
   ```bash
   python -c "from checks.check_ssl_cert import check_ssl_cert; print(check_ssl_cert('https://example.com'))"
   ```

2. **Test API Endpoints**:
   ```bash
   # Start the API
   python api.py
   
   # In another terminal, test endpoints
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/monitor \
     -H "Content-Type: application/json" \
     -d '{"url": "example.com", "checks": ["ssl_cert"]}'
   ```

3. **Test with Different Websites**: Verify your changes work with various websites

### Automated Testing

If you add tests:
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_ssl_checks.py

# Run with coverage
pytest --cov=checks tests/
```

## Documentation

### Documentation Updates

When contributing, update relevant documentation:

- **README.md**: For user-facing changes
- **API Documentation**: For API endpoint changes
- **Code Comments**: For complex logic
- **CHANGELOG.md**: For version changes (maintainers will handle)

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Use proper Markdown formatting
- Check spelling and grammar
- Verify all links work

### Example Documentation

```markdown
## New Feature Name

Brief description of the feature.

### Usage

\`\`\`bash
# Example command
python api.py --feature-flag
\`\`\`

### Configuration

Add to `config.yaml`:
\`\`\`yaml
feature_enabled: true
feature_option: value
\`\`\`
```

## Questions?

If you have questions:

1. Check existing documentation
2. Search closed issues
3. Ask in an issue or discussion
4. Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for contributing to Website Monitor! 🚀
