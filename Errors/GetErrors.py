from .NotFound.customErrors import *
from .ContentInvalid.customErrors import *
from .FormatInvalid.customErrors import *
from .AuthErrors.customErrors import *


class NotFound(NotFoundCustomErrors):
    pass

class ContentInvalid(ContentInvalidCustomErrors):
    pass


class FormatInvalid(FormatInvalidCustomErrors):
    pass


class PermissionErrors(PermissionCustomErrors):
    pass


class Errors:
    class NotFound(NotFound):
        pass

    class ContentInvalid(ContentInvalid):
        pass

    class FormatInvalid(FormatInvalid):
        pass

    class PermissionErrors(PermissionErrors):
        pass
