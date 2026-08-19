#!/bin/bash

# ============================================================================
# FORENSICS PRO - One-Command Setup Script
# ============================================================================

set -e  # Exit on error

echo "🚀 FORENSICS PRO - Setup Script"
echo "================================"
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Create necessary directories
echo "✓ Setting up directories..."
mkdir -p uploads
mkdir -p core/bin
echo "✅ Directories created"
echo ""

# Build and start services
echo "✓ Building and starting services..."
echo "  This may take 2-3 minutes on first run..."
echo ""

docker-compose down 2>/dev/null || true
docker-compose up --build -d

# Wait for services to be ready
echo ""
echo "✓ Waiting for services to start..."
sleep 10

# Check services
echo ""
echo "✓ Checking service health..."

# Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "⏳ Frontend starting (may take a moment)..."
fi

# Backend
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "⏳ Backend starting (may take a moment)..."
fi

# Database
if nc -z localhost 5432 2>/dev/null; then
    echo "✅ Database is running"
else
    echo "⏳ Database starting..."
fi

echo ""
echo "============================================"
echo "🎉 FORENSICS PRO IS READY!"
echo "============================================"
echo ""
echo "🌐 Open in your browser:"
echo "   Frontend: http://localhost:3000"
echo "   API:      http://localhost:5000"
echo ""
echo "📝 Quick Start:"
echo "   1. Open http://localhost:3000"
echo "   2. Click 'Upload & Analyze' tab"
echo "   3. Drag & drop a memory dump file"
echo "   4. View results and generate report"
echo ""
echo "📚 Documentation:"
echo "   ./QUICKSTART.md"
echo "   ./docs/"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "Happy forensic analysis! 🔍"
