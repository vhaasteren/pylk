# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive development workflow documentation (`development-workflow.md`)
- AI prompt templates for planning, reviewing, and committing (`prompts/`)
- RAG (Retrieval-Augmented Generation) tools for AI-assisted development
- Pre-commit hooks for code quality (Black, Ruff, Commitizen)
- Automated versioning with setuptools_scm
- Makefile targets for common development tasks
- Test infrastructure with pytest and pytest-qt
- Code style guidelines and contributing documentation

### Changed
- **BREAKING**: Migrated from `setup.py`/`setup.cfg` to modern `pyproject.toml` configuration
- **BREAKING**: Package name changed from `pylk` to `pylk-pulsar` for PyPI compatibility
- Updated project structure to follow modern Python packaging standards
- Improved import organization and code formatting
- Enhanced development container configuration with additional tools

### Fixed
- Import sorting issues across all Python files
- Code formatting inconsistencies
- Pre-commit hook compatibility issues
- Git repository ownership issues in development container

### Removed
- Legacy `setup.py` and `setup.cfg` files
- Old code directories from pre-commit checks (`pylk-old/`, `old-rag-code/`, `src-old/`)

### Security
- Temporarily disabled MyPy and detect-secrets hooks due to setuptools compatibility issues
- Added exclusions for old code directories to prevent false positives

## [0.1.0] - 2024-01-10

### Added
- Initial release of Pylk GUI for pint-pulsar
- Basic Qt-based interface using qtpy
- Main window with basic functionality
- Support for Python 3.8+

### Dependencies
- qtpy for cross-platform Qt support
- pint-pulsar for pulsar timing analysis
- astropy, numpy, scipy for scientific computing
- matplotlib for plotting
- loguru for logging
