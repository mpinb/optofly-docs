"""Enable auto exposure/gain and auto white balance."""

from ximea import Camera, Image

cam = Camera()
cam.open_device()

cam.enable_aeag()  # auto exposure / auto gain
cam.enable_auto_wb()  # auto white balance

img = Image()
cam.start_acquisition()
cam.get_image(img)
cam.stop_acquisition()

cam.disable_aeag()
cam.disable_auto_wb()
cam.close_device()
