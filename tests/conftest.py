import os

# Set headless Qt as default for tests
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Use pytest-qt's built-in fixtures
# pytest-qt automatically provides qapp and qtbot fixtures
