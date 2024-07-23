from fastapi import HTTPException


class PermissionError(HTTPException):
    
    def __init__(self, reason, error_code: int, status_code=403) -> None:
        super().__init__(status_code=status_code, detail={"msg": f"Cant access resource because {reason}", "error_code": error_code})


