from fastapi import HTTPException


class ContentInvalidError(HTTPException):

    def __init__(self, variable_name, value, issue, error_code: int) -> None:
        super().__init__(status_code=400, detail={"msg": f"{variable_name} value {value} is invalid. Issue : {issue}.", "error_code": error_code})
