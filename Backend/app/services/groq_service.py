"""Groq AI service for generating explanations"""
from groq import Groq
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqService:
    """Service for generating AI explanations using Groq"""
    
    def __init__(self):
        if settings.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None
        else:
            logger.warning("GROQ_API_KEY not set, using fallback explanations")
            self.client = None
    
    def generate_explanation(self, result: dict) -> str:
        """Generate explanation for analysis result"""
        if not self.client:
            logger.info("Using fallback explanation (Groq unavailable)")
            return self._fallback_explanation(result)
        
        try:
            logger.info(f"Generating explanation for result: {result.get('id')}")
            prompt = self._build_prompt(result)
            
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI expert in vehicle accident detection systems. Explain analysis results in a clear, technical manner."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            explanation = response.choices[0].message.content
            logger.info("Explanation generated successfully")
            return explanation
        
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}", exc_info=True)
            logger.info("Falling back to default explanation")
            return self._fallback_explanation(result)
    
    def _build_prompt(self, result: dict) -> str:
        """Build prompt for Groq"""
        status = result.get("status", "unknown")
        confidence = result.get("confidence", 0)
        details = result.get("details", {})
        
        prompt = f"""Analyze this vehicle accident detection result:

Status: {status}
Confidence: {confidence:.2%}
Spatial Features: {details.get('spatialFeatures', 'N/A')}
Temporal Features: {details.get('temporalFeatures', 'N/A')}
Frames Analyzed: {details.get('frameCount', 'N/A')}
Duration: {details.get('duration', 'N/A')}

Provide a detailed explanation covering:
1. Spatial Analysis - What the model detected in the video frames
2. Temporal Analysis - Movement patterns and sequences observed
3. Model Architecture - Brief explanation of YOLOv8 + LSTM approach
4. Confidence Score - What the {confidence:.2%} confidence means

Keep it technical but accessible. Use markdown formatting with headers."""
        
        return prompt
    
    def _fallback_explanation(self, result: dict) -> str:
        """Fallback explanation when Groq is unavailable"""
        status = result.get("status", "unknown")
        confidence = result.get("confidence", 0)
        details = result.get("details", {})
        
        return f"""# Analysis Explanation

## Overview
Based on the spatio-temporal analysis, our model detected: **{status}** with {confidence:.2%} confidence.

## Spatial Analysis
The YOLOv8 object detection model analyzed individual frames to identify vehicles, their positions, and spatial relationships.

**Detected Features:** {details.get('spatialFeatures', 'N/A')}

## Temporal Analysis
The system processed frame sequences to understand movement patterns over time.

**Observed Patterns:** {details.get('temporalFeatures', 'N/A')}

## Model Architecture
Our hybrid approach combines:
- **YOLOv8**: Real-time object detection for spatial features
- **Pattern Analysis**: Heuristic-based temporal analysis
- **Confidence Aggregation**: Combines both analyses for final prediction

## Analysis Details
- **Frames Analyzed:** {details.get('frameCount', 'N/A')}
- **Video Duration:** {details.get('duration', 'N/A')}
- **Confidence Score:** {confidence:.2%}

The confidence score represents the model's certainty in this classification, derived from spatial and temporal feature analysis."""


# Global instance
groq_service = GroqService()
