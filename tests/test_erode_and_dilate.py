import numpy as np


def test_erode_reduces_white_region(backend, test_binary_image):
    """Erosion should reduce the white region."""
    result = backend.erode(test_binary_image)
    assert np.sum(result == 255) < np.sum(test_binary_image == 255)

def test_dilate_increases_white_region(backend, test_binary_image):
    """Dilation should increase the white region."""
    result = backend.dilate(test_binary_image)
    assert np.sum(result == 255) > np.sum(test_binary_image == 255)

def test_erode_dilate_default_params(backend, test_binary_image):
    """Tests that erode and dilate work with default parameters."""
    eroded = backend.erode(test_binary_image)
    dilated = backend.dilate(test_binary_image)
    assert eroded is not None
    assert dilated is not None
    assert eroded.shape == test_binary_image.shape
    assert dilated.shape == test_binary_image.shape

def test_erode_more_iterations_reduces_more(backend, test_binary_image):
    """More iterations should erode more of the white region."""
    eroded_1 = backend.erode(test_binary_image, iterations=1)
    eroded_3 = backend.erode(test_binary_image, iterations=3)
    assert np.sum(eroded_3 == 255) < np.sum(eroded_1 == 255)

def test_dilate_more_iterations_increases_more(backend, test_binary_image):
    """More iterations should dilate more of the white region."""
    dilated_1 = backend.dilate(test_binary_image, iterations=1)
    dilated_3 = backend.dilate(test_binary_image, iterations=3)
    assert np.sum(dilated_3 == 255) > np.sum(dilated_1 == 255)

def test_erode_larger_kernel_reduces_more(backend, test_binary_image):
    """Larger kernel should erode more of the white region."""
    eroded_3 = backend.erode(test_binary_image, kernel_size=3)
    eroded_7 = backend.erode(test_binary_image, kernel_size=7)
    assert np.sum(eroded_7 == 255) < np.sum(eroded_3 == 255)

def test_dilate_larger_kernel_increases_more(backend, test_binary_image):
    """Larger kernel should dilate more of the white region."""
    dilated_3 = backend.dilate(test_binary_image, kernel_size=3)
    dilated_7 = backend.dilate(test_binary_image, kernel_size=7)
    assert np.sum(dilated_7 == 255) > np.sum(dilated_3 == 255)

def test_erode_then_dilate_restores_approximately(backend, test_binary_image):
    """Eroding then dilating should approximately restore the original shape."""
    eroded = backend.erode(test_binary_image, iterations=1)
    restored = backend.dilate(eroded, iterations=1)
    diff = np.sum(restored != test_binary_image)
    assert diff < 500
