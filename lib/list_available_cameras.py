import subprocess
import re


def list_available_cameras():
    """Lists available video cameras and their indices using FFmpeg."""
    try:
        # Run FFmpeg command to list DirectShow devices
        result = subprocess.run(
            ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            stderr=subprocess.PIPE,  # FFmpeg outputs device list to stderr
            text=True
        )
        output = result.stderr

        # Parse output to find only video devices
        cameras = []
        for line in output.splitlines():
            # Match lines with video devices
            if "(video)" in line:
                # Extract the device name
                match = re.search(r'"([^"]+)"', line)
                if match:
                    cameras.append(match.group(1))
        return cameras
    except FileNotFoundError:
        print("FFmpeg is not installed or not found in PATH.")
        return []
