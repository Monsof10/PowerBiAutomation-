# Contributing Guidelines

## Code Standards

This project follows NASA coding standards and clean code principles:

### Principles

1. **Clarity Over Cleverness** - Write code that is easy to understand
2. **Single Responsibility** - Each function does one thing well
3. **DRY (Don't Repeat Yourself)** - Avoid code duplication
4. **Error Handling** - Handle all exceptions gracefully
5. **Documentation** - Document all public interfaces
6. **Testing** - Test before committing

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Keep functions under 50 lines when possible
- Maximum line length: 100 characters

### Example

```python
def process_report(report_url: str, output_path: str) -> str:
    """
    Process Power BI report and export to PDF.
    
    Args:
        report_url: URL of the Power BI report
        output_path: Path where PDF should be saved
        
    Returns:
        str: Path to the exported PDF file
        
    Raises:
        ValueError: If report_url is invalid
        ConnectionError: If unable to connect to Power BI
    """
    if not report_url:
        raise ValueError("Report URL cannot be empty")
    
    try:
        # Implementation here
        return output_path
    except Exception as e:
        logger.error(f"Failed to process report: {e}")
        raise
```

## Development Workflow

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Commit** with clear messages
6. **Push** to your fork
7. **Submit** a pull request

## Commit Messages

Format:
```
type: brief description

Detailed explanation if needed
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Example:
```
feat: add support for multiple reports

- Added batch processing capability
- Updated configuration for multiple URLs
- Added tests for batch processing
```

## Testing

Before submitting:

```bash
# Run setup verification
python test_setup.py

# Test your changes manually
python your_module.py

# Check code style (if available)
pylint your_module.py
```

## Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] All functions have docstrings
- [ ] Error handling is comprehensive
- [ ] Changes are tested
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No sensitive data in commits

## Questions?

Open an issue for discussion before starting major changes.

