"""
Script to generate test data for the Messenger application.
This script is a skeleton for students to implement.
"""
import os
import uuid
import logging
import random
from datetime import datetime, timedelta
from cassandra.cluster import Cluster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cassandra connection settings
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "localhost")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", "9042"))
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "messenger")

# Test data configuration
NUM_USERS = 10  # Number of users to create
NUM_CONVERSATIONS = 15  # Number of conversations to create
MAX_MESSAGES_PER_CONVERSATION = 50  # Maximum number of messages per conversation

def connect_to_cassandra():
    """Connect to Cassandra cluster."""
    logger.info("Connecting to Cassandra...")
    try:
        cluster = Cluster([CASSANDRA_HOST])
        session = cluster.connect(CASSANDRA_KEYSPACE)
        logger.info("Connected to Cassandra!")
        return cluster, session
    except Exception as e:
        logger.error(f"Failed to connect to Cassandra: {str(e)}")
        raise

def get_next_id(session, counter_name):
    """
    Get the next sequential ID from the counters table.
    """
    session.execute(
        """
        UPDATE counters SET counter_value = counter_value + 1 WHERE counter_name = %s
        """,
        (counter_name,)
    )
    result = session.execute(
        """
        SELECT counter_value FROM counters WHERE counter_name = %s
        """,
        (counter_name,)
    )
    return result.one().counter_value

def generate_test_data(session):
    """
    Generate test data in Cassandra.
    
    This function creates:
    - Users (with IDs 1-NUM_USERS)
    - Conversations between random pairs of users
    - Messages in each conversation with realistic timestamps
    """
    logger.info("Generating test data...")

    # Generate user IDs
    user_ids = list(range(1, NUM_USERS + 1))
    logger.info(f"Generated user IDs: {user_ids}")

    # Generate conversations
    conversations = []
    for _ in range(NUM_CONVERSATIONS):
        sender_id, receiver_id = random.sample(user_ids, 2)
        conversation_id = get_next_id(session, "conversation_id")  # Get the next conversation ID
        last_timestamp = datetime.utcnow()
        last_message = f"Last message in conversation {conversation_id}"
        
        # Insert into user_conversations table
        session.execute(
            """
            INSERT INTO user_conversations (sender_id, receiver_id, conversation_id, last_timestamp, last_message)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (sender_id, receiver_id, conversation_id, last_timestamp, last_message)
        )
        
        # Insert into conversations table
        session.execute(
            """
            INSERT INTO conversations (conversation_id, sender_id, receiver_id, last_timestamp)
            VALUES (%s, %s, %s, %s)
            """,
            (conversation_id, sender_id, receiver_id, last_timestamp)
        )
        
        conversations.append((conversation_id, sender_id, receiver_id))
        logger.info(f"Created conversation: {conversation_id} between {sender_id} and {receiver_id}")

    # Generate messages for each conversation
    for conversation_id, sender_id, receiver_id in conversations:
        num_messages = random.randint(1, MAX_MESSAGES_PER_CONVERSATION)
        for _ in range(num_messages):
            message_id = get_next_id(session, "message_id")  # Get the next message ID
            timestamp = datetime.utcnow() - timedelta(seconds=random.randint(0, 3600))
            content = f"Message {message_id} in conversation {conversation_id}"
            
            # Insert into messages table
            session.execute(
                """
                INSERT INTO messages (conversation_id, timestamp, message_id, content, sender_id, receiver_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (conversation_id, timestamp, message_id, content, sender_id, receiver_id)
            )
        logger.info(f"Generated {num_messages} messages for conversation {conversation_id}")

    logger.info(f"Generated {NUM_CONVERSATIONS} conversations with messages")
    logger.info(f"User IDs range from 1 to {NUM_USERS}")
    logger.info("Use these IDs for testing the API endpoints")

def main():
    """Main function to generate test data."""
    cluster = None
    
    try:
        # Connect to Cassandra
        cluster, session = connect_to_cassandra()
        
        # Generate test data
        generate_test_data(session)
        
        logger.info("Test data generation completed successfully!")
    except Exception as e:
        logger.error(f"Error generating test data: {str(e)}")
    finally:
        if cluster:
            cluster.shutdown()
            logger.info("Cassandra connection closed")

if __name__ == "__main__":
    main() 