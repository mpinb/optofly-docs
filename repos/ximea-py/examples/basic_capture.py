"""Basic single image capture."""

from ximea import Camera, Image

cam = Camera()
cam.open_device()

cam.set_exposure(10000)  # microseconds

img = Image()
cam.start_acquisition()
cam.get_image(img)
cam.stop_acquisition()

# Get image as numpy array (requires numpy)
data = img.get_image_data_numpy()

cam.close_device()
