"""Benchmark maximum framerate with a circular buffer."""

import argparse
import ctypes
import time

import numpy as np

from ximea import Camera, Image


def run_benchmark(
    num_frames: int,
    buffer_size: int,
    exposure_us: int,
    roi_size: tuple[int, int] | None,
) -> None:
    with Camera() as cam:
        cam.set_imgdataformat("XI_MONO8")
        cam.set_exposure(exposure_us)
        cam.set_acq_timing_mode("XI_ACQ_TIMING_MODE_FREE_RUN")

        # set ROI to center crop if specified
        if roi_size is not None:
            roi_w, roi_h = roi_size
            sensor_w = cam.get_width_maximum()
            sensor_h = cam.get_height_maximum()
            cam.set_width(roi_w)
            cam.set_height(roi_h)
            off_x = (sensor_w - roi_w) // 2
            off_y = (sensor_h - roi_h) // 2
            inc_x = cam.get_offsetX_increment()
            inc_y = cam.get_offsetY_increment()
            cam.set_offsetX(off_x // inc_x * inc_x)
            cam.set_offsetY(off_y // inc_y * inc_y)

        width = cam.get_width()
        height = cam.get_height()
        print(f"Resolution: {width}x{height}")
        print(f"Exposure: {exposure_us} us")
        print(f"Buffer size: {buffer_size} frames")
        print(f"Capturing {num_frames} frames...\n")

        frame_bytes = width * height
        ring_buffer = np.empty((buffer_size, height, width), dtype=np.uint8)
        buf_idx = 0
        img = Image()
        dropped = 0
        prev_nframe = None

        cam.start_acquisition()
        t_start = time.perf_counter()

        for i in range(num_frames):
            cam.get_image(img, timeout=5000)

            # fast copy: memmove straight into pre-allocated numpy slot
            dest = ring_buffer[buf_idx % buffer_size].ctypes.data
            ctypes.memmove(dest, img.bp, frame_bytes)
            buf_idx += 1

            # detect dropped frames via nframe gaps
            if prev_nframe is not None:
                gap = img.nframe - prev_nframe - 1
                if gap > 0:
                    dropped += gap
            prev_nframe = img.nframe

            if (i + 1) % 100 == 0:
                elapsed = time.perf_counter() - t_start
                fps = (i + 1) / elapsed
                print(f"  frame {i + 1}/{num_frames}  fps={fps:.1f}  dropped={dropped}")

        elapsed = time.perf_counter() - t_start
        cam.stop_acquisition()

    fps = num_frames / elapsed
    print("\nResults:")
    print(f"  Frames captured: {num_frames}")
    print(f"  Frames dropped:  {dropped}")
    print(f"  Elapsed time:    {elapsed:.2f} s")
    print(f"  Average FPS:     {fps:.1f}")
    print(f"  Buffer contents: {min(buf_idx, buffer_size)} frames")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-n",
        "--num-frames",
        type=int,
        default=1000,
        help="total frames to capture (default: 1000)",
    )
    parser.add_argument(
        "-k",
        "--buffer-size",
        type=int,
        default=100,
        help="circular buffer size in frames (default: 100)",
    )
    parser.add_argument(
        "-e",
        "--exposure",
        type=int,
        default=1000,
        help="exposure time in microseconds (default: 1000)",
    )
    parser.add_argument(
        "-r",
        "--roi",
        type=int,
        nargs=2,
        default=None,
        metavar=("W", "H"),
        help="ROI width and height, centered on sensor (default: full frame)",
    )
    args = parser.parse_args()

    run_benchmark(
        num_frames=args.num_frames,
        buffer_size=args.buffer_size,
        exposure_us=args.exposure,
        roi_size=tuple(args.roi) if args.roi else None,
    )


if __name__ == "__main__":
    main()
