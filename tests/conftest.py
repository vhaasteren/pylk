import os

# Force headless Qt for tests (override devcontainer settings)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = ""

# Use pytest-qt's built-in fixtures
# pytest-qt automatically provides qapp and qtbot fixtures
