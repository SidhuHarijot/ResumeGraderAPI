from fastapi import HTTPException


class NotFoundError(HTTPException):

    def __init__(self, resource: str, value: str, error_code: int):
        super().__init__(status_code=404, detail={"msg": f"{resource} not found with {value}.", "error_code": error_code})

