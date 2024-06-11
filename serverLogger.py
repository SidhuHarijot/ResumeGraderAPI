import zlib
import datetime
import os

class Logger:
    logFolder = "Logs/"
    compressed = "Logs/Compressed/"
    decompressed = "Logs/Decompressed/"

    @staticmethod
    def initialize():
        if not os.path.exists(Logger.logFolder):
            os.makedirs(Logger.logFolder)
        if not os.path.exists(Logger.compressed):
            os.makedirs(Logger.compressed)
        if not os.path.exists(Logger.decompressed):
            os.makedirs(Logger.decompressed)

    @classmethod
    def log(self, type, message, func, level):
        with open(self.logFolder + "/logs" + datetime.datetime.strftime(datetime.date.today(), "%d-%m-%Y") + ".txt", "a+") as logFile:
            time = datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S")
            logLine = f"[{type}] [{time}] - [{level}] - [{func}] - {message}\n\n"
            print(logLine)
            logFile.write(logLine)

    @classmethod
    def logFactories(self, message, func, level="INFO"):
        self.log("Factories", message, func, level)

    @classmethod
    def logDatabase(self, message, func, level="INFO"):
        self.log("Database", message, func, level)

    @classmethod
    def logValidation(self, message, func, level="INFO"):
        self.log("Validation", message, func, level)

    @classmethod
    def logService(self, message, func, level="INFO"):
        self.log("Service", message, func, level)
    

    @classmethod
    def logMain(self, message, func, level="INFO"):
        self.log("Main", message, func, level)

    @classmethod
    def getLogFile(self, date: str):
        datenow = date[:2] + "-" + date[2:4] + "-" + date[4:]
        if (datenow != datetime.datetime.strftime(datetime.date.today(), "%d-%m-%Y")):
            self.decompressLogs(datenow)
        return self.logFolder + "logs" + datenow + ".txt"

    @classmethod
    def compressLogs(self):
        for file in os.listdir(self.logFolder):
            if file != ("logs" + datetime.datetime.strftime(datetime.date.today(), "%d-%m-%y") + ".txt"):
                continue
            if file == "Compressed" or file == "Decompressed":
                continue
            with open(self.logFolder + file, "rb+") as logFile:
                compressed = zlib.compress(logFile.read())
                with open(self.compressed + file, "wb+") as compressedFile:
                    compressedFile.write(compressed)
            os.remove(self.logFolder + file)
                
    @classmethod
    def decompressLog(self, date):
        with open(self.compressed + "logs" + date + ".txt", "rb+") as compressedFile:
            decompressed = zlib.decompress(compressedFile.read())
            with open(self.decompressed + "logs" + date + ".txt", "wb+") as logFile:
                logFile.write(decompressed)
    
    @classmethod
    def decompressLogs(self):
        for file in os.listdir(self.compressed):
            with open(self.compressed + file, "rb") as compressedFile:
                decompressed = zlib.decompress(compressedFile.read())
                with open(self.decompressed + file, "wb+") as logFile:
                    logFile.write(decompressed)
        with open(self.logFolder + "logs" + datetime.datetime.strftime(datetime.date.today(), "%d-%m-%Y") + ".txt", "r") as logFile:
            with open(self.decompressed + "logs" + datetime.datetime.strftime(datetime.date.today(), "%d-%m-%Y") + ".txt", "w+") as decompressedFile:
                decompressedFile.write(logFile.read())
    
    @classmethod
    def clearDecompressedLogs(self):
        for file in os.listdir(self.decompressed):
            os.remove(self.decompressed + file)

if __name__ == "__main__":
    month = 1
    print(f"{month:02d}")
