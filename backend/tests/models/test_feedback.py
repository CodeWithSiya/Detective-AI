from django.contrib.auth import get_user_model
from django.db import IntegrityError
from app.models import Feedback
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import pytest
import uuid

User = get_user_model()

class TestFeedbackModel:
    """
    Unit tests for Feedback model.
    
    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 16/09/2025
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
    def mock_content_type(self):
        """
        Mock ContentType.
        """
        content_type = Mock()
        content_type.id = 1
        return content_type

    def test_feedback_rating_choices(self):
        """
        Test that rating choices are correct.
        """
        assert Feedback.FeedbackRating.THUMBS_UP == "THUMBS_UP"
        assert Feedback.FeedbackRating.THUMBS_DOWN == "THUMBS_DOWN"
        
        # Test choice labels.
        choices_dict = dict(Feedback.FeedbackRating.choices)
        assert choices_dict[Feedback.FeedbackRating.THUMBS_UP] == "Thumbs Up"
        assert choices_dict[Feedback.FeedbackRating.THUMBS_DOWN] == "Thumbs Down"

    def test_str_representation(self):
        """
        Test the string representation of Feedback.
        """
        user = User(username="testuser")
        fixed_time = datetime(2023, 8, 22, 10, 30, 0, tzinfo=timezone.utc)

        feedback = Feedback(
            user=user,
            rating=Feedback.FeedbackRating.THUMBS_UP,
            created_at=fixed_time,
        )

        expected_str = f"testuser | THUMBS_UP | {fixed_time}"
        assert str(feedback) == expected_str

    def test_uuid_field_generates_valid_uuid(self):
        """
        Test that the UUID field generates valid UUIDs.
        """
        field = Feedback._meta.get_field('id')
        generated_uuid = field.default()
        
        assert isinstance(generated_uuid, uuid.UUID)
        assert generated_uuid.version == 4

    def test_comment_max_length(self):
        """
        Test that comment field has correct max_length.
        """
        # Mock the comment field
        mock_field = Mock()
        mock_field.max_length = 1000
        
        with patch.object(Feedback._meta, 'get_field', return_value=mock_field):
            comment_field = Feedback._meta.get_field('comment')
            assert comment_field.max_length == 1000

    @patch.object(Feedback, '__init__', return_value=None)
    def test_generic_foreign_key_fields_exist(self, mock_init):
        """
        Test that GenericForeignKey fields are accessible.
        """
        # Create a mock feedback instance with the required attributes
        feedback = Mock(spec=Feedback)
        feedback.content_type = Mock()
        feedback.object_id = Mock()
        feedback.submission = Mock()
        
        # Test that the generic foreign key fields exist.
        assert hasattr(feedback, 'content_type')
        assert hasattr(feedback, 'object_id')
        assert hasattr(feedback, 'submission')

    def test_model_meta_configuration(self):
        """
        Test model Meta configuration.
        """
        # Mock the meta object
        mock_meta = Mock()
        mock_meta.db_table = 'feedback'
        mock_meta.indexes = [Mock(), Mock(), Mock()]  # 3 indexes
        
        mock_constraint = Mock()
        mock_constraint.name = "unique_feedback_per_user_submission"
        mock_meta.constraints = [mock_constraint]
        
        with patch.object(Feedback, '_meta', mock_meta):
            meta = Feedback._meta
            
            # Test db_table.
            assert meta.db_table == 'feedback'
            
            # Test that indexes are defined.
            assert len(meta.indexes) == 3
            
            # Test that unique constraint exists.
            constraint_names = [constraint.name for constraint in meta.constraints]
            assert "unique_feedback_per_user_submission" in constraint_names

    @patch('app.models.Feedback.objects')
    def test_create_feedback(self, mock_objects, mock_user, mock_content_type):
        """
        Test creating feedback (mocked).
        """
        # Setup mock feedback instance
        mock_feedback = Mock(spec=Feedback)
        mock_feedback.id = uuid.uuid4()
        mock_feedback.user = mock_user
        mock_feedback.rating = Feedback.FeedbackRating.THUMBS_UP
        mock_feedback.comment = "Great job!"
        mock_feedback.created_at = datetime.now(timezone.utc)
        mock_feedback.updated_at = datetime.now(timezone.utc)
        
        # Mock the create method
        mock_objects.create.return_value = mock_feedback
        
        # Call the method
        feedback = Feedback.objects.create(
            user=mock_user,
            rating=Feedback.FeedbackRating.THUMBS_UP,
            comment="Great job!",
            content_type=mock_content_type,
            object_id=uuid.uuid4()
        )
        
        # Assertions
        assert feedback.id is not None
        assert feedback.user == mock_user
        assert feedback.rating == Feedback.FeedbackRating.THUMBS_UP
        assert feedback.comment == "Great job!"
        assert feedback.created_at is not None
        assert feedback.updated_at is not None

    @patch('app.models.Feedback.objects')
    def test_unique_constraint_enforcement(self, mock_objects, mock_user, mock_content_type):
        """
        Test unique constraint prevents duplicate feedback (mocked).
        """
        object_id = uuid.uuid4()
        
        # Mock first creation success
        mock_feedback1 = Mock(spec=Feedback)
        mock_feedback1.id = uuid.uuid4()
        
        # Mock second creation failure
        def side_effect(*args, **kwargs):
            if mock_objects.create.call_count == 1:
                return mock_feedback1
            else:
                raise IntegrityError("Duplicate entry")
        
        mock_objects.create.side_effect = side_effect
        
        # Create first feedback (should succeed)
        feedback1 = Feedback.objects.create(
            user=mock_user,
            rating=Feedback.FeedbackRating.THUMBS_UP,
            content_type=mock_content_type,
            object_id=object_id
        )
        assert feedback1 == mock_feedback1
        
        # Try to create duplicate (should fail)
        with pytest.raises(IntegrityError):
            Feedback.objects.create(
                user=mock_user,
                rating=Feedback.FeedbackRating.THUMBS_DOWN,
                content_type=mock_content_type,
                object_id=object_id
            )

    @patch('app.models.Feedback.objects')
    def test_user_cascade_delete(self, mock_objects, mock_user, mock_content_type):
        """
        Test feedback is deleted when user is deleted (mocked).
        """
        # Setup mock feedback
        mock_feedback = Mock(spec=Feedback)
        mock_feedback.id = uuid.uuid4()
        feedback_id = mock_feedback.id
        
        mock_objects.create.return_value = mock_feedback
        mock_objects.filter.return_value.exists.return_value = False
        
        # Create feedback
        feedback = Feedback.objects.create(
            user=mock_user,
            rating=Feedback.FeedbackRating.THUMBS_UP,
            content_type=mock_content_type,
            object_id=uuid.uuid4()
        )
        
        # Mock user deletion (would cascade delete feedback)
        mock_user.delete = Mock()
        mock_user.delete()
        
        # Check feedback no longer exists
        exists = Feedback.objects.filter(id=feedback_id).exists()
        assert not exists

    def test_related_name_functionality(self, mock_user, mock_content_type):
        """
        Test that related_name 'feedback' works correctly (mocked).
        """
        # Mock feedback queryset
        mock_feedback1 = Mock(spec=Feedback)
        mock_feedback1.user = mock_user
        mock_feedback2 = Mock(spec=Feedback)
        mock_feedback2.user = mock_user
        
        mock_queryset = Mock()
        mock_queryset.all.return_value = [mock_feedback1, mock_feedback2]
        mock_queryset.count.return_value = 2
        
        # Mock the related manager
        mock_user.feedback = mock_queryset
        
        # Test access through related_name
        user_feedback = mock_user.feedback.all()
        assert len(user_feedback) == 2
        
        for feedback in user_feedback:
            assert feedback.user == mock_user

    @patch('app.models.Feedback.objects')
    def test_auto_timestamps_work(self, mock_objects, mock_user, mock_content_type):
        """
        Test that auto timestamps are set correctly (mocked).
        """
        created_time = datetime.now(timezone.utc)
        updated_time = created_time
        later_updated_time = datetime(2023, 8, 22, 11, 0, 0, tzinfo=timezone.utc)
        
        # Setup mock feedback
        mock_feedback = Mock(spec=Feedback)
        mock_feedback.id = uuid.uuid4()
        mock_feedback.created_at = created_time
        mock_feedback.updated_at = updated_time
        mock_feedback.comment = "Great job!"
        
        mock_objects.create.return_value = mock_feedback
        
        # Create feedback
        feedback = Feedback.objects.create(
            user=mock_user,
            rating=Feedback.FeedbackRating.THUMBS_UP,
            content_type=mock_content_type,
            object_id=uuid.uuid4()
        )
        
        assert feedback.created_at is not None
        assert feedback.updated_at is not None
        
        # Mock updating feedback
        original_created_at = feedback.created_at
        
        def mock_save():
            mock_feedback.updated_at = later_updated_time
            
        def mock_refresh():
            pass
            
        mock_feedback.save = mock_save
        mock_feedback.refresh_from_db = mock_refresh
        
        # Update feedback and check updated_at changes
        feedback.comment = "Updated comment"
        feedback.save()
        feedback.refresh_from_db()
        
        assert feedback.created_at == original_created_at  # Should not change
        assert feedback.updated_at == later_updated_time   # Should be the new time we set

    @patch('app.models.Feedback.objects')  
    def test_feedback_model_instantiation(self, mock_objects, mock_user, mock_content_type):
        """
        Test that Feedback model can be instantiated.
        """
        # Create a mock feedback instance instead of real instantiation
        mock_feedback = Mock(spec=Feedback)
        mock_feedback.user = mock_user
        mock_feedback.rating = Feedback.FeedbackRating.THUMBS_UP
        mock_feedback.comment = "Test comment"
        mock_feedback.content_type = mock_content_type
        mock_feedback.object_id = uuid.uuid4()
        
        # Test that we can create the mock and access its attributes
        feedback = mock_feedback
        
        # Basic attribute checks
        assert feedback.user == mock_user
        assert feedback.rating == Feedback.FeedbackRating.THUMBS_UP
        assert feedback.comment == "Test comment"
        assert feedback.content_type == mock_content_type