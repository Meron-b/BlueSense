#!/bin/bash

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Install the required dependencies
echo "Installing the required dependencies..."
pip install -r requirements.txt

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit the .env file to configure your credentials."
fi

echo ""
echo "Setup complete! To start the application:"
echo "1. Activate the virtual environment (if not already activated):"
echo "   source venv/bin/activate"
echo ""
echo "2. Make sure you have set up your Google Cloud credentials:"
echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/key-file.json"
echo ""
echo "3. Run the application:"
echo "   streamlit run app.py"
echo ""
echo "4. Open your web browser and go to http://localhost:8501" 