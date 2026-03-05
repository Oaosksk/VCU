"""Inference script - Load model from database and run predictions"""
import torch
import torch.nn as nn
import numpy as np
import time
from pathlib import Path
from scripts.config import LOAD_FROM
from scripts.db_utils import load_model_from_db, log_inference


class AccidentLSTM(nn.Module):
    """LSTM model architecture (must match training)"""
    def __init__(self, input_size=3, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=0.3)
        self.fc1 = nn.Linear(hidden_size, 32)
        self.fc2 = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        x = self.relu(self.fc1(last_output))
        x = self.dropout(x)
        x = self.sigmoid(self.fc2(x))
        return x


def load_model(model_name='lstm_crash_detector', model_version='1.0', filesystem_path=None):
    """Load model based on LOAD_FROM config"""
    
    if LOAD_FROM == "db":
        print(f"Loading model from database: {model_name} v{model_version}")
        
        # Load from database
        model_data = load_model_from_db(model_name, model_version)
        
        # Reconstruct model
        arch = model_data['architecture']
        model = AccidentLSTM(
            input_size=arch['input_size'],
            hidden_size=arch['hidden_size'],
            num_layers=arch['num_layers']
        )
        
        # Load weights from binary data
        import io
        buffer = io.BytesIO(model_data['model_data'])
        state_dict = torch.load(buffer, map_location='cpu')
        model.load_state_dict(state_dict)
        
        print(f"✅ Model loaded from database (ID: {model_data['model_id']})")
        
        return {
            'model': model,
            'model_id': model_data['model_id'],
            'labels': model_data['labels'],
            'preprocessing': model_data.get('preprocessing', {})
        }
    
    elif LOAD_FROM == "filesystem":
        print(f"Loading model from filesystem: {filesystem_path}")
        
        if not filesystem_path or not Path(filesystem_path).exists():
            raise FileNotFoundError(f"Model file not found: {filesystem_path}")
        
        # Load from file
        model = AccidentLSTM()
        model.load_state_dict(torch.load(filesystem_path, map_location='cpu'))
        
        print(f"✅ Model loaded from filesystem")
        
        return {
            'model': model,
            'model_id': None,
            'labels': {0: 'no_accident', 1: 'accident'},
            'preprocessing': {}
        }
    
    else:
        raise ValueError(f"Invalid LOAD_FROM config: {LOAD_FROM}. Use 'db' or 'filesystem'")


def predict(model_dict, input_features):
    """Run prediction on input features"""
    
    model = model_dict['model']
    model.eval()
    
    # Convert to tensor
    if isinstance(input_features, np.ndarray):
        input_tensor = torch.FloatTensor(input_features)
    else:
        input_tensor = torch.FloatTensor(np.array(input_features))
    
    # Add batch dimension if needed
    if len(input_tensor.shape) == 2:
        input_tensor = input_tensor.unsqueeze(0)
    
    # Inference
    start_time = time.time()
    
    with torch.no_grad():
        output = model(input_tensor)
        confidence = output.item()
        predicted_class = 1 if confidence > 0.5 else 0
    
    inference_time_ms = (time.time() - start_time) * 1000
    
    # Get label
    labels = model_dict['labels']
    prediction_label = labels.get(predicted_class, f"class_{predicted_class}")
    
    # Log to database if loaded from DB
    if model_dict['model_id'] is not None:
        try:
            log_inference(
                model_id=model_dict['model_id'],
                input_data={'shape': list(input_tensor.shape), 'sample': input_features[:5].tolist() if len(input_features) > 5 else input_features.tolist()},
                prediction=prediction_label,
                confidence=float(confidence),
                inference_time_ms=inference_time_ms
            )
        except Exception as e:
            print(f"⚠️  Warning: Could not log inference: {e}")
    
    return {
        'prediction': prediction_label,
        'class_index': predicted_class,
        'confidence': confidence,
        'inference_time_ms': inference_time_ms
    }


def main():
    """Example usage"""
    print("="*60)
    print("LSTM Accident Detection - Inference from Database")
    print("="*60)
    
    # Load model
    try:
        model_dict = load_model(
            model_name='lstm_crash_detector',
            model_version='1.0',
            filesystem_path='storage/models/lstm_crash_detector.pth'
        )
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Example input (150 frames x 3 features)
    print("\nGenerating sample input...")
    sample_input = np.random.rand(150, 3).astype(np.float32)
    
    # Run prediction
    print("Running inference...")
    result = predict(model_dict, sample_input)
    
    # Display results
    print("\n" + "="*60)
    print("PREDICTION RESULTS")
    print("="*60)
    print(f"Prediction:      {result['prediction']}")
    print(f"Class Index:     {result['class_index']}")
    print(f"Confidence:      {result['confidence']:.4f}")
    print(f"Inference Time:  {result['inference_time_ms']:.2f} ms")
    print("="*60)
    
    # Instructions
    print("\n📝 USAGE:")
    print("  from scripts.inference_from_db import load_model, predict")
    print("  model_dict = load_model('lstm_crash_detector', '1.0')")
    print("  result = predict(model_dict, your_features)")
    print("\n💡 TIP: Change LOAD_FROM in config.py to switch between 'db' and 'filesystem'")


if __name__ == "__main__":
    main()
