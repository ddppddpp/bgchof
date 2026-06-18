# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Critical Non-Obvious Patterns

### Module Import Structure
- Modules in `src/` must be imported WITHOUT the `src.` prefix (e.g., `import bgchof`, not `import src.bgchof`)
- API uses `context.py` to add parent directory to sys.path before importing
- Docker requires `ENV PYTHONPATH=/app/src:$PYTHONPATH` to make imports work

### Function Naming Convention Mismatch
- Core module uses snake_case: `get_fasting_message_for_date()`, `get_status_for_date()`
- Deprecated camelCase functions exist for compatibility: `getFastingMessageForDate()`, `getStatusForDate()`
- ALWAYS use snake_case versions in new code - camelCase will be removed

### Cache System (Non-Standard)
- Fasting data cached in `.bgchofcache/` directory (created at runtime)
- Cache location controlled by `BGCHOF_CFG_CFG_DATAFILE_PREFIX` env var
- Cache files are CSV format: `{year}.csv` with columns [dayNumber, Status]
- Module auto-generates cache files on first use for each year
- Status values are integers 0-6 representing fasting levels

### Testing
- Run from project root: `pytest` or `tox`
- Tests must run from `src/` directory for CLI testing: `cd src && python bgchof.py`
- Tox config ignores specific pydocstyle errors: D100, D104

### Docker Specifics
- Flask API runs on port 5000 inside container
- API file location: `api/api.py` (not in src/)
- CMD uses incorrect Flask run syntax but works: `python3 api/api.py run --host=0.0.0.0`
- Actual Flask startup is via `if __name__ == '__main__': app.run(host='0.0.0.0',port='5000')`

### Code Style (from tox.ini)
- Formatter: black
- Docstring style: pydocstyle (with D100, D104 ignored)
- Python version: 3.9+ required

### Package Structure Quirk
- setup.py lists modules with inconsistent naming: `fastingIO`, `fastingStatus` (camelCase)
- Actual files use snake_case: `fasting_io.py`, `fasting_status.py`
- This mismatch is intentional for backward compatibility
