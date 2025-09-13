from rest_framework import serializers
from app.models.feedback import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for feedback data representation.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 08/09/2025
    """
    analysis_id = serializers.UUIDField(source='object_id', read_only=True)
    submission_name = serializers.CharField(read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'rating', 'comment', 'analysis_id', 'submission_name', 'created_at', 'updated_at']

class FeedbackAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for admin feedback views with user information.
    """
    analysis_id = serializers.UUIDField(source='object_id', read_only=True)
    submission_name = serializers.CharField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'username', 'user_email', 'rating', 'comment', 'analysis_id', 'submission_name', 'created_at', 'updated_at']

class FeedbackUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating feedback.
    """
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']