"""Read the camera sensor temperature."""

from ximea import Camera

cam = Camera()
cam.open_device()

temp = cam.get_temp()
print(f"Sensor temperature: {temp:.1f} C")

cam.close_device()
