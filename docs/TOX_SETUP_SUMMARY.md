# Tox Configuration Summary

This document summarizes the tox setup for the agent-manager project.

---

## ✅ What Was Configured

### 1. **Added Tox Dependency**

Updated `pyproject.toml`:
```toml
[project.optional-dependencies]
dev = [
    "ruff>=0.1.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "tox>=4.0.0",  # ← Added
]
```

### 2. **Created `tox.ini`**

Comprehensive tox configuration with 13 test environments:

#### Test Environments
- **`py312`** - Run tests with Python 3.12
- **`coverage`** - Run tests with full coverage reporting
- **`integration`** - Run only integration tests
- **`unit`** - Run only unit tests  
- **`quick`** - Quick test run without coverage

#### Code Quality Environments
- **`lint`** - Run ruff linting
- **`format`** - Auto-format code with ruff
- **`format-check`** - Check formatting without changes
- **`type-check`** - Run mypy type checking (optional)

#### Combined Environments
- **`all`** - Run all checks (lint + format + coverage)

#### Utility Environments
- **`clean`** - Clean up generated files
- **`coverage-report`** - Generate coverage report

### 3. **Updated Documentation**

#### Created `TOX_USAGE.md`
- Comprehensive usage guide
- All environments explained
- Common usage patterns
- CI/CD integration examples
- Troubleshooting tips

#### Updated `tests/README.md`
- Added "Running Tests with Tox" section
- Tox environment examples
- Parallel execution instructions
- CI/CD usage examples

---

## 🚀 Quick Start

```bash
# Install tox and dependencies
cd agent_manager
pip install -e ".[dev]"

# Run default environments (py312, lint, coverage)
tox

# List all available environments
tox list

# Run a specific environment
tox -e py312

# Run tests with coverage
tox -e coverage

# Run all checks before committing
tox -e all
```

---

## 📋 Default Environments

When you run `tox` without arguments, it runs:
1. **`py312`** - Tests with Python 3.12
2. **`lint`** - Ruff linting
3. **`coverage`** - Tests with coverage reporting

---

## 🎯 Common Workflows

### During Development
```bash
# Quick test feedback
tox -e quick

# Run specific test file
tox -e py312 -- tests/test_agent_manager.py
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

# Or comprehensive checks
tox -e all

# Parallel execution
tox -p auto
```

---

## 📊 Configuration Highlights

### Pytest Configuration
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short --disable-warnings

markers =
    integration: Integration tests
    unit: Unit tests
    slow: Slow running tests
```

### Coverage Configuration
```ini
[coverage:run]
source = agent_manager
omit =
    */tests/*
    */test_*.py
    */__pycache__/*

[coverage:report]
precision = 2
show_missing = true
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

---

## 🔧 Advanced Usage

### Passing Arguments to Pytest
```bash
# Verbose output
tox -e py312 -- -v

# Stop on first failure
tox -e py312 -- -x

# Run tests matching pattern
tox -e py312 -- -k "config"

# Run with debugger
tox -e py312 -- --pdb
```

### Parallel Execution
```bash
# Auto-detect CPUs
tox -p auto

# Run specific environments in parallel
tox -e py312,lint,coverage -p auto
```

### Recreate Environments
```bash
# Recreate all environments
tox -r

# Recreate specific environment
tox -e py312 -r
```

---

## 📁 File Locations

```
agent_manager/
├── tox.ini                          # Tox configuration
├── pyproject.toml                   # Package config (includes tox dep)
├── TOX_USAGE.md                     # Detailed usage guide
├── TOX_SETUP_SUMMARY.md            # This file
└── tests/
    ├── README.md                    # Updated with tox section
    └── test_agent_manager.py        # Integration tests
```

---

## 🎨 Benefits

### 1. **Isolated Environments**
- Each tox environment runs in its own virtualenv
- No dependency conflicts
- Reproducible results

### 2. **Multiple Test Configurations**
- Run tests with different Python versions
- Run with/without coverage
- Separate integration and unit tests
- Combine checks (lint + format + test)

### 3. **CI/CD Ready**
- Single command for all checks: `tox -e all`
- Parallel execution support: `tox -p auto`
- Coverage reporting (XML, HTML, terminal)

### 4. **Developer Friendly**
- Quick feedback with `tox -e quick`
- Easy environment recreation with `-r`
- Pass arguments directly to pytest
- Clean up generated files with `tox -e clean`

### 5. **Consistent**
- Same commands work locally and in CI
- Same environment for all developers
- No "works on my machine" issues

---

## 🔗 Integration Examples

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

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running tox checks..."
tox -e format-check,lint,quick

if [ $? -ne 0 ]; then
    echo "Tox checks failed. Commit aborted."
    exit 1
fi
```

---

## 📚 Resources

- **Tox Documentation**: https://tox.wiki/
- **Pytest Documentation**: https://docs.pytest.org/
- **Coverage.py**: https://coverage.readthedocs.io/
- **Ruff Documentation**: https://docs.astral.sh/ruff/

---

## ✅ Verification

To verify the tox setup:

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. List environments
tox list

# Expected output:
# py312 -> Run tests with Python 3.12
# lint -> Run linting with ruff
# coverage -> Run tests with coverage analysis
# ...

# 3. Run quick test
tox -e quick

# 4. Run all checks
tox -e all
```

---

## 🎯 Next Steps

1. **Install tox**: `pip install -e ".[dev]"`
2. **Run tests**: `tox`
3. **View coverage**: `open htmlcov/index.html`
4. **Integrate with CI/CD**: Add tox to your CI pipeline
5. **Set up pre-commit hooks**: Run tox checks before commits

---

**Status**: ✅ Tox is fully configured and ready to use!

**Default command**: `tox`  
**Recommended for CI**: `tox -e all`  
**For development**: `tox -e quick`

