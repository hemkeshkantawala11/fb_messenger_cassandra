from typing import List, Union
from pydantic import BaseModel

class ValidationErrorItem(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str

class HTTPValidationError(BaseModel):
    detail: List[ValidationErrorItem]

    @staticmethod
    def format_validation_error(loc: List[Union[str, int]], msg: str, error_type: str) -> "HTTPValidationError":
        return HTTPValidationError(
            detail=[
                ValidationErrorItem(
                    loc=loc,
                    msg=msg,
                    type=error_type
                )
            ]
        )