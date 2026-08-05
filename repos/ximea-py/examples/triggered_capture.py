"""Triggered capture with pre/post-trigger circular buffer and GPU encoding."""

import argparse
import csv
import ctypes
import logging
import os
import queue
import select
import sys
import termios
import threading
import time
import tty
from datetime import datetime

import av
import matplotlib.pyplot as plt
import numpy as np

from ximea import Camera, Image

log = logging.getLogger(__name__)

IDLE = 0
TRIGGERED = 1

METADATA_COLS = ["nframe", "ts_sec", "ts_usec", "cam_time_ns"]


def _annotate_hist(ax: plt.Axes, diffs: np.ndarray) -> None:
    """Add median line and stats box to a histogram axis."""
    ax.axvline(np.median(diffs), color="red", linestyle="--", label="median")
    stats_text = (
        f"mean={np.mean(diffs):.1f}\n"
        f"std={np.std(diffs):.1f}\n"
        f"min={np.min(diffs)}\n"
        f"max={np.max(diffs)}"
    )
    ax.text(
        0.97,
        0.95,
        stats_text,
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        fontsize=8,
        fontfamily="monospace",
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.8},
    )
    ax.legend(fontsize=8)


def save_debug_histograms(metadata: np.ndarray, n_frames: int, base_path: str) -> None:
    """Save debug histograms: nframe diffs, inter-frame time, jitter, and timeline."""
    meta = metadata[:n_frames]
    cam_time_us = meta[:, 1] * 1_000_000 + meta[:, 2]  # tsSec * 1e6 + tsUSec
    ifi_us = np.diff(cam_time_us).astype(np.float64)  # inter-frame interval
    nframe_diffs = np.diff(meta[:, 0])

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("Capture debug diagnostics", fontsize=14)

    # top-left: nframe diffs (should be all 1s)
    ax = axes[0, 0]
    ax.hist(nframe_diffs, bins="auto", edgecolor="black", linewidth=0.5)
    ax.set_title("Frame counter diff (expect all 1)")
    ax.set_xlabel("nframe[i+1] - nframe[i]")
    ax.set_ylabel("count")
    _annotate_hist(ax, nframe_diffs)

    # top-right: inter-frame interval histogram in microseconds
    ax = axes[0, 1]
    ax.hist(ifi_us, bins="auto", edgecolor="black", linewidth=0.5)
    ax.set_title("Inter-frame interval (us)")
    ax.set_xlabel("us")
    ax.set_ylabel("count")
    _annotate_hist(ax, ifi_us)

    # bottom-left: jitter (deviation from median IFI)
    ax = axes[1, 0]
    median_ifi = np.median(ifi_us)
    jitter_us = ifi_us - median_ifi
    ax.hist(jitter_us, bins="auto", edgecolor="black", linewidth=0.5)
    ax.set_title(f"Jitter (deviation from {median_ifi:.0f} us median)")
    ax.set_xlabel("us")
    ax.set_ylabel("count")
    _annotate_hist(ax, jitter_us)

    # bottom-right: inter-frame interval over time
    ax = axes[1, 1]
    ax.plot(ifi_us, linewidth=0.5, alpha=0.7)
    ax.axhline(median_ifi, color="red", linestyle="--", linewidth=1, label="median")
    ax.set_title("Inter-frame interval over time")
    ax.set_xlabel("frame index")
    ax.set_ylabel("us")
    ax.legend(fontsize=8)

    fig.tight_layout()
    png_path = f"{base_path}_debug.png"
    fig.savefig(png_path, dpi=150)
    plt.close(fig)
    log.info("debug histograms: %s", png_path)


# rolling FPS window size
FPS_WINDOW = 500


def encoder_loop(
    q: queue.Queue,
    fps: int,
    output_dir: str,
    width: int,
    height: int,
    done_event: threading.Event,
) -> None:
    """Persistent encoder thread. Pulls (buffer, metadata, n_frames, timestamp) from queue."""
    while not done_event.is_set() or not q.empty():
        try:
            buf, metadata, n_frames, ts = q.get(timeout=0.5)
        except queue.Empty:
            continue

        base = os.path.join(output_dir, f"capture_{ts}")
        video_path = f"{base}.mp4"
        csv_path = f"{base}.csv"
        log.info("writing %d frames to %s", n_frames, video_path)

        t0 = time.perf_counter()

        # write video
        container = av.open(video_path, mode="w")
        stream = container.add_stream("h264_nvenc", rate=fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = "yuv420p"

        for i in range(n_frames):
            frame = av.VideoFrame.from_ndarray(buf[i], format="gray8")
            for packet in stream.encode(frame):
                container.mux(packet)

        for packet in stream.encode():
            container.mux(packet)
        container.close()

        # write csv
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["frame_idx", "nframe", "ts_sec", "ts_usec", "cam_time_ns"])
            for i, row in enumerate(metadata[:n_frames]):
                writer.writerow([i, row[0], row[1], row[2], row[3]])

        # write debug histograms
        save_debug_histograms(metadata, n_frames, base)

        elapsed = time.perf_counter() - t0
        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        log.info(
            "encode done: %.1f MB, %.2fs (%d fps encode), csv: %s",
            size_mb,
            elapsed,
            n_frames / elapsed,
            csv_path,
        )
        q.task_done()


def run(
    k: int,
    exposure_us: int,
    roi_size: tuple[int, int] | None,
    output_dir: str,
    encode_fps: int,
    target_fps: float | None,
) -> None:
    os.makedirs(output_dir, exist_ok=True)

    with Camera() as cam:
        cam.set_imgdataformat("XI_MONO8")
        cam.set_exposure(exposure_us)

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

        if target_fps is not None:
            cam.set_acq_timing_mode("XI_ACQ_TIMING_MODE_FRAME_RATE_LIMIT")
            cam.set_framerate(target_fps)
        else:
            cam.set_acq_timing_mode("XI_ACQ_TIMING_MODE_FREE_RUN")

        width = cam.get_width()
        height = cam.get_height()
        frame_bytes = width * height
        buf_size = 3 * k

        log.info("Resolution: %dx%d", width, height)
        log.info("Exposure: %d us", exposure_us)
        log.info(
            "Buffer: %d pre-trigger + %d post-trigger = %d frames",
            k,
            2 * k,
            buf_size,
        )
        log.info(
            "Buffer memory: %.1f GB (x2 buffers)",
            2 * buf_size * frame_bytes / (1024**3),
        )
        log.info("Output: %s/", output_dir)
        log.info("Press Enter to trigger, Ctrl-C to quit.")

        # double buffer: frames + metadata
        # metadata columns: nframe, tsSec, tsUSec, cam_time_ns
        buffers = [
            np.empty((buf_size, height, width), dtype=np.uint8),
            np.empty((buf_size, height, width), dtype=np.uint8),
        ]
        meta_buffers = [
            np.zeros((buf_size, 4), dtype=np.int64),
            np.zeros((buf_size, 4), dtype=np.int64),
        ]
        active_idx = 0
        buf_idx = 0

        # encoder thread
        encode_queue: queue.Queue = queue.Queue(maxsize=2)
        done_event = threading.Event()
        encoder = threading.Thread(
            target=encoder_loop,
            args=(encode_queue, encode_fps, output_dir, width, height, done_event),
            daemon=True,
        )
        encoder.start()

        # terminal raw mode for non-blocking keypress
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        img = Image()
        state = IDLE
        post_trigger_remaining = 0
        dropped = 0
        prev_nframe = None
        total_frames = 0
        last_status_time = time.perf_counter()
        last_status_frames = 0

        try:
            cam.start_acquisition()

            # cache attribute lookups for hot loop
            _memmove = ctypes.memmove
            _select = select.select
            _stdin = sys.stdin
            _empty = []

            while True:
                cam.get_image(img, timeout=5000)

                # memmove into active buffer
                slot = buf_idx % buf_size
                _memmove(buffers[active_idx][slot].ctypes.data, img.bp, frame_bytes)

                # record metadata (camera timestamps only, no syscall)
                meta_buffers[active_idx][slot] = (
                    img.nframe,
                    img.tsSec,
                    img.tsUSec,
                    img.tsSec * 1_000_000_000 + img.tsUSec * 1000,
                )

                buf_idx += 1
                total_frames += 1

                # dropped frame tracking
                if prev_nframe is not None:
                    gap = img.nframe - prev_nframe - 1
                    if gap > 0:
                        dropped += gap
                prev_nframe = img.nframe

                # state machine
                if state == IDLE:
                    # check for keypress every 10 frames to reduce syscalls
                    if (
                        total_frames % 10 == 0
                        and _select([_stdin], _empty, _empty, 0)[0]
                    ):
                        _stdin.read(1)
                        state = TRIGGERED
                        post_trigger_remaining = 2 * k
                        log.info(
                            "TRIGGERED at frame %d, recording %d post-trigger frames",
                            total_frames,
                            2 * k,
                        )

                elif state == TRIGGERED:
                    post_trigger_remaining -= 1
                    if post_trigger_remaining <= 0:
                        # swap buffers
                        full_buf = buffers[active_idx]
                        standby_idx = 1 - active_idx

                        if encode_queue.full():
                            log.warning("encoder busy, skipping this trigger")
                        else:
                            # reorder ring buffer so frames are sequential
                            full_meta = meta_buffers[active_idx]
                            n_filled = min(buf_idx, buf_size)
                            ordered = np.empty(
                                (n_filled, height, width), dtype=np.uint8
                            )
                            ordered_meta = np.empty((n_filled, 4), dtype=np.int64)
                            start = buf_idx % buf_size
                            if n_filled == buf_size:
                                # buffer wrapped: oldest frame is at 'start'
                                ordered[: buf_size - start] = full_buf[start:]
                                ordered[buf_size - start :] = full_buf[:start]
                                ordered_meta[: buf_size - start] = full_meta[start:]
                                ordered_meta[buf_size - start :] = full_meta[:start]
                            else:
                                ordered[:n_filled] = full_buf[:n_filled]
                                ordered_meta[:n_filled] = full_meta[:n_filled]

                            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                            encode_queue.put((ordered, ordered_meta, n_filled, ts))

                        active_idx = standby_idx
                        buf_idx = 0
                        state = IDLE
                        log.info(
                            "buffer swapped, back to IDLE (dropped so far: %d)", dropped
                        )

                # periodic status (rolling FPS)
                if total_frames % FPS_WINDOW == 0:
                    now = time.perf_counter()
                    dt = now - last_status_time
                    rolling_fps = (total_frames - last_status_frames) / dt
                    last_status_time = now
                    last_status_frames = total_frames
                    state_str = (
                        "IDLE"
                        if state == IDLE
                        else f"TRIGGERED ({post_trigger_remaining} remaining)"
                    )
                    log.debug(
                        "[%s] frames=%d  fps=%.1f  dropped=%d",
                        state_str,
                        total_frames,
                        rolling_fps,
                        dropped,
                    )

        except KeyboardInterrupt:
            log.info("shutting down...")
        finally:
            cam.stop_acquisition()
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

            # wait for encoder to finish
            done_event.set()
            encoder.join(timeout=30)

            log.info("total frames: %d", total_frames)
            log.info("total dropped: %d", dropped)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-k",
        type=int,
        default=500,
        help="pre-trigger frames; post-trigger is 2k (default: 500)",
    )
    parser.add_argument(
        "-e",
        "--exposure",
        type=int,
        default=1000,
        help="exposure in microseconds (default: 1000)",
    )
    parser.add_argument(
        "-r",
        "--roi",
        type=int,
        nargs=2,
        default=None,
        metavar=("W", "H"),
        help="ROI width and height, centered (default: full frame)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="./captures",
        help="output directory (default: ./captures)",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=None,
        help="target capture framerate; uses frame-rate timing mode (default: free-run)",
    )
    parser.add_argument(
        "--encode-fps",
        type=int,
        default=500,
        help="framerate written into the mp4 container (default: 500)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable debug logging (periodic FPS reports)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    run(
        k=args.k,
        exposure_us=args.exposure,
        roi_size=tuple(args.roi) if args.roi else None,
        output_dir=args.output_dir,
        encode_fps=args.encode_fps,
        target_fps=args.fps,
    )


if __name__ == "__main__":
    main()
