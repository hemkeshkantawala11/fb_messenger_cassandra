from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
import logging

from app.models.cassandra_models import MessageModel, ConversationModel
from app.schemas.message import MessageCreate, MessageResponse, PaginatedMessageResponse
logger = logging.getLogger(__name__)

class MessageController:
    """
    Controller for handling message operations
    """
    
    async def send_message(self, message_data: MessageCreate) -> MessageResponse:
        """
        Send a message from one user to another
        
        Args:
            message_data: The message data including content, sender_id, and receiver_id
            
        Returns:
            The created message with metadata
        
        Raises:
            HTTPException: If message sending fails
        """
        try:
            # Create conversation first
            conversation = await ConversationModel.create_or_get_conversation(
                message_data.sender_id,
                message_data.receiver_id
            )
            
            logger.info(f"Conversation created: {conversation['conversation_id']}")
            # Create message
            message = await MessageModel.create_message(
                conversation_id=conversation['conversation_id'],
                sender_id=message_data.sender_id,
                receiver_id=message_data.receiver_id,
                content=message_data.content
            )

            logger.info(f"Message created: {message}")


            message_response = MessageResponse(
                id=message['message_id'],
                sender_id=message['sender_id'],
                receiver_id=message['receiver_id'],
                content=message['content'],
                created_at=message['timestamp'],
                conversation_id=conversation['conversation_id']
            )
            
            return message_response
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message: {str(e)}"
            )
    
    async def get_conversation_messages(
        self, 
        conversation_id: int, 
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedMessageResponse:
        """
        Get all messages in a conversation with pagination
        
        Args:
            conversation_id: ID of the conversation
            page: Page number
            limit: Number of messages per page
            
        Returns:
            Paginated list of messages
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        try:
            # First, check if the conversation exists
            conversation = await ConversationModel.get_conversation(conversation_id)

            logger.info(f"Conversation fetched: {conversation}")
            # Check if conversation exists
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation with ID {conversation_id} not found"
                )
            
            # Fetch messages and total count from the model
            messages, total = await MessageModel.get_conversation_messages(
                conversation_id=conversation_id,
                page=page,
                limit=limit
            )
            logger.info(f"Messages fetched: {messages}")
            # Construct the paginated response
            return PaginatedMessageResponse(
                total=total,
                page=page,
                limit=limit,
                data=[MessageResponse(**msg) for msg in messages]
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Handle other exceptions
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch conversation messages: {str(e)}"
            )
    
    async def get_messages_before_timestamp(
        self, 
        conversation_id: int, 
        before_timestamp: datetime,
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedMessageResponse:
        """
        Get messages in a conversation before a specific timestamp with pagination
        
        Args:
            conversation_id: ID of the conversation
            before_timestamp: Get messages before this timestamp
            page: Page number
            limit: Number of messages per page
            
        Returns:
            Paginated list of messages
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        try:
            # First, check if the conversation exists
            conversation = await ConversationModel.get_conversation(conversation_id)

            logger.info(f"Conversation fetched: {conversation}")

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation with ID {conversation_id} not found"
                )
            
            # Fetch messages before the timestamp and total count from the model
            messages, total = await MessageModel.get_messages_before_timestamp(
                conversation_id=conversation_id,
                before_timestamp=before_timestamp,
                page=page,
                limit=limit
            )
            
            # Construct the paginated response
            return PaginatedMessageResponse(
                total=total,
                page=page,
                limit=limit,
                data=[MessageResponse(**msg) for msg in messages]
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Handle other exceptions
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch messages before timestamp: {str(e)}"
            )
