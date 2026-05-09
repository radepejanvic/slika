import numpy as np
import os


def test_load_image(backend, test_image_path):
    """Tests if the backend is loading the image as a NumPy array."""
    img = backend.load(test_image_path)
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert img.shape == (100, 100, 3)

def test_save_image(backend, test_image, tmp_path):
    """Verifies that the save function successfully writes the file to the disk."""
    img = test_image
    out_path = os.path.join(tmp_path, "output.jpg")
    backend.save(img, out_path)
    assert os.path.exists(out_path)
