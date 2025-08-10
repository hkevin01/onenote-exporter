@echo off
echo 🚀 OneNote Exporter Setup (Podman)
echo ==================================

REM Check if podman is installed
where podman >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Podman is not installed!
    echo.
    echo Please install Podman first:
    echo   Windows: Download from https://podman.io/getting-started/installation
    echo   Or use: winget install RedHat.Podman
    pause
    exit /b 1
)

REM Check for compose tool
where podman-compose >nul 2>nul
if %errorlevel% equ 0 (
    set COMPOSE_CMD=podman-compose
) else (
    where docker-compose >nul 2>nul
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=docker-compose
        echo ⚠️  Using docker-compose with podman (fallback)
    ) else (
        echo ❌ Neither podman-compose nor docker-compose found!
        echo.
        echo Please install podman-compose:
        echo   pip install podman-compose
        echo   OR install docker-compose for compatibility
        pause
        exit /b 1
    )
)

echo ✅ Using: %COMPOSE_CMD%

REM Navigate to project root
cd /d "%~dp0\.."

REM Create necessary directories
echo 📁 Creating directories...
if not exist output mkdir output
if not exist cache mkdir cache

REM Copy environment template if .env doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env >nul
    echo ✅ Created .env file - please edit it with your Azure app details
    echo.
    echo Next steps:
    echo 1. Edit .env file with your TENANT_ID and CLIENT_ID
    echo 2. Run: %COMPOSE_CMD% -f podman/podman-compose.yml build
    echo 3. Run: %COMPOSE_CMD% -f podman/podman-compose.yml run --rm onenote-exporter --list
    echo.
    echo For Azure app setup instructions, see README.md
) else (
    echo ✅ .env file already exists
)

REM Build the Podman image
echo 🔨 Building Podman image...
cd podman
%COMPOSE_CMD% -f podman-compose.yml build

echo.
echo 🎉 Setup complete! Your OneNote Exporter is ready to use with Podman.
echo.
echo Quick start:
echo   %COMPOSE_CMD% -f podman/podman-compose.yml run --rm onenote-exporter --list
echo   %COMPOSE_CMD% -f podman/podman-compose.yml run --rm onenote-exporter --notebook "My Notes" --merge
echo.
echo For more usage examples, see README.md or podman/README.md
pause
