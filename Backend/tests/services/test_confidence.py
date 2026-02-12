"""Tests for Temporal Confidence Aggregation (Novel Component)"""
import pytest
import numpy as np
from app.services.confidence_service import TemporalConfidenceAggregator


@pytest.fixture
def aggregator():
    return TemporalConfidenceAggregator(
        window_size=15,
        spike_threshold=0.3,
        consistency_threshold=0.6
    )


# --- aggregate() ---

class TestAggregate:
    def test_empty_input(self, aggregator):
        result = aggregator.aggregate([])
        assert result['final_confidence'] == 0.0
        assert result['is_accident'] == False

    def test_none_input(self, aggregator):
        result = aggregator.aggregate(None)
        assert result['final_confidence'] == 0.0

    def test_single_frame(self, aggregator):
        result = aggregator.aggregate([0.9])
        assert 0.0 <= result['final_confidence'] <= 1.0

    def test_all_zeros(self, aggregator):
        result = aggregator.aggregate([0.0] * 30)
        assert result['is_accident'] == False
        assert result['final_confidence'] <= 0.3

    def test_all_high(self, aggregator):
        result = aggregator.aggregate([0.95] * 30)
        assert result['is_accident'] == True
        assert result['final_confidence'] > 0.7

    def test_mixed_signals(self, aggregator):
        # Alternating high and low — should NOT be detected as accident
        confs = [0.1, 0.9] * 15
        result = aggregator.aggregate(confs)
        # Consistency should be low due to alternating
        assert result['temporal_stability'] < 0.9

    def test_result_keys_present(self, aggregator):
        result = aggregator.aggregate([0.5] * 20)
        expected_keys = [
            'final_confidence', 'is_accident', 'temporal_stability',
            'spike_filtered', 'event_frames', 'max_confidence',
            'mean_confidence', 'confidence_variance'
        ]
        for key in expected_keys:
            assert key in result

    def test_confidence_clipped(self, aggregator):
        result = aggregator.aggregate([0.99] * 50)
        assert 0.0 <= result['final_confidence'] <= 1.0


# --- Spike Filtering ---

class TestSpikeFiltering:
    def test_no_spikes(self, aggregator):
        confs = np.array([0.1, 0.1, 0.1, 0.1])
        filtered, detected = aggregator._filter_spikes(confs)
        assert detected is False
        np.testing.assert_array_equal(filtered, confs)

    def test_single_spike_detected(self, aggregator):
        confs = np.array([0.1, 0.1, 0.9, 0.1, 0.1])
        filtered, detected = aggregator._filter_spikes(confs)
        assert detected == True
        assert filtered[2] < 0.9  # Spike replaced with neighbor avg

    def test_short_sequence_no_crash(self, aggregator):
        confs = np.array([0.9, 0.1])
        filtered, detected = aggregator._filter_spikes(confs)
        assert detected == False  # Too short to filter

    def test_sustained_high_not_filtered(self, aggregator):
        confs = np.array([0.1, 0.8, 0.85, 0.9, 0.1])
        filtered, detected = aggregator._filter_spikes(confs)
        # Sustained high values should NOT be filtered as spikes
        assert filtered[2] == 0.85


# --- Sliding Window ---

class TestSlidingWindow:
    def test_short_sequence(self, aggregator):
        confs = np.array([0.5, 0.6])
        scores = aggregator._sliding_window_aggregate(confs)
        assert len(scores) == 1  # Single window with mean

    def test_long_sequence(self, aggregator):
        confs = np.array([0.5] * 30)
        scores = aggregator._sliding_window_aggregate(confs)
        assert len(scores) == 30 - 15 + 1  # 16 windows

    def test_values_weighted(self, aggregator):
        # Later values should have more weight
        confs = np.array([0.0] * 14 + [1.0])
        scores = aggregator._sliding_window_aggregate(confs)
        # Weighted avg should be higher than simple avg
        simple_avg = np.mean(confs)
        assert scores[0] > simple_avg


# --- Temporal Consistency ---

class TestTemporalConsistency:
    def test_all_low(self, aggregator):
        confs = np.array([0.1] * 20)
        score = aggregator._check_temporal_consistency(confs)
        assert score < 0.2

    def test_all_high(self, aggregator):
        confs = np.array([0.9] * 20)
        score = aggregator._check_temporal_consistency(confs)
        assert score > 0.8

    def test_empty(self, aggregator):
        score = aggregator._check_temporal_consistency(np.array([]))
        assert score == 0.0

    def test_three_consecutive(self, aggregator):
        confs = np.array([0.1, 0.1, 0.8, 0.8, 0.8, 0.1, 0.1])
        score = aggregator._check_temporal_consistency(confs)
        # Should acknowledge 3 consecutive high frames
        assert score > 0.0


# --- Event Detection ---

class TestEventDetection:
    def test_no_events(self, aggregator):
        confs = np.array([0.1] * 10)
        events = aggregator._detect_event_frames(confs)
        assert events == []

    def test_single_event(self, aggregator):
        confs = np.array([0.1, 0.1, 0.8, 0.9, 0.85, 0.1])
        events = aggregator._detect_event_frames(confs)
        assert len(events) == 1
        assert events[0] == (2, 4)

    def test_multiple_events(self, aggregator):
        confs = np.array([0.9, 0.8, 0.1, 0.1, 0.7, 0.8])
        events = aggregator._detect_event_frames(confs)
        assert len(events) == 2
