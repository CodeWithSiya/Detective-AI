import anthropic
from typing import Dict, Any, List, Optional
import json
import os
from dataclasses import dataclass
import base64

@dataclass
class DetectionReason:
    type: str  # 'critical' | 'warning' | 'info' | 'success'
    title: str
    description: str
    impact: str  # 'High' | 'Medium' | 'Low' | 'Positive'

@dataclass
class AnalysisDetails:
    found_keywords: List[str]
    found_patterns: List[str]
    found_transitions: List[str]
    found_jargon: List[str]
    found_buzzwords: List[str]
    found_human_indicators: List[str]

class ClaudeService:
    """
    Service for integrating Claude AI to provide text analysis reasoning.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 05/09/2025  
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialise Claude service.

        :param api_key: Anthropic API key.
        :param model: Claude model to use.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def analyse_text_patterns(self, text:str, base_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Claude to analyse text patterns and provide detailed reasoning.

        :param text: The text to analyse.
        :param base_prediction: Basic model prediction results
        :return: Enhanced analysis with reasoning and patterns
        """
        prompt = self.build_text_analysis_prompt(text, base_prediction)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ] 
            )

            # Parse Claude's response.
            analysis_result = self.parse_claude_response(response.content[0].text) # type: ignore
            return analysis_result
        
        except Exception as e:
            # Fallback to basic analysis if Claude fails.
            return self.fallback_text_analysis(str(e))
        
    def analyse_image_patterns(self, image_path: str, base_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Claude to analyse image patterns and provide detailed reasoning for AI detection.

        :param image_path: Path to the image file to analyse.
        :param base_prediction: Basic model prediction results.
        :return: Enhanced analysis with explanation.
        """
        try:
            # Read and encode the image.
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            # Determine media type
            image_format = image_path.lower().split('.')[-1]
            if image_format in ['jpg', 'jpeg']:
                media_type = "image/jpeg"
            elif image_format == 'png':
                media_type = "image/png"
            else:
                media_type = "image/jpeg"

            prompt = self.build_image_analysis_prompt(base_prediction)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            # Parse Claude's response.
            explanation = response.content[0].text.strip()  # type: ignore

            return {
                'explanation': explanation
            }
        
        except Exception as e:
            # Fallback explanation if Claude fails
            return self.fallback_image_analysis(str(e), base_prediction)
        
    def build_text_analysis_prompt(self, text:str, base_prediction: Dict[str, Any]):
        """
        Build the analysis prompt for Claude.
        """
        return f"""
        You are an expert AI content detection system. Your role is to analyse text for signs that it may have been written by AI, and provide a clear, structured evaluation.

        TASK:
        Look at the text below and decide whether it shows patterns of being AI-generated. Use both the model’s results and your own reasoning.

        TEXT TO ANALYSE:
        {text}

        MODEL RESULTS:
        - Probability: {base_prediction.get('probability', 0):.3f}
        - Is AI Generated: {base_prediction.get('is_ai_generated', False)}
        - Confidence: {base_prediction.get('confidence', 0):.3f}

        OUTPUT FORMAT (Reply ONLY with valid JSON):
        {{
        "detection_reasons": [
            {{
            "type": "critical" | "warning" | "info" | "success",
            "title": "short category name",
            "description": "detailed but simple explanation",
            "impact": "High" | "Medium" | "Low" | "Positive"
            }}
        ],
        "analysis_details": {{
            "found_keywords": ["list of AI-typical words"],
            "found_patterns": ["list of exact AI-like phrases"],
            "found_transitions": ["list of formal transitions"],
            "found_jargon": ["list of corporate jargon"],
            "found_buzzwords": ["list of buzzwords"],
            "found_human_indicators": ["list of human-style features"]
        }}
        }}

        DETECTION CATEGORIES:
        - CRITICAL: Obvious AI phrases or direct references to AI
        - WARNING: Repetitive words, suspiciously formal patterns
        - INFO: Mild or unclear signs of AI writing
        - SUCCESS: Strong signs of human writing

        THINGS TO LOOK FOR:
        - Very formal or stiff language
        - Repetitive sentence structures
        - Generic or vague wording
        - No personal voice
        - Perfect grammar and neat structure throughout
        - Common AI transitions ("Furthermore", "Moreover", "In conclusion")
        - Buzzwords and corporate talk
        - Human markers such as personal stories, informal language, typos, or contractions (like "can't" or "won’t")

        CONSTRAINTS:
        - Respond only with valid JSON (no extra text or formatting)
        - Always include arrays, even if empty
        - Make sure reasons match the category type
        - Do not use academic or formal terms like 'pedagogical' or 'didactic'.' Instead, explain things in plain, everyday language that sounds natural to a general audience.
        - When extracting AI patterns, quote each one briefly in 3 to 4 words that capture the essence of the pattern if it is too long, using clear, everyday language.
        - Write in British English with correct spelling (analysed not analyzed, colour not color)
        """
    
    def build_image_analysis_prompt(self, base_prediction: Dict[str, Any]) -> str:
        """
        Build the analysis prompt for image analysis with Claude.
        """
        probability = base_prediction.get('probability', 0)
        is_ai_generated = base_prediction.get('is_ai_generated', False)
        confidence = base_prediction.get('confidence', 0)

        return f"""
        You are an expert AI image detection system. Your role is to analyse this image for signs that it may have been AI-generated, and provide a clear, natural explanation.

        TASK:
        - Look at this image and explain whether it shows patterns of being AI-generated. Use both the model's results and your visual analysis.
        - Do not mention or reference any separate model results. Present your answer as one system's opinion.

        ANALYSIS RESULTS:
        - Probability of AI: {probability:.3f}
        - Is AI Generated: {is_ai_generated}
        - Confidence: {confidence:.3f}

        INSTRUCTIONS:
        - Respond in bullet points only
        - Keep each bullet point short and easy to digest.
        - Use plain text only - no bold, italics, or formatting
        - Write in everyday language, not technical jargon
        - Focus each point on specific observations
        - Make it sound natural and conversational

        THINGS TO LOOK FOR:
        - Unrealistic textures or surfaces
        - Inconsistent lighting or shadows
        - Perfect symmetry or unnatural smoothness
        - Strange artifacts or distortions
        - Overly polished or too perfect appearance
        - Inconsistent perspective or proportions
        - Signs of human creativity, imperfections, or natural variation

        OUTPUT:
        - Write 4-6 bullet points explaining your findings
        - Use plain text only and keep each point focused and digestible 
        - Write in British English with correct spelling (analysed not analyzed, colour not color)
        - Use simple language that a general audience can understand.
        """
    
    def parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Claude's JSON response.
        """
        try:
            # Clean up the response text.
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:].strip()
            if response_text.endswith("```"):
                response_text = response_text[:-3].strip()

            parsed = json.loads(response_text)

            # Validate structure.
            detection_reasons = parsed.get('detection_reasons', [])
            analysis_details = parsed.get('analysis_details', {})

            return {
                'detection_reasons': detection_reasons,
                'analysis_details': analysis_details
            }
    
        except (json.JSONDecodeError, KeyError) as e:
            # Return empty structure if parsing fails.
            return self.fallback_text_analysis(f"JSON parsing error: {str(e)}")
        
    def fallback_text_analysis(self, error_message: str) -> Dict[str, Any]:
        """
        Provide fallback analysis when Claude fails.
        """
        return {
        'detection_reasons': [{
            'type': 'warning',
            'title': 'Claude Analysis Unavailable',
            'description': f'Enhanced analysis failed: {error_message}',
            'impact': 'Low'
        }],
        'analysis_details': {
            'found_keywords': [],
            'found_patterns': [],
            'found_transitions': [],
            'found_jargon': [],
            'found_buzzwords': [],
            'found_human_indicators': []
        }
    }

    def fallback_image_analysis(self, error_message: str, base_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide fallback analysis when Claude image analysis fails.
        """
        probability = base_prediction.get('probability', 0)
        is_ai_generated = base_prediction.get('is_ai_generated', False)

        if is_ai_generated:
            explanation = f"The detection model identified this image as likely AI-generated with {probability:.1%} confidence. While detailed visual analysis isn't available, the model detected patterns commonly associated with AI-created content."
        else:
            explanation = f"The detection model suggests this image appears to be human-created with {1 - probability:.1%} confidence. The image likely shows characteristics typical of traditional photography or artwork."

        return {
            'explanation': explanation
        }

    def create_text_submission_name(self, text: str, max_length: int = 20):
        """
        Create a very brief summarised name for each submission.

        :param text: The text to summarize.
        :param max_length: Maximum length of the summary name (characters).
        :return: Brief summary name.
        """
        try:
            # Clean the text and truncate if very long.
            cleaned_text = text.strip()
            if not cleaned_text:
                return "Empty Submission"
            
            # Use first 500 characters for analysis to keep prompt size manageable.
            text_sample = cleaned_text[:500]
            
            prompt = f"""
            Create a brief, descriptive title for this text submission (max {max_length} characters).
            The title should capture the main topic and include "Analysis" at the end.

            Guidelines:
            - Focus on the main subject/theme
            - Keep it under {max_length} characters total
            - End with "Analysis" (e.g., "Climate Change Analysis", "Product Review Analysis")
            - Use simple, clear language
            - Avoid quotes, punctuation, or extra formatting

            Text: {text_sample}

            Reply with ONLY the title, nothing else.
            """
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=20,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract and clean the title.
            title = response.content[0].text.strip()  # type: ignore
            title = title.replace('"', '').replace("'", "").strip()
                
            return title
            
        except Exception:
            raise  

    def create_image_submission_name(self, image_path: str, max_length: int = 50) -> str:
        """
        Create a descriptive name for an image submission using Claude's vision capabilities.

        :param image_path: Path to the image file
        :param max_length: Maximum length of the name
        :return: Descriptive name for the submission
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determine media type
            image_format = image_path.lower().split('.')[-1]
            if image_format in ['jpg', 'jpeg']:
                media_type = "image/jpeg"
            elif image_format == 'png':
                media_type = "image/png"
            else:
                media_type = "image/jpeg"

            prompt = f"""
            Create a brief, descriptive title for this image submission (max {max_length} characters).
            The title should describe what you see and end with "Analysis".

            Guidelines:
            - Describe the main subject/scene in the image
            - Keep it under {max_length} characters total
            - End with "Analysis" (e.g., "Portrait Analysis", "Landscape Analysis", "Abstract Art Analysis")
            - Use simple, clear language
            - Focus on the most prominent visual element

            Reply with ONLY the title, nothing else.
            """

            response = self.client.messages.create(
                model=self.model,
                max_tokens=20,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            # Extract and clean the title
            title = response.content[0].text.strip()  # type: ignore
            title = title.replace('"', '').replace("'", "").strip()
            
            # Ensure it's not too long
            if len(title) > max_length:
                title = title[:max_length-3] + "..."

            return title
        
        except Exception as e:
            # Fallback to filename-based name
            filename = os.path.basename(image_path)
            name_without_ext = os.path.splitext(filename)[0]
            return f"{name_without_ext[:max_length-9]} Analysis"