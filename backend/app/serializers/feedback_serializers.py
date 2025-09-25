from rest_framework import serializers
from app.models.feedback import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for feedback data representation.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 08/09/2025
    """
    analysis_id = serializers.UUIDField(source='object_id', read_only=True)
    analysis_type = serializers.SerializerMethodField()
    submission_name = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = [
            'id', 'rating', 'comment', 'analysis_id', 'analysis_type', 
            'submission_name', 'status', 'created_at', 'updated_at', 'resolved_at'
        ]

    def get_analysis_type(self, obj):
        """
        Determine if this is for text or image analysis.
        """
        model_name = obj.content_type.model
        if 'text' in model_name.lower():
            return 'text'
        elif 'image' in model_name.lower():
            return 'image'
        return 'unknown'

    def get_submission_name(self, obj):
        """
        Get the submission name from the related analysis result.
        """
        try:
            # Get the actual analysis result through the generic foreign key
            analysis = obj.analysis_result
            if analysis and hasattr(analysis, 'submission') and analysis.submission:
                return analysis.submission.name
            return 'Unknown Submission'
        except Exception:
            return 'Unknown Submission'

class FeedbackAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for admin feedback views with user information.
    """
    analysis_id = serializers.UUIDField(source='object_id', read_only=True)
    submission_name = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id', 'username', 'user_email', 'rating', 'comment', 'analysis_id', 
            'submission_name', 'status', 'created_at', 'updated_at', 'resolved_at'
        ]

    def get_submission_name(self, obj):
        """
        Get the submission name from the related analysis result.
        """
        try:
            analysis = obj.analysis_result
            if analysis and hasattr(analysis, 'submission') and analysis.submission:
                return analysis.submission.name
            return 'Unknown Submission'
        except Exception:
            return 'Unknown Submission'

class FeedbackUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating feedback.
    """
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']