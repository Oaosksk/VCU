"""
Diagnostic tool to check what's happening during inference.
Run this to see detailed physics/LSTM scores for any video.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
import logging
from app.services.inference_service import analyze_video_file

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def diagnose_video(video_id: str):
    """Run analysis and show detailed breakdown"""
    print(f"\n{'='*70}")
    print(f"DIAGNOSTIC TEST FOR VIDEO: {video_id}")
    print(f"{'='*70}\n")
    
    try:
        result = await analyze_video_file(video_id, db=None)
        
        print(f"\n{'='*70}")
        print("FINAL RESULT:")
        print(f"{'='*70}")
        print(f"Status: {result['status']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Raw Confidence: {result['details']['rawConfidence']}")
        print(f"Severity: {result['severity']}")
        print(f"Accident Type: {result['accidentType']}")
        print(f"\nReasoning: {result['reasoning']}")
        print(f"\nTemporal Stability: {result['details']['temporalStability']}")
        print(f"Total Vehicles: {result['details']['totalVehicles']}")
        print(f"Frame Count: {result['details']['frameCount']}")
        
        if result['details']['eventFrames']:
            print(f"\nEvent Frames: {result['details']['eventFrames']}")
        
        print(f"\n{'='*70}\n")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnostic_test.py <video_id>")
        print("\nExample: python diagnostic_test.py 12345-abcde-67890")
        sys.exit(1)
    
    video_id = sys.argv[1]
    asyncio.run(diagnose_video(video_id))
