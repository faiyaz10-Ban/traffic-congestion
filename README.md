# Dhaka Traffic Project

A Flask-based project that uses YOLO for vehicle detection and OSMnx for route calculation in Dhaka, Bangladesh.

## Project Structure

my_dhaka_traffic_project/ 
├── data/ 
    │ └── videos/
├── models/ 
    │ └── yolo_11x_finetuned.pt ├── scripts/ │ ├── inference.py
│ ├── congestion_analysis.py │ ├── routing.py
│ ├── osmnx_utils.py
│ └── db_utils.py
├── flask_app/ │ ├── app.py
│ ├── templates/ │ │ └── index.html
│ └── static/ │ └── style.css
├── requirements.txt
└── README.md
