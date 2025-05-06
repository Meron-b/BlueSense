#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup script..."
    bash setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating from example..."
    cp .env.example .env
    echo "Please edit the .env file to configure your credentials."
fi

# Run the test connections script
echo "Testing API connections..."
python test_connections.py

# Ask if the user wants to continue
read -p "Do you want to start the BlueSense application? (y/n): " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo "Starting BlueSense..."
    streamlit run app.py
else
    echo "Exiting..."
fi 