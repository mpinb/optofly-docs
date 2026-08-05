"""Capture an image using an external hardware trigger."""

from ximea import Camera, Image

cam = Camera()
cam.open_device()
cam.set_exposure(10000)

# Configure external trigger
cam.set_trigger_source("XI_TRG_EDGE_RISING")

img = Image()
cam.start_acquisition()

# Blocks until trigger signal is received
cam.get_image(img, timeout=10000)
data = img.get_image_data_numpy()

cam.stop_acquisition()
cam.close_device()
