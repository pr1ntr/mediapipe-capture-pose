import tkinter as tk

import cv2

from lib.state_manager import StateManager
from lib.webcam_manager import WebcamManager
from PIL import Image, ImageTk
import os


class BaseGUI:
    def __init__(self, root, width, height):
        self.root = root
        self.root.title("Base GUI")
        self.root.geometry(f"{width}x{height}")  # Set window size
        self.button_state = False
        self.state_manager = StateManager()

        self.state_manager.subscribe("running", self._on_running_change)

        self.webcam_manager = WebcamManager()
        self.video_label = tk.Label(self.root)
        self.video_label.pack(expand=True, pady=10)

        self._add_webcam_config_fields()
        self._add_start_stop_button()

    def _add_start_stop_button(self):
        """Add the Start/Stop button at the bottom."""
        self.button_state = False
        self.toggle_button = tk.Button(
            self.root,
            text="Start",
            command=self._toggle_button_action
        )
        self.toggle_button.pack(side=tk.BOTTOM, pady=20)

    def _add_webcam_config_fields(self):
        """Add input fields for width, height, and FPS at the top, horizontally centered."""
        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        # Context Label
        tk.Label(frame, text="Webcam Settings:", font=("Arial", 12, "bold")).grid(
            row=0,
            column=0,
            columnspan=10,
            pady=(0, 10)
        )

        # Width
        tk.Label(frame, text="Width:").grid(row=1, column=0)
        self.width_entry = tk.Entry(frame, width=8)
        self.width_entry.insert(0, self.state_manager.get_state("width"))
        self.width_entry.grid(row=1, column=1, padx=10)

        # Height
        tk.Label(frame, text="Height:").grid(row=1, column=2)
        self.height_entry = tk.Entry(frame, width=8)
        self.height_entry.insert(0, self.state_manager.get_state("height"))
        self.height_entry.grid(row=1, column=3, padx=10)

        # FPS
        tk.Label(frame, text="FPS:").grid(row=1, column=4, padx=10)
        self.fps_entry = tk.Entry(frame, width=8)
        self.fps_entry.insert(0, self.state_manager.get_state("fps"))
        self.fps_entry.grid(row=1, column=5, padx=10)

        # Apply button
        self.apply_button = tk.Button(frame, text="Apply", command=self._apply_changes)
        self.apply_button.grid(row=1, column=6, padx=10)

        # New line
        # Check box save file or not
        self.save_checkbox_var = tk.BooleanVar(value=self.state_manager.get_state('save_to_file'))
        self.save_checkbox = tk.Checkbutton(frame, text="Save to file",
                                            variable=self.save_checkbox_var,
                                            command=lambda: self.state_manager.set_state('save_to_file',
                                                                                         self.save_checkbox_var.get()))
        self.save_checkbox.grid(row=2, column=3)

        # Os file path and name select
        tk.Label(frame, text="File path:").grid(row=2, column=4)
        self.file_path = tk.Entry(frame, width=20)
        self.file_path.insert(0, self.state_manager.get_state("file_path"))
        self.file_path.grid(row=2, column=5)

        # Apply filepath button
        self.apply_button = tk.Button(frame, text="Set", command=self._apply_file_path)
        self.apply_button.grid(row=2, column=6, padx=10)

        # dropdown menu for webcam selection
        frame = tk.Frame(self.root)
        frame.pack(pady=0)

        tk.Label(frame, text="Select Webcam:").grid(row=0, column=5, padx=10)

        webcams = self.state_manager.get_state("webcams")
        self.webcam_label = tk.StringVar(value=webcams[self.state_manager.get_state("webcam_index")])
        self.webcam_dropdown = tk.OptionMenu(frame, self.webcam_label, *webcams,
                                             command=lambda x: self._on_webcam_select(webcams, x))
        self.webcam_dropdown.grid(row=0, column=6, padx=10)

    def _on_webcam_select(self, webcams, selected_value):
        """Handles the selection of a webcam from the dropdown."""
        # Store the index of the selected value in the state manager
        self.state_manager.set_state("webcam_index", webcams.index(selected_value))

        # Update the visible label
        self.webcam_label.set(selected_value)

    def _apply_file_path(self):
        """Apply changes from input fields to the StateManager."""
        try:
            file_path = self.file_path.get()
            # make sure the file path is valid
            if not os.path.exists(file_path):
                self.file_path.delete(0, tk.END)
            else:
                self.state_manager.set_state("file_path", file_path)
                print(f"Settings updated: file_path={file_path}")
        except ValueError:
            print("Invalid input! Please enter a file path.")

    def _apply_changes(self):
        """Apply changes from input fields to the StateManager."""
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            fps = int(self.fps_entry.get())

            self.state_manager.set_state("width", width)
            self.state_manager.set_state("height", height)
            self.state_manager.set_state("fps", fps)

            print(f"Settings updated: width={width}, height={height}, fps={fps}")
        except ValueError:
            print("Invalid input! Please enter integers for width, height, and fps.")

    def _update_video_frame(self):
        """Render the latest frame in the GUI at the specified FPS."""
        frame = self.webcam_manager.get_latest_frame()
        if frame is not None:
            # Convert the frame to an ImageTk object and display it
            frame = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=frame)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
            self._save_frame_file(frame)

        # Schedule the next frame update based on the declared FPS
        fps = self.state_manager.get_state("fps")
        self.root.after(int(1000 / fps), self._update_video_frame)

    def _save_frame_file(self, image):
        """Save the latest frame to a file."""
        file_path = self.state_manager.get_state("file_path")
        save_to_file = self.state_manager.get_state("save_to_file")
        if save_to_file and file_path:
            image.save(f"{file_path}/image.png")

    def _on_running_change(self, value):
        """Callback for 'running' state changes."""
        if value:
            self.toggle_button.config(text="Stop")
            self.webcam_manager.start()
            self._update_video_frame()
        else:
            self.toggle_button.config(text="Start")
            self.webcam_manager.stop()
            self.video_label.config(image="")

    def _toggle_button_action(self):
        self.state_manager.set_state("running", not self.state_manager.get_state("running"))


if __name__ == "__main__":
    root = tk.Tk()
    app = BaseGUI(root, width=1024, height=1024)
    root.mainloop()
