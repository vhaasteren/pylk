#!/bin/bash
set -euo pipefail

echo "🔧 Installing PINT (pint-pulsar) with fallback strategies..."

# Activate virtual environment
source .venv/bin/activate

# Update pip and setuptools first
echo "📦 Updating pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Strategy 1: Try installing pint-pulsar normally
echo "🎯 Strategy 1: Installing pint-pulsar normally..."
if pip install --no-cache-dir pint-pulsar; then
    echo "✅ pint-pulsar installed successfully!"
    python -c "import pint; print(f'PINT version: {pint.__version__}')"
    exit 0
fi

echo "❌ Strategy 1 failed, trying Strategy 2..."

# Strategy 2: Try installing without nestle dependency
echo "🎯 Strategy 2: Installing pint-pulsar without nestle dependency..."
if pip install --no-cache-dir pint-pulsar --no-deps; then
    echo "📦 Installing core dependencies manually..."
    pip install --no-cache-dir astropy numpy scipy matplotlib uncertainties loguru jplephem
    echo "✅ pint-pulsar installed without nestle dependency!"
    python -c "import pint; print(f'PINT version: {pint.__version__}')"
    exit 0
fi

echo "❌ Strategy 2 failed, trying Strategy 3..."

# Strategy 3: Try installing from source
echo "🎯 Strategy 3: Installing PINT from source..."
if pip install --no-cache-dir git+https://github.com/nanograv/PINT.git; then
    echo "✅ PINT installed from source successfully!"
    python -c "import pint; print(f'PINT version: {pint.__version__}')"
    exit 0
fi

echo "❌ Strategy 3 failed, trying Strategy 4..."

# Strategy 4: Try installing with specific setuptools version
echo "🎯 Strategy 4: Installing with specific setuptools version..."
pip install "setuptools<70"  # Use older setuptools version
if pip install --no-cache-dir pint-pulsar; then
    echo "✅ pint-pulsar installed with older setuptools!"
    python -c "import pint; print(f'PINT version: {pint.__version__}')"
    exit 0
fi

echo "❌ All strategies failed. Manual installation required."
echo "💡 Try running: pip install pint-pulsar"
echo "💡 Or: pip install git+https://github.com/nanograv/PINT.git"
exit 1
