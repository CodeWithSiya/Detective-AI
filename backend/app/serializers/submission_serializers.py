from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from app.models.text_submission import TextSubmission
from app.models.text_analysis_result import TextAnalysisResult

class TextSubmissionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing submissions - just name and basic info.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 10/09/2025 
    """
    
    class Meta:
        model = TextSubmission
        fields = ['id', 'name', 'created_at']

class TextSubmissionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer with all content including full Claude analysis.
    """
    analysis_result = serializers.SerializerMethodField()

    class Meta:
        model = TextSubmission
        fields = ['id', 'name', 'content', 'character_count', 'created_at', 'analysis_result']

    def get_analysis_result(self, obj):
        """
        Get the complete latest analysis result including all enhanced data.
        """
        try:
            content_type = ContentType.objects.get_for_model(obj)
            analysis = TextAnalysisResult.objects.filter(
                content_type=content_type,
                object_id=obj.id,
                status=TextAnalysisResult.Status.COMPLETED
            ).order_by('-created_at').first()

            if analysis:
                return {
                    # Basic analysis data.
                    'id': str(analysis.id),
                    'status': analysis.status,
                    'is_ai_generated': analysis.detection_result,
                    'probability': analysis.probability,
                    'confidence': analysis.confidence,
                    'processing_time_ms': analysis.processing_time_ms,
                    'created_at': analysis.created_at,
                    'completed_at': analysis.completed_at,
                    
                    # Full Claude analysis data.
                    'enhanced_analysis_used': analysis.enhanced_analysis_used,
                    'detection_reasons': analysis.detection_reasons,
                    'analysis_details': analysis.analysis_details,
                    'statistics': analysis.statistics,
                    
                    # Computed properties
                    'has_flagged_content': analysis.has_flagged_content,
                    'ai_indicators_count': analysis.ai_indicators_count,
                }
            
            return None
        except Exception:
            return None

class TextSubmissionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating text submissions.
    """
    class Meta:
        model = TextSubmission
        fields = ['name', 'content']

    def validate_content(self, value):
        """
        Validate content length to ensure meaningful submissions.
        """
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long.")
        return value.strip()