import cv2
from modules.config import COLOR_WARNING, COLOR_ALERT, COLOR_CYAN, COLOR_WHITE, COLOR_BLACK

def draw_zones(frame, loiter_coords, restricted_coords, line_y, width):
    """
    Renders visual zones (Yellow Loiter Zone, Red Restricted Area, Cyan Counting Line) on the frame.
    """
    # Unpack coordinates
    lx1, ly1, lx2, ly2 = loiter_coords
    rx1, ry1, rx2, ry2 = restricted_coords

    # Semi-transparent overlay drawing
    overlay = frame.copy()
    # Yellow overlay for Loiter Zone
    cv2.rectangle(overlay, (lx1, ly1), (lx2, ly2), (0, 255, 255), -1)
    # Red overlay for Restricted Area
    cv2.rectangle(overlay, (rx1, ry1), (rx2, ry2), (0, 0, 255), -1)
    
    # Overlay blend alpha
    alpha = 0.10
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Draw solid borders and titles
    # Loiter Zone (Yellow)
    cv2.rectangle(frame, (lx1, ly1), (lx2, ly2), (0, 255, 255), 2)
    cv2.putText(
        frame, "LOITER ZONE", (lx1 + 10, ly1 + 25),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA
    )
    
    # Restricted Area (Red)
    cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), (0, 0, 255), 2)
    cv2.putText(
        frame, "RESTRICTED AREA", (rx1 + 10, ry1 + 25),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA
    )

    # Virtual Counting Line (Cyan)
    cv2.line(frame, (0, line_y), (width, line_y), COLOR_CYAN, 2)
    cv2.putText(
        frame, "COUNTING LINE", (10, line_y - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_CYAN, 2, cv2.LINE_AA
    )

def draw_hud(frame, entry_count, exit_count, occupancy, width):
    """
    Renders the persistent counting and occupancy heads-up display card.
    """
    hud_x1 = width - 285
    hud_y1 = 15

    # Semi-transparent card background
    hud_overlay = frame.copy()
    cv2.rectangle(hud_overlay, (hud_x1, hud_y1), (width - 15, hud_y1 + 90), COLOR_BLACK, -1)
    cv2.addWeighted(hud_overlay, 0.40, frame, 0.60, 0, frame)

    # Draw card border and values text
    cv2.rectangle(frame, (hud_x1, hud_y1), (width - 15, hud_y1 + 90), COLOR_WHITE, 1)
    cv2.putText(
        frame, f"ENTRY COUNT: {entry_count}", (hud_x1 + 15, hud_y1 + 25),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2, cv2.LINE_AA
    )
    cv2.putText(
        frame, f"EXIT COUNT: {exit_count}", (hud_x1 + 15, hud_y1 + 50),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2, cv2.LINE_AA
    )
    cv2.putText(
        frame, f"CURRENT OCCUPANCY: {occupancy}", (hud_x1 + 15, hud_y1 + 75),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2, cv2.LINE_AA
    )

def draw_global_banners(frame, loiter_alerts, intrusion_alerts):
    """
    Renders global warnings at the top-left of the stream if alerts are active.
    """
    banner_y = 15
    if loiter_alerts:
        cv2.rectangle(frame, (15, banner_y), (270, banner_y + 40), COLOR_WARNING, -1)
        cv2.putText(
            frame, "LOITERING DETECTED", (28, banner_y + 27),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 2, cv2.LINE_AA
        )
        banner_y += 50

    if intrusion_alerts:
        cv2.rectangle(frame, (15, banner_y), (270, banner_y + 40), COLOR_ALERT, -1)
        cv2.putText(
            frame, "INTRUSION ALERT", (28, banner_y + 27),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 2, cv2.LINE_AA
        )
