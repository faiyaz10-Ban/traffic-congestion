import os

def map_location_to_coordinates(video_folder):
    location_mapping = {
        "Housebuilding": (23.8103, 90.4125),
        "Mirpur": (23.8042, 90.3662),
        "Gulshan": (23.7925, 90.4078),
        "Panthapath": (23.7529, 90.3854),
        "Merul Badda": (23.7808, 90.4266),
        "Bijoy Sorony": (23.7628, 90.3852)
    }

    files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
    dynamic_mapping = {}

    for file in files:
        location_name = os.path.splitext(file)[0]
        coordinates = location_mapping.get(location_name)
        if coordinates:
            dynamic_mapping[location_name] = coordinates

    return dynamic_mapping
