#!/bin/bash

# GRINGO AI OS - Stop Script
# Safely stops all GRINGO services

echo "🛑 Stopping GRINGO AI OS..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Stop Streamlit processes
echo -e "${YELLOW}🔄 Stopping GRINGO interface...${NC}"
pkill -f "streamlit.*ultimate_gringo"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ GRINGO interface stopped${NC}"
else
    echo -e "${YELLOW}⚠️  No GRINGO interface running${NC}"
fi

# Stop Ollama (optional - user might want to keep it running)
read -p "Stop Ollama AI service too? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🔄 Stopping Ollama service...${NC}"
    pkill -f "ollama serve"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Ollama service stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  No Ollama service running${NC}"
    fi
else
    echo -e "${GREEN}✅ Ollama service left running${NC}"
fi

echo -e "${GREEN}🎉 GRINGO AI OS shutdown complete!${NC}"
