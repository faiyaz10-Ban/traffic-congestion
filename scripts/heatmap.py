import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

import folium
from folium.plugins import HeatMap

def generate_heatmap(congestion_data, output_path):
    """
    Generates a congestion heatmap and saves it as an HTML file.

    Args:
        congestion_data (list): List of [latitude, longitude, weight] for congestion points.
            Example: [
                [23.7529, 90.3854, 5],  # Panthapath
                [23.7808, 90.4266, 15], # Merul Badda
                [23.7628, 90.3852, 10]  # Bijoy Sorony
            ]
        output_path (str): Path to save the heatmap HTML file.

    Returns:
        None
    """
    # Center the map at a central point in Dhaka
    dhaka_coords = [23.8103, 90.4125]
    heatmap_map = folium.Map(location=dhaka_coords, zoom_start=12)

    # Add heatmap layer
    HeatMap(congestion_data).add_to(heatmap_map)

    # Save the map to an HTML file
    heatmap_map.save(output_path)


def calculate_routes(origin_name, destinations, congestion_data):
    location_mapping = {
        "Housebuilding": (23.8103, 90.4125),
        "Mirpur": (23.8042, 90.3662),
        "Gulshan": (23.7925, 90.4078)
    }
    origin_coords = location_mapping.get(origin_name)
    if not origin_coords:
        raise ValueError(f"Unknown origin location: {origin_name}")

    G = ox.graph_from_place("Dhaka, Bangladesh", network_type="drive")
    routes = {}
    for name, coords in destinations.items():
        orig_node = ox.nearest_nodes(G, origin_coords[1], origin_coords[0])
        dest_node = ox.nearest_nodes(G, coords[1], coords[0])
        route = nx.shortest_path(G, orig_node, dest_node, weight="length")
        routes[name] = {
            "route": route,
            "distance": nx.shortest_path_length(G, orig_node, dest_node, weight="length")
        }

    fig, ax = ox.plot_graph_routes(G, [r["route"] for r in routes.values()], route_colors=["r", "g", "b"], show=False)
    map_path = f"processed/maps/{origin_name}_route_map.png"
    plt.savefig(map_path)
    plt.close()

    return map_path, routes
