# Contributing to ASURA

Thank you for your interest in contributing to ASURA! We welcome contributions from the community.

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- Git

### Setup Development Environment

1. **Fork the repository**
   - Go to https://github.com/ParthSalunkhe7052/Asura-Security-Scan
   - Click "Fork" button
   - Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Asura-Security-Scan.git
   cd Asura-Security-Scan
   ```

2. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Run tests**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm run test
   ```

## 📝 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes
- Write clear, concise commit messages
- Follow existing code style
- Add tests for new features
- Update documentation as needed

### 3. Code Style Guidelines

#### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions small and focused

```python
def scan_project(project_path: str) -> dict:
    """
    Scan a project for security vulnerabilities.
    
    Args:
        project_path: Absolute path to the project directory
        
    Returns:
        Dictionary containing scan results
    """
    pass
```

#### JavaScript/React (Frontend)
- Use functional components with hooks
- Follow React best practices
- Use meaningful variable names
- Keep components small and reusable

```jsx
const SecurityCard = ({ vulnerability, onExplain }) => {
  // Component logic
};
```

### 4. Run Linters
```bash
# Backend
cd backend
flake8 app/
black app/

# Frontend
cd frontend
npm run lint
```

### 5. Commit Your Changes
```bash
git add .
git commit -m "feat: add new security scanner integration"
# or
git commit -m "fix: resolve scan timeout issue"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### 6. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots (if UI changes)

## 🧪 Testing Guidelines

### Writing Tests

#### Backend Tests
```python
# tests/test_scanner.py
import pytest
from app.core.scanner import SecurityScanner

def test_scan_detects_vulnerabilities():
    scanner = SecurityScanner()
    results = scanner.run_bandit("./test_project")
    assert len(results) > 0
```

#### Frontend Tests
```jsx
// tests/SecurityCard.test.jsx
import { render, screen } from '@testing-library/react';
import SecurityCard from '../components/SecurityCard';

test('renders vulnerability details', () => {
  render(<SecurityCard vulnerability={mockVuln} />);
  expect(screen.getByText('SQL Injection')).toBeInTheDocument();
});
```

### Test Coverage
- Aim for >80% coverage for new code
- Test edge cases and error conditions
- Use mocks for external dependencies

## 🐛 Reporting Bugs

### Before Submitting a Bug Report
- Check existing issues
- Verify bug exists in latest version
- Collect relevant information

### Bug Report Template
```markdown
**Describe the bug**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Windows 11]
- Python version: [e.g. 3.11.0]
- Node version: [e.g. 18.0.0]
- ASURA version: [e.g. 0.3.0]

**Additional context**
Any other relevant information.
```

## 💡 Suggesting Enhancements

We welcome feature suggestions! Please:
1. Check if it's already requested
2. Explain the use case
3. Describe the proposed solution
4. Consider implementation complexity

## 🔍 Code Review Process

All submissions require review. We aim to:
- Review PRs within 48 hours
- Provide constructive feedback
- Merge approved PRs quickly

### Review Checklist
- [ ] Code follows project style
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear

## 📚 Areas We Need Help

### High Priority
- [ ] Adding support for more programming languages
- [ ] Writing Semgrep rules for framework-specific issues
- [ ] Improving test coverage
- [ ] Performance optimizations

### Medium Priority
- [ ] UI/UX improvements
- [ ] Documentation and tutorials
- [ ] Example projects
- [ ] Integration with CI/CD tools

### Good First Issues
Look for issues labeled `good-first-issue` - these are great for newcomers!

## 🤝 Community Guidelines

### Be Respectful
- Be welcoming and inclusive
- Respect differing viewpoints
- Accept constructive criticism
- Focus on what's best for the community

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code contributions

## 📞 Getting Help

If you need help:
1. Check the [README.md](README.md)
2. Review [QUICK_START.md](QUICK_START.md)
3. Search existing issues
4. Ask in GitHub Discussions

## 🙏 Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Mentioned in release notes
- Added to contributors list (if significant contributions)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to ASURA! Together we're making security testing accessible for everyone.** 🔥
