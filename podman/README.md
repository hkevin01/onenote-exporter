# 🐳 Podman Setup for OneNote Exporter

Alternative container runtime setup using Podman instead of Docker.

## Why Podman?

- **Rootless**: Runs without root privileges for better security
- **Daemonless**: No background daemon required
- **Pod Support**: Native Kubernetes pod support
- **Docker Compatible**: Drop-in replacement for most Docker commands
- **Lightweight**: Lower resource usage than Docker

## Requirements

- **Podman**: Container runtime
- **podman-compose** (recommended) or **docker-compose**: For compose file support

## Installation

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install podman
pip install podman-compose
```

### Linux (RHEL/CentOS/Fedora)

```bash
sudo dnf install podman
pip install podman-compose
```

### macOS

```bash
brew install podman
pip install podman-compose

# Initialize podman machine (first time only)
podman machine init
podman machine start
```

### Windows

```bash
# Using winget
winget install RedHat.Podman

# Or download from: https://podman.io/getting-started/installation
# Then install podman-compose:
pip install podman-compose
```

## Quick Start

### 1. One-Command Setup

```bash
# Clone repository
git clone https://github.com/username/onenote-exporter.git
cd onenote-exporter

# Run Podman setup
./podman/setup-podman.sh     # Linux/macOS
# OR
podman\setup-podman.bat      # Windows
```

### 2. Manual Setup

```bash
# 1. Create directories and environment
mkdir -p output cache
cp .env.example .env

# 2. Edit .env with Azure credentials
# TENANT_ID=your-tenant-id
# CLIENT_ID=your-client-id

# 3. Build with Podman
cd podman
podman-compose -f podman-compose.yml build

# 4. Start using
podman-compose -f podman-compose.yml run --rm onenote-exporter --list
```

## Usage Commands

### List Notebooks

```bash
podman-compose -f podman/podman-compose.yml run --rm onenote-exporter --list
```

### Export Notebook

```bash
podman-compose -f podman/podman-compose.yml run --rm onenote-exporter \
  --notebook "My Notes" --merge --formats md,docx
```

### Export by ID

```bash
podman-compose -f podman/podman-compose.yml run --rm onenote-exporter \
  --notebook-id "1-abc123..." --merge
```

## Alternative: Direct Podman Commands

If you prefer not to use compose:

```bash
# Build image
podman build -t onenote-exporter .

# Run with environment variables
podman run --rm -it \
  -e TENANT_ID=your-tenant-id \
  -e CLIENT_ID=your-client-id \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/cache:/app/.cache" \
  onenote-exporter --notebook "My Notes" --merge
```

## Troubleshooting

### Podman Machine (macOS/Windows)

```bash
# Check machine status
podman machine list

# Start machine if stopped
podman machine start

# Reset if issues
podman machine stop
podman machine rm
podman machine init
podman machine start
```

### Permission Issues (Linux)

```bash
# Enable rootless mode
echo 'kernel.unprivileged_userns_clone=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Or use system-wide install
sudo podman run --rm -it ...
```

### Compose Tool Missing

```bash
# Install podman-compose
pip install podman-compose

# Or use docker-compose as fallback
# (works with podman socket)
sudo systemctl enable --now podman.socket
export DOCKER_HOST=unix:///run/user/$UID/podman/podman.sock
```

## Benefits vs Docker

| Feature | Podman | Docker |
|---------|--------|--------|
| Root required | No | Yes |
| Background daemon | No | Yes |
| Resource usage | Lower | Higher |
| Security | Higher | Standard |
| Kubernetes pods | Native | Via compose |
| Compatibility | Docker API | Native |

## Files in this Directory

- `podman-compose.yml` - Podman compose configuration
- `setup-podman.sh` - Linux/macOS setup script
- `setup-podman.bat` - Windows setup script
- `README.md` - This documentation

## Back to Docker

To switch back to Docker, simply use the root-level setup:

```bash
./setup.sh              # Linux/macOS
setup.bat               # Windows
```

Both setups can coexist - use whichever container runtime you prefer!
