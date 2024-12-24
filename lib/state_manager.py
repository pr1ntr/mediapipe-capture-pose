import os
import json

class StateManager:
    _instance = None
    STATE_FILE_PATH = "./state/state.json"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.state = {
                "running": False,
                "width": 512,
                "height": 512,
                "fps": 5,
                "file_path": "",
                "save_to_file": False
            }
            self.subscribers = {}
            self._load_state()
            self._initialized = True

    def _load_state(self):
        """Load state from a file if it exists, otherwise create a blank file."""
        os.makedirs(os.path.dirname(self.STATE_FILE_PATH), exist_ok=True)
        if os.path.exists(self.STATE_FILE_PATH):
            try:
                with open(self.STATE_FILE_PATH, "r") as f:
                    self.state = json.load(f)
            except (IOError, json.JSONDecodeError):
                self._save_state()
        else:
            self._save_state()

    def _save_state(self):
        """Persist the current state to the file."""
        with open(self.STATE_FILE_PATH, "w") as f:
            json.dump(self.state, f, indent=4)

    def get_state(self, key):
        return self.state.get(key)

    def set_state(self, key, value):
        self.state[key] = value
        self._save_state()
        self._notify_subscribers(key, value)

    def subscribe(self, key, callback):
        if key not in self.subscribers:
            self.subscribers[key] = []
        if callback not in self.subscribers[key]:
            self.subscribers[key].append(callback)

    def _notify_subscribers(self, key, value):
        if key in self.subscribers:
            for subscriber in self.subscribers[key]:
                subscriber(value)
