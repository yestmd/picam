#!/usr/bin/env python3
import argparse, os, shlex, subprocess, sys

PRESETS = {
    "wide60":        {"size": "2304x1296", "fps": 60, "bitrate": 6_000_000, "buffers": 4, "denoise": "off"},
    "wide60-lowbuf": {"size": "2304x1296", "fps": 60, "bitrate": 5_000_000, "buffers": 2, "denoise": "off"},
    "wide50":        {"size": "2304x1296", "fps": 50, "bitrate": 6_000_000, "buffers": 2, "denoise": "off"},
    "wide1536p60":   {"size": "1536x864",  "fps": 60, "bitrate": 5_000_000, "buffers": 3, "denoise": "off"},
    "full30":        {"size": "4608x2592", "fps": 30, "bitrate": 25_000_000, "buffers": 4, "denoise": "off"},
    "1080p60":       {"size": "1920x1080", "fps": 60, "bitrate": 5_000_000, "buffers": 3, "denoise": "off"},
}

def parse_size(s):
    w, h = s.split("x", 1)
    return int(w), int(h)

def build_cmd(es_path, size, fps, bitrate, buffers, codec, dur, denoise):
    w, h = parse_size(size)
    t_ms = dur * 1000 if dur > 0 else 0
    extra = f"--nopreview --inline --buffer-count {buffers} --codec {codec} " \
            f"--bitrate {bitrate} --framerate {fps} --width {w} --height {h} " \
            f"--denoise {denoise}"
    return f"rpicam-vid -t {t_ms} {extra} -o {shlex.quote(es_path)}", fps

def main():
    p = argparse.ArgumentParser(description="rpicam-vid recorder (raw ES -> MP4) with presets")
    p.add_argument("output_mp4")
    p.add_argument("--dur", type=int, default=0)
    p.add_argument("--mode", choices=PRESETS.keys())
    p.add_argument("--size")
    p.add_argument("--fps", type=int)
    p.add_argument("--bitrate", type=int)
    p.add_argument("--buffers", type=int)
    p.add_argument("--codec", choices=["h264","hevc"], default="h264")
    p.add_argument("--denoise", choices=["on","off"], help="Default off; 'on' increases memory use")
    args = p.parse_args()

    # defaults = wide60
    cfg = PRESETS["wide60"].copy()
    if args.mode:
        cfg.update(PRESETS[args.mode])
    if args.size:     cfg["size"] = args.size
    if args.fps:      cfg["fps"] = args.fps
    if args.bitrate:  cfg["bitrate"] = args.bitrate
    if args.buffers:  cfg["buffers"] = args.buffers
    if args.denoise:  cfg["denoise"] = args.denoise

    out_dir = os.path.dirname(args.output_mp4) or "."
    os.makedirs(out_dir, exist_ok=True)
    base, _ = os.path.splitext(args.output_mp4)
    es_path = base + ".h264"

    cmd, fps = build_cmd(es_path, cfg["size"], cfg["fps"], cfg["bitrate"], cfg["buffers"], args.codec, args.dur, cfg["denoise"])
    print(f"Recording raw ({args.codec}) → {es_path}")
    if args.dur == 0:
        print("Press Ctrl+C to stop…")

    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("Recording failed.")
        if e.stderr:
            print("----- rpicam-vid stderr -----")
            print(e.stderr.strip())
            print("-----------------------------")
        print("Hints: set gpu_mem=256 and cma=256M, reduce resolution/fps/bitrate, --buffers 2, --denoise off.")
        return 1

    print(f"Muxing → {args.output_mp4}")
    mux = f"ffmpeg -y -r {fps} -i {shlex.quote(es_path)} -c copy {shlex.quote(args.output_mp4)}"
    subprocess.run(mux, shell=True, check=True)
    try: os.remove(es_path)
    except FileNotFoundError: pass
    print("Done.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
