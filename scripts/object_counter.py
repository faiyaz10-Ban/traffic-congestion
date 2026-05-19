import cv2
import os
from ultralytics import solutions
import numpy as np

def get_line_points(video_width, video_height):
    """
    Dynamically adjust the line points for counting based on video resolution.
    """
    start_point = (int(video_width * 0.1), int(video_height * 0.5))  # 10% from left, 50% from top
    end_point   = (int(video_width * 0.9), int(video_height * 0.5))  # 90% from left, 50% from top
    return [start_point, end_point]

def process_video_with_counter(video_path, output_path):
    """
    Process a video using Ultralytics ObjectCounter to count objects for all classes found in the model.

    Args:
        video_path (str): Path to the input video file.
        output_path (str): Path to save the processed video.

    Returns:
        tuple: (total_counts, frame_count)
               - total_counts (dict): total counts of objects per class
               - frame_count (int): total number of frames processed
    """
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), f"Error reading video file: {video_path}"

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    region_points = get_line_points(width, height)

    # Video writer
    video_writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )
    model = "/home/asif/Desktop/my_dhaka_traffic_project/models/best.pt"
    # Initialize ObjectCounter without specifying classes (i.e., detect all)
    counter = solutions.ObjectCounter(
        show=True,
        region=region_points,
        model = model,
        classes_names=model.names,
        raw_tracks=True,
    )

    # We'll store counts in a dictionary keyed by class name
    total_counts = {}
    frame_count = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Video frame is empty or video processing completed.")
            break

        # Basic validation
        if frame is None or not isinstance(frame, np.ndarray) or len(frame.shape) != 3:
            print(
                f"Invalid frame encountered. Skipping. "
                f"Type={type(frame)} Shape={frame.shape if frame is not None else 'None'}"
            )
            continue

        frame_count += 1

        # 1) Perform counting (populates counter.results for this frame)
        try:
            counter.count(frame)
        except Exception as e:
            print(f"Error during frame processing: {e}")
            continue

        # 2) Create annotated frame (NumPy array)
        try:
            processed_frame = counter.annotate(frame.copy())
        except Exception as e:
            print(f"Error creating annotated frame: {e}")
            continue

        # 3) Aggregate class counts (for all classes returned by the model)
        for cls, cls_count in counter.results.items():
            total_counts[cls] = total_counts.get(cls, 0) + cls_count

        # 4) Write the processed (annotated) frame
        video_writer.write(processed_frame)

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()

    return total_counts, frame_count

def process_videos_in_folder(video_folder, output_folder):
    """
    Process all videos in the folder for object counting.

    Returns:
        dict:
            {
                "example.mp4": {
                    "counts": { ... },
                    "frame_count": ...
                },
                ...
            }
    """
    video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
    all_video_data = {}

    for video_file in video_files:
        video_path = os.path.join(video_folder, video_file)
        output_path = os.path.join(output_folder, f"processed_{video_file}")
        print(f"Processing video: {video_file}")

        counts, frame_count = process_video_with_counter(video_path, output_path)
        all_video_data[video_file] = {
            "counts": counts,
            "frame_count": frame_count
        }

    return all_video_data
