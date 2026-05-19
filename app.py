from flask import Flask, request, jsonify, send_file
import os
import sys
from scripts.congestion import analyze_congestion_from_counts
from scripts.routes import calculate_routes
from scripts.heatmap import generate_heatmap
from scripts.object_counter import process_videos_in_folder, process_video_with_counter
from scripts.utils import map_location_to_coordinates

# Ensure the current directory is in the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Flask app initialization
app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
PREDEFINED_FOLDER = os.path.join(os.getcwd(), "prevideo")
PROCESSED_FOLDER = os.path.join(os.getcwd(), "processed")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(f"{PROCESSED_FOLDER}/videos", exist_ok=True)
os.makedirs(f"{PROCESSED_FOLDER}/maps", exist_ok=True)

# Predefined destinations (latitude, longitude)
DESTINATIONS = {
    "Panthapath": (23.7529, 90.3854),
    "Merul Badda": (23.7808, 90.4266),
    "Bijoy Sorony": (23.7628, 90.3852)
}


@app.route('/api/process_predefined', methods=['GET'])
def process_predefined_videos():
    """
    Process all predefined video feeds and generate results.
    """
    try:
        # Step 1: Process predefined videos for object counting
        if not os.listdir(PREDEFINED_FOLDER):
            return jsonify({"error": "No videos found in predefined folder"}), 404

        video_data = process_videos_in_folder(PREDEFINED_FOLDER, f"{PROCESSED_FOLDER}/videos")

        # Step 2: Map video filenames to their locations (coordinates)
        location_to_coordinates = map_location_to_coordinates(PREDEFINED_FOLDER)
        results = []

        for video, data in video_data.items():
            location = os.path.splitext(video)[0]  # Use file name (without extension) as location
            if location not in location_to_coordinates:
                print(f"Skipping {location} as no coordinates found.")
                continue

            # Step 3: Analyze congestion from object counts
            congestion_data = analyze_congestion_from_counts(data["counts"], data["frame_count"])

            # Step 4: Generate route map
            route_map_path, routes = calculate_routes(location, DESTINATIONS, congestion_data)

            # Step 5: Generate congestion heatmap
            heatmap_path = os.path.join(PROCESSED_FOLDER, "maps", f"{location}_congestion_heatmap.html")
            congestion_points = [
                [DESTINATIONS[name][0], DESTINATIONS[name][1], congestion_data["average_counts_per_frame"].get(name, 0)]
                for name in DESTINATIONS.keys()
            ]
            generate_heatmap(congestion_points, heatmap_path)

            # Step 6: Append results for each processed video
            results.append({
                "video": video,
                "congestion_data": congestion_data,
                "routes": routes,
                "processed_video_download": f"/api/download?file=processed/videos/processed_{video}",
                "route_map_download": f"/api/download?file=processed/maps/{location}_route_map.png",
                "heatmap_download": f"/api/download?file=processed/maps/{location}_congestion_heatmap.html"
            })

        return jsonify({
            "message": "Predefined videos processed successfully",
            "results": results
        })

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/api/upload_video', methods=['POST'])
def upload_video():
    """
    Upload a video file for processing and return results.
    """
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    try:
        # Save the uploaded video
        video = request.files['video']
        video_filename = video.filename
        input_video_path = os.path.join(UPLOAD_FOLDER, video_filename)
        video.save(input_video_path)

        # Process the video
        output_video_path = os.path.join(PROCESSED_FOLDER, "videos", f"processed_{video_filename}")
        counts, frame_count = process_video_with_counter(input_video_path, output_video_path)

        # Analyze congestion
        congestion_data = analyze_congestion_from_counts(counts, frame_count)

        # Return the results
        return jsonify({
            "message": "Video processed successfully",
            "congestion_data": congestion_data,
            "processed_video_download": f"/api/download?file=processed/videos/processed_{video_filename}"
        })

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/api/download', methods=['GET'])
def download_file():
    """
    Download processed files (videos, maps, or heatmaps).
    """
    file_path = request.args.get('file')
    if not file_path:
        return jsonify({"error": "No file specified"}), 400

    full_path = os.path.join(os.getcwd(), file_path)
    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(full_path, as_attachment=True)


if __name__ == '__main__':
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
