"""
Models package initialisation.
"""
# Initialising User model packages.
from .user import User

# Initialising Submission model packages.
from .submission import Submission
from .text_submission import TextSubmission
from .image_submission import ImageSubmission

# Intialising Analysis model packages.
from .analysis_result import AnalysisResult
from .text_analysis_result import TextAnalysisResult
from .image_analysis_result import ImageAnalysisResult