import time
from modules.config import COLOR_WARNING, COLOR_ALERT, COLOR_DEFAULT, LOITER_THRESHOLD

class LoiteringDetector:
    """
    Stateful class to monitor track IDs residing in a Loiter Zone.
    Maintains timers and alert flags for active tracks across frames.
    """
    def __init__(self, threshold=LOITER_THRESHOLD):
        self.threshold = threshold
        self.timers = {}          # Maps track_id -> entry timestamp
        self.alerted_tracks = set() # Set of track_ids that already logged alerts

    def update(self, track_id, is_inside):
        """
        Updates the loitering state of a given track ID.
        Returns:
            color (tuple): The rendering color based on threat level.
            status_text (str): Bounding box status label.
            local_alert (str or None): Bounding box alert text.
            elapsed (float): Time spent inside the zone.
        """
        color = COLOR_DEFAULT
        status_text = f"ID {track_id}"
        local_alert = None
        elapsed = 0.0

        if is_inside:
            # Register entrance time if new
            if track_id not in self.timers:
                self.timers[track_id] = time.time()

            elapsed = time.time() - self.timers[track_id]
            status_text = f"ID {track_id} | {elapsed:.1f} sec"

            if elapsed > self.threshold:
                color = COLOR_ALERT
                local_alert = "LOITERING ALERT"
                
                # Check for first-time alert log to prevent spam
                if track_id not in self.alerted_tracks:
                    print(f"ALERT: Person ID {track_id} loitering for {elapsed:.1f} seconds")
                    self.alerted_tracks.add(track_id)
            else:
                color = COLOR_WARNING
        else:
            # Reset states on exit
            self.timers.pop(track_id, None)
            self.alerted_tracks.discard(track_id)

        return color, status_text, local_alert, elapsed

    def cleanup(self, active_ids):
        """
        Removes timers and alert states for tracks that disappeared from the frame.
        """
        disappeared_ids = set(self.timers.keys()) - active_ids
        for tid in disappeared_ids:
            self.timers.pop(tid, None)
            self.alerted_tracks.discard(tid)
