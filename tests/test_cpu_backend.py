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
def backend():
    return OpenCVBackend()

def test_load_image(backend, test_image_path):
    """Tests if the backend is loading the image as a NumPy array."""
    img = backend.load(test_image_path)
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert img.shape == (100, 100, 3)

def test_resize_image(backend, test_image_path):
    """Tests the change of image dimensions."""
    img = backend.load(test_image_path)
    resized = backend.resize(img, 50, 50)
    assert resized.shape == (50, 50, 3)

def test_color_conversions(backend, test_image_path):
    """
    Parameterized test for multiple conversions at once.
    Checks if the channel count changes as expected.
    """
    img = backend.load(test_image_path)
    
    gray = backend.cvt_color(img, 'bgr2gray')
    assert len(gray.shape) == 2
    
    hsv = backend.cvt_color(img, 'bgr2hsv')
    assert hsv.shape == (100, 100, 3)
    assert hsv.dtype == np.uint8

def test_invalid_color_code(backend, test_image_path):
    """Verifies error handling for invalid conversion codes."""
    img = backend.load(test_image_path)
    with pytest.raises(ValueError): 
        backend.cvt_color(img, 'TEST_CODE')

def test_save_image(backend, test_image_path, tmp_path):
    """Verifies that the save function successfully writes the file to the disk."""
    img = backend.load(test_image_path)
    out_path = os.path.join(tmp_path, "output.jpg")
    backend.save(img, out_path)
    assert os.path.exists(out_path)