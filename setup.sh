#!/bin/bash
# Setup script for Power BI Automation

echo "======================================"
echo "Power BI Automation - Setup Script"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium

# Create .env from example
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please edit it with your credentials."
else
    echo ""
    echo "⚠️  .env file already exists, skipping..."
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p downloads output logs

echo ""
echo "======================================"
echo "✅ Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your credentials"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the application: streamlit run main.py"
echo ""
echo "For help, see README.md"

