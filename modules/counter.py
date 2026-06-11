class LineCrossCounter:
    """
    Stateful class to monitor line crossing events for tracked centroids.
    Calculates direction (Entry/Exit) and prevents duplicate counts.
    """
    def __init__(self):
        self.track_history = {}  # Maps track_id -> previous Y coordinate
        self.entered_ids = set() # Set of entered track IDs
        self.exited_ids = set()  # Set of exited track IDs
        self.entry_count = 0
        self.exit_count = 0

    def update(self, track_id, cy, line_y):
        """
        Updates the track history and monitors line crossing transitions.
        """
        prev_y = self.track_history.get(track_id)
        
        if prev_y is not None:
            # Case A: Crossing Top-to-Bottom (ENTRY)
            if prev_y < line_y <= cy:
                if track_id not in self.entered_ids:
                    self.entry_count += 1
                    self.entered_ids.add(track_id)
                    self.exited_ids.discard(track_id) # Remove from exited so they can exit again
                    
                    print(f"ENTRY: Person ID {track_id}")
                    print(f"CROSSING DEBUG - Track ID: {track_id} | Previous Y: {prev_y} | Current Y: {cy} | Crossing Direction: ENTRY")

            # Case B: Crossing Bottom-to-Top (EXIT)
            elif prev_y > line_y >= cy:
                if track_id not in self.exited_ids:
                    self.exit_count += 1
                    self.exited_ids.add(track_id)
                    self.entered_ids.discard(track_id) # Remove from entered so they can enter again
                    
                    print(f"EXIT: Person ID {track_id}")
                    print(f"CROSSING DEBUG - Track ID: {track_id} | Previous Y: {prev_y} | Current Y: {cy} | Crossing Direction: EXIT")

        # Save current position for next frame comparison
        self.track_history[track_id] = cy

    def cleanup(self, active_ids):
        """
        Removes Y position history for tracks that disappeared from the frame.
        """
        disappeared_ids = set(self.track_history.keys()) - active_ids
        for tid in disappeared_ids:
            self.track_history.pop(tid, None)
            
    def get_occupancy(self):
        """
        Returns net occupancy, keeping value at or above 0.
        """
        return max(0, self.entry_count - self.exit_count)
