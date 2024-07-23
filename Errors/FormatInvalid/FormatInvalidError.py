from fastapi import HTTPException


class FormatInvalidError(HTTPException):
    
    def __init__(self, variable_name, value, recommended_format, error_code: int) -> None:
        super().__init__(status_code=400, detail={"msg": f"{variable_name} could not be resolved. Recommended format{recommended_format}, value {value}", "error_code": error_code})
