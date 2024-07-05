from pathlib import Path
from .utility import log, logError
import shutil
import PyPDF2
import docx2txt


class FileUtility:
    TEMP_DIR = Path("temp_files")
    
    @staticmethod
    def initialize_temp_dir():
        log("Initializing temporary directory", "FileUtility.initialize_temp_dir")
        FileUtility.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        log("Temporary directory initialized", "FileUtility.initialize_temp_dir")

    @staticmethod
    def save_temp_file(file) -> Path:
        log("Saving temporary file", "FileUtility.save_temp_file")
        temp_file_path = FileUtility.TEMP_DIR / file.filename
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        log("Temporary file saved", "FileUtility.save_temp_file")
        return temp_file_path

    @staticmethod
    def extract_text(file_path: Path) -> str:
        log("Extracting text from file", "FileUtility.extract_text")
        if file_path.suffix == '.pdf':
            return FileUtility._extract_text_from_pdf(file_path)
        elif file_path.suffix == '.docx':
            return FileUtility._extract_text_from_docx(file_path)
        else:
            return FileUtility._extract_text_from_txt(file_path)
        

    @staticmethod
    def _extract_text_from_pdf(file_path: Path) -> str:
        log("Extracting text from PDF", "FileUtility._extract_text_from_pdf")
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            log("Text extracted from PDF", "FileUtility._extract_text_from_pdf")
            return ''.join([page.extract_text() for page in reader.pages])

    @staticmethod
    def _extract_text_from_docx(file_path: Path) -> str:
        log("Extracting text from DOCX", "FileUtility._extract_text_from_docx")
        return docx2txt.process(str(file_path))

    @staticmethod
    def _extract_text_from_txt(file_path: Path) -> str:
        with file_path.open("r", encoding='utf-8') as file:
            log("Text extracted from TXT", "FileUtility._extract_text_from_txt")
            return file.read()

