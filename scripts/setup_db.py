"""
Script to initialize Cassandra keyspace and tables for the Messenger application.
"""
import os
import time
import logging
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cassandra connection settings
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "localhost")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", "9042"))
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "messenger")

def wait_for_cassandra():
    """Wait for Cassandra to be ready before proceeding."""
    logger.info("Waiting for Cassandra to be ready...")
    cluster = None
    
    for _ in range(10):  # Try 10 times
        try:
            cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
            session = cluster.connect()
            logger.info("Cassandra is ready!")
            return cluster
        except Exception as e:
            logger.warning(f"Cassandra not ready yet: {str(e)}")
            time.sleep(5)  # Wait 5 seconds before trying again
    
    logger.error("Failed to connect to Cassandra after multiple attempts.")
    raise Exception("Could not connect to Cassandra")

def create_keyspace(session):
    """
    Create the keyspace if it doesn't exist.
    
    This is where students will define the keyspace configuration.
    """
    logger.info(f"Creating keyspace {CASSANDRA_KEYSPACE} if it doesn't exist...")
    query = """
    CREATE KEYSPACE IF NOT EXISTS {} WITH REPLICATION = {{
        'class': 'SimpleStrategy',
        'replication_factor': 1
    }}""".format(CASSANDRA_KEYSPACE)
    session.execute(query)
    
    logger.info(f"Keyspace {CASSANDRA_KEYSPACE} is ready.")

def create_tables(session):
    """
    Create the tables for the application.
    
    This function creates the necessary tables to implement:
    - Sending messages between users
    - Fetching user conversations ordered by recent activity
    - Fetching all messages in a conversation
    - Fetching messages before a given timestamp (for pagination)
    """
    logger.info("Creating tables...")
    
    # Messages table - stores all messages with conversation_id as partition key
    # This allows efficient retrieval of all messages in a conversation
    # Clustering by timestamp DESC allows fetching recent messages first and pagination
    session.execute("""DROP TABLE IF EXISTS messenger.user_conversations;""")
    session.execute("""
    CREATE TABLE IF NOT EXISTS user_conversations (
        sender_id INT,
        receiver_id INT,
        conversation_id INT,
        last_timestamp TIMESTAMP,
        last_message TEXT,
        PRIMARY KEY (conversation_id)
    );
    """)
    logger.info("Created user_conversations table")
    
    # Conversation participants table - tracks who is in each conversation
    # This allows checking if a user is part of a conversation
    session.execute("""DROP TABLE IF EXISTS messenger.messages;""")
    session.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        conversation_id INT,
        timestamp TIMESTAMP,
        message_id INT,
        content TEXT,
        sender_id INT,
        receiver_id INT,
        PRIMARY KEY (conversation_id, timestamp, message_id)
    ) WITH CLUSTERING ORDER BY (timestamp DESC, message_id ASC);
    """)
    logger.info("Created messages table")
    
    # User conversations table - allows quick lookup of a user's conversations
    # Ordered by last_message_at DESC to get most recent conversations first
    session.execute("""DROP TABLE IF EXISTS messenger.conversations;""")
    session.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id INT,
        sender_id INT,
        receiver_id INT,
        last_timestamp TIMESTAMP,
        PRIMARY KEY (conversation_id, sender_id));
    """)
    logger.info("Created conversations table")
    
   
    # Counter table for generating sequential IDs
    # This helps with creating sequential IDs for messages and conversations
    session.execute("""DROP TABLE IF EXISTS messenger.counters;""")
    session.execute("""
    CREATE TABLE IF NOT EXISTS counters (
        counter_name TEXT,
        counter_value COUNTER,
        PRIMARY KEY (counter_name)
    );
    """)
    logger.info("Created counters table")
    
    logger.info("Tables created successfully.")

def main():
    """Initialize the database."""
    logger.info("Starting Cassandra initialization...")
    
    # Wait for Cassandra to be ready
    cluster = wait_for_cassandra()
    
    try:
        # Connect to the server
        session = cluster.connect()
        
        # Create keyspace and tables
        create_keyspace(session)
        session.set_keyspace(CASSANDRA_KEYSPACE)
        create_tables(session)
        
        logger.info("Cassandra initialization completed successfully.")
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        raise
    finally:
        if cluster:
            cluster.shutdown()

if __name__ == "__main__":
    main() 