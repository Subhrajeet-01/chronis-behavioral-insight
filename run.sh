#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================================================${NC}"
echo -e "${BLUE}   CHRONIS BEHAVIORAL INSIGHT ENGINE — WORKFLOW ENGINE                 ${NC}"
echo -e "${BLUE}=======================================================================${NC}"

# 1. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}[1/4] Creating virtual environment (.venv)...${NC}"
    python3 -m venv .venv
else
    echo -e "${GREEN}[1/4] Virtual environment (.venv) already exists.${NC}"
fi

echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# 2. Install Dependencies
echo -e "${BLUE}[2/4] Installing dependencies from requirements.txt...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 3. Run Test Suite
echo -e "\n${BLUE}[3/4] Running test suite (pytest)...${NC}"
python -m pytest tests/ -v

# 4. Run Analysis Pipeline on Synthetic Data
echo -e "\n${BLUE}[4/4] Executing pipeline on Chronis Dataset...${NC}"
python main.py --data "Chronis_TaskA_Synthetic_Behavioral_Data_v2-2 (1).csv"

echo -e "\n${GREEN}=======================================================================${NC}"
echo -e "${GREEN}   EXECUTION COMPLETE SUCCESSFULLY!                                    ${NC}"
echo -e "${GREEN}=======================================================================${NC}"
echo -e "${GREEN}• CLI Summary printed above.${NC}"
echo -e "${GREEN}• JSON Report saved to: chronis_report.json${NC}"
echo -e "${GREEN}• HTML Premium Dashboard saved to: chronis_report.html${NC}"
echo -e "${BLUE}Double-click chronis_report.html to open the visual timeline dashboard.${NC}"
echo -e "${BLUE}=======================================================================${NC}\n"
