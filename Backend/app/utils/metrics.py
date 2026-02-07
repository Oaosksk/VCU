"""Metrics calculation for accident detection evaluation"""
import numpy as np
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate evaluation metrics for accident detection"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all counters"""
        self.true_positives = 0
        self.true_negatives = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.inference_times = []
    
    def update(self, y_true: int, y_pred: int, inference_time: float = None):
        """
        Update metrics with single prediction
        
        Args:
            y_true: Ground truth (0=no_accident, 1=accident)
            y_pred: Prediction (0=no_accident, 1=accident)
            inference_time: Time taken for inference (seconds)
        """
        if y_true == 1 and y_pred == 1:
            self.true_positives += 1
        elif y_true == 0 and y_pred == 0:
            self.true_negatives += 1
        elif y_true == 0 and y_pred == 1:
            self.false_positives += 1
        elif y_true == 1 and y_pred == 0:
            self.false_negatives += 1
        
        if inference_time is not None:
            self.inference_times.append(inference_time)
    
    def update_batch(self, y_true: List[int], y_pred: List[int], 
                    inference_times: List[float] = None):
        """
        Update metrics with batch of predictions
        
        Args:
            y_true: List of ground truth labels
            y_pred: List of predictions
            inference_times: List of inference times
        """
        for i, (true, pred) in enumerate(zip(y_true, y_pred)):
            inf_time = inference_times[i] if inference_times else None
            self.update(true, pred, inf_time)
    
    def accuracy(self) -> float:
        """
        Calculate accuracy: (TP + TN) / (TP + TN + FP + FN)
        
        Returns:
            float: Accuracy score (0-1)
        """
        total = self.true_positives + self.true_negatives + self.false_positives + self.false_negatives
        if total == 0:
            return 0.0
        return (self.true_positives + self.true_negatives) / total
    
    def precision(self) -> float:
        """
        Calculate precision: TP / (TP + FP)
        Measures correctness of positive predictions
        
        Returns:
            float: Precision score (0-1)
        """
        denominator = self.true_positives + self.false_positives
        if denominator == 0:
            return 0.0
        return self.true_positives / denominator
    
    def recall(self) -> float:
        """
        Calculate recall: TP / (TP + FN)
        Measures ability to find all positive cases
        
        Returns:
            float: Recall score (0-1)
        """
        denominator = self.true_positives + self.false_negatives
        if denominator == 0:
            return 0.0
        return self.true_positives / denominator
    
    def f1_score(self) -> float:
        """
        Calculate F1-score: 2 * (Precision * Recall) / (Precision + Recall)
        Harmonic mean of precision and recall
        
        Returns:
            float: F1 score (0-1)
        """
        prec = self.precision()
        rec = self.recall()
        
        if prec + rec == 0:
            return 0.0
        
        return 2 * (prec * rec) / (prec + rec)
    
    def avg_inference_time(self) -> float:
        """
        Calculate average inference time
        
        Returns:
            float: Average time in seconds
        """
        if not self.inference_times:
            return 0.0
        return np.mean(self.inference_times)
    
    def get_all_metrics(self) -> Dict[str, float]:
        """
        Get all metrics as dictionary
        
        Returns:
            dict: All calculated metrics
        """
        return {
            'accuracy': self.accuracy(),
            'precision': self.precision(),
            'recall': self.recall(),
            'f1_score': self.f1_score(),
            'avg_inference_time': self.avg_inference_time(),
            'true_positives': self.true_positives,
            'true_negatives': self.true_negatives,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives,
            'total_samples': (self.true_positives + self.true_negatives + 
                            self.false_positives + self.false_negatives)
        }
    
    def print_metrics(self):
        """Print formatted metrics"""
        metrics = self.get_all_metrics()
        
        print("\n" + "="*60)
        print("EVALUATION METRICS")
        print("="*60)
        print(f"Accuracy:           {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
        print(f"Precision:          {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
        print(f"Recall:             {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
        print(f"F1-Score:           {metrics['f1_score']:.4f} ({metrics['f1_score']*100:.2f}%)")
        print(f"Avg Inference Time: {metrics['avg_inference_time']:.4f}s")
        print("-"*60)
        print(f"True Positives:     {metrics['true_positives']}")
        print(f"True Negatives:     {metrics['true_negatives']}")
        print(f"False Positives:    {metrics['false_positives']}")
        print(f"False Negatives:    {metrics['false_negatives']}")
        print(f"Total Samples:      {metrics['total_samples']}")
        print("="*60 + "\n")
    
    def confusion_matrix(self) -> np.ndarray:
        """
        Get confusion matrix
        
        Returns:
            numpy array: [[TN, FP], [FN, TP]]
        """
        return np.array([
            [self.true_negatives, self.false_positives],
            [self.false_negatives, self.true_positives]
        ])


def calculate_metrics_from_predictions(y_true: List[int], y_pred: List[int], 
                                      inference_times: List[float] = None) -> Dict[str, float]:
    """
    Convenience function to calculate metrics from predictions
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        inference_times: Optional inference times
    
    Returns:
        dict: All metrics
    """
    calculator = MetricsCalculator()
    calculator.update_batch(y_true, y_pred, inference_times)
    return calculator.get_all_metrics()
