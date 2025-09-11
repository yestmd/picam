# file: record_60fps.py
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import time

picam2 = Picamera2()

# Pick a practical 60 fps resolution. 2304x1296 keeps wide FOV with 2x2 binning.
video_size = (2304, 1296)   # Alternatives: (1920,1080), (1536,864), (1280,720)

video_config = picam2.create_video_configuration(
    main={"size": video_size, "format": "YUV420"},
    queue=False  # lower latency on Pi 3
)
picam2.configure(video_config)

# Strict 60 fps: 1/60 s = 16,666,666 ns
FR_60_NS = 16_666_666

# Lock AE to avoid the ISP trying to extend exposure and dropping fps in low light
picam2.set_controls({
    "AeEnable": False,
    "FrameDurationLimits": (FR_60_NS, FR_60_NS),
    # Keep exposure ≤ frame duration; try ~1/1000s initially, the gain will compensate
    "ExposureTime": 1000,           # microseconds
    "AnalogueGain": 4.0,            # bump as needed for brightness
})

# H.264 encoding; keep bitrate conservative for Pi 3 B+ disk I/O
encoder = H264Encoder(bitrate=10_000_000)  # ~10 Mb/s
output = FfmpegOutput("video_60fps.mp4")   # MP4 container with ffmpeg muxer

picam2.start_recording(encoder, output)
print("Recording 60 fps CFR… Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    picam2.stop_recording()
    print("Saved to video_60fps.mp4")
