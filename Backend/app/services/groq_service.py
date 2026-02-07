"""Groq AI service for generating explanations"""
from groq import Groq
from app.core.config import settings


class GroqService:
    """Service for generating AI explanations using Groq"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
    
    def generate_explanation(self, result: dict) -> str:
        """Generate explanation for analysis result"""
        if not self.client:
            return self._fallback_explanation(result)
        
        try:
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
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Groq API error: {e}")
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
        
        return f"""# Analysis Explanation

## Overview
Based on the spatio-temporal analysis, our model detected: **{status}** with {confidence:.2%} confidence.

## Spatial Analysis
The YOLOv8 object detection model analyzed individual frames to identify vehicles, their positions, and spatial relationships. Key spatial features include vehicle trajectories, collision patterns, and environmental context.

## Temporal Analysis
The LSTM network processed frame sequences to understand movement patterns over time. This includes velocity changes, sudden decelerations, and behavioral anomalies that indicate potential accidents.

## Model Architecture
Our hybrid approach combines:
- **YOLOv8**: Real-time object detection for spatial features
- **LSTM**: Sequential analysis for temporal patterns
- **Confidence Aggregation**: Combines both analyses for final prediction

## Confidence Score
The {confidence:.2%} confidence score represents the model's certainty in this classification, derived from both spatial and temporal feature analysis."""


# Global instance
groq_service = GroqService()
