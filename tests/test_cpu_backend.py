import pytest
import numpy as np
import cv2
import os
from backend.cpu_backend import OpenCVBackend 

@pytest.fixture
def test_image_path(tmp_path):
    img_path = os.path.join(tmp_path, "test_input.jpg")
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:] = (255, 0, 0)
    cv2.imwrite(img_path, img)
    return img_path

@pytest.fixture
def test_image(tmp_path):
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:] = (255, 0, 0) 
    return img

@pytest.fixture
def test_grayscale_image(tmp_path):
    img = np.zeros((100, 100), dtype=np.uint8)
    img[:50] = 200 
    img[50:] = 50   
    return img

@pytest.fixture
def backend():
    return OpenCVBackend()

def test_load_image(backend, test_image_path):
    """Tests if the backend is loading the image as a NumPy array."""
    img = backend.load(test_image_path)
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert img.shape == (100, 100, 3)

def test_resize_image(backend, test_image):
    """Tests the change of image dimensions."""
    img = test_image
    resized = backend.resize(img, 50, 50)
    assert resized.shape == (50, 50, 3)

def test_color_conversions(backend, test_image):
    """
    Parameterized test for multiple conversions at once.
    Checks if the channel count changes as expected.
    """
    img = test_image
    
    gray = backend.cvt_color(img, 'bgr2gray')
    assert len(gray.shape) == 2
    
    hsv = backend.cvt_color(img, 'bgr2hsv')
    assert hsv.shape == (100, 100, 3)
    assert hsv.dtype == np.uint8

def test_invalid_color_code(backend, test_image):
    """Verifies error handling for invalid conversion codes."""
    img = test_image
    with pytest.raises(ValueError): 
        backend.cvt_color(img, 'TEST_CODE')

def test_save_image(backend, test_image, tmp_path):
    """Verifies that the save function successfully writes the file to the disk."""
    img = test_image
    out_path = os.path.join(tmp_path, "output.jpg")
    backend.save(img, out_path)
    assert os.path.exists(out_path)

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