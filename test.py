from Processing.DataValidation.GPTOutValidation import GradeValidation
from ServerLogging.serverLogger import Logger


Logger.initialize()

print(GradeValidation.clean_output([1, 2, 3, 4, 5, 6], 5, 8, {0: 1, 2: 2, 4: 3, 5: 4, 6: 5, 7: 6}))
