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
    userId = serializers.IntegerField(source='user.id', read_only=True)
    userName = serializers.SerializerMethodField()
    submissionId = serializers.SerializerMethodField()
    analysisId = serializers.UUIDField(source='object_id', read_only=True)
    feedbackText = serializers.CharField(source='comment', read_only=True)
    submittedAt = serializers.DateTimeField(source='created_at', read_only=True)
    analysisType = serializers.SerializerMethodField()
    originalPrediction = serializers.SerializerMethodField()
    confidence = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = [
            'id', 'userId', 'userName', 'submissionId', 'analysisId', 
            'feedbackText', 'submittedAt', 'status', 'analysisType',
            'originalPrediction', 'confidence'
        ]

    def get_userName(self, obj):
        """Get user's full name with fallback to username."""
        try:
            if obj and obj.user:
                return obj.user.full_name or obj.user.username
            return 'Unknown User'
        except Exception:
            return 'Unknown User'

    def get_submissionId(self, obj):
        """Get the submission ID from the related analysis result."""
        try:
            if not obj or not obj.content_object:
                return None
                
            analysis = obj.content_object
            
            # Check if analysis has content_object (for generic FK to submissions)
            if hasattr(analysis, 'content_object') and analysis.content_object:
                submission = analysis.content_object
                return str(submission.id) if submission else None
            
            # Check if analysis has direct submission FK
            elif hasattr(analysis, 'submission') and analysis.submission:
                return str(analysis.submission.id)
            
            return None
        except Exception:
            return None

    def get_analysisType(self, obj):
        """Determine if this is for text or image analysis."""
        try:
            if not obj or not obj.content_type:
                return 'text'
                
            model_name = obj.content_type.model.lower()
            if 'text' in model_name:
                return 'text'
            elif 'image' in model_name:
                return 'image'
            return 'text'
        except Exception:
            return 'text'

    def get_originalPrediction(self, obj):
        """Get the original AI prediction from the analysis result."""
        try:
            if not obj or not obj.content_object:
                return 'Unknown'
                
            analysis = obj.content_object
            
            if not hasattr(analysis, 'detection_result'):
                return 'Unknown'
                
            detection_result = analysis.detection_result
            
            # Handle enum values
            if hasattr(detection_result, 'value'):
                detection_result = detection_result.value
                
            if detection_result == 'AI_GENERATED':
                return 'AI Generated'
            elif detection_result == 'HUMAN_WRITTEN':
                return 'Human Written'
            
            return 'Unknown'
        except Exception:
            return 'Unknown'

    def get_confidence(self, obj):
        """Get the confidence percentage from the analysis result."""
        try:
            if not obj or not obj.content_object:
                return 0
                
            analysis = obj.content_object
            
            if not hasattr(analysis, 'confidence') or analysis.confidence is None:
                return 0
                
            return round(analysis.confidence * 100) if analysis.confidence else 0
        except Exception:
            return 0

class FeedbackUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating feedback.
    """
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']