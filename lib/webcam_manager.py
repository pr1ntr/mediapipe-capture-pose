import cv2
from threading import Thread
import time
from lib.state_manager import StateManager
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np


class WebcamManager:
    def __init__(self):
        self.state_manager = StateManager()
        self.cap = None
        self.running = False
        self.thread = None
        self.initialization_thread = None
        self.latest_frame = None

        base_options = python.BaseOptions(model_asset_path='./pose_landmarker.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True)

        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

    def _configure_camera(self):
        """Configure the webcam based on the state."""
        width = self.state_manager.get_state("width")
        height = self.state_manager.get_state("height")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def draw_landmarks_on_black(self, detection_result):
        """Draw pose landmarks on a black background."""
        # Get dimensions from StateManager
        width = self.state_manager.get_state("width")
        height = self.state_manager.get_state("height")

        # Create a black canvas
        black_image = np.zeros((height, width, 3), dtype=np.uint8)

        # Get pose landmarks from the detection result
        pose_landmarks_list = detection_result.pose_landmarks

        # Draw the pose landmarks on the black canvas
        for pose_landmarks in pose_landmarks_list:
            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
            ])
            solutions.drawing_utils.draw_landmarks(
                black_image,
                pose_landmarks_proto,
                solutions.pose.POSE_CONNECTIONS,
                solutions.drawing_styles.get_default_pose_landmarks_style()
            )

        return black_image

    def _capture_loop(self):
        """Capture frames from the webcam."""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                detection_result = self.detector.detect(mp_image)
                self.latest_frame = self.draw_landmarks_on_black(detection_result)
            time.sleep(1 / self.state_manager.get_state("fps"))

    def _initialize_webcam(self):
        """Initialize the webcam in a separate thread."""
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Default webcam
        if not self.cap.isOpened():
            raise RuntimeError("Unable to open webcam.")
        self._configure_camera()

    def start(self):
        """Start the webcam capture."""
        if self.running:
            return

        # Initialize webcam in a separate thread to avoid blocking
        def initialize_and_start():
            self._initialize_webcam()
            self.running = True
            self.thread = Thread(target=self._capture_loop, daemon=True)
            self.thread.start()

        self.initialization_thread = Thread(target=initialize_and_start, daemon=True)
        self.initialization_thread.start()

    def stop(self):
        """Stop the webcam capture."""
        if not self.running:
            return
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
            self.cap = None

    def get_frame(self):
        """Get the latest frame from the webcam."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR (OpenCV format) to RGB (Pillow format)
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def get_latest_frame(self):
        """Get the most recent frame from the buffer."""
        return getattr(self, "latest_frame", None)
