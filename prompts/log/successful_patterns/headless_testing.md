# Headless Testing Pattern

## Problem
GUI tests fail in headless environments (CI/CD, automated testing) because they try to create real Qt widgets or show dialogs.

## Symptoms
- Tests fail with "could not connect to display" errors
- QFileDialog tests hang or fail
- Widget creation fails in headless environment
- Tests are not portable across different environments

## Root Cause
Tests are written assuming a graphical environment with user interaction capabilities.

## Solution Pattern

### 1. Headless Qt Environment
```python
# Set environment variable for headless Qt
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Or use pytest-qt fixture
def test_widget(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)
    # Test widget behavior
```

### 2. Dependency Injection for File Operations
```python
# Instead of direct QFileDialog usage
class MyWidget:
    def __init__(self, file_dialog_provider=None):
        self.file_dialog_provider = file_dialog_provider or QFileDialog.getOpenFileName
    
    def open_file(self):
        filename, _ = self.file_dialog_provider()
        if filename:
            self.load_file(filename)

# In tests, inject mock file dialog
def test_open_file():
    widget = MyWidget(file_dialog_provider=lambda: ("test.txt", ""))
    widget.open_file()
    assert widget.current_file == "test.txt"
```

### 3. Mock External Dependencies
```python
# Mock file I/O operations
def test_save_functionality(monkeypatch, tmp_path):
    # Mock the save dialog to return a temp file
    def mock_save_dialog(*args, **kwargs):
        return str(tmp_path / "test_output.txt"), ""
    
    monkeypatch.setattr(QFileDialog, 'getSaveFileName', mock_save_dialog)
    
    widget = MyWidget()
    widget.save_data()
    assert (tmp_path / "test_output.txt").exists()
```

### 4. Synthetic Test Data
```python
# Use synthetic data instead of real files
def test_data_loading():
    # Create synthetic data instead of loading real PINT files
    synthetic_data = {
        'residuals': [0.1, -0.2, 0.3, -0.1],
        'times': [1000, 2000, 3000, 4000]
    }
    
    model = MockModel()
    model.data = synthetic_data
    widget = MyWidget()
    widget.set_model(model)
    assert len(widget.displayed_residuals) == 4
```

## Implementation Checklist
- [ ] Set QT_QPA_PLATFORM=offscreen for headless testing
- [ ] Use pytest-qt fixtures for widget testing
- [ ] Inject file dialog providers instead of direct usage
- [ ] Mock external dependencies (file I/O, network calls)
- [ ] Use synthetic data for unit tests
- [ ] Test both headless and GUI environments

## Test Patterns
```python
# Basic headless widget test
def test_widget_creation(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)
    assert widget.isVisible() == False  # Widget created but not shown

# Test with dependency injection
def test_file_operations(monkeypatch, tmp_path):
    def mock_file_dialog(*args, **kwargs):
        return str(tmp_path / "test.txt"), ""
    
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', mock_file_dialog)
    
    widget = MyWidget()
    widget.open_file()
    assert widget.current_file is not None

# Test signal/slot interactions
def test_signal_handling(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)
    
    # Simulate signal emission
    widget.model.data_loaded.emit("test_data")
    assert widget.displayed_data == "test_data"
```

## Environment Setup
```bash
# For headless testing
export QT_QPA_PLATFORM=offscreen

# For pytest-qt
pip install pytest-qt

# For CI/CD
# Add QT_QPA_PLATFORM=offscreen to test environment
```

## Related Patterns
- **Dependency Injection**: Use for external dependencies
- **Mock Objects**: Use for complex external systems
- **Synthetic Data**: Use for predictable test scenarios
- **Environment Isolation**: Use for consistent test environments

## Anti-Patterns to Avoid
- **Direct QFileDialog usage**: Use dependency injection instead
- **Real file I/O in tests**: Use mocks or temp files instead
- **Environment-dependent tests**: Use headless mode consistently
- **Complex setup/teardown**: Keep tests simple and isolated

## Common Issues and Solutions
- **"could not connect to display"**: Set QT_QPA_PLATFORM=offscreen
- **Tests hang on dialogs**: Use dependency injection for dialogs
- **Inconsistent test results**: Use synthetic data and mocks
- **Slow tests**: Use headless mode and avoid real I/O
