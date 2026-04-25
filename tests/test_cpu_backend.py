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
    img[:50] = 200  # one half white
    img[50:] = 50  # other half black
    return img

@pytest.fixture
def test_binary_image():
    img = np.zeros((100, 100), dtype=np.uint8)
    img[25:75, 25:75] = 255  # white square in the middle
    return img

@pytest.fixture
def test_noisy_binary_image():
    """Binary image with small noise spots outside the main region."""
    img = np.zeros((100, 100), dtype=np.uint8)
    img[25:75, 25:75] = 255  # white square in the middle
    img[5, 5] = 255           # small noise spot outside the main region
    img[90, 90] = 255         # small noise spot outside the main region
    img[10, 80] = 255         # small noise spot outside the main region
    return img


@pytest.fixture
def test_binary_image_with_holes():
    """Binary image with small black holes inside the main region."""
    img = np.zeros((100, 100), dtype=np.uint8)
    img[25:75, 25:75] = 255  # white square in the middle
    img[40, 40] = 0           # small hole inside the main region
    img[50, 50] = 0           # small hole inside the main region
    img[60, 60] = 0           # small hole inside the main region
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