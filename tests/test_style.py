import subprocess, sys

def test_ruff():
    subprocess.check_call([sys.executable, "-m", "ruff", "check", "pylk"])

def test_black():
    subprocess.check_call([sys.executable, "-m", "black", "--check", "pylk"])
