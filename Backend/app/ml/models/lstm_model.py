"""LSTM model for temporal accident detection"""
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AccidentLSTM(nn.Module):
    """LSTM model for temporal sequence analysis"""

    def __init__(self, input_size=3, hidden_size=64, num_layers=2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            dropout=0.3 if num_layers > 1 else 0
        )

        self.fc1 = nn.Linear(hidden_size, 32)
        self.fc2 = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        """Forward pass through LSTM"""
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        x = self.relu(self.fc1(last_output))
        x = self.dropout(x)
        x = self.sigmoid(self.fc2(x))
        return x


class LSTMDetector:
    """LSTM-based accident detector"""

    def __init__(self, model_path=None):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path

        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path):
        """Load trained LSTM model"""
        try:
            model_path = Path(model_path)
            if not model_path.exists():
                raise FileNotFoundError(f"LSTM model not found at {model_path}")

            self.model = AccidentLSTM().to(self.device)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            logger.info(f"LSTM model loaded from {model_path}")
            return True

        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to load LSTM model: {e}")
            raise RuntimeError(f"Failed to load LSTM model: {e}")

    def predict(self, features):
        """
        Predict accident probability from temporal features

        Args:
            features: numpy array of shape (sequence_length, feature_dim)
                     e.g., (150, 3) for 150 frames with 3 features each

        Returns:
            float: Accident probability (0-1)

        Raises:
            RuntimeError: If model is not loaded or prediction fails
        """
        if self.model is None:
            raise RuntimeError("LSTM model not loaded. Cannot make predictions.")

        try:
            # Ensure correct shape
            if len(features.shape) == 2:
                features = features[np.newaxis, :]  # Add batch dimension

            features_tensor = torch.FloatTensor(features).to(self.device)

            with torch.no_grad():
                output = self.model(features_tensor)
                confidence = float(output.squeeze())

            return confidence

        except torch.cuda.OutOfMemoryError:
            logger.warning("GPU OOM during LSTM prediction, falling back to CPU")
            torch.cuda.empty_cache()
            self.device = torch.device('cpu')
            self.model.to(self.device)
            return self.predict(features)
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"LSTM prediction failed: {e}")
        finally:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def predict_sequence(self, features):
        """
        Predict frame-by-frame confidences for temporal aggregation

        Args:
            features: numpy array of shape (sequence_length, feature_dim)

        Returns:
            list: Frame-wise confidence scores

        Raises:
            RuntimeError: If model is not loaded or prediction fails
        """
        if self.model is None:
            raise RuntimeError("LSTM model not loaded. Cannot make sequence predictions.")

        try:
            frame_confidences = []

            # Use sliding window for frame-wise predictions
            window_size = 30  # Use 30 frames context

            for i in range(len(features)):
                start_idx = max(0, i - window_size + 1)
                window = features[start_idx:i+1]

                # Pad if needed
                if len(window) < window_size:
                    padding = np.zeros((window_size - len(window), features.shape[1]))
                    window = np.vstack([padding, window])

                conf = self.predict(window)
                frame_confidences.append(conf)

            return frame_confidences

        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Sequence prediction failed: {e}")
