# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Pre-fit residuals plotting** - Load PAR+TIM files and display pre-fit timing residuals with error bars
- **PulsarModel** - PINT integration for loading pulsar data and computing residuals
- **ProjectController** - Project lifecycle management with signal-based architecture
- **PlkView** - Matplotlib-based plotting widget with save functionality
- **MainWindow integration** - Seamless switching between placeholder and plotting views
- **Status bar updates** - Real-time display of TOA count, RMS, and file information
- **Save Plot functionality** - Export residuals plots as PNG files via menu or button
- **Improved UI behavior** - PlkView only visible when project is loaded, preventing empty plot display
- **Test-friendly save functionality** - Automatic temporary file usage during testing to avoid dialog boxes
- **Window sizing** - Minimum window size set to 1000x800 pixels (matching pintk)
- **Plot widget sizing** - PlkView automatically ensures at least 80% of main window width for proper plot display
- **Dock widget synchronization** - Dock widget close buttons ('x') now automatically update corresponding menu bar checkboxes
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
