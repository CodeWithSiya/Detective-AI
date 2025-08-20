import os
from typing import Optional
import PyPDF2
from docx import Document

class TextExtractor:
    """
    Service class for extracting text from various file formats.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025 
    """

    @staticmethod
    def extract_text(file_path: str, file_type: str) -> Optional[str]:
        """
        Extract text from a file based on its type.

        :param file_path: Path to the file.
        :param file_type: File extension (pdf, txt, docx).
        :returns: Extracted text content or None if extraction fails.
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        try:
            if file_type == "txt":
                return TextExtractor.extract_txt(file_path)
            elif file_type == 'pdf':
                return TextExtractor.extract_pdf(file_path)
            elif file_type == 'docx':
                return TextExtractor.extract_docx(file_path)
            else:
                print(f"Unsupported file type: {file_type}")

        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return None
        
    @staticmethod
    def extract_txt(file_path: str) -> Optional[str]:
        """
        Extract text from TXT files.

        :param file_path: Path to the file.
        :returns: Extracted text content as a string.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
        
    @staticmethod
    def extract_pdf(file_path: str) -> Optional[str]:
        """
        Extract text from PDF files.

        :param file_path: Path to the file.   
        :returns: Extracted text content as a string.
        """
        try:    
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        
        except Exception as e:
            print(f"PDF extraction failed: {str(e)}")
            return None

    @staticmethod
    def extract_docx(file_path: str) -> Optional[str]:
        """
        Extract text from DOCX files.

        :param file_path: Path to the file.   
        :returns: Extracted text content as a string.
        """
        try:
            document = Document(file_path)
            text = []
            for paragraph in document.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text)
        
        except Exception as e:
            print(f"DOCX extraction failed: {str(e)}")
            return None
        
    @staticmethod
    def get_supported_extensions() -> list:
        """
        Get list of supported file extensions.

        :returns: List of supported file extensions.
        """
        return ['txt', 'pdf', 'docx']