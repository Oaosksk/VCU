"""Train LSTM model for accident detection"""
import numpy as np
import pickle
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class VideoDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class AccidentLSTM(nn.Module):
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


def train_model(features_file, output_model, epochs=50, batch_size=16, lr=0.001):
    """Train LSTM model"""
    
    # Load features
    print(f"Loading features from {features_file}...")
    with open(features_file, 'rb') as f:
        data = pickle.load(f)
        X = data['X']
        y = data['y']
    
    print(f"Dataset: {X.shape}, Labels: {y.shape}")
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")
    
    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = AccidentLSTM().to(device)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    train_dataset = VideoDataset(X_train, y_train)
    test_dataset = VideoDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    # Train
    print(f"\nTraining for {epochs} epochs...")
    print("="*60)
    
    best_acc = 0
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        
        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device).unsqueeze(1)
            
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        # Evaluate
        model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for X_batch, y_batch in test_loader:
                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device)
                
                outputs = model(X_batch).squeeze()
                predicted = (outputs > 0.5).float()
                
                total += y_batch.size(0)
                correct += (predicted == y_batch).sum().item()
        
        accuracy = correct / total
        avg_loss = train_loss / len(train_loader)
        
        print(f"Epoch {epoch+1:3d}/{epochs} | Loss: {avg_loss:.4f} | Acc: {accuracy:.4f}", end='')
        
        # Save best model
        if accuracy > best_acc:
            best_acc = accuracy
            
            # Create directory if needed
            output_path = Path(output_model)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            torch.save(model.state_dict(), output_model)
            print(f" ✓ Best model saved!")
        else:
            print()
    
    print("="*60)
    print(f"\nTraining complete!")
    print(f"Best accuracy: {best_acc:.4f}")
    print(f"Model saved to: {output_model}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--features', default='features.pkl', help='Features file')
    parser.add_argument('--output', default='storage/models/lstm_crash_detector.pth', help='Output model')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    args = parser.parse_args()
    
    train_model(args.features, args.output, args.epochs, args.batch_size, args.lr)
