"""Discover connected cameras and read device info."""

from ximea import Camera

cam = Camera()
num = cam.get_number_devices()
print(f"Found {num} XIMEA camera(s)")

# Open by device index
cam = Camera(dev_id=0)
cam.open_device()

# Or open by serial number
cam2 = Camera()
cam2.open_device_by_SN("12345678")

print(f"Name: {cam.get_device_name()}")
print(f"Serial: {cam.get_device_sn()}")
print(f"Type: {cam.get_device_type()}")

cam.close_device()
