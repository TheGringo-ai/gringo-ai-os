#!/bin/bash

# GRINGO AI OS - Complete Startup Script
# Handles Ollama + GRINGO startup with error checking

echo "🚀 GRINGO AI OS - Starting Complete System..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a process is running
check_process() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_tries=30
    local tries=0
    
    while [ $tries -lt $max_tries ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready!${NC}"
            return 0
        fi
        sleep 1
        tries=$((tries + 1))
        echo -e "${YELLOW}⏳ Waiting for $name... ($tries/$max_tries)${NC}"
    done
    echo -e "${RED}❌ $name failed to start${NC}"
    return 1
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+ first.${NC}"
    exit 1
fi

# Check if requirements are installed
echo -e "${BLUE}📦 Checking Python dependencies...${NC}"
if ! python3 -c "import streamlit, pandas, psutil" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Installing missing Python packages...${NC}"
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Python dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Python dependencies OK${NC}"
fi

# Check and start Ollama
echo -e "${BLUE}🤖 Checking Ollama AI service...${NC}"
if command -v ollama &> /dev/null; then
    if ! check_process "ollama serve"; then
        echo -e "${YELLOW}🔄 Starting Ollama service...${NC}"
        ollama serve > /dev/null 2>&1 &
        sleep 3
        
        # Wait for Ollama to be ready
        if wait_for_service "http://localhost:11434" "Ollama"; then
            echo -e "${GREEN}✅ Ollama is running${NC}"
        else
            echo -e "${RED}❌ Ollama failed to start - AI features may not work${NC}"
        fi
    else
        echo -e "${GREEN}✅ Ollama already running${NC}"
    fi
    
    # Check if any models are installed
    if ollama list | grep -q ":"; then
        echo -e "${GREEN}✅ AI models available${NC}"
    else
        echo -e "${YELLOW}⚠️  No AI models found. Install with: ollama pull llama2${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Ollama not installed. AI features disabled.${NC}"
    echo -e "${BLUE}📝 Install with: curl -fsSL https://ollama.ai/install.sh | sh${NC}"
fi

# Stop any existing Streamlit processes
echo -e "${BLUE}🔄 Stopping any existing GRINGO instances...${NC}"
pkill -f "streamlit.*ultimate_gringo" > /dev/null 2>&1
sleep 2

# Start GRINGO AI OS
echo -e "${BLUE}🚀 Starting GRINGO AI OS interface...${NC}"
streamlit run ultimate_gringo.py --server.port 8507 > /dev/null 2>&1 &

# Wait for Streamlit to be ready
if wait_for_service "http://localhost:8507" "GRINGO AI OS"; then
    echo -e "${GREEN}🎉 GRINGO AI OS is ready!${NC}"
    echo -e "${BLUE}📱 Opening browser...${NC}"
    
    # Open browser based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:8507
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:8507
    else
        echo -e "${YELLOW}📱 Please open: http://localhost:8507${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ GRINGO AI OS is now running!${NC}"
    echo -e "${BLUE}🌐 Access at: http://localhost:8507${NC}"
    echo -e "${YELLOW}⚠️  Keep this terminal open or run in background${NC}"
    echo -e "${BLUE}🛑 To stop: Press Ctrl+C or run: pkill -f streamlit${NC}"
    echo ""
else
    echo -e "${RED}❌ Failed to start GRINGO AI OS${NC}"
    echo -e "${YELLOW}💡 Try manually: streamlit run ultimate_gringo.py --server.port 8507${NC}"
    exit 1
fi

# Create workspace if it doesn't exist
if [ ! -d "gringo_workspace" ]; then
    echo -e "${BLUE}📁 Creating workspace directory...${NC}"
    mkdir -p gringo_workspace/{projects,tools,agents,temp}
    echo -e "${GREEN}✅ Workspace created${NC}"
fi

# Keep the script running to show logs
echo -e "${BLUE}� Monitoring GRINGO AI OS (press Ctrl+C to stop)...${NC}"
echo ""

# Wait for user to stop or process to end
while check_process "streamlit.*ultimate_gringo"; do
    sleep 5
done

echo -e "${YELLOW}👋 GRINGO AI OS stopped. Goodbye!${NC}"
