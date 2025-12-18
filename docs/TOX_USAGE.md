# Tox Configuration Guide

This document explains the tox configuration for agent-manager and how to use it effectively.

---

## Overview

Tox is configured to provide multiple test environments for different purposes:
- Running tests with different Python versions
- Running tests with coverage
- Linting and formatting checks
- Type checking (optional)
- Specialized test runs (integration vs. unit)

---

## Quick Start

```bash
# Install tox
pip install -e ".[dev]"

# Run default environments (py312, lint, coverage)
tox

# Run a specific environment
tox -e py312

# List all available environments
tox list
```

---

## Available Environments

### Testing Environments

| Environment | Description | Command |
|-------------|-------------|---------|
| `py312` | Run tests with Python 3.12 | `tox -e py312` |
| `coverage` | Run tests with full coverage reporting | `tox -e coverage` |
| `integration` | Run only integration tests | `tox -e integration` |
| `unit` | Run only unit tests | `tox -e unit` |
| `quick` | Quick test run without coverage | `tox -e quick` |

### Code Quality Environments

| Environment | Description | Command |
|-------------|-------------|---------|
| `lint` | Run ruff linting | `tox -e lint` |
| `format` | Auto-format code with ruff | `tox -e format` |
| `format-check` | Check formatting without changes | `tox -e format-check` |
| `type-check` | Run mypy type checking (optional) | `tox -e type-check` |

### Combined Environments

| Environment | Description | Command |
|-------------|-------------|---------|
| `all` | Run all checks (lint + format + coverage) | `tox -e all` |

### Utility Environments

| Environment | Description | Command |
|-------------|-------------|---------|
| `clean` | Clean up generated files | `tox -e clean` |
| `coverage-report` | Generate coverage report from existing data | `tox -e coverage-report` |

---

## Common Usage Patterns

### During Development

```bash
# Quick test run while developing
tox -e quick

# Run tests with coverage when feature is complete
tox -e coverage

# Check formatting before committing
tox -e format-check

# Auto-fix formatting issues
tox -e format
```

### Before Committing

```bash
# Run all quality checks
tox -e all
```

### In CI/CD

```bash
# Run default environments
tox

# Or run all checks
tox -e all

# Parallel execution for speed
tox -p auto
```

### Debugging

```bash
# Run specific test file
tox -e py312 -- tests/test_agent_manager.py -v

# Run with pytest debugger
tox -e py312 -- --pdb

# Run specific test method
tox -e py312 -- tests/test_agent_manager.py::TestRunCommand::test_run_command_explicit
```

---

## Passing Arguments to Pytest

Any arguments after `--` are passed directly to pytest:

```bash
# Verbose output
tox -e py312 -- -v

# Show local variables on failure
tox -e py312 -- -l

# Stop on first failure
tox -e py312 -- -x

# Run only failed tests from last run
tox -e py312 -- --lf

# Run tests matching a pattern
tox -e py312 -- -k "config"
```

---

## Parallel Execution

Run multiple environments simultaneously for faster feedback:

```bash
# Auto-detect number of CPUs
tox -p auto

# Run specific environments in parallel
tox -e py312,lint,coverage -p auto

# Limit parallel processes
tox -p 2
```

---

## Coverage Reports

After running the `coverage` environment:

```bash
# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# View terminal report
tox -e coverage-report
```

Coverage reports show:
- **Line coverage**: Which lines were executed
- **Branch coverage**: Which code paths were taken
- **Missing lines**: Lines that weren't tested

---

## Configuration Details

### tox.ini Location

The `tox.ini` file is located in `agent_manager/tox.ini` (same directory as `pyproject.toml`).

### Key Configuration Sections

```ini
[tox]
# Default environments to run
envlist = py312, lint, coverage

[testenv]
# Base configuration for all test environments
deps = pytest, pytest-cov, PyYAML, GitPython

[pytest]
# Pytest configuration
testpaths = tests
addopts = -v --strict-markers

[coverage:run]
# Coverage tracking configuration
source = agent_manager

[coverage:report]
# Coverage reporting configuration
show_missing = true
```

---

## Customization

### Adding a New Test Environment

Add to `tox.ini`:

```ini
[testenv:myenv]
description = My custom test environment
deps =
    pytest
    my-custom-dependency
commands =
    pytest tests/my_special_tests/ {posargs}
```

Run with:
```bash
tox -e myenv
```

### Setting Environment Variables

```ini
[testenv:with-env]
setenv =
    MY_VAR = value
    DEBUG = 1
commands =
    pytest tests/ {posargs}
```

---

## Troubleshooting

### Tox Not Found

```bash
# Install tox
pip install tox

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Environment Recreation

If dependencies change, recreate the environment:

```bash
# Recreate all environments
tox -r

# Recreate specific environment
tox -e py312 -r
```

### Clean Build

Remove all tox environments and rebuild:

```bash
# Clean everything
tox -e clean

# Rebuild from scratch
rm -rf .tox
tox
```

### Dependency Issues

If you get dependency conflicts:

```bash
# Check installed packages in environment
tox -e py312 --notest
.tox/py312/bin/pip list

# Force reinstall
tox -e py312 -r --force-dep pytest==7.4.0
```

---

## Integration with IDEs

### PyCharm

1. Go to Settings → Tools → Python Integrated Tools
2. Set Default test runner to "pytest"
3. Set tox as external tool (optional)

### VS Code

Add to `.vscode/settings.json`:

```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install tox
        run: pip install tox
      - name: Run tox
        run: tox -e all
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### GitLab CI

```yaml
test:
  image: python:3.12
  before_script:
    - pip install tox
  script:
    - tox -e all
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## Best Practices

### 1. Run Tests Before Committing

```bash
# Quick pre-commit check
tox -e quick

# Full check before pushing
tox -e all
```

### 2. Use Parallel Execution

```bash
# Save time with parallel execution
tox -p auto
```

### 3. Keep Environments Clean

```bash
# Periodically clean old environments
tox -e clean
```

### 4. Check Coverage

```bash
# Aim for high coverage
tox -e coverage

# Review HTML report
open htmlcov/index.html
```

### 5. Use Specific Environments

```bash
# Don't run everything during development
tox -e quick  # Fast feedback

# Run comprehensive checks before PR
tox -e all
```

---

## Performance Tips

1. **Use `quick` environment during development** - Skips coverage for faster runs
2. **Run tests in parallel** - Use `-p auto` flag
3. **Run specific test files** - Don't run entire suite every time
4. **Cache dependencies** - Tox caches virtual environments
5. **Use `--lf` flag** - Rerun only failed tests

---

## Summary

Tox provides:
- ✅ Isolated test environments
- ✅ Reproducible test runs
- ✅ Easy CI/CD integration
- ✅ Multiple test configurations
- ✅ Parallel execution support

**Default command**: `tox`  
**Recommended for CI**: `tox -e all`  
**For development**: `tox -e quick`

---

For more information, see the [official tox documentation](https://tox.wiki/).

