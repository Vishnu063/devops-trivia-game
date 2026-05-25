#!/bin/bash
echo "🚀 Starting DevOps Trivia Game..."
docker-compose up -d --build
sleep 3
echo ""
echo "✅ Game is running!"
echo "📱 Play at: http://localhost:5000"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
