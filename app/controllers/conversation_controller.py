from fastapi import HTTPException, status
from app.models.cassandra_models import ConversationModel
from app.schemas.conversation import ConversationResponse, PaginatedConversationResponse
import logging

logger = logging.getLogger(__name__)   
class ConversationController:
    """
    Controller for handling conversation operations
    """
    
    async def get_user_conversations(
        self, 
        user_id: int, 
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedConversationResponse:
        """
        Get all conversations for a user with pagination
        
        Args:
            user_id: ID of the user
            page: Page number
            limit: Number of conversations per page
            
        Returns:
            Paginated list of conversations
            
        Raises:
            HTTPException: If user not found or access denied
        """
        try:
            # Fetch conversations and total count from the model
            conversations, total = await ConversationModel.get_user_conversations(user_id, page, limit)
            
            # Construct the paginated response
            return PaginatedConversationResponse(
                total=total,
                page=page,
                limit=limit,
                data=[ConversationResponse(**conv) for conv in conversations]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch user conversations: {str(e)}"
            )
    
    async def get_conversation(self, conversation_id: int) -> ConversationResponse:
        """
        Get a specific conversation by ID
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Conversation details
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        try:
            # Fetch conversation details from the model
            conversation = await ConversationModel.get_conversation(conversation_id)
            
            logger.info(f"Conversation fetched: {conversation}")
            # Check if conversation exists
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation with ID {conversation_id} not found"
                )
            
            # Return conversation response

            message = ConversationResponse(
                id = conversation["conversation_id"],
                user1_id = conversation["sender_id"],
                user2_id = conversation["receiver_id"],
                last_message_at = conversation["last_message_at"],
                last_message_content = conversation["last_message_content"]
            )
            return message
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Handle other exceptions
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch conversation: {str(e)}"
            )
