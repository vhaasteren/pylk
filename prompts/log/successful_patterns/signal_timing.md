# Signal Timing Pattern

## Problem
Late signal subscription causes widgets to miss initial data updates, resulting in empty or stale displays.

## Symptoms
- Widget shows empty state when first loaded
- Data appears only after user interaction
- Inconsistent display between different loading scenarios

## Root Cause
Signals are emitted before the widget subscribes to them, causing the widget to miss the initial data update.

## Solution Pattern

### 1. Early Signal Emission
```python
# In model - emit signals immediately when data changes
def load_data(self, data):
    self._data = data
    self.data_loaded.emit(data)  # Emit immediately
```

### 2. Idempotent set_model()
```python
# In widget - handle signals idempotently
def set_model(self, model):
    self.model = model
    if model:
        # Subscribe to signals
        model.data_loaded.connect(self._on_data_loaded)
        # Render current state immediately
        self._on_data_loaded(model.data)
```

### 3. Immediate State Rendering
```python
# Always render current state, regardless of signal timing
def _on_data_loaded(self, data):
    if data:
        self._render_data(data)
    else:
        self._render_empty_state()
```

## Implementation Checklist
- [ ] Model emits signals immediately when data changes
- [ ] Widget subscribes to signals in set_model()
- [ ] Widget renders current state immediately after subscription
- [ ] Widget handles both signal-driven and direct data updates
- [ ] Widget gracefully handles empty/missing data

## Test Patterns
```python
# Test that widget renders data immediately when model is set
def test_widget_renders_immediately(self):
    model = MockModel()
    model.data = "test_data"
    widget = MyWidget()
    widget.set_model(model)
    assert widget.displayed_data == "test_data"

# Test that widget updates when signal is emitted
def test_widget_updates_on_signal(self):
    model = MockModel()
    widget = MyWidget()
    widget.set_model(model)
    model.data_loaded.emit("new_data")
    assert widget.displayed_data == "new_data"
```

## Related Patterns
- **Dependency Injection**: Use for model/widget relationships
- **State Management**: Keep widget state synchronized with model
- **Error Handling**: Gracefully handle missing or invalid data

## Anti-Patterns to Avoid
- **Late signal emission**: Don't delay signals for convenience
- **Missing immediate rendering**: Don't rely only on signals for initial state
- **Complex signal dependencies**: Keep signal/slot relationships simple
- **State synchronization bugs**: Ensure widget always reflects model state
