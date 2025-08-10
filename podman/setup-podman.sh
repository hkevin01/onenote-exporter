#!/bin/bash
set -e

echo "🚀 OneNote Exporter Setup (Podman)"
echo "=================================="

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman is not installed!"
    echo ""
    echo "Please install Podman first:"
    echo "  Ubuntu/Debian: sudo apt install podman"
    echo "  RHEL/CentOS/Fedora: sudo dnf install podman"
    echo "  macOS: brew install podman"
    echo "  Windows: See https://podman.io/getting-started/installation"
    exit 1
fi

# Check if podman-compose is available
if command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "⚠️  Using docker-compose with podman (fallback)"
else
    echo "❌ Neither podman-compose nor docker-compose found!"
    echo ""
    echo "Please install podman-compose:"
    echo "  pip install podman-compose"
    echo "  OR install docker-compose for compatibility"
    exit 1
fi

echo "✅ Using: $COMPOSE_CMD"

# Navigate to project root
cd "$(dirname "$0")/.."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p output cache

# Copy environment template if .env doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file - please edit it with your Azure app details"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your TENANT_ID and CLIENT_ID"
    echo "2. Run: $COMPOSE_CMD -f podman/podman-compose.yml build"
    echo "3. Run: $COMPOSE_CMD -f podman/podman-compose.yml run --rm onenote-exporter --list"
    echo ""
    echo "For Azure app setup instructions, see README.md"
else
    echo "✅ .env file already exists"
fi

# Build the Podman image
echo "🔨 Building Podman image..."
cd podman
$COMPOSE_CMD -f podman-compose.yml build

echo ""
echo "🎉 Setup complete! Your OneNote Exporter is ready to use with Podman."
echo ""
echo "Quick start:"
echo "  $COMPOSE_CMD -f podman/podman-compose.yml run --rm onenote-exporter --list"
echo "  $COMPOSE_CMD -f podman/podman-compose.yml run --rm onenote-exporter --notebook \"My Notes\" --merge"
echo ""
echo "For more usage examples, see README.md or podman/README.md"
