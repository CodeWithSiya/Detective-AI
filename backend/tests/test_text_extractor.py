import os
import tempfile
import pytest
from unittest.mock import patch, mock_open, MagicMock
from app.services.text_extractor import TextExtractor

class TestTextExtractor:
    """
    Unit tests for TextExtractor service class.
    """

    def test_get_supported_extensions(self):
        """Test that get_supported_extensions returns correct file types."""
        expected_extensions = ['txt', 'pdf', 'docx']
        actual_extensions = TextExtractor.get_supported_extensions()
        assert actual_extensions == expected_extensions

    def test_extract_text_file_not_found(self):
        """Test extract_text with non-existent file."""
        result = TextExtractor.extract_text("nonexistent_file.txt", "txt")
        assert result is None

    @patch('builtins.open', new_callable=mock_open, read_data='Hello, World!')
    @patch('os.path.exists', return_value=True)
    def test_extract_txt_success(self, mock_exists, mock_file):
        """Test successful text extraction from TXT file."""
        result = TextExtractor.extract_txt("test.txt")
        assert result == "Hello, World!"
        mock_file.assert_called_once_with("test.txt", 'r', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open, read_data='Simple text content')
    @patch('os.path.exists', return_value=True)
    def test_extract_text_txt_file(self, mock_exists, mock_file):
        """Test extract_text method with TXT file."""
        result = TextExtractor.extract_text("test.txt", "txt")
        assert result == "Simple text content"

    def test_extract_text_unsupported_file_type(self):
        """Test extract_text with unsupported file type."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_file.flush()
            
            try:
                result = TextExtractor.extract_text(temp_file.name, "xyz")
                assert result is None
            finally:
                os.unlink(temp_file.name)

    @patch('PyPDF2.PdfReader')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_extract_pdf_success(self, mock_exists, mock_file, mock_pdf_reader):
        """Test successful text extraction from PDF file."""
        # Mock PDF page with text
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF content line 1"
        
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_pdf_instance
        
        result = TextExtractor.extract_pdf("test.pdf")
        assert result == "PDF content line 1"

    @patch('PyPDF2.PdfReader')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_extract_pdf_multiple_pages(self, mock_exists, mock_file, mock_pdf_reader):
        """Test PDF extraction with multiple pages."""
        # Mock multiple PDF pages
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_pdf_instance
        
        result = TextExtractor.extract_pdf("test.pdf")
        assert result == "Page 1 content\nPage 2 content"

    @patch('PyPDF2.PdfReader', side_effect=Exception("PDF read error"))
    @patch('builtins.open', new_callable=mock_open)
    def test_extract_pdf_exception(self, mock_file, mock_pdf_reader):
        """Test PDF extraction with exception."""
        result = TextExtractor.extract_pdf("test.pdf")
        assert result is None

    @patch('app.services.text_extractor.Document')
    @patch('os.path.exists', return_value=True)
    def test_extract_docx_success(self, mock_exists, mock_document):
        """Test successful text extraction from DOCX file."""
        # Mock DOCX paragraphs
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "First paragraph"
        
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "Second paragraph"
        
        mock_doc_instance = MagicMock()
        mock_doc_instance.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_document.return_value = mock_doc_instance
        
        result = TextExtractor.extract_docx("test.docx")
        assert result == "First paragraph\nSecond paragraph"

    @patch('app.services.text_extractor.Document', side_effect=Exception("DOCX read error"))
    def test_extract_docx_exception(self, mock_document):
        """Test DOCX extraction with exception."""
        result = TextExtractor.extract_docx("test.docx")
        assert result is None

    @patch('PyPDF2.PdfReader')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_extract_text_pdf_file(self, mock_exists, mock_file, mock_pdf_reader):
        """Test extract_text method with PDF file."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF test content"
        
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_pdf_instance
        
        result = TextExtractor.extract_text("test.pdf", "pdf")
        assert result == "PDF test content"

    @patch('app.services.text_extractor.Document')
    @patch('os.path.exists', return_value=True)
    def test_extract_text_docx_file(self, mock_exists, mock_document):
        """Test extract_text method with DOCX file."""
        mock_paragraph = MagicMock()
        mock_paragraph.text = "DOCX test content"
        
        mock_doc_instance = MagicMock()
        mock_doc_instance.paragraphs = [mock_paragraph]
        mock_document.return_value = mock_doc_instance
        
        result = TextExtractor.extract_text("test.docx", "docx")
        assert result == "DOCX test content"

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', side_effect=Exception("File read error"))
    def test_extract_text_exception_handling(self, mock_file, mock_exists):
        """Test extract_text exception handling."""
        result = TextExtractor.extract_text("error_file.txt", "txt")
        assert result is None

    def test_extract_txt_empty_file(self):
        """Test extraction from empty TXT file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write("")
            temp_file.flush()
            
            try:
                result = TextExtractor.extract_txt(temp_file.name)
                assert result == ""
            finally:
                os.unlink(temp_file.name)

    def test_extract_txt_with_special_characters(self):
        """Test extraction from TXT file with special characters."""
        test_content = "Hello! @#$%^&*()_+ 中文 émojis 🚀"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_file:
            temp_file.write(test_content)
            temp_file.flush()
            
            try:
                result = TextExtractor.extract_txt(temp_file.name)
                assert result == test_content
            finally:
                os.unlink(temp_file.name)

    @patch('PyPDF2.PdfReader')
    @patch('builtins.open', new_callable=mock_open)
    def test_extract_pdf_empty_pages(self, mock_file, mock_pdf_reader):
        """Test PDF extraction with empty pages."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_pdf_instance
        
        result = TextExtractor.extract_pdf("empty.pdf")
        assert result == ""

    @patch('app.services.text_extractor.Document')
    def test_extract_docx_empty_document(self, mock_document):
        """Test DOCX extraction with empty document."""
        mock_doc_instance = MagicMock()
        mock_doc_instance.paragraphs = []
        mock_document.return_value = mock_doc_instance
        
        result = TextExtractor.extract_docx("empty.docx")
        assert result == ""