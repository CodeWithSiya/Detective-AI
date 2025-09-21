from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from app.models.text_submission import TextSubmission
from app.models.text_analysis_result import TextAnalysisResult
from app.models.image_submission import ImageSubmission 
from app.models.image_analysis_result import ImageAnalysisResult

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
    
class ImageSubmissionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing image submissions - just name and basic info.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 21/09/2025 
    """
    image_url = serializers.SerializerMethodField()
    dimensions = serializers.SerializerMethodField()
    
    class Meta:
        model = ImageSubmission
        fields = ['id', 'name', 'created_at', 'image_url', 'file_size', 'dimensions']
    
    def get_image_url(self, obj):
        """Get the image URL."""
        return obj.image_url
    
    def get_dimensions(self, obj):
        """Get image dimensions as string."""
        if obj.width and obj.height:
            return f"{obj.width}x{obj.height}"
        return None

class ImageSubmissionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer with all content including full analysis data.
    """
    analysis_result = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    dimensions = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()

    class Meta:
        model = ImageSubmission
        fields = [
            'id', 'name', 'created_at', 'image_url', 'file_size', 
            'file_size_mb', 'width', 'height', 'dimensions', 'analysis_result'
        ]

    def get_analysis_result(self, obj):
        """
        Get the complete latest analysis result including all analysis data.
        """
        try:
            content_type = ContentType.objects.get_for_model(obj)
            analysis = ImageAnalysisResult.objects.filter(
                content_type=content_type,
                object_id=obj.id,
                status=ImageAnalysisResult.Status.COMPLETED
            ).order_by('-created_at').first()

            if analysis:
                return {
                    # Basic analysis data
                    'id': str(analysis.id),
                    'status': analysis.status,
                    'detection_result': analysis.detection_result,
                    'probability': analysis.probability,
                    'confidence': analysis.confidence,
                    'processing_time_ms': analysis.processing_time_ms,
                    'created_at': analysis.created_at,
                    'completed_at': analysis.completed_at,
                }
            
            return None
        except Exception:
            return None

    def get_image_url(self, obj):
        """Get the image URL."""
        return obj.image_url

    def get_dimensions(self, obj):
        """Get image dimensions as string."""
        if obj.width and obj.height:
            return f"{obj.width}x{obj.height}"
        return None

    def get_file_size_mb(self, obj):
        """Get file size in MB."""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None