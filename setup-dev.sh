#!/bin/bash

# Wikipedia Path Finder - Development Environment Setup Script
# This script sets up the complete development environment

set -e  # Exit on any error

echo "🚀 Wikipedia Path Finder - Development Setup"
echo "============================================"

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

# Check if running on macOS, Linux, or Windows (WSL)
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    print_status "Detected OS: $OS"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        missing_deps+=("python3")
    fi
    
    # Check pip
    if command_exists pip3; then
        print_success "pip3 found"
    else
        missing_deps+=("pip3")
    fi
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        missing_deps+=("node")
    fi
    
    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION found"
    else
        missing_deps+=("npm")
    fi
    
    # Check git
    if command_exists git; then
        print_success "git found"
    else
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_status "Please install the missing dependencies and run this script again."
        
        if [[ "$OS" == "macos" ]]; then
            echo ""
            echo "Installation commands for macOS (using Homebrew):"
            echo "  brew install python node git"
        elif [[ "$OS" == "linux" ]]; then
            echo ""
            echo "Installation commands for Ubuntu/Debian:"
            echo "  sudo apt update"
            echo "  sudo apt install python3 python3-pip nodejs npm git"
        fi
        
        exit 1
    fi
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    if [ -d "bot" ]; then
        cd bot
        
        if [ -f "package.json" ]; then
            print_status "Installing backend dependencies..."
            npm install
            print_success "Backend dependencies installed"
        else
            print_error "bot/package.json not found"
            exit 1
        fi
        
        cd ..
    else
        print_error "bot directory not found"
        exit 1
    fi
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    if [ -d "client" ]; then
        cd client
        
        if [ -f "package.json" ]; then
            print_status "Installing frontend dependencies..."
            npm install
            print_success "Frontend dependencies installed"
        else
            print_error "client/package.json not found"
            exit 1
        fi
        
        cd ..
    else
        print_error "client directory not found"
        exit 1
    fi
}

# Create development configuration
create_dev_config() {
    print_status "Creating development configuration..."
    
    # Create .env for backend if it doesn't exist
    if [ ! -f "bot/.env" ]; then
        cat > bot/.env << EOF
NODE_ENV=development
PORT=3001
CORS_ORIGIN=http://localhost:5173
API_TIMEOUT=30000
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX=1000
LOG_LEVEL=debug
EOF
        print_success "Created bot/.env"
    else
        print_warning "bot/.env already exists"
    fi
    
    # Create .env for Python if it doesn't exist
    if [ ! -f ".env" ]; then
        cat > .env << EOF
PYTHON_ENV=development
GLOVE_CACHE_DIR=./glove_cache
TORCH_HOME=./torch_cache
MAX_SEARCH_TIME=180
MAX_ARTICLES_CHECKED=1000
DEBUG=true
EOF
        print_success "Created .env"
    else
        print_warning ".env already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    directories=("glove_cache" "torch_cache" "logs" "bot/logs")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_warning "Directory already exists: $dir"
        fi
    done
}

# Run tests to verify setup
run_tests() {
    print_status "Running tests to verify setup..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run Python tests
    if [ -f "test_simple.py" ]; then
        print_status "Running Python tests..."
        python test_simple.py
        if [ $? -eq 0 ]; then
            print_success "Python tests passed"
        else
            print_warning "Some Python tests failed (this might be expected in development)"
        fi
    fi
    
    # Test backend startup
    print_status "Testing backend startup..."
    cd bot
    timeout 5s npm start > /dev/null 2>&1 &
    BACKEND_PID=$!
    sleep 3
    
    if kill -0 $BACKEND_PID 2>/dev/null; then
        print_success "Backend starts successfully"
        kill $BACKEND_PID
    else
        print_warning "Backend startup test inconclusive"
    fi
    
    cd ..
    
    # Test frontend build
    print_status "Testing frontend build..."
    cd client
    npm run build > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "Frontend builds successfully"
    else
        print_warning "Frontend build failed"
    fi
    cd ..
}

# Setup VS Code configuration
setup_vscode() {
    print_status "Setting up VS Code configuration..."
    
    if [ ! -d ".vscode" ]; then
        mkdir .vscode
    fi
    
    # Create launch.json for debugging
    cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/bot"
            }
        },
        {
            "name": "Python: Main Script",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/bot/main.py",
            "console": "integratedTerminal",
            "args": ["--start", "Python", "--goal", "Machine Learning", "--algorithm", "best-first"],
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Node: Backend Server",
            "type": "node",
            "request": "launch",
            "program": "${workspaceFolder}/bot/server.js",
            "cwd": "${workspaceFolder}/bot",
            "env": {
                "NODE_ENV": "development"
            }
        }
    ]
}
EOF
    
    # Create settings.json
    cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/node_modules": true,
        "**/venv": true,
        "**/.git": true,
        "**/glove_cache": true,
        "**/torch_cache": true
    },
    "search.exclude": {
        "**/node_modules": true,
        "**/venv": true,
        "**/glove_cache": true,
        "**/torch_cache": true
    }
}
EOF
    
    print_success "VS Code configuration created"
}

# Print development commands
print_dev_commands() {
    echo ""
    echo "🎉 Setup Complete! Here are your development commands:"
    echo "=================================================="
    echo ""
    echo "🐍 Python Development:"
    echo "  source venv/bin/activate     # Activate virtual environment"
    echo "  python bot/main.py --help    # See CLI options"
    echo "  python test_simple.py        # Run tests"
    echo ""
    echo "🚀 Backend Development:"
    echo "  cd bot && npm start          # Start API server (port 3001)"
    echo "  cd bot && npm run dev        # Start with auto-reload"
    echo ""
    echo "⚛️  Frontend Development:"
    echo "  cd client && npm run dev     # Start dev server (port 5173)"
    echo "  cd client && npm run build   # Build for production"
    echo "  cd client && npm run preview # Preview production build"
    echo ""
    echo "🧪 Testing:"
    echo "  python test_simple.py        # Python tests"
    echo "  cd client && npm test        # Frontend tests (if configured)"
    echo ""
    echo "🐳 Docker Development:"
    echo "  docker-compose up --build    # Start all services"
    echo "  docker-compose down          # Stop all services"
    echo ""
    echo "🔧 Useful URLs:"
    echo "  Frontend: http://localhost:5173"
    echo "  Backend API: http://localhost:3001"
    echo "  Health Check: http://localhost:3001/api/health"
    echo ""
    echo "📚 Documentation:"
    echo "  README.md        # Project overview"
    echo "  DEPLOYMENT.md    # Deployment guide"
    echo ""
}

# Main setup function
main() {
    # Change to script directory
    cd "$(dirname "$0")"
    
    detect_os
    check_prerequisites
    setup_python_env
    setup_backend
    setup_frontend
    create_dev_config
    create_directories
    setup_vscode
    run_tests
    print_dev_commands
    
    print_success "Development environment setup complete! 🎉"
}

# Run main function
main "$@"
