
# Cassandra Schema Documentation

This document provides an overview of the tables used in the **Messenger** application and how they support message storage, user conversations, and ID generation.

---

## Keyspace: `messenger`

### 1. `user_conversations`

**Purpose:**  
Stores the latest message exchanged between two users and enables fast access to recent interactions.

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS user_conversations (
    sender_id INT,
    receiver_id INT,
    conversation_id INT,
    last_timestamp TIMESTAMP,
    last_message TEXT,
    PRIMARY KEY (conversation_id)
);
```

**Fields:**
- `sender_id`: ID of the user who sent the last message.
- `receiver_id`: ID of the user who received the last message.
- `conversation_id`: Unique ID for the conversation (also the primary key).
- `last_timestamp`: Timestamp of the most recent message.
- `last_message`: Content of the most recent message.

**Notes:**
- This table gives a quick view of recent conversations and their last message content.

---

### 2. `messages`

**Purpose:**  
Stores all messages in a conversation, ordered by time and message ID.

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS messages (
    conversation_id INT,
    timestamp TIMESTAMP,
    message_id INT,
    content TEXT,
    sender_id INT,
    receiver_id INT,
    PRIMARY KEY (conversation_id, timestamp, message_id)
) WITH CLUSTERING ORDER BY (timestamp DESC, message_id ASC);
```

**Fields:**
- `conversation_id`: ID of the conversation the message belongs to.
- `timestamp`: Time when the message was sent.
- `message_id`: Unique ID for the message (within the conversation).
- `content`: Text content of the message.
- `sender_id`: ID of the sender.
- `receiver_id`: ID of the receiver.

**Notes:**
- Messages are ordered by most recent first (`timestamp DESC`).
- Efficient for fetching latest messages in a conversation.

---

### 3. `conversations`

**Purpose:**  
Tracks all active conversations and associated participants.

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id INT,
    sender_id INT,
    receiver_id INT,
    last_timestamp TIMESTAMP,
    PRIMARY KEY (conversation_id, sender_id)
);
```

**Fields:**
- `conversation_id`: Unique ID for the conversation.
- `sender_id`: Participant who initiated or is part of the conversation.
- `receiver_id`: The other participant in the conversation.
- `last_timestamp`: Time of the most recent message in the conversation.

**Notes:**
- Useful for verifying if a user is part of a conversation.
- Could be queried per `sender_id` if secondary index is added.

---

### 4. `counters`

**Purpose:**  
Maintains a counter used to generate sequential IDs (e.g., for `message_id`, `conversation_id`).

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS counters (
    counter_name TEXT,
    counter_value COUNTER,
    PRIMARY KEY (counter_name)
);
```

**Fields:**
- `counter_name`: Name or type of the counter (e.g., `"conversation_id"`).
- `counter_value`: A counter column storing the current numeric value.

**Notes:**
- Useful for generating auto-incrementing IDs in a distributed-safe manner.

---

## Summary

| Table              | Purpose                                     | Key Columns                      |
|--------------------|---------------------------------------------|----------------------------------|
| `user_conversations` | Latest message info for each conversation | `conversation_id`                |
| `messages`         | Stores all messages with ordering           | `conversation_id, timestamp`     |
| `conversations`    | Tracks participants in each conversation    | `conversation_id, sender_id`     |
| `counters`         | Provides ID counters                        | `counter_name`                   |
