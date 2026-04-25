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
