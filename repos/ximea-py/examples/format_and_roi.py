"""Configure image format, region of interest, exposure, and gain."""

from ximea import Camera, Image

cam = Camera()
cam.open_device()

# Set image format
cam.set_imgdataformat("XI_RGB24")

# Set region of interest
cam.set_width(640)
cam.set_height(480)
cam.set_offsetX(100)
cam.set_offsetY(100)

# Adjust exposure and gain
cam.set_exposure(20000)
cam.set_gain(5.0)

img = Image()
cam.start_acquisition()
cam.get_image(img)
cam.stop_acquisition()

data = img.get_image_data_numpy()  # shape: (480, 640, 3)
cam.close_device()
