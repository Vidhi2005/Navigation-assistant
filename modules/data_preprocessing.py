"""
Data Preprocessing Pipeline for Navigation Assistant
Handles image augmentation and dataset preparation for custom training
"""

import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
import os
from pathlib import Path
import json
from typing import List, Tuple, Dict


class NavigationDataPreprocessor:
    """
    Preprocessing and augmentation for navigation-specific dataset
    """
    
    def __init__(self, image_size=(640, 640)):
        """
        Initialize preprocessor
        
        Args:
            image_size: Target image size (width, height)
        """
        self.image_size = image_size
        
        # Training augmentation pipeline
        self.train_transform = A.Compose([
            # Geometric transforms
            A.HorizontalFlip(p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.1,
                scale_limit=0.2,
                rotate_limit=15,
                border_mode=cv2.BORDER_CONSTANT,
                p=0.5
            ),
            A.Perspective(scale=(0.05, 0.1), p=0.3),
            
            # Color/lighting augmentation (important for outdoor/indoor variations)
            A.RandomBrightnessContrast(
                brightness_limit=0.3,
                contrast_limit=0.3,
                p=0.5
            ),
            A.RandomGamma(gamma_limit=(80, 120), p=0.3),
            A.HueSaturationValue(
                hue_shift_limit=10,
                sat_shift_limit=30,
                val_shift_limit=20,
                p=0.3
            ),
            
            # Weather/environmental effects
            A.RandomShadow(
                shadow_roi=(0, 0.5, 1, 1),
                num_shadows_lower=1,
                num_shadows_upper=2,
                shadow_dimension=5,
                p=0.2
            ),
            A.RandomFog(fog_coef_lower=0.1, fog_coef_upper=0.3, p=0.1),
            A.RandomRain(
                slant_lower=-10,
                slant_upper=10,
                drop_length=20,
                drop_width=1,
                p=0.1
            ),
            
            # Blur (simulate motion/low vision)
            A.OneOf([
                A.MotionBlur(blur_limit=5, p=1.0),
                A.GaussianBlur(blur_limit=(3, 7), p=1.0),
                A.MedianBlur(blur_limit=5, p=1.0),
            ], p=0.3),
            
            # Noise
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.2),
            
            # Resize to target size
            A.Resize(self.image_size[1], self.image_size[0]),
            
        ], bbox_params=A.BboxParams(
            format='yolo',
            label_fields=['class_labels'],
            min_area=0,
            min_visibility=0.3
        ))
        
        # Validation transform (no augmentation)
        self.val_transform = A.Compose([
            A.Resize(self.image_size[1], self.image_size[0]),
        ], bbox_params=A.BboxParams(
            format='yolo',
            label_fields=['class_labels']
        ))
    
    def augment(self, image: np.ndarray, bboxes: List, class_labels: List) -> Tuple[np.ndarray, List, List]:
        """
        Apply augmentation to image and bounding boxes
        
        Args:
            image: OpenCV image (BGR)
            bboxes: List of bounding boxes in YOLO format [x_center, y_center, width, height] (normalized)
            class_labels: List of class IDs
        
        Returns:
            Augmented image, bboxes, class_labels
        """
        try:
            transformed = self.train_transform(
                image=image,
                bboxes=bboxes,
                class_labels=class_labels
            )
            
            return (
                transformed['image'],
                transformed['bboxes'],
                transformed['class_labels']
            )
        except Exception as e:
            print(f"⚠️ Augmentation failed: {e}")
            # Return original if augmentation fails
            return image, bboxes, class_labels
    
    def preprocess_for_inference(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model inference
        
        Args:
            image: OpenCV image (BGR)
        
        Returns:
            Preprocessed image
        """
        # Resize
        resized = cv2.resize(image, self.image_size)
        
        # Normalize (0-1)
        normalized = resized.astype(np.float32) / 255.0
        
        return normalized
    
    def simulate_low_vision(self, image: np.ndarray, severity: str = 'moderate') -> np.ndarray:
        """
        Simulate visual impairments for testing
        
        Args:
            image: OpenCV image
            severity: 'mild', 'moderate', 'severe'
        
        Returns:
            Simulated image
        """
        if severity == 'mild':
            # Slight blur
            return cv2.GaussianBlur(image, (5, 5), 0)
        
        elif severity == 'moderate':
            # Blur + reduced contrast
            blurred = cv2.GaussianBlur(image, (11, 11), 0)
            return cv2.addWeighted(blurred, 0.7, np.zeros_like(blurred), 0, 50)
        
        elif severity == 'severe':
            # Heavy blur + tunnel vision
            blurred = cv2.GaussianBlur(image, (21, 21), 0)
            
            # Create vignette effect (tunnel vision)
            h, w = image.shape[:2]
            mask = np.zeros((h, w), dtype=np.float32)
            cv2.circle(mask, (w//2, h//2), min(h, w)//3, 1, -1)
            mask = cv2.GaussianBlur(mask, (101, 101), 0)
            
            for i in range(3):
                blurred[:, :, i] = blurred[:, :, i] * mask
            
            return blurred
        
        return image


class DatasetBuilder:
    """
    Build and organize dataset for YOLO training
    """
    
    # Navigation-specific classes
    NAVIGATION_CLASSES = [
        'person', 'wheelchair', 'cane', 'walker',  # People
        'stairs_up', 'stairs_down', 'escalator', 'elevator',  # Vertical
        'curb', 'pothole', 'uneven_surface',  # Ground hazards
        'traffic_light', 'crosswalk', 'zebra_crossing',  # Traffic
        'door_open', 'door_closed', 'automatic_door',  # Doors
        'pole', 'pillar', 'wall', 'barrier',  # Obstacles
        'bench', 'table', 'chair',  # Furniture
        'vehicle_car', 'vehicle_bike', 'vehicle_bus'  # Vehicles
    ]
    
    def __init__(self, dataset_root: str):
        """
        Initialize dataset builder
        
        Args:
            dataset_root: Root directory for dataset
        """
        self.dataset_root = Path(dataset_root)
        self.preprocessor = NavigationDataPreprocessor()
        
        # Create directory structure
        self.setup_directories()
    
    def setup_directories(self):
        """Create YOLO dataset structure"""
        directories = [
            'images/train',
            'images/val',
            'images/test',
            'labels/train',
            'labels/val',
            'labels/test'
        ]
        
        for dir_path in directories:
            (self.dataset_root / dir_path).mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Dataset structure created at {self.dataset_root}")
    
    def create_data_yaml(self, output_path: str = None):
        """
        Create data.yaml file for YOLO training
        
        Args:
            output_path: Path to save data.yaml
        """
        if output_path is None:
            output_path = self.dataset_root / 'data.yaml'
        
        data_yaml = {
            'path': str(self.dataset_root.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': len(self.NAVIGATION_CLASSES),
            'names': self.NAVIGATION_CLASSES
        }
        
        import yaml
        with open(output_path, 'w') as f:
            yaml.dump(data_yaml, f, default_flow_style=False)
        
        print(f"✅ Created {output_path}")
        return output_path
    
    def augment_dataset(self, num_augmentations: int = 5):
        """
        Augment existing training images
        
        Args:
            num_augmentations: Number of augmented versions per image
        """
        train_images = list((self.dataset_root / 'images/train').glob('*.jpg'))
        
        print(f"Augmenting {len(train_images)} images...")
        
        for img_path in train_images:
            # Load image
            image = cv2.imread(str(img_path))
            
            # Load corresponding label
            label_path = self.dataset_root / 'labels/train' / f"{img_path.stem}.txt"
            
            if not label_path.exists():
                continue
            
            # Parse YOLO format labels
            bboxes = []
            class_labels = []
            
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        bbox = [float(x) for x in parts[1:5]]
                        class_labels.append(class_id)
                        bboxes.append(bbox)
            
            # Generate augmented versions
            for i in range(num_augmentations):
                aug_img, aug_bboxes, aug_labels = self.preprocessor.augment(
                    image, bboxes, class_labels
                )
                
                # Save augmented image
                aug_img_path = self.dataset_root / 'images/train' / f"{img_path.stem}_aug{i}.jpg"
                cv2.imwrite(str(aug_img_path), aug_img)
                
                # Save augmented labels
                aug_label_path = self.dataset_root / 'labels/train' / f"{img_path.stem}_aug{i}.txt"
                
                with open(aug_label_path, 'w') as f:
                    for cls, bbox in zip(aug_labels, aug_bboxes):
                        f.write(f"{cls} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n")
        
        print(f"✅ Augmentation complete!")
    
    def validate_dataset(self):
        """Validate dataset structure and labels"""
        issues = []
        
        for split in ['train', 'val', 'test']:
            img_dir = self.dataset_root / 'images' / split
            label_dir = self.dataset_root / 'labels' / split
            
            images = list(img_dir.glob('*.jpg'))
            
            for img_path in images:
                label_path = label_dir / f"{img_path.stem}.txt"
                
                if not label_path.exists():
                    issues.append(f"Missing label: {label_path}")
                    continue
                
                # Validate label format
                with open(label_path, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        parts = line.strip().split()
                        
                        if len(parts) != 5:
                            issues.append(f"{label_path}:{line_num} - Invalid format")
                            continue
                        
                        try:
                            cls = int(parts[0])
                            bbox = [float(x) for x in parts[1:5]]
                            
                            # Validate class ID
                            if cls < 0 or cls >= len(self.NAVIGATION_CLASSES):
                                issues.append(f"{label_path}:{line_num} - Invalid class {cls}")
                            
                            # Validate bbox coordinates (0-1)
                            for coord in bbox:
                                if coord < 0 or coord > 1:
                                    issues.append(f"{label_path}:{line_num} - Bbox out of range")
                        
                        except ValueError:
                            issues.append(f"{label_path}:{line_num} - Invalid values")
        
        if issues:
            print(f"⚠️ Found {len(issues)} issues:")
            for issue in issues[:10]:  # Show first 10
                print(f"  - {issue}")
        else:
            print("✅ Dataset validation passed!")
        
        return issues


# Test module
if __name__ == "__main__":
    print("Testing Data Preprocessing Pipeline...")
    
    # Test augmentation
    preprocessor = NavigationDataPreprocessor()
    
    # Load sample image
    cap = cv2.VideoCapture(0)
    ret, image = cap.read()
    cap.release()
    
    if ret:
        # Sample bbox and label
        bboxes = [[0.5, 0.5, 0.3, 0.4]]  # YOLO format
        class_labels = [0]  # person
        
        # Augment
        aug_img, aug_bboxes, aug_labels = preprocessor.augment(
            image, bboxes, class_labels
        )
        
        print(f"✅ Augmentation successful")
        print(f"   Original: {image.shape}")
        print(f"   Augmented: {aug_img.shape}")
        
        # Show results
        cv2.imshow('Original', cv2.resize(image, (640, 640)))
        cv2.imshow('Augmented', aug_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    print("Test complete!")
