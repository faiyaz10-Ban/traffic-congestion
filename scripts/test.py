from ultralytics import YOLO

# Load a model
model = YOLO("/home/asif/Desktop/my_dhaka_traffic_project/models/best.pt")  # pretrained YOLO11n model

# Run batched inference on a list of images
results = model("/home/asif/Desktop/Data/Frames/Train/frame_0000.jpg")