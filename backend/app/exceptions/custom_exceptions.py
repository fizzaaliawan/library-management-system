from fastapi import HTTPException, status

class EntityNotFoundException(HTTPException):
    def __init__(self, name: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{name} with identifier '{identifier}' not found."
        )

class InsufficientCopiesException(HTTPException):
    def __init__(self, title: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No copies of '{title}' are currently available."
        )

class InactiveAccountException(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account '{email}' is inactive or soft-deleted."
        )
