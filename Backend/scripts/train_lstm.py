"""
Retrain LSTM with:
 - Weighted BCE loss for class imbalance
 - Focal loss option for harder samples
 - Auto class weight calculation
 - Early stopping
 - Learning rate scheduling
"""
import numpy as np
import pickle
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from sklearn.model_selection import StratifiedKFold
from pathlib import Path
from datetime import datetime
import sys
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.ml.models.lstm_model import AccidentLSTM


class VideoDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)

    def __len__(self): return len(self.X)
    def __getitem__(self, idx): return self.X[idx], self.y[idx]


class FocalBCELoss(nn.Module):
    """
    Focal Loss for binary classification.
    Down-weights easy examples, focuses on hard ones.
    Good for imbalanced datasets.
    """
    def __init__(self, alpha=0.25, gamma=2.0, pos_weight=None):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.pos_weight = pos_weight

    def forward(self, pred, target):
        bce = nn.functional.binary_cross_entropy(pred, target, reduction='none')
        pt = torch.exp(-bce)
        focal_weight = self.alpha * (1 - pt) ** self.gamma
        if self.pos_weight is not None:
            # Per-sample weight based on class
            w = torch.where(target == 1, self.pos_weight, torch.ones_like(target))
            focal_weight = focal_weight * w
        return (focal_weight * bce).mean()


def train_model(features_file, output_model, epochs=100, batch_size=16, lr=0.0005):
    print(f"\n{'='*60}")
    print(f"  LSTM Accident Detector — Balanced Retraining")
    print(f"{'='*60}\n")

    # ── Load features ──────────────────────────────────────────────
    print(f"Loading features from {features_file}...")
    with open(features_file, 'rb') as f:
        data = pickle.load(f)
        X = data['X']
        y = data['y']

    print(f"Dataset: X={X.shape}  y={y.shape}")
    n_accident  = int(np.sum(y == 1))
    n_normal    = int(np.sum(y == 0))
    print(f"  Accident (y=1): {n_accident}")
    print(f"  Normal   (y=0): {n_normal}")
    print(f"  Ratio:          {n_accident/max(n_normal,1):.1f}:1")

    if len(X) < 10:
        print(f"\nERROR: Need at least 10 videos. Have {len(X)}.")
        print("Run: python scripts/create_normal_clips.py  first")
        return

    # ── Class weights for imbalance ────────────────────────────────
    # If 150 accident : 6 normal → pos_weight = 6/150 ≈ 0.04 (deweight accident per sample)
    # Inverse-frequency weighting
    total = len(y)
    w_accident = total / (2.0 * n_accident) if n_accident > 0 else 1.0
    w_normal   = total / (2.0 * n_normal)   if n_normal  > 0 else 1.0
    pos_weight = torch.tensor([w_accident / w_normal], dtype=torch.float32)
    print(f"\nClass weights: accident={w_accident:.3f}  normal={w_normal:.3f}")
    print(f"pos_weight for BCELoss: {pos_weight.item():.4f}")

    # ── Weighted sampler so each batch has balanced classes ─────────
    sample_weights = np.where(y == 1, w_accident, w_normal)
    sampler = WeightedRandomSampler(
        weights=torch.FloatTensor(sample_weights),
        num_samples=len(sample_weights),
        replacement=True
    )

    # ── Train/Val split preserving class ratio ─────────────────────
    # With very few normal samples, use 90/10 split
    np.random.seed(42)
    indices = np.arange(len(X))
    accident_idx = indices[y == 1]
    normal_idx   = indices[y == 0]

    val_n_acc  = max(1, int(0.1 * len(accident_idx)))
    val_n_norm = max(1, int(0.1 * len(normal_idx))) if len(normal_idx) >= 5 else 1

    val_idx   = np.concatenate([
        np.random.choice(accident_idx, val_n_acc,  replace=False),
        np.random.choice(normal_idx,   val_n_norm, replace=False),
    ])
    train_idx = np.setdiff1d(indices, val_idx)

    X_train, y_train = X[train_idx], y[train_idx]
    X_val,   y_val   = X[val_idx],   y[val_idx]

    print(f"\nTrain: {len(X_train)} samples  (acc={int(np.sum(y_train==1))}, norm={int(np.sum(y_train==0))})")
    print(f"Val:   {len(X_val)}  samples  (acc={int(np.sum(y_val==1))}, norm={int(np.sum(y_val==0))})")

    # ── Setup ──────────────────────────────────────────────────────
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")

    model     = AccidentLSTM().to(device)
    criterion = FocalBCELoss(alpha=0.25, gamma=2.0, pos_weight=pos_weight.to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    train_weights = np.where(y_train == 1, w_accident, w_normal)
    train_sampler = WeightedRandomSampler(torch.FloatTensor(train_weights), len(train_weights), replacement=True)

    train_loader = DataLoader(VideoDataset(X_train, y_train), batch_size=batch_size, sampler=train_sampler)
    val_loader   = DataLoader(VideoDataset(X_val,   y_val),   batch_size=batch_size, shuffle=False)

    # ── Training loop ──────────────────────────────────────────────
    print(f"\nTraining for {epochs} epochs...")
    print(f"{'='*60}")

    best_val_acc = 0.0
    best_epoch   = 0
    patience     = 20
    no_improve   = 0

    for epoch in range(epochs):
        # Train
        model.train()
        train_loss = 0.0
        for Xb, yb in train_loader:
            Xb = Xb.to(device)
            yb = yb.to(device).unsqueeze(1)
            optimizer.zero_grad()
            out  = model(Xb)
            loss = criterion(out, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            train_loss += loss.item()

        scheduler.step()

        # Validate
        model.eval()
        val_correct = val_total = 0
        val_tp = val_fp = val_fn = val_tn = 0

        with torch.no_grad():
            for Xb, yb in val_loader:
                Xb = Xb.to(device)
                out  = model(Xb).squeeze()
                pred = (out > 0.5).float().cpu()
                yb   = yb.cpu()
                val_correct += (pred == yb).sum().item()
                val_total   += yb.size(0)
                val_tp += ((pred == 1) & (yb == 1)).sum().item()
                val_fp += ((pred == 1) & (yb == 0)).sum().item()
                val_fn += ((pred == 0) & (yb == 1)).sum().item()
                val_tn += ((pred == 0) & (yb == 0)).sum().item()

        val_acc      = val_correct / max(val_total, 1)
        avg_loss     = train_loss / max(len(train_loader), 1)
        lr_now       = scheduler.get_last_lr()[0]

        # Print every 5 epochs
        if (epoch + 1) % 5 == 0 or epoch == 0:
            prec = val_tp / max(val_tp + val_fp, 1)
            rec  = val_tp / max(val_tp + val_fn, 1)
            f1   = 2 * prec * rec / max(prec + rec, 1e-6)
            print(f"Epoch {epoch+1:3d}/{epochs}  loss={avg_loss:.4f}  val_acc={val_acc:.3f}"
                  f"  F1={f1:.3f}  TP={val_tp} FP={val_fp} FN={val_fn} TN={val_tn}  lr={lr_now:.6f}", end='')

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch   = epoch + 1
            output_path  = Path(output_model)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), output_model)
            if (epoch + 1) % 5 == 0 or epoch == 0:
                print('  [SAVED]')
            no_improve = 0
        else:
            if (epoch + 1) % 5 == 0 or epoch == 0:
                print()
            no_improve += 1

        # Early stopping
        if no_improve >= patience:
            print(f"\nEarly stopping at epoch {epoch+1} (no improvement for {patience} epochs)")
            break

    print(f"\n{'='*60}")
    print(f"Training complete!")
    print(f"Best val accuracy: {best_val_acc:.4f} at epoch {best_epoch}")
    print(f"Model saved to: {output_model}")
    print(f"{'='*60}")

    # ── Quick sanity check on trained model ───────────────────────
    print("\n=== SANITY CHECK ===")
    # Load into a fresh CPU model (avoids device mismatch)
    check_model = AccidentLSTM().cpu()
    check_model.load_state_dict(torch.load(output_model, map_location='cpu', weights_only=True))
    check_model.eval()

    for label, idxs in [("Accident (y=1)", accident_idx[:5]), ("Normal   (y=0)", normal_idx[:5])]:
        preds = []
        for i in idxs:
            inp = torch.FloatTensor(X[i]).unsqueeze(0)  # CPU tensor
            with torch.no_grad():
                out = check_model(inp)
            preds.append(float(out.squeeze()))
        avg = np.mean(preds) if preds else 0
        status = "✓ OK" if (avg > 0.5) == label.startswith('A') else "✗ CHECK"
        print(f"  {label}: mean_pred={avg:.4f}  {status}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train balanced LSTM for accident detection")
    parser.add_argument('--features', default='features.pkl',                              help='Features pickle file')
    parser.add_argument('--output',   default='storage/models/lstm_crash_detector.pth',   help='Model output path')
    parser.add_argument('--epochs',   type=int,   default=100,   help='Max epochs (early stop may cut short)')
    parser.add_argument('--batch',    type=int,   default=16,    help='Batch size')
    parser.add_argument('--lr',       type=float, default=0.0005, help='Learning rate')
    args = parser.parse_args()

    train_model(args.features, args.output, args.epochs, args.batch, args.lr)
