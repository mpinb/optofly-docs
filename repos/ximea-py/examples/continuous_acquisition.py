"""Capture frames in a continuous loop."""

from ximea import Camera, Image

cam = Camera()
cam.open_device()
cam.set_exposure(10000)
cam.set_imgdataformat("XI_MONO8")

img = Image()
cam.start_acquisition()

for i in range(100):
    cam.get_image(img, timeout=5000)
    data = img.get_image_data_numpy()
    print(f"Frame {img.nframe}: {data.shape}, mean={data.mean():.1f}")

cam.stop_acquisition()
cam.close_device()
