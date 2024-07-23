from .PermissionError import PermissionError
from fastapi import HTTPException


class PermissionCustomErrors:
    class NoTokenError(PermissionError):
        def __init__(self) -> None:
            super().__init__("No token provided", 1201, 401)
    
    class InvalidTokenError(PermissionError):
        def __init__(self) -> None:
            super().__init__("Invalid token provided", 1202)
