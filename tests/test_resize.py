import numpy as np


def test_resize_changes_dimensions(backend, test_image_path):
    """Tests that resize changes image dimensions correctly."""
    img = backend.load(test_image_path)
    result = backend.resize(img, 50, 50)
    assert result.shape == (50, 50, 3)

def test_resize_upscale(backend, test_image_path):
    """Tests that resize can upscale an image."""
    img = backend.load(test_image_path)
    result = backend.resize(img, 200, 200)
    assert result.shape == (200, 200, 3)

def test_resize_non_square(backend, test_image_path):
    """Tests that resize works with non-square dimensions."""
    img = backend.load(test_image_path)
    result = backend.resize(img, 300, 150)
    assert result.shape == (150, 300, 3)

def test_resize_preserves_channels(backend, test_image_path):
    """Tests that resize does not change the number of channels."""
    img = backend.load(test_image_path)
    result = backend.resize(img, 50, 50)
    assert result.shape[2] == img.shape[2]

def test_resize_returns_numpy_array(backend, test_image_path):
    """Tests that resize returns a numpy array."""
    img = backend.load(test_image_path)
    result = backend.resize(img, 50, 50)
    assert isinstance(result, np.ndarray)

def test_resize_grayscale(backend, test_grayscale_image):
    """Tests that resize works correctly on grayscale images."""
    result = backend.resize(test_grayscale_image, 50, 50)
    assert result.shape == (50, 50)
