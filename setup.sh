#!/bin/bash

# Auto-KG Setup Script
echo "Setting up Auto-KG (Automatic Knowledge Graph Builder)"
echo "====================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "Please edit .env file to configure your settings"
else
    echo "✓ .env file already exists"
fi

# Check if Neo4j is available
echo ""
echo "Checking Neo4j availability..."
if command -v neo4j &> /dev/null; then
    echo "✓ Neo4j found in PATH"
elif command -v docker &> /dev/null; then
    echo "Neo4j not found, but Docker is available"
    echo "You can run Neo4j with Docker using:"
    echo "  docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest"
else
    echo "⚠ Neo4j not found. Please install Neo4j or Docker to run the database."
    echo "Installation instructions:"
    echo "  - Neo4j: https://neo4j.com/download/"
    echo "  - Docker: https://docs.docker.com/get-docker/"
fi

echo ""
echo "Setup completed! 🎉"
echo ""
echo "Quick start:"
echo "  1. Start Neo4j database"
echo "  2. Configure .env file with your Neo4j credentials"
echo "  3. Run: python main.py full --max-pages 20 --serve"
echo ""
echo "For help: python main.py --help"