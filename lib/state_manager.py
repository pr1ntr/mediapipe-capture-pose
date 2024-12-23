class StateManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of StateManager exists."""
        if not cls._instance:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.state = {"running": False, "width": 512, "height": 512, "fps": 5}
            self.subscribers = {}
            self._initialized = True

    def get_state(self, key):
        """Get a specific state property."""
        return self.state.get(key)

    def set_state(self, key, value):
        """Set a specific state property and notify subscribers."""
        self.state[key] = value
        self._notify_subscribers(key, value)

    def subscribe(self, key, callback):
        """Subscribe a callback function to a specific key."""
        if key not in self.subscribers:
            self.subscribers[key] = []
        if callback not in self.subscribers[key]:
            self.subscribers[key].append(callback)

    def _notify_subscribers(self, key, value):
        """Notify subscribers of a specific key about a state change."""
        if key in self.subscribers:
            for subscriber in self.subscribers[key]:
                subscriber(value)

