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

def generate_test_data(session):
    """
    Generate test data in Cassandra.
    
    This function creates:
    - Users (with IDs 1-NUM_USERS)
    - Conversations between random pairs of users
    - Messages in each conversation with realistic timestamps
    """
    logger.info("Generating test data...")
    
    # 1. Create a set of user IDs (1 to NUM_USERS)
    user_ids = list(range(1, NUM_USERS + 1))
    logger.info(f"Created {len(user_ids)} user IDs")
    
    # 2. Create conversations between random pairs of users
    conversation_id = 1
    conversations = []
    
    # Track which user pairs already have conversations to avoid duplicates
    user_pairs = set()
    
    for _ in range(NUM_CONVERSATIONS):
        # Keep trying until we find a unique user pair
        while True:
            user1_id = random.choice(user_ids)
            user2_id = random.choice([u for u in user_ids if u != user1_id])
            
            # Ensure user1_id < user2_id for consistent pair representation
            if user1_id > user2_id:
                user1_id, user2_id = user2_id, user1_id
                
            user_pair = (user1_id, user2_id)
            
            if user_pair not in user_pairs:
                user_pairs.add(user_pair)
                break
        
        # Create conversation
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        # Insert into conversations table
        session.execute(
            """
            INSERT INTO conversations (conversation_id, user1_id, user2_id, created_at)
            VALUES (%s, %s, %s, %s)
            """,
            (conversation_id, user1_id, user2_id, created_at)
        )
        
        # Insert into conversation_participants table
        session.execute(
            """
            INSERT INTO conversation_participants (conversation_id, user_id, last_read_at)
            VALUES (%s, %s, %s)
            """,
            (conversation_id, user1_id, created_at)
        )
        
        session.execute(
            """
            INSERT INTO conversation_participants (conversation_id, user_id, last_read_at)
            VALUES (%s, %s, %s)
            """,
            (conversation_id, user2_id, created_at)
        )
        
        conversations.append({
            'id': conversation_id,
            'user1_id': user1_id,
            'user2_id': user2_id,
            'created_at': created_at
        })
        
        conversation_id += 1
    
    logger.info(f"Created {len(conversations)} conversations")
    
    # 3. Generate messages for each conversation
    message_id = 1
    
    for conv in conversations:
        # Generate a random number of messages for this conversation
        num_messages = random.randint(5, MAX_MESSAGES_PER_CONVERSATION)
        
        # Track the last message for updating user_conversations table
        last_message = None
        
        # Generate messages with timestamps in ascending order (older to newer)
        start_time = conv['created_at']
        end_time = datetime.now()
        
        for i in range(num_messages):
            # Randomly select sender and receiver
            if random.choice([True, False]):
                sender_id = conv['user1_id']
                receiver_id = conv['user2_id']
            else:
                sender_id = conv['user2_id']
                receiver_id = conv['user1_id']
            
            # Generate a random timestamp between start_time and end_time
            # Ensure messages are in chronological order
            message_time = start_time + (end_time - start_time) * (i / num_messages) + timedelta(
                seconds=random.randint(0, 3600)
            )
            
            # Generate random message content
            message_templates = [
                "Hey, how are you?",
                "What's up?",
                "Can we meet tomorrow?",
                "Did you see the news?",
                "I'm going to be late.",
                "Let's catch up soon!",
                "Have you finished the project?",
                "Happy birthday!",
                "Thanks for your help!",
                "I'll call you later."
            ]
            content = random.choice(message_templates)
            
            # Insert into messages table
            session.execute(
                """
                INSERT INTO messages (message_id, conversation_id, sender_id, receiver_id, content, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (message_id, conv['id'], sender_id, receiver_id, content, message_time)
            )
            
            # Insert into messages_by_timestamp table
            session.execute(
                """
                INSERT INTO messages_by_timestamp (conversation_id, timestamp, message_id, sender_id, receiver_id, content)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (conv['id'], message_time, message_id, sender_id, receiver_id, content)
            )
            
            # Update last message
            last_message = {
                'id': message_id,
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'content': content,
                'created_at': message_time
            }
            
            message_id += 1
        
        # 4. Update user_conversations table with the last message for each participant
        if last_message:
            # For user1
            session.execute(
                """
                INSERT INTO user_conversations (user_id, conversation_id, other_user_id, last_message_at, last_message_content)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    conv['user1_id'],
                    conv['id'],
                    conv['user2_id'],
                    last_message['created_at'],
                    last_message['content']
                )
            )
            
            # For user2
            session.execute(
                """
                INSERT INTO user_conversations (user_id, conversation_id, other_user_id, last_message_at, last_message_content)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    conv['user2_id'],
                    conv['id'],
                    conv['user1_id'],
                    last_message['created_at'],
                    last_message['content']
                )
            )
    
    # Initialize counters
    session.execute(
        """
        UPDATE counters SET counter_value = counter_value + %s WHERE counter_name = %s
        """,
        (message_id, "message_id")
    )
    
    session.execute(
        """
        UPDATE counters SET counter_value = counter_value + %s WHERE counter_name = %s
        """,
        (conversation_id, "conversation_id")
    )
    
    logger.info(f"Generated {message_id-1} messages across {len(conversations)} conversations")
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