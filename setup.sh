#!/usr/bin/env bash
# Installation Helper Script

echo "=========================================="
echo "CV Matching RAG System - Setup Helper"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created - please edit with your API keys"
    echo ""
fi

# Check Python version
echo "Checking Python version..."
python --version

# Check Docker
echo ""
echo "Checking Docker installation..."
docker --version
docker-compose --version

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: docker-compose build"
echo "3. Run: docker-compose up -d"
echo "4. Visit: http://localhost:3301"
echo ""
