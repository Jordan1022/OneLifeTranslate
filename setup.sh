#!/bin/bash

# OneLife Translation Stream Setup Script
# Automates installation and configuration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if ! command_exists python3; then
        print_error "Python 3 not found. Please install Python 3.11 or later."
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if ! printf '%s\n3.11' "$python_version" | sort -V -C; then
        print_warning "Python $python_version found. Python 3.11+ recommended."
    else
        print_success "Python $python_version found"
    fi
}

# Function to check Node.js version
check_node() {
    if ! command_exists node; then
        print_error "Node.js not found. Please install Node.js 18 or later."
        print_status "Download from: https://nodejs.org/"
        exit 1
    fi
    
    node_version=$(node -v | sed 's/v//')
    if ! printf '%s\n18.0.0' "$node_version" | sort -V -C; then
        print_warning "Node.js $node_version found. Node.js 18+ recommended."
    else
        print_success "Node.js $node_version found"
    fi
}

# Function to check FFmpeg
check_ffmpeg() {
    if ! command_exists ffmpeg; then
        print_warning "FFmpeg not found. This is required for HLS streaming."
        print_status "Please install FFmpeg:"
        print_status "  Ubuntu/Debian: sudo apt install ffmpeg"
        print_status "  macOS: brew install ffmpeg"
        print_status "  Windows: Download from https://ffmpeg.org/"
        print_status "Continuing without FFmpeg (mock mode will work)..."
    else
        print_success "FFmpeg found"
    fi
}

# Function to setup Python environment
setup_python() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Python environment setup complete"
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install npm dependencies
    print_status "Installing npm dependencies..."
    npm install
    
    # Build frontend
    print_status "Building frontend..."
    npm run build
    
    cd ..
    
    print_success "Frontend setup complete"
}

# Function to setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Environment file created from template"
        print_warning "Please edit .env file with your API keys"
        print_status "Required API keys:"
        print_status "  - OPENAI_API_KEY: Get from https://platform.openai.com/"
        print_status "  - ELEVEN_API_KEY: Get from https://elevenlabs.io/"
    else
        print_status "Environment file already exists"
    fi
}

# Function to create directories
create_directories() {
    print_status "Creating required directories..."
    
    directories=("stream" "logs" "frontend/dist")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
    
    print_success "Directories created"
}

# Function to run tests
run_tests() {
    print_status "Running basic tests..."
    
    # Test Python imports
    source venv/bin/activate
    python3 -c "
import sys
try:
    import fastapi, uvicorn, openai
    print('✓ Core Python packages imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
    
    # Test frontend build
    if [ -f "frontend/dist/index.html" ]; then
        print_success "Frontend build verified"
    else
        print_warning "Frontend build not found"
    fi
    
    print_success "Basic tests completed"
}

# Main setup function
main() {
    echo "🎤 OneLife Translation Stream Setup"
    echo "=================================="
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    check_python
    check_node
    check_ffmpeg
    echo ""
    
    # Setup components
    setup_python
    echo ""
    
    setup_frontend
    echo ""
    
    setup_environment
    echo ""
    
    create_directories
    echo ""
    
    run_tests
    echo ""
    
    # Final instructions
    print_success "🎉 Setup completed successfully!"
    echo ""
    print_status "Next steps:"
    print_status "1. Edit .env file with your API keys (if not already done)"
    print_status "2. For testing without API keys, set USE_MOCK=true in .env"
    print_status "3. Run the application: python main.py"
    print_status "4. Open http://localhost:8000 in your browser"
    echo ""
    print_status "For production deployment:"
    print_status "• Install Dante Virtual Soundcard"
    print_status "• Configure audio routing"
    print_status "• Set up proper API keys"
    print_status "• Test with actual audio input"
    echo ""
    print_status "Documentation: See README.md for detailed instructions"
}

# Check if running from correct directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the OneLife Translation Stream root directory"
    exit 1
fi

# Run main setup
main
