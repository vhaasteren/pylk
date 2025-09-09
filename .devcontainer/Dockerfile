FROM python:3.12-bookworm

# Install system dependencies and PyQt6
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-pyqt6 \
    python3-pyqt6.qtsvg \
    python3-pyqt6.qtmultimedia \
    qt6-base-dev \
    qt6-base-dev-tools \
    qt6-declarative-dev \
    qt6-declarative-dev-tools \
    qt6-multimedia-dev \
    qt6-charts-dev \
    qt6-connectivity-dev \
    qt6-datavisualization-dev \
    qt6-3d-dev \
    qt6-5compat-dev \
    qt6-pdf-dev \
    qt6-lottie-dev \
    qt6-httpserver-dev \
    qt6-languageserver-dev \
    qt6-networkauth-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxkbcommon-x11-dev \
    libxcb-cursor-dev \
    libxcb-icccm4-dev \
    xauth \
    build-essential \
    pkg-config \
    python3-dev \
    python3-pip \
    git \
    curl \
    wget \
 && rm -rf /var/lib/apt/lists/* \
 && ln -sf /usr/bin/qmake6 /usr/bin/qmake

# Create a non-root user for development
RUN useradd -m -s /bin/bash vscode \
    && usermod -aG sudo vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to the vscode user
USER vscode
WORKDIR /workspaces/pylk

# Set up Python environment
ENV PATH="/home/vscode/.local/bin:${PATH}"

