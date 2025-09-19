import anthropic
from typing import Dict, Any, List, Optional
import json
import os
from dataclasses import dataclass

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
        prompt = self.build_analysis_prompt(text, base_prediction)

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
            return self.fallback_analysis(str(e))
        
    def build_analysis_prompt(self, text:str, base_prediction: Dict[str, Any]):
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
            return self.fallback_analysis(f"JSON parsing error: {str(e)}")
        
    def fallback_analysis(self, error_message: str) -> Dict[str, Any]:
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

    def create_submission_name(self, text: str, max_length: int = 20):
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