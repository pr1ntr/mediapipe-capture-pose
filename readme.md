# Capture Posenet Controlnet Images with MediaPipe

Make sure you install the prerequisites for mediapipe.

Do what it says here
https://ai.google.dev/edge/mediapipe/framework/getting_started/install#installing_on_windows
But you won't need to build it from source. I think you mainly need VC++ Redist, MSYS2 and Bazel.

Create a virtual environment and install the requirements.

```bash
python -m venv venv
pip install -r requirements.txt
```

install the pose detection model

```bash
wget -O pose_landmarker.task -q https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task
```

Try it.

```bash
python main.py
```
