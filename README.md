# PINT GUI Development Environment

A development container setup for building PINT (Pulsar Timing) GUI applications using PyQt6.

## Overview

This project provides a complete development environment for PINT GUI development, including:
- Python 3.11 with PyQt6
- PINT pulsar timing library
- X11 forwarding for GUI applications on macOS
- All necessary dependencies pre-installed

## Prerequisites

### macOS Requirements
- macOS 10.15 (Catalina) or later
- Apple Silicon (M1/M2/M3) or Intel Mac
- Docker Desktop for Mac
- Visual Studio Code with Dev Containers extension
- XQuartz (for GUI display)

## Setup Instructions

### 1. Install Docker Desktop
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Install and start Docker Desktop
3. Ensure Docker is running before proceeding

### 2. Install Visual Studio Code
1. Download VS Code from [code.visualstudio.com](https://code.visualstudio.com/)
2. Install the "Dev Containers" extension by Microsoft
3. Restart VS Code after installation

### 3. Install XQuartz (Critical for GUI Applications)
1. Download XQuartz from [xquartz.org](https://www.xquartz.org/)
2. Install XQuartz (requires admin password)
3. **IMPORTANT**: After installation, you MUST reboot your Mac for XQuartz to work properly
4. After reboot, open XQuartz from Applications > Utilities
5. Go to XQuartz > Preferences > Security
6. Check "Allow connections from network clients"
7. **CRITICAL**: You must reboot again after enabling this setting

### 4. Verify XQuartz Configuration
After the second reboot, verify XQuartz is properly configured:
```bash
ps aux | grep Xquartz
```
You should see `--listen tcp` in the output. If you see `--nolisten tcp`, XQuartz is not properly configured and you need to reboot again.

### 5. Clone and Open Project
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd pylk
   ```
2. Open in VS Code:
   ```bash
   code .
   ```

### 6. Open in Dev Container
1. VS Code should detect the `.devcontainer` folder
2. Click "Reopen in Container" when prompted
3. Or use Command Palette (Cmd+Shift+P) > "Dev Containers: Reopen in Container"

## Running the Application

### ⚠️ Important: X11 Forwarding Setup
**After every reboot**, you need to allow X11 connections from Docker:
```bash
xhost +localhost
```
This is required for GUI applications to work in the Docker container.

### Start the GUI Application
Once the container is running, you can start the PINT GUI:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the main application
pylk
```

### Alternative: Run pintk directly
```bash
# Run the PINT GUI tool
pintk
```

## Troubleshooting

### GUI Display Issues
If you get "couldn't connect to display" errors:

1. **First, try the X11 forwarding command** (most common fix):
   ```bash
   xhost +localhost
   ```

2. **Check XQuartz is running**:
   ```bash
   ps aux | grep Xquartz
   ```
   Should show `--listen tcp`

3. **Verify DISPLAY variable**:
   ```bash
   echo $DISPLAY
   ```
   Should show `host.docker.internal:0`

4. **If still not working**:
   - Reboot your Mac
   - Ensure XQuartz is set to "Allow connections from network clients"
   - Check that Docker Desktop is running

### Container Build Issues
If the container fails to build:

1. **Check Docker is running**:
   ```bash
   docker --version
   ```

2. **Clean Docker cache**:
   ```bash
   docker system prune -a
   ```

3. **Rebuild container**:
   - Command Palette > "Dev Containers: Rebuild Container"

### Python Package Issues
If Python packages are not found:

1. **Check virtual environment**:
   ```bash
   which python
   source .venv/bin/activate
   ```

2. **Verify system packages**:
   ```bash
   python -c "import PyQt6; print('PyQt6 OK')"
   python -c "import pint; print('PINT OK')"
   ```

## Development

### Project Structure
```
pylk/
├── .devcontainer/          # Dev container configuration
│   ├── Dockerfile         # Container image definition
│   └── devcontainer.json  # VS Code dev container settings
├── pylk/                  # Main application code
│   └── app.py            # Main application entry point
├── CHANGELOG.md          # Project changelog
└── README.md             # This file
```

### Adding Dependencies
To add new Python packages:

1. Edit `.devcontainer/devcontainer.json`
2. Add packages to `postCreateCommand`
3. Rebuild the container

### Customizing the Container
Modify `.devcontainer/Dockerfile` to:
- Add system packages
- Change Python version
- Install additional tools

## Architecture Notes

### Why This Setup?
- **PyQt6**: Modern Qt6 bindings for Python
- **System Packages**: PyQt6 installed via apt for better compatibility
- **Virtual Environment**: Isolated Python environment with system package access
- **X11 Forwarding**: Enables GUI applications to run in containers on macOS

### Display Forwarding
The container uses X11 forwarding to display GUI applications:
- `DISPLAY=host.docker.internal:0` routes display to macOS
- XQuartz acts as the X11 server on macOS
- `.Xauthority` is mounted for authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test in the dev container
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues with:
- **Dev Container**: Check VS Code Dev Containers documentation
- **XQuartz**: Check XQuartz documentation and ensure proper reboot
- **Docker**: Check Docker Desktop documentation
- **PINT**: Check PINT documentation

## Known Issues

- **macOS Apple Silicon**: Requires XQuartz and proper reboot sequence
- **Memory Usage**: PyQt6 compilation can be memory-intensive
- **Display Latency**: X11 forwarding may have slight display lag

---

**Note**: This development environment is specifically optimized for macOS with Apple Silicon. For other platforms, you may need to adjust the X11 forwarding configuration.
