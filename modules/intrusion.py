from modules.config import COLOR_ALERT, COLOR_DEFAULT

class IntrusionDetector:
    """
    Stateful class to monitor track IDs entering a Restricted Area.
    Triggers immediate alarms and prevents redundant logs.
    """
    def __init__(self):
        self.intrusion_alerted = {} # Maps track_id -> True/False alert state

    def update(self, track_id, is_inside):
        """
        Updates the intrusion state of a given track ID.
        Returns:
            color (tuple or None): Alert color if intruding, otherwise None (allow cascade to other systems).
            local_alert (str or None): Bounding box alert text.
        """
        color = None
        local_alert = None

        if is_inside:
            color = COLOR_ALERT
            local_alert = "INTRUSION ALERT"
            
            # Print immediate console log exactly once per entry
            if track_id not in self.intrusion_alerted:
                print(f"ALERT: Person ID {track_id} entered restricted area")
                self.intrusion_alerted[track_id] = True
        else:
            # Clear state on exit
            self.intrusion_alerted.pop(track_id, None)

        return color, local_alert

    def cleanup(self, active_ids):
        """
        Removes intrusion state registry for tracks that disappeared from the frame.
        """
        disappeared_ids = set(self.intrusion_alerted.keys()) - active_ids
        for tid in disappeared_ids:
            self.intrusion_alerted.pop(tid, None)
