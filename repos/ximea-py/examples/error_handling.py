"""Proper error handling with Xi_error."""

from ximea import Camera, Image, Xi_error

cam = Camera()

try:
    cam.open_device()
    cam.set_exposure(10000)

    img = Image()
    cam.start_acquisition()
    cam.get_image(img)
    data = img.get_image_data_numpy()
    cam.stop_acquisition()
except Xi_error as e:
    print(f"Camera error: {e}")
finally:
    cam.close_device()
