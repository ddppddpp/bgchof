# Python 3.14 Modernization Guide for bgchof

## Executive Summary

This document outlines the changes needed to modernize the bgchof codebase for Python 3.14 compatibility and to leverage modern Python features introduced in recent versions (3.10-3.14).

## Current State

- **Current Python Version**: 3.9+
- **Target Python Version**: 3.14
- **Key Dependencies**: pytest, flask, requests

## Recommended Modernization Changes

### 1. Type Hints and Type System Enhancements

#### 1.1 Use PEP 604 Union Syntax (Python 3.10+)

**Current Pattern:**
```python
from typing import Optional, Union, List

def read_fasting_list(input_year: int) -> Optional[List[str]]:
    ...
```

**Modernized:**
```python
def read_fasting_list(input_year: int) -> list[str] | None:
    ...
```

**Files to Update:**
- `src/bgchof.py`
- `src/fasting_io.py`
- `src/generateCalendar.py`
- `src/calculateEasterSunday.py`

#### 1.2 Use Built-in Generic Types (Python 3.9+)

**Current Pattern:**
```python
from typing import List, Dict

def generate_list(input_year: int) -> List[int]:
    ...
```

**Modernized:**
```python
def generate_list(input_year: int) -> list[int]:
    ...
```

**Impact:** Remove all imports from `typing` module for `List`, `Dict`, `Tuple`, `Set`

### 2. Structural Pattern Matching (Python 3.10+)

#### 2.1 Replace Complex if-elif Chains

**File:** `src/calculateEasterSunday.py` (lines 130-149)

**Current:**
```python
if remainder_28 in [9, 15, 20, 26]:
    match_column = "II"
elif remainder_28 in [4, 10, 21, 27]:
    match_column = "III"
elif remainder_28 in [5, 11, 16, 22]:
    match_column = "IV"
# ... etc
```

**Modernized:**
```python
match remainder_28:
    case 9 | 15 | 20 | 26:
        match_column = "II"
    case 4 | 10 | 21 | 27:
        match_column = "III"
    case 5 | 11 | 16 | 22:
        match_column = "IV"
    case 6 | 17 | 23 | 0:
        match_column = "V"
    case 1 | 7 | 12 | 18:
        match_column = "VI"
    case 2 | 13 | 19 | 24:
        match_column = "VII"
    case 3 | 8 | 14 | 25:
        match_column = "VIII"
    case _:
        raise ValueError(f"Invalid remainder_28: {remainder_28}")
```

#### 2.2 Simplify Status Value Handling

**File:** `src/fasting_status.py` (lines 51-62)

**Current:**
```python
if input_value == 0:
    return_message = fastingStatusMessage[0]
elif input_value < 7:
    # complex logic
```

**Modernized:**
```python
match input_value:
    case 0:
        return fastingStatusMessage[0]
    case n if 1 <= n < 7:
        # build message
    case _:
        raise ValueError(f"Invalid fasting value: {input_value}")
```

### 3. Exception Groups and except* (Python 3.11+)

**File:** `src/fasting_io.py` (lines 67, 80)

**Current:**
```python
except:
    sys.stderr.write("Can't create the cache directory.\n")
    exit(1)
```

**Modernized:**
```python
except OSError as e:
    sys.stderr.write(f"Can't create the cache directory: {e}\n")
    raise
except PermissionError as e:
    sys.stderr.write(f"Permission denied: {e}\n")
    raise
```

**Critical:** Replace all bare `except:` clauses with specific exception types.

### 4. f-strings Enhancements (Python 3.12+)

#### 4.1 Use f-string Debugging Syntax

**Current:**
```python
sys.stderr.write("Can't find the data file for year " + str(input_year) + ". Creating new one...\n")
```

**Modernized:**
```python
sys.stderr.write(f"Can't find the data file for year {input_year}. Creating new one...\n")
```

#### 4.2 Use Multi-line f-strings

**File:** `src/generateCalendar.py` (line 390)

**Current:**
```python
sys.stderr.write(f"USAGE:{argv[0]} <year for which to generate \
                a fasting caledndar in format YYYY> \n")
```

**Modernized:**
```python
sys.stderr.write(
    f"USAGE: {argv[0]} <year for which to generate "
    f"a fasting calendar in format YYYY>\n"
)
```

### 5. dataclasses and Frozen Dataclasses

**New File:** `src/models.py`

```python
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True, slots=True)
class FastingDay:
    """Represents a single day's fasting status."""
    date: date
    status: int
    
    def __post_init__(self):
        if not 0 <= self.status <= 6:
            raise ValueError(f"Status must be 0-6, got {self.status}")

@dataclass(frozen=True, slots=True)
class FastingYear:
    """Represents a year's fasting calendar."""
    year: int
    days: list[int]
    
    def __post_init__(self):
        if len(self.days) not in (365, 366):
            raise ValueError(f"Invalid number of days: {len(self.days)}")
```

### 6. pathlib Instead of os.path

**File:** `src/fasting_io.py`

**Current:**
```python
import os
file_name = BGCHOF_CFG_CFG_DATAFILE_PREFIX + str(input_year) + ".csv"
if not os.path.isdir(BGCHOF_CFG_CFG_DATAFILE_PREFIX):
    os.makedirs(BGCHOF_CFG_CFG_DATAFILE_PREFIX, CFG_DATAFILE_MODE, exist_ok=True)
```

**Modernized:**
```python
from pathlib import Path

cache_dir = Path(BGCHOF_CFG_CFG_DATAFILE_PREFIX)
file_path = cache_dir / f"{input_year}.csv"
cache_dir.mkdir(mode=CFG_DATAFILE_MODE, parents=True, exist_ok=True)
```

### 7. Modern Package Configuration

#### 7.1 Replace setup.py with pyproject.toml

**Current:** `setup.py` + minimal `pyproject.toml`

**Modernized:** Single `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "bgchof"
version = "0.6.0"
description = "(B)ul(g)arian (Ch)ristian (O)rthodox (F)asting"
authors = [
    {name = "Ivailo Djilianov", email = "your.email@example.com"}
]
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
keywords = ["fasting", "orthodox", "calendar", "bulgarian"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
]

dependencies = [
    "flask>=3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "black>=24.0.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "requests>=2.31.0",
]

[project.urls]
Homepage = "https://www.github.com/ddppddpp/bgchof"
Repository = "https://www.github.com/ddppddpp/bgchof"
Issues = "https://github.com/ddppddpp/bgchof/issues"

[project.scripts]
bgchof = "bgchof:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
bgchof = ["py.typed"]

[tool.black]
line-length = 100
target-version = ["py310", "py311", "py312", "py313", "py314"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by black)
]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=term-missing --cov-report=html"
```

### 8. Replace distutils (Removed in Python 3.12)

**File:** `setup.py` (lines 1-4)

**Current:**
```python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
```

**Issue:** `distutils` was removed in Python 3.12

**Solution:** Remove fallback, setuptools is standard now. Better yet, migrate to pyproject.toml entirely.

### 9. Modernize String Formatting

**Replace all string concatenation with f-strings:**

**Files to update:**
- `src/bgchof.py` (line 106)
- `src/calculateEasterSunday.py` (lines 51, 232)
- `src/fasting_io.py` (lines 40, 81)
- `src/generateCalendar.py` (line 390)

### 10. Use tomllib for Configuration (Python 3.11+)

**New Feature:** Add TOML-based configuration support

**New File:** `src/config.py`

```python
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # fallback for 3.10

def load_config() -> dict:
    """Load configuration from pyproject.toml or config.toml"""
    config_path = Path("config.toml")
    if not config_path.exists():
        config_path = Path("pyproject.toml")
    
    with open(config_path, "rb") as f:
        return tomllib.load(f)
```

### 11. Improve Error Messages with Notes (Python 3.11+)

**Current:**
```python
raise ValueError("The argument should be a valid year for which to calculate Easter Sunday")
```

**Modernized:**
```python
err = ValueError(
    f"Invalid year: {input_year}. Must be between {I_FIRST_VALID_YEAR} and {I_LAST_VALID_YEAR}"
)
err.add_note(f"Received: {input_year} (type: {type(input_year).__name__})")
err.add_note("Bulgaria adopted the Gregorian calendar in 1917")
raise err
```

### 12. Use Self Type (Python 3.11+)

For future class-based refactoring:

```python
from typing import Self

class FastingCalculator:
    def with_year(self, year: int) -> Self:
        self.year = year
        return self
```

### 13. Modernize Docker Base Image

**File:** `Dockerfile`

**Current:**
```dockerfile
FROM python:3.9-slim-bullseye
```

**Modernized:**
```dockerfile
FROM python:3.14-slim-bookworm
```

### 14. Update Testing Framework

**File:** `tox.ini`

**Current:**
```ini
[tox]
envlist=py39
```

**Modernized:**
```ini
[tox]
envlist = py310,py311,py312,py313,py314
skip_missing_interpreters = true

[testenv]
deps = 
    pytest>=8.0.0
    pytest-cov>=4.1.0
    ruff>=0.3.0
    mypy>=1.8.0
commands =
    ruff check src/ tests/
    mypy src/
    pytest --cov=src --cov-report=term-missing
```

### 15. Add Type Checking Support

**New File:** `src/py.typed`

Empty file to indicate the package supports type checking.

**Update all modules to include complete type hints:**

```python
from typing import Never  # Python 3.11+

def unreachable() -> Never:
    raise AssertionError("This code should never be reached")
```

## Migration Priority

### Phase 1: Critical (Breaking Changes)
1. ✅ Remove distutils fallback
2. ✅ Update Python version requirement to 3.10+
3. ✅ Replace bare `except:` clauses
4. ✅ Update Docker base image

### Phase 2: High Priority (Modern Syntax)
1. ✅ Convert to built-in generic types (list, dict, etc.)
2. ✅ Use PEP 604 union syntax (X | Y)
3. ✅ Add structural pattern matching
4. ✅ Migrate to pyproject.toml

### Phase 3: Medium Priority (Improvements)
1. ✅ Replace string concatenation with f-strings
2. ✅ Use pathlib instead of os.path
3. ✅ Add dataclasses for data structures
4. ✅ Improve error messages with notes

### Phase 4: Low Priority (Nice to Have)
1. ✅ Add tomllib configuration support
2. ✅ Add comprehensive type hints
3. ✅ Create py.typed marker
4. ✅ Update testing infrastructure

## Compatibility Strategy

### Option 1: Drop Python 3.9 Support
- Simplest approach
- Allows immediate use of all modern features
- Update `python_requires=">=3.10"`

### Option 2: Maintain Backward Compatibility
- Keep Python 3.9 support temporarily
- Use conditional imports for new features
- Gradual migration path

**Recommended:** Option 1 - Python 3.9 reaches end-of-life in October 2025

## Testing Strategy

1. **Update CI/CD** to test against Python 3.10-3.14
2. **Add type checking** to CI pipeline (mypy)
3. **Add linting** with ruff (faster than flake8)
4. **Increase test coverage** to 90%+

## Dependencies Update

### Current
```
pytest>=6.2.5, <6.3.0
flask>=2.0.0, <3.0.0
requests>=2.25.0, <3.0.0
```

### Modernized
```
pytest>=8.0.0
flask>=3.0.0
requests>=2.31.0
```

## Breaking Changes for Users

1. **Minimum Python version**: 3.9 → 3.10
2. **Import changes**: None (internal only)
3. **API changes**: None (backward compatible)
4. **Deprecated functions**: Remove camelCase functions (already deprecated)

## Timeline Recommendation

- **Q1 2026**: Phase 1 (Critical changes)
- **Q2 2026**: Phase 2 (Modern syntax)
- **Q3 2026**: Phase 3 (Improvements)
- **Q4 2026**: Phase 4 (Nice to have)

## Resources

- [What's New in Python 3.10](https://docs.python.org/3/whatsnew/3.10.html)
- [What's New in Python 3.11](https://docs.python.org/3/whatsnew/3.11.html)
- [What's New in Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)
- [What's New in Python 3.13](https://docs.python.org/3/whatsnew/3.13.html)
- [What's New in Python 3.14](https://docs.python.org/3.14/whatsnew/3.14.html)
- [PEP 604 – Union Types](https://peps.python.org/pep-0604/)
- [PEP 634 – Structural Pattern Matching](https://peps.python.org/pep-0634/)
- [PEP 680 – tomllib](https://peps.python.org/pep-0680/)