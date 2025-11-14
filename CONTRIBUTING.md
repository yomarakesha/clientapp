# Contributing to MediaMTX Professional Client

Thank you for your interest in contributing! This document provides guidelines for contributing.

## Code of Conduct

- Be respectful and professional
- Focus on the code and ideas, not individuals
- Help others learn and grow

## How to Contribute

### 1. Fork the repository
```bash
# Click "Fork" on GitHub
```

### 2. Clone your fork
```bash
git clone https://github.com/YOUR-USERNAME/mediamtx-professional-client.git
cd mediamtx-professional-client
```

### 3. Create a feature branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 4. Make your changes
- Write clean, readable code
- Add comments for complex logic
- Follow PEP 8 style guide for Python

### 5. Test your changes
```bash
python professional_client.py
# Test the feature/fix manually
```

### 6. Commit your changes
```bash
git add .
git commit -m "Add feature: description of what you added"
# Good commit messages:
# - Start with verb: Add, Fix, Update, Remove, Refactor
# - Be specific and descriptive
# - Keep it concise
```

### 7. Push to your fork
```bash
git push origin feature/your-feature-name
```

### 8. Create a Pull Request
- Go to GitHub and click "New Pull Request"
- Describe what you changed and why
- Reference any related issues

## Pull Request Guidelines

- Describe the changes clearly
- Reference issue numbers if applicable
- Include before/after screenshots for UI changes
- Make sure code is tested
- Keep PRs focused on one feature/fix

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python professional_client.py

# Generate config
python generate_mediamtx_config.py
```

## Reporting Issues

### When reporting bugs, include:
- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs

### When suggesting features:
- Explain the use case
- Describe the desired behavior
- Provide examples if possible

## Documentation

- Update README if adding features
- Update SETUP_GUIDE_RU.md for setup changes
- Update FAQ.md for common questions
- Add examples if adding new functionality

## Code Style

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Questions?** Open an issue or discussion on GitHub!

Thank you for contributing! 🚀
