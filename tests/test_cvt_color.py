import numpy as np
import pytest


def test_cvt_color_bgr2gray(backend, test_image_path):
    """Tests BGR to grayscale conversion produces single channel image."""
    img = backend.load(test_image_path)
    result = backend.cvt_color(img, 'bgr2gray')
    assert len(result.shape) == 2

def test_cvt_color_bgr2rgb(backend, test_image_path):
    """Tests BGR to RGB conversion preserves shape."""
    img = backend.load(test_image_path)
    result = backend.cvt_color(img, 'bgr2rgb')
    assert result.shape == img.shape

def test_cvt_color_bgr2rgb_swaps_channels(backend, test_image_path):
    """Tests that BGR to RGB conversion correctly swaps channels."""
    img = backend.load(test_image_path)
    result = backend.cvt_color(img, 'bgr2rgb')
    assert np.array_equal(result[:, :, 0], img[:, :, 2])
    assert np.array_equal(result[:, :, 2], img[:, :, 0])

def test_cvt_color_gray2bgr(backend, test_grayscale_image):
    """Tests grayscale to BGR conversion produces 3 channel image."""
    result = backend.cvt_color(test_grayscale_image, 'gray2bgr')
    assert len(result.shape) == 3
    assert result.shape[2] == 3

def test_cvt_color_bgr2hsv(backend, test_image_path):
    """Tests BGR to HSV conversion preserves shape and dtype."""
    img = backend.load(test_image_path)
    result = backend.cvt_color(img, 'bgr2hsv')
    assert result.shape == img.shape
    assert result.dtype == np.uint8

def test_cvt_color_bgr2hls(backend, test_image_path):
    """Tests BGR to HLS conversion preserves shape and dtype."""
    img = backend.load(test_image_path)
    result = backend.cvt_color(img, 'bgr2hls')
    assert result.shape == img.shape
    assert result.dtype == np.uint8

def test_cvt_color_bgr2lab(backend, test_image_path):
    """Tests BGR to LAB conversion preserves shape."""
    img = backend.load(test_image_path)
    result = backend.cvt_color(img, 'bgr2lab')
    assert result.shape == img.shape

def test_cvt_color_bgr2luv(backend, test_image_path):
    """Tests BGR to LUV conversion preserves shape."""
    img = backend.load(test_image_path)
    result = backend.cvt_color(img, 'bgr2luv')
    assert result.shape == img.shape

def test_cvt_color_roundtrip_bgr_rgb(backend, test_image_path):
    """Tests that BGR->RGB->BGR roundtrip preserves the original image."""
    img = backend.load(test_image_path)
    rgb = backend.cvt_color(img, 'bgr2rgb')
    result = backend.cvt_color(rgb, 'rgb2bgr')
    assert np.array_equal(result, img)

def test_cvt_color_roundtrip_bgr_hsv(backend, test_image_path):
    """Tests that BGR->HSV->BGR roundtrip approximately preserves the original image."""
    img = backend.load(test_image_path)
    hsv = backend.cvt_color(img, 'bgr2hsv')
    result = backend.cvt_color(hsv, 'hsv2bgr')
    assert np.allclose(result, img, atol=1)

def test_cvt_color_invalid_code(backend, test_image_path):
    """Tests that invalid color code raises ValueError."""
    img = backend.load(test_image_path)
    with pytest.raises(ValueError):
        backend.cvt_color(img, 'INVALID_CODE')

def test_cvt_color_all_three_channel_codes(backend, test_image_path):
    """Tests that all three channel conversion codes execute without error."""
    img = backend.load(test_image_path)
    three_channel_codes = [
        'bgr2rgb', 'rgb2bgr', 'bgr2hsv', 'bgr2hls', 'bgr2lab', 'bgr2luv'
    ]
    for code in three_channel_codes:
        result = backend.cvt_color(img, code)
        assert result is not None
        assert result.shape == img.shape
