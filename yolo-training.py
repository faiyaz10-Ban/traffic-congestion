import torch
from ultralytics import YOLO
import yaml
from pathlib import Path
import shutil

def setup_dataset_config():
    """
    Creates YAML configuration for the dataset with the specific path
    """
    dataset_config = {
        'path': '/home/asif/dataset',  # Your specific dataset path
        'train': '/home/asif/dataset/train/',
        'val': '/home/asif/dataset/valid/',
        'test': '/home/asif/dataset/test/',
        
        # Class names with COCO vehicle classes and new classes
        'names': {
            0: 'cng',    # COCO class
            1: 'bicycle',
            2: 'car',
            3: 'motorcycle',
            4: 'rickshaw',
            5: 'bus',
            6: 'truck'     # COCO class
        }
    }
    
    # Save configuration in the dataset directory for better organization
    config_path = Path('/home/asif/dataset/dataset.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(dataset_config, f, default_flow_style=False)
    
    return str(config_path)

def train_model(epochs=50, imgsz=640, batch_size = 16):
    """
    Trains the model using transfer learning from COCO weights
    """
    # Load pretrained YOLO model with COCO weights
    model = YOLO('/home/asif/Desktop/my_dhaka_traffic_project/yolo11x.pt')
    
    # Set up output directory in the dataset path
    output_dir = Path('/home/asif/dataset/results')
    output_dir.mkdir(exist_ok=True)
    
    # Training configuration
    training_args = {
        'data': '/home/asif/dataset/dataset.yaml',
        'epochs': epochs,
        'imgsz': imgsz,
        'batch': batch_size,
        'patience': 50,
        'device': 'cuda',
        'workers': 8,
        'cos_lr': True,
        'lr0': 0.001,
        'lrf': 0.0001,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 5.0,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'box': 7.5,
        'cls': 0.5,
        'dfl': 1.5,
        'save': True,
        'save_period': 10,
        'project': str(output_dir / 'training'),
        'name': 'transfer_learning',
        'exist_ok': True,
        'pretrained': True,
        'freeze': [0, 1, 2, 3, 4, 5]
    }
    
    # Start training
    results = model.train(**training_args)
    
    # Fine-tuning configuration
    fine_tune_args = {
        **training_args,
        'epochs': 20,
        'lr0': 0.0001,
        'lrf': 0.00001,
        'freeze': None,
        'project': str(output_dir / 'fine_tuning'),
        'name': 'fine_tune'
    }
    
    # Fine-tune the model
    results_fine_tune = model.train(**fine_tune_args)
    
    return results, results_fine_tune, model

def validate_model(model):
    """
    Validates the trained model
    """
    results = model.val(data='/home/asif/dataset/dataset.yaml')
    return results

def main():
    # Setup dataset configuration
    config_path = setup_dataset_config()
    print(f"Dataset configuration saved to: {config_path}")
    
    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Train the model
    print("Starting transfer learning...")
    results, results_fine_tune, model = train_model(epochs=100)
    
    # Validate the model
    print("Validating model...")
    val_results = validate_model(model)
    
    print("Training completed!")
    print(f"Results saved in {Path('/home/asif/dataset/results')}")

if __name__ == "__main__":
    main()
