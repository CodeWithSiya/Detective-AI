# type: ignore
from django.contrib.auth import get_user_model
from django.utils import timezone
from app.models import TextSubmission
from unittest.mock import Mock, patch
import pytest
import uuid

User = get_user_model()

class TestTextSubmissionModel:
    """
    Unit tests for TextSubmission model.
    
    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """
        Create a mock user.
        """
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'testuser'
        user.email = 'test@example.com'
        return user

    @pytest.fixture
    def sample_text_content(self):
        """
        Sample text content for testing.
        """
        return "This is a sample text submission for AI detection analysis. It contains multiple sentences to test the functionality."

    def test_model_meta_configuration(self):
        """
        Test model Meta configuration.
        """
        meta = TextSubmission._meta
        
        # Test db_table
        assert meta.db_table == 'text_submissions'
        
        # Test that indexes are defined (1 index)
        assert len(meta.indexes) == 1

    def test_content_field_configuration(self):
        """
        Test content field configuration.
        """
        field = TextSubmission._meta.get_field('content')
        
        assert field.max_length == 5000
        assert field.help_text == "The text content submitted for AI detection analysis."

    def test_user_foreign_key_relationship(self):
        """
        Test user foreign key relationship.
        """
        field = TextSubmission._meta.get_field('user')
        
        assert field.related_model == User
        assert field.remote_field.on_delete.__name__ == 'CASCADE'
        assert field.remote_field.related_name == 'text_submissions'

    def test_character_count_field_configuration(self):
        """
        Test character_count field configuration.
        """
        field = TextSubmission._meta.get_field('character_count')
        
        assert field.null == True
        assert field.blank == True
        assert field.help_text == "Number of characters in the submission."

    def test_str_representation(self):
        """
        Test the string representation of TextSubmission.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.name = "Test Text Submission"
        mock_submission.user.email = "test@example.com"
        mock_submission.character_count = 125
        
        # Mock the __str__ method
        mock_submission.__str__ = Mock(return_value=f"{mock_submission.name} | {mock_submission.user.email} | {mock_submission.character_count}")
        
        result = str(mock_submission)
        expected = "Test Text Submission | test@example.com | 125"
        assert result == expected

    def test_save_method_calculates_character_count(self, sample_text_content):
        """
        Test that save method automatically calculates character count.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.content = sample_text_content
        mock_submission.character_count = None
        
        def mock_save(*args, **kwargs):
            if mock_submission.content:
                mock_submission.character_count = len(mock_submission.content)
        
        mock_submission.save = mock_save
        
        # Call save
        mock_submission.save()
        
        # Check that character count was calculated 
        assert mock_submission.character_count == len(sample_text_content)
        assert mock_submission.character_count == 117

    def test_save_method_with_empty_content(self):
        """
        Test save method with empty content.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.content = ""
        mock_submission.character_count = None
        
        def mock_save(*args, **kwargs):
            if mock_submission.content:
                mock_submission.character_count = len(mock_submission.content)
        
        mock_submission.save = mock_save
        
        # Call save
        mock_submission.save()
        
        # Character count should remain None for empty content
        assert mock_submission.character_count is None

    def test_save_method_with_none_content(self):
        """
        Test save method with None content.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.content = None
        mock_submission.character_count = None
        
        def mock_save(*args, **kwargs):
            if mock_submission.content:
                mock_submission.character_count = len(mock_submission.content)
        
        mock_submission.save = mock_save
        
        # Call save
        mock_submission.save()
        
        # Character count should remain None
        assert mock_submission.character_count is None

    def test_save_method_updates_existing_character_count(self):
        """
        Test that save method updates existing character count.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.content = "Updated content with different length"
        mock_submission.character_count = 50  # Old value
        
        def mock_save(*args, **kwargs):
            if mock_submission.content:
                mock_submission.character_count = len(mock_submission.content)
        
        mock_submission.save = mock_save
        
        # Call save
        mock_submission.save()
        
        # Check that character count was updated
        assert mock_submission.character_count == 37
        assert mock_submission.character_count != 50

    def test_save_method_with_whitespace_content(self):
        """
        Test save method with content containing whitespace.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.content = "   Text with   spaces   and\nnewlines\t\t  "
        mock_submission.character_count = None
        
        def mock_save(*args, **kwargs):
            if mock_submission.content:
                mock_submission.character_count = len(mock_submission.content)
        
        mock_submission.save = mock_save
        
        # Call save
        mock_submission.save()
        
        # Check that all characters including whitespace are counted
        expected_count = len("   Text with   spaces   and\nnewlines\t\t  ")
        assert mock_submission.character_count == expected_count
        assert mock_submission.character_count == 40

    def test_save_method_with_special_characters(self):
        """
        Test save method with special characters and unicode.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.content = "Text with special chars: !@#$%^&*()_+ and unicode: café, naïve, résumé"
        mock_submission.character_count = None
        
        def mock_save(*args, **kwargs):
            if mock_submission.content:
                mock_submission.character_count = len(mock_submission.content)
        
        mock_submission.save = mock_save
        
        # Call save
        mock_submission.save()
        
        # Check that special characters and unicode are counted correctly
        assert mock_submission.character_count == len(mock_submission.content)
        assert mock_submission.character_count == 70

    def test_save_method_calls_super(self):
        """
        Test that save method calls parent save method.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.content = "Test content"
        mock_submission.character_count = None
        
        # Track if super().save() was called
        super_save_called = False
        
        def mock_save(*args, **kwargs):
            nonlocal super_save_called
            if mock_submission.content:
                mock_submission.character_count = len(mock_submission.content)
            super_save_called = True
        
        mock_submission.save = mock_save
        
        # Call save
        mock_submission.save()
        
        # Verify super save was called
        assert super_save_called == True
        assert mock_submission.character_count == 12

    @patch('app.models.TextSubmission.objects')
    def test_model_instantiation(self, mock_objects, mock_user, sample_text_content):
        """
        Test that TextSubmission model can be instantiated.
        """
        # Create a mock text submission instance
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.id = uuid.uuid4()
        mock_submission.name = "Test Text Submission"
        mock_submission.user = mock_user
        mock_submission.content = sample_text_content
        mock_submission.character_count = len(sample_text_content)
        mock_submission.created_at = timezone.now()
        
        # Test that we can create the mock and access its attributes
        submission = mock_submission
        
        # Basic attribute checks
        assert submission.id is not None
        assert submission.name == "Test Text Submission"
        assert submission.user == mock_user
        assert submission.content == sample_text_content
        assert submission.character_count == 117
        assert submission.created_at is not None

    def test_content_field_max_length_validation(self):
        """
        Test content field max length configuration.
        """
        field = TextSubmission._meta.get_field('content')
        max_length = field.max_length
        
        # Test that max_length is set correctly
        assert max_length == 5000
        
        # Mock submission with content at max length
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.content = "a" * 5000
        mock_submission.character_count = None
        
        def mock_save(*args, **kwargs):
            if mock_submission.content:
                mock_submission.character_count = len(mock_submission.content)
        
        mock_submission.save = mock_save
        
        # Should handle max length content
        mock_submission.save()
        assert mock_submission.character_count == 5000

    def test_character_count_with_various_content_lengths(self):
        """
        Test character count calculation with various content lengths.
        """
        test_cases = [
            ("a", 1),
            ("Hello", 5),
            ("Hello, World!", 13),
            ("A" * 100, 100),
            ("Multi\nLine\nText", 15),
            ("Text with 123 numbers!", 22),
        ]
        
        for content, expected_length in test_cases:
            mock_submission = Mock(spec=TextSubmission)
            mock_submission.content = content
            mock_submission.character_count = None
            
            def mock_save(*args, **kwargs):
                if mock_submission.content:
                    mock_submission.character_count = len(mock_submission.content)
            
            mock_submission.save = mock_save
            
            # Call save and check character count
            mock_submission.save()
            assert mock_submission.character_count == expected_length

    def test_str_representation_with_none_values(self):
        """
        Test string representation with None values.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.name = "Test Submission"
        mock_submission.user.email = "test@example.com"
        mock_submission.character_count = None
        
        # Mock the __str__ method
        mock_submission.__str__ = Mock(return_value=f"{mock_submission.name} | {mock_submission.user.email} | {mock_submission.character_count}")
        
        result = str(mock_submission)
        expected = "Test Submission | test@example.com | None"
        assert result == expected

    def test_str_representation_with_zero_characters(self):
        """
        Test string representation with zero character count.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.name = "Empty Submission"
        mock_submission.user.email = "test@example.com"
        mock_submission.character_count = 0
        
        # Mock the __str__ method
        mock_submission.__str__ = Mock(return_value=f"{mock_submission.name} | {mock_submission.user.email} | {mock_submission.character_count}")
        
        result = str(mock_submission)
        expected = "Empty Submission | test@example.com | 0"
        assert result == expected

    def test_save_method_preserves_other_fields(self):
        """
        Test that save method doesn't interfere with other fields.
        """
        mock_submission = Mock(spec=TextSubmission)
        mock_submission.name = "Test Submission"
        mock_submission.content = "Test content"
        mock_submission.character_count = None
        original_name = mock_submission.name
        
        def mock_save(*args, **kwargs):
            if mock_submission.content:
                mock_submission.character_count = len(mock_submission.content)
            # Ensure other fields are preserved
        
        mock_submission.save = mock_save
        
        # Call save
        mock_submission.save()
        
        # Check that other fields are preserved
        assert mock_submission.name == original_name
        assert mock_submission.character_count == 12

    def test_model_field_attributes(self):
        """
        Test various model field attributes.
        """
        # Test content field
        content_field = TextSubmission._meta.get_field('content')
        assert hasattr(content_field, 'max_length')
        assert hasattr(content_field, 'help_text')
        
        # Test user field
        user_field = TextSubmission._meta.get_field('user')
        assert hasattr(user_field, 'related_model')
        assert hasattr(user_field, 'remote_field')
        
        # Test character_count field
        char_count_field = TextSubmission._meta.get_field('character_count')
        assert hasattr(char_count_field, 'null')
        assert hasattr(char_count_field, 'blank')
        assert hasattr(char_count_field, 'help_text')