#!/bin/bash
# """Setup and management script for Oceanic RAG Chatbot"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"
}

check_openai_key() {
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY environment variable is not set"
        print_warning "Please set it using: export OPENAI_API_KEY='your-key-here'"
        exit 1
    fi
    print_success "OpenAI API Key is set"
}

install_dependencies() {
    print_header "Installing Dependencies"
    
    check_python
    
    if [ ! -d "venv" ]; then
        print_warning "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    print_warning "Installing Python packages..."
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

create_directories() {
    print_header "Creating Directories"
    
    mkdir -p logs
    mkdir -p extracted_images
    mkdir -p chroma_db
    
    print_success "Directories created"
}

setup_env() {
    print_header "Setting up Environment"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from template"
            print_warning "Please update .env with your OpenAI API key"
        fi
    else
        print_success ".env file already exists"
    fi
}

run_ingestion() {
    print_header "Running Data Ingestion"
    
    check_openai_key
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    print_warning "Loading website data and documents..."
    python3 data_ingestion.py
    
    if [ $? -eq 0 ]; then
        print_success "Data ingestion completed"
    else
        print_error "Data ingestion failed"
        exit 1
    fi
}

run_streamlit() {
    print_header "Starting Streamlit App"
    
    check_openai_key
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    print_warning "Starting Streamlit interface on http://localhost:8501"
    streamlit run streamlit_app.py
}

run_cli() {
    print_header "Starting CLI Chatbot"
    
    check_openai_key
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python3 rag_chatbot.py
}

run_docker() {
    print_header "Running with Docker"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY environment variable is not set"
        exit 1
    fi
    
    print_warning "Building and starting Docker container..."
    docker-compose up -d
    print_success "Docker container started"
    print_warning "Access the app at http://localhost:8501"
}

show_help() {
    cat << EOF
${BLUE}Oceanic RAG Chatbot - Setup & Management Script${NC}

Usage: ./setup.sh [COMMAND]

Commands:
    install         Install all dependencies
    setup           Create directories and environment files
    ingest          Run data ingestion pipeline
    streamlit       Start Streamlit web interface
    cli             Start CLI chatbot
    docker          Run with Docker Compose
    full            Install, setup, ingest, and run streamlit
    clean           Clean up generated files (logs, images, db)
    help            Show this help message

Examples:
    ./setup.sh install
    ./setup.sh full
    ./setup.sh streamlit
    ./setup.sh docker

${YELLOW}First time setup:${NC}
    1. Set your OpenAI API key: export OPENAI_API_KEY='your-key'
    2. Run: ./setup.sh full

EOF
}

clean_up() {
    print_header "Cleaning Up"
    
    read -p "Are you sure you want to delete logs, images, and vector DB? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf logs/*.log
        rm -rf extracted_images/*
        rm -rf chroma_db
        print_success "Cleanup completed"
    else
        print_warning "Cleanup cancelled"
    fi
}

# Main script logic
case "${1:-help}" in
    install)
        install_dependencies
        create_directories
        ;;
    setup)
        setup_env
        create_directories
        ;;
    ingest)
        run_ingestion
        ;;
    streamlit)
        run_streamlit
        ;;
    cli)
        run_cli
        ;;
    docker)
        run_docker
        ;;
    full)
        install_dependencies
        create_directories
        setup_env
        run_ingestion
        print_success "Setup completed! Starting Streamlit..."
        run_streamlit
        ;;
    clean)
        clean_up
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
