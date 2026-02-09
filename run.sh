#!/bin/bash
# IVR AI Agent System - Development Control Script

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$REPO_DIR/backend"
FRONTEND_DIR="$REPO_DIR/frontend"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_banner() {
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════╗"
    echo "║   IVR AI Agent System - Control Script     ║"
    echo "╚════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Commands
install_deps() {
    print_info "Installing Python dependencies..."
    pip install -r "$REPO_DIR/requirements.txt"
    print_success "Dependencies installed"
}

start_backend() {
    print_info "Starting backend server..."
    print_info "API will be available at http://localhost:8000"
    print_info "API Docs at http://localhost:8000/docs"
    cd "$BACKEND_DIR"
    python main.py
}

start_frontend() {
    print_info "Starting frontend server..."
    print_info "Frontend will be available at http://localhost:8080"
    cd "$FRONTEND_DIR"
    python -m http.server 8080
}

start_all() {
    print_info "Starting both backend and frontend..."
    
    # Start backend in background
    (cd "$BACKEND_DIR" && python main.py) &
    BACKEND_PID=$!
    print_success "Backend started (PID: $BACKEND_PID)"
    
    sleep 2
    
    # Start frontend
    print_info "Starting frontend..."
    cd "$FRONTEND_DIR"
    python -m http.server 8080
}

setup_env() {
    print_info "Setting up environment..."
    if [ ! -f "$REPO_DIR/.env" ]; then
        cp "$REPO_DIR/.env.example" "$REPO_DIR/.env"
        print_success "Created .env file from template"
        print_error "Please edit .env and add your OpenAI API key!"
    else
        print_info ".env file already exists"
    fi
}

test_api() {
    print_info "Testing API health..."
    response=$(curl -s http://localhost:8000/api/v1/health)
    
    if [[ $response == *"healthy"* ]]; then
        print_success "API is healthy"
        echo "$response" | python -m json.tool 2>/dev/null || echo "$response"
    else
        print_error "API health check failed"
        echo "Response: $response"
    fi
}

clean() {
    print_info "Cleaning up..."
    rm -rf "$REPO_DIR/__pycache__"
    rm -rf "$BACKEND_DIR/__pycache__"
    rm -rf "$REPO_DIR/.pytest_cache"
    rm -rf "$REPO_DIR/build"
    rm -rf "$REPO_DIR/dist"
    print_success "Cleanup complete"
}

docker_build() {
    print_info "Building Docker image..."
    docker build -t ivr-ai-system .
    print_success "Docker image built"
}

docker_run() {
    print_info "Running Docker container..."
    docker run -p 8000:8000 -p 8080:8080 \
        -e "OPENAI_API_KEY=${OPENAI_API_KEY}" \
        ivr-ai-system
}

docker_compose_up() {
    print_info "Starting services with Docker Compose..."
    docker-compose up --build
}

show_help() {
    print_banner
    echo "Usage: ./run.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install       Install Python dependencies"
    echo "  setup        Setup environment (.env file)"
    echo "  backend      Start backend server only"
    echo "  frontend     Start frontend server only"
    echo "  start        Start both backend and frontend"
    echo "  test         Test API health"
    echo "  clean        Clean up temporary files"
    echo "  docker-build Build Docker image"
    echo "  docker-run   Run Docker container"
    echo "  docker-up    Start with Docker Compose"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh install          # Install dependencies first"
    echo "  ./run.sh setup            # Create .env file"
    echo "  ./run.sh backend          # Run backend only"
    echo ""
}

# Main
if [ $# -eq 0 ]; then
    show_help
else
    case "$1" in
        install)
            install_deps
            ;;
        setup)
            setup_env
            ;;
        backend)
            start_backend
            ;;
        frontend)
            start_frontend
            ;;
        start)
            start_all
            ;;
        test)
            test_api
            ;;
        clean)
            clean
            ;;
        docker-build)
            docker_build
            ;;
        docker-run)
            docker_run
            ;;
        docker-up)
            docker_compose_up
            ;;
        help)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
fi
