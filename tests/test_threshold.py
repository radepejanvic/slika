import numpy as np
import cv2
import pytest


def test_threshold_binary(backend, test_grayscale_image):
    """Tests basic binary threshold on grayscale image."""
    img = test_grayscale_image
    result = backend.threshold(img, value=127)
    assert result is not None
    assert isinstance(result, np.ndarray)
    assert result.shape == img.shape
    unique_values = np.unique(result)
    assert all(v in [0, 255] for v in unique_values)

def test_threshold_binary_inv(backend, test_grayscale_image):
    """Tests that binary and binary_inv produce inverted results."""
    img = test_grayscale_image
    binary = backend.threshold(img, value=127, type='binary')
    binary_inv = backend.threshold(img, value=127, type='binary_inv')
    assert np.array_equal(binary, cv2.bitwise_not(binary_inv))

def test_threshold_custom_max_value(backend, test_grayscale_image):
    """Tests that max_value parameter is respected."""
    img = test_grayscale_image
    result = backend.threshold(img, value=127, max_value=128, type='binary')
    unique_values = np.unique(result)
    assert all(v in [0, 128] for v in unique_values)

def test_threshold_invalid_type(backend, test_grayscale_image):
    """Verifies error handling for invalid threshold type."""
    img = test_grayscale_image
    with pytest.raises(ValueError):
        backend.threshold(img, value=127, type='INVALID_TYPE')

def test_threshold_requires_grayscale(backend, test_image):
    """Verifies that threshold raises error on non-grayscale image."""
    img = test_image
    with pytest.raises(ValueError):
        backend.threshold(img, value=127)

def test_threshold_all_types(backend, test_grayscale_image):
    """Tests that all valid threshold types execute without error."""
    img = test_grayscale_image
    for t in ['binary', 'binary_inv', 'trunc', 'tozero', 'tozero_inv']:
        result = backend.threshold(img, value=127, type=t)
        assert result is not None
        