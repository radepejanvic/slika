def test_crop_basic(backend, test_color_image):
    """Tests that crop returns correct dimensions."""
    result = backend.crop(test_color_image, x=10, y=10, width=50, height=50)
    assert result.shape == (50, 50, 3)

def test_crop_from_origin(backend, test_color_image):
    """Tests crop starting from (0, 0)."""
    result = backend.crop(test_color_image, x=0, y=0, width=50, height=50)
    assert result.shape == (50, 50, 3)

def test_crop_exceeds_width(backend, test_color_image):
    """Tests that crop clamps correctly when width exceeds image bounds."""
    result = backend.crop(test_color_image, x=80, y=0, width=50, height=50)
    assert result.shape[1] == 20  # 80 + 50 = 130, clamped to 100, so width = 20

def test_crop_exceeds_height(backend, test_color_image):
    """Tests that crop clamps correctly when height exceeds image bounds."""
    result = backend.crop(test_color_image, x=0, y=80, width=50, height=50)
    assert result.shape[0] == 20  # 80 + 50 = 130, clamped to 100, so height = 20

def test_crop_grayscale(backend, test_grayscale_image):
    """Tests that crop works correctly on grayscale images."""
    result = backend.crop(test_grayscale_image, x=10, y=10, width=30, height=30)
    assert result.shape == (30, 30)
