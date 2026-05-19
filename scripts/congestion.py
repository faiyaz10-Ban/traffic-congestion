def analyze_congestion_from_counts(object_counts, frame_count):
    """
    Analyze congestion levels from object counter responses.

    Args:
        object_counts (dict): A dictionary of total counts for each class.
        frame_count (int): Total number of frames in the video.

    Returns:
        dict: Congestion data including average counts and congestion levels for each class.
    """
    # Calculate average counts per frame
    avg_counts_per_frame = {cls: count / frame_count for cls, count in object_counts.items()}

    # Determine congestion levels based on thresholds
    congestion_levels = {
        cls: (
            "light" if avg < 5 else
            "moderate" if avg < 15 else
            "heavy"
        ) for cls, avg in avg_counts_per_frame.items()
    }

    # Return the congestion analysis
    return {
        "total_counts": object_counts,
        "average_counts_per_frame": avg_counts_per_frame,
        "congestion_levels": congestion_levels
    }
