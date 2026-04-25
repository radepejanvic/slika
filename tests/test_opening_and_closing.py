import numpy as np


def test_opening_removes_noise(backend, test_noisy_binary_image):
    """Opening should remove small noise spots outside the main region."""
    result = backend.opening(test_noisy_binary_image)
    assert result[5, 5] == 0
    assert result[90, 90] == 0
    assert result[10, 80] == 0

def test_opening_preserves_main_region(backend, test_noisy_binary_image):
    """Opening should preserve the main white region."""
    result = backend.opening(test_noisy_binary_image)
    assert np.any(result[25:75, 25:75] == 255)

def test_closing_fills_holes(backend, test_binary_image_with_holes):
    """Closing should fill small holes inside the white region."""
    result = backend.closing(test_binary_image_with_holes)
    assert result[40, 40] == 255
    assert result[50, 50] == 255
    assert result[60, 60] == 255

def test_closing_preserves_outer_black_region(backend, test_binary_image_with_holes):
    """Closing should not significantly affect the outer black region."""
    result = backend.closing(test_binary_image_with_holes)
    assert result[0, 0] == 0
    assert result[99, 99] == 0

def test_opening_default_params(backend, test_noisy_binary_image):
    """Tests that opening works with default parameters."""
    result = backend.opening(test_noisy_binary_image)
    assert result is not None
    assert result.shape == test_noisy_binary_image.shape

def test_closing_default_params(backend, test_binary_image_with_holes):
    """Tests that closing works with default parameters."""
    result = backend.closing(test_binary_image_with_holes)
    assert result is not None
    assert result.shape == test_binary_image_with_holes.shape

def test_opening_more_iterations(backend, test_noisy_binary_image):
    """More iterations should reduce the white region further."""
    result_1 = backend.opening(test_noisy_binary_image, iterations=1)
    result_3 = backend.opening(test_noisy_binary_image, iterations=3)
    assert np.sum(result_3 == 255) <= np.sum(result_1 == 255)

def test_closing_more_iterations(backend, test_binary_image_with_holes):
    """More iterations should fill more of the black region."""
    result_1 = backend.closing(test_binary_image_with_holes, iterations=1)
    result_3 = backend.closing(test_binary_image_with_holes, iterations=3)
    assert np.sum(result_3 == 255) >= np.sum(result_1 == 255)

def test_opening_is_erode_then_dilate(backend, test_noisy_binary_image):
    """Opening should be equivalent to erosion followed by dilation."""
    opened = backend.opening(test_noisy_binary_image, kernel_size=3)
    eroded = backend.erode(test_noisy_binary_image, kernel_size=3)
    dilated = backend.dilate(eroded, kernel_size=3)
    assert np.array_equal(opened, dilated)

def test_closing_is_dilate_then_erode(backend, test_binary_image_with_holes):
    """Closing should be equivalent to dilation followed by erosion."""
    closed = backend.closing(test_binary_image_with_holes, kernel_size=3)
    dilated = backend.dilate(test_binary_image_with_holes, kernel_size=3)
    eroded = backend.erode(dilated, kernel_size=3)
    assert np.array_equal(closed, eroded)
