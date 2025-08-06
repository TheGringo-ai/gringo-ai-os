#!/bin/bash

# GRINGO AI OS Launcher Script
# Quick start script for GRINGO with all services

echo "🤖 Starting GRINGO AI OS..."
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+ first.${NC}"
    exit 1
fi

# Check if requirements are installed
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if ! python3 -c "import streamlit" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    pip3 install -r requirements.txt
fi

# Check if Ollama is running (optional)
echo -e "${BLUE}🤖 Checking Ollama service...${NC}"
if command -v ollama &> /dev/null; then
    if ! pgrep -f "ollama serve" > /dev/null; then
        echo -e "${YELLOW}🚀 Starting Ollama service...${NC}"
        ollama serve &
        sleep 3
    fi
    echo -e "${GREEN}✅ Ollama service is running${NC}"
else
    echo -e "${YELLOW}⚠️  Ollama not found - AI features will be limited${NC}"
    echo -e "${BLUE}💡 Install Ollama from https://ollama.ai for full AI capabilities${NC}"
fi

# Create workspace if it doesn't exist
if [ ! -d "gringo_workspace" ]; then
    echo -e "${BLUE}📁 Creating workspace...${NC}"
    mkdir -p gringo_workspace/{projects,tools,agents,temp}
    echo -e "${GREEN}✅ Workspace created${NC}"
fi

# Find available port
PORT=8504
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null; do
    PORT=$((PORT + 1))
done

echo -e "${BLUE}🚀 Starting GRINGO on port $PORT...${NC}"
echo -e "${GREEN}🌐 Open your browser to: http://localhost:$PORT${NC}"
echo -e "${BLUE}💡 Press Ctrl+C to stop GRINGO${NC}"
echo ""

# Start Streamlit
streamlit run ultimate_gringo.py --server.port $PORT --server.headless true --server.runOnSave true

echo -e "${YELLOW}👋 GRINGO stopped. Goodbye!${NC}"
