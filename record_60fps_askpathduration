# file: record_60fps.py
import sys
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

if len(sys.argv) < 2:
    print("Usage: python3 record_60fps.py <output_path> [duration_seconds]")
    sys.exit(1)

output_path = sys.argv[1]
duration = None
if len(sys.argv) >= 3:
    try:
        duration = int(sys.argv[2])
    except ValueError:
        print("Duration must be an integer (seconds).")
        sys.exit(1)

picam2 = Picamera2()

# Practical 60 fps resolution (binned wide view)
video_size = (2304, 1296)

video_config = picam2.create_video_configuration(
    main={"size": video_size, "format": "YUV420"},
    queue=False
)
picam2.configure(video_config)

# Lock to 60 fps CFR
FR_60_NS = 16_666_666
picam2.set_controls({
    "AeEnable": False,
    "FrameDurationLimits": (FR_60_NS, FR_60_NS),
    "ExposureTime": 1000,     # 1/1000 s
    "AnalogueGain": 4.0,
})

encoder = H264Encoder(bitrate=10_000_000)
output = FfmpegOutput(output_path)

picam2.start_recording(encoder, output)
print(f"Recording 60 fps CFR… Saving to {output_path}")

try:
    if duration is not None:
        print(f"Recording for {duration} seconds…")
        time.sleep(duration)
    else:
        print("Press Ctrl+C to stop recording manually.")
        while True:
            time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    picam2.stop_recording()
    print(f"Finished. File saved: {output_path}")
