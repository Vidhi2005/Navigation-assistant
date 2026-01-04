"""
Training Script for Custom Navigation Model
Fine-tune YOLOv8 on navigation-specific dataset
"""

from ultralytics import YOLO
import yaml
from pathlib import Path
import torch


def train_navigation_model(
    data_yaml='datasets/navigation_custom/data.yaml',
    base_model='yolov8n.pt',
    epochs=100,
    imgsz=640,
    batch=16,
    device='cuda' if torch.cuda.is_available() else 'cpu'
):
    """
    Train custom navigation model
    
    Args:
        data_yaml: Path to data.yaml
        base_model: Base YOLO model to fine-tune
        epochs: Training epochs
        imgsz: Image size
        batch: Batch size
        device: cuda or cpu
    """
    
    print("=" * 70)
    print("TRAINING NAVIGATION ASSISTANT MODEL")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Data: {data_yaml}")
    print(f"  Base Model: {base_model}")
    print(f"  Epochs: {epochs}")
    print(f"  Image Size: {imgsz}")
    print(f"  Batch Size: {batch}")
    print(f"  Device: {device}")
    print("=" * 70 + "\n")
    
    # Load pre-trained model
    model = YOLO(base_model)
    
    # Train
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        
        # Training settings
        patience=50,  # Early stopping
        save=True,
        save_period=10,  # Save checkpoint every 10 epochs
        
        # Augmentation
        augment=True,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.0,
        
        # Optimizer
        optimizer='AdamW',
        lr0=0.01,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        
        # Loss weights
        box=7.5,
        cls=0.5,
        dfl=1.5,
        
        # Other
        workers=8,
        project='runs/train',
        name='navigation_model',
        exist_ok=True,
        pretrained=True,
        verbose=True,
    )
    
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print(f"\nBest model saved to: {model.trainer.best}")
    print(f"Results saved to: {model.trainer.save_dir}")
    
    # Validate
    print("\nRunning validation...")
    metrics = model.val()
    
    print(f"\nValidation Metrics:")
    print(f"  mAP50: {metrics.box.map50:.3f}")
    print(f"  mAP50-95: {metrics.box.map:.3f}")
    print(f"  Precision: {metrics.box.mp:.3f}")
    print(f"  Recall: {metrics.box.mr:.3f}")
    
    return model, results, metrics


def export_model(model_path, formats=['onnx', 'tflite']):
    """
    Export trained model to different formats
    
    Args:
        model_path: Path to trained model
        formats: List of export formats
    """
    model = YOLO(model_path)
    
    for fmt in formats:
        print(f"\nExporting to {fmt}...")
        model.export(format=fmt)
        print(f"✅ Exported to {fmt}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Navigation Model')
    parser.add_argument('--data', default='datasets/navigation_custom/data.yaml',
                       help='Path to data.yaml')
    parser.add_argument('--model', default='yolov8n.pt',
                       help='Base model')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Training epochs')
    parser.add_argument('--batch', type=int, default=16,
                       help='Batch size')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='Image size')
    parser.add_argument('--export', action='store_true',
                       help='Export after training')
    
    args = parser.parse_args()
    
    # Train
    model, results, metrics = train_navigation_model(
        data_yaml=args.data,
        base_model=args.model,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz
    )
    
    # Export if requested
    if args.export:
        best_model = model.trainer.best
        export_model(best_model, formats=['onnx', 'tflite', 'torchscript'])
