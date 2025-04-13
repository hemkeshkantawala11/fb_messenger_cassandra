from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from app.schemas.error import HTTPValidationError, ValidationErrorItem
import logging

logger = logging.getLogger(__name__)

async def format_validation_error(loc, msg, error_type):
    """
    Format the error into the HTTPValidationError schema.
    """
    return HTTPValidationError(
        detail=[
            ValidationErrorItem(
                loc=loc,
                msg=msg,
                type=error_type
            )
        ]
    ).dict()

async def error_handling_middleware(request: Request, call_next):
    """
    Middleware to handle errors globally and format them into the HTTPValidationError schema.
    """
    try:
        # Process the request
        response = await call_next(request)
        return response
    except Exception as e:
        # Log the error
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

        # Format the error
        error_response = await format_validation_error(
            loc=["middleware", "error_handling_middleware"],
            msg=str(e),
            error_type="UnhandledException"
        )

        # Return the formatted error response
        return JSONResponse(
            status_code=500,
            content=error_response
        )