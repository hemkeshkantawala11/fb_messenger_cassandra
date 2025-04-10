# FB Messenger Backend Implementation with Cassandra

This repository contains the stub code for the Distributed Systems course assignment to implement a Facebook Messenger backend using Apache Cassandra as the distributed database.

## Architecture

The application follows a typical FastAPI structure:

- `app/`: Main application package
  - `api/`: API routes and endpoints
  - `controllers/`: Controller logic (stubs provided)
  - `models/`: Database models (stubs provided, to be implemented by students)
  - `schemas/`: Pydantic models for request/response validation
  - `db/`: Database connection utilities (Cassandra client)

## Requirements

- Docker and Docker Compose (for containerized development environment)
- Python 3.11+ (for local development)

## Quick Setup with Docker

This repository includes a Docker setup to simplify the development process. All you need to get started is:

1. Clone this repository
2. Make sure Docker and Docker Compose are installed on your system
3. Run the initialization script:
   ```
   ./init.sh
   ```

This will:
- Start both FastAPI application and Cassandra containers
- Initialize the Cassandra keyspace and tables
- Optionally generate test data for development
- Make the application available at http://localhost:8000

Access the API documentation at http://localhost:8000/docs

To stop the application:
```
docker-compose down
```

### Test Data

The setup script includes an option to generate test data for development purposes. This will create:

- 10 test users (with IDs 1-10)
- 15 conversations between random pairs of users
- Multiple messages in each conversation with realistic timestamps

You can use these IDs for testing your API implementations. If you need to regenerate the test data:

```
docker-compose exec app python scripts/generate_test_data.py
```

## Manual Setup (Alternative)

If you prefer not to use Docker, you can set up the environment manually:

1. Clone this repository
2. Install Cassandra locally and start it
3. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```
5. Run the setup script to initialize Cassandra:
   ```
   python scripts/setup_db.py
   ```
6. Start the application:
   ```
   uvicorn app.main:app --reload
   ```

## Cassandra Data Model

For this assignment, you will need to design and implement your own data model in Cassandra to support the required API functionality:

1. Sending messages between users
2. Retrieving conversations for a user, ordered by most recent activity
3. Retrieving messages in a conversation, ordered by timestamp
4. Retrieving messages before a specific timestamp

Your data model should consider:
- Efficient distribution of data across nodes
- Appropriate partition keys and clustering columns
- How to handle pagination efficiently
- How to optimize for the required query patterns

## Assignment Tasks

You need to implement:

1. Cassandra schema design - create tables to support the required queries
2. Message and Conversation models (`app/models/`) to interact with Cassandra
3. Controller methods in the stub classes (`app/controllers/`):
   - Send Message from one user to another (only the DB interaction parts here. No need to implement websocket etc needed to actually deliver message to other user)
   - Get Recent Conversations of a user (paginated)
   - Get Messages in a particular conversation (paginated)
   - Get Messages in a conversation prior to a specific timestamp (paginated)

## API Endpoints

### Messages

- `POST /api/messages/`: Send a message from one user to another
- `GET /api/messages/conversation/{conversation_id}`: Get all messages in a conversation
- `GET /api/messages/conversation/{conversation_id}/before`: Get messages before a timestamp

### Conversations

- `GET /api/conversations/user/{user_id}`: Get all conversations for a user
- `GET /api/conversations/{conversation_id}`: Get a specific conversation

## Evaluation Criteria

- Correct implementation of all required endpoints
- Proper error handling and edge cases
- Efficient Cassandra queries (avoid hotspots and ensure good distribution)
- Code quality and organization
- Proper implementation of pagination
- Performance considerations for distributed systems
- Adherence to Cassandra data modeling best practices 