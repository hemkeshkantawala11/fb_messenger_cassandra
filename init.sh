#!/bin/bash
set -e

echo "Starting initialization..."

# Create necessary directories if they don't exist
mkdir -p scripts

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker before proceeding."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "Docker Compose not found. Please install Docker Compose before proceeding."
    exit 1
fi

# Start the containers in detached mode
echo "Starting Docker containers..."
docker compose up -d

# Wait for Cassandra to be ready (this may take a while on first run)
echo "Waiting for Cassandra to initialize (this may take a minute or two)..."
docker compose exec -T cassandra bash -c "for i in {1..30}; do if cqlsh -e 'describe cluster' &>/dev/null; then echo 'Cassandra ready!'; exit 0; fi; echo 'Waiting for Cassandra...'; sleep 5; done; echo 'Cassandra did not start in time'; exit 1"

# Inform about setup needed
echo "====================================================================="
echo "IMPORTANT: You need to implement the database schema yourself!"
echo "1. You should design and implement the keyspace and tables in the"
echo "   scripts/setup_db.py file according to your data model design."
echo "2. After implementing, run: docker-compose exec app python scripts/setup_db.py"
echo "3. You'll also need to implement the test data generation in"
echo "   scripts/generate_test_data.py for testing purposes."
echo "====================================================================="

echo "The FastAPI application is running at http://localhost:8000"
echo "Swagger API documentation available at http://localhost:8000/docs"
echo ""
echo "To stop the application, run: docker-compose down" 