#!/usr/bin/env python3
"""
YOLOv8 Dataset Preparation Script for RDD2022 (Road Damage Detection)

This script:
1. Extracts RDD2022 dataset
2. Organizes into YOLO format
3. Filters to pothole class only
4. Creates data.yaml
5. Verifies dataset integrity
"""

import os
import shutil
import zipfile
import yaml
import json
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# RDD2022 class mapping (your dataset may vary - check annotations)
# Common damage classes in RDD2022:
# D00 - Longitudinal crack
# D01 - Pothole
# D10 - Alligator crack
# D11 - Latitude crack
# D12 - Block crack
# D20 - Utility cut
# D40 - Patched area

POTHOLE_CLASSES = ["D01", "D1", "Pothole", "pothole", "1"]
RDD_CLASS_MAP = {"D00": 0, "D01": 1, "D10": 2, "D11": 3, "D12": 4, "D20": 5, "D40": 6}

# Our simplified classes (only pothole = 0)
CLASS_ID = 0  # pothole = 0 in our model

# Paths
PROJECT_ROOT = Path(__file__).parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
TRAIN_DIR = DATASETS_DIR / "train"
VALID_DIR = DATASETS_DIR / "valid"


def find_zip_file() -> Path | None:
    """Find RDD2022 zip file in common locations"""
    search_paths = [
        PROJECT_ROOT,
        PROJECT_ROOT.parent,
        Path.home() / "Downloads",
    ]

    extensions = [".zip", ".tar.gz", ".tar"]
    prefixes = ["RDD", "rdd", "road", "damage"]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        for ext in extensions:
            for prefix in prefixes:
                pattern = f"{prefix}*{ext}"
                matches = list(search_path.glob(pattern))
                if matches:
                    logger.info(f"Found: {matches[0]}")
                    return matches[0]

    return None


def extract_dataset(zip_path: Path, extract_to: Path):
    """Extract dataset zip file"""
    logger.info(f"Extracting {zip_path}...")

    extract_to.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)

    logger.info("Extraction complete")


def find_annotation_format(folder: Path) -> Dict:
    """
    Detect annotation format in dataset

    Returns dict with:
    - type: 'yolo' | 'coco' | 'voc' | 'bbox' | 'unknown'
    - class_info: class mapping if available
    """
    folder = Path(folder)

    # Check for YOLO format (class xCenter yCenter width height in .txt files)
    yolo_files = list(folder.rglob("*.txt"))
    if yolo_files:
        sample = yolo_files[0]
        with open(sample, "r") as f:
            content = f.read().strip()

        parts = content.split()
        if len(parts) >= 5:
            try:
                float(parts[1])
                return {"type": "yolo", "classes": list(range(int(parts[0]) + 1))}
            except:
                pass

    # Check for COCO format (.json annotations)
    json_files = list(folder.rglob("*.json"))
    if json_files:
        return {"type": "coco", "file": str(json_files[0])}

    # Check for VOC format (.xml annotations)
    xml_files = list(folder.rglob("*.xml"))
    if xml_files:
        return {"type": "voc", "file": str(xml_files[0])}

    return {"type": "unknown"}


def convert_coco_to_yolo(
    coco_file: Path, images_dir: Path, output_dir: Path, target_class: str = "D01"
) -> int:
    """Convert COCO annotations to YOLO format"""
    with open(coco_file, "r") as f:
        coco = json.load(f)

    images = {img["id"]: img for img in coco["images"]}
    categories = {cat["id"]: cat for cat in coco["categories"]}

    converted = 0

    for ann in coco["annotations"]:
        if ann.get("category_id") != target_class:
            continue

        img = images[ann["image_id"]]
        img_width = img["width"]
        img_height = img["height"]

        # COCO bbox: [x, y, w, h] -> YOLO: [class, x_center, y_center, w, h]
        bbox = ann["bbox"]
        x_center = (bbox[0] + bbox[2] / 2) / img_width
        y_center = (bbox[1] + bbox[3] / 2) / img_height
        width = bbox[2] / img_width
        height = bbox[3] / img_height

        # Write YOLO label file
        img_name = Path(img["file_name"]).stem
        label_file = output_dir / f"{img_name}.txt"

        with open(label_file, "a") as f:
            f.write(
                f"{CLASS_ID} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
            )

        converted += 1

    logger.info(f"Converted {converted} annotations to YOLO format")
    return converted


def organize_dataset(source_dir: Path, target_dir: Path, target_class: str = "D01"):
    """Organize dataset into YOLO format"""

    target_dir.mkdir(parents=True, exist_ok=True)
    images_dir = target_dir / "images"
    labels_dir = target_dir / "labels"
    images_dir.mkdir(exist_ok=True)
    labels_dir.mkdir(exist_ok=True)

    # Find images and annotations
    image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG"]
    images = []

    for ext in image_extensions:
        images.extend(list(source_dir.rglob(ext)))

    logger.info(f"Found {len(images)} images")

    # Detect format
    format_info = find_annotation_format(source_dir)
    logger.info(f"Detected format: {format_info}")

    # Process based on format
    if format_info["type"] == "yolo":
        # Copy YOLO format files directly
        label_files = list(source_dir.rglob("*.txt"))

        for img in images:
            label_path = img.with_suffix(".txt")

            if label_path.exists():
                # Copy files
                shutil.copy(img, images_dir / img.name)
                shutil.copy(label_path, labels_dir / label_path.name)

    elif format_info["type"] == "coco":
        coco_file = Path(format_info["file"])
        convert_coco_to_yolo(coco_file, source_dir, labels_dir, target_class)

        for img in images:
            shutil.copy(img, images_dir / img.name)

    else:
        # Just copy images (labels may be in separate folder)
        label_dir = source_dir / "labels"
        if not label_dir.exists():
            label_dir = source_dir / "Label"

        for img in images:
            shutil.copy(img, images_dir / img.name)

            if label_dir.exists():
                label_path = label_dir / f"{img.stem}.txt"
                if label_path.exists():
                    shutil.copy(label_path, labels_dir / label_path.name)

    logger.info(f"Dataset organized in {target_dir}")


def filter_pothole_only(labels_dir: Path):
    """Filter labels to keep only pothole class"""

    POTHOLE_CLASS_IDS = [1]  # D01 = 1 in RDD

    label_files = list(labels_dir.rglob("*.txt"))
    kept = 0
    removed = 0

    for label_file in label_files:
        with open(label_file, "r") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue

            class_id = int(parts[0])

            # Keep only pothole class
            if class_id in POTHOLE_CLASS_IDS:
                parts[0] = str(CLASS_ID)  # Remap to 0
                new_lines.append(" ".join(parts))
                kept += 1
            else:
                removed += 1

        if new_lines:
            with open(label_file, "w") as f:
                f.write("\n".join(new_lines))

    logger.info(f"Kept {kept}, removed {removed} annotations")


def create_data_yaml(train_dir: Path, valid_dir: Path, output_path: Path):
    """Create YOLO data.yaml configuration file"""

    data = {
        "path": str(train_dir.parent),
        "train": "train/images",
        "val": "valid/images",
        "nc": 1,
        "names": ["pothole"],
    }

    with open(output_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)

    logger.info(f"Created {output_path}")


def verify_dataset(train_dir: Path, valid_dir: Path) -> Dict:
    """Verify dataset integrity"""

    issues = []

    for split, split_dir in [("train", train_dir), ("valid", valid_dir)]:
        images_dir = split_dir / "images"
        labels_dir = split_dir / "labels"

        if not images_dir.exists():
            issues.append(f"{split}: images dir missing")
            continue

        if not labels_dir.exists():
            issues.append(f"{split}: labels dir missing")
            continue

        images = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
        labels = list(labels_dir.glob("*.txt"))

        # Check for missing labels
        for img in images:
            label_file = labels_dir / f"{img.stem}.txt"
            if not label_file.exists():
                issues.append(f"{split}: missing label for {img.name}")

        # Check for malformed labels
        for label_file in labels:
            try:
                with open(label_file, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) != 5:
                            issues.append(f"{label_file}: malformed line")
                            continue

                        # Check normalized values
                        for i, v in enumerate(parts[1:], 1):
                            val = float(v)
                            if not (0 <= val <= 1):
                                issues.append(f"{label_file}: value out of range")
            except Exception as e:
                issues.append(f"{label_file}: {e}")

    result = {"issues": issues, "valid": len(issues) == 0}

    if issues:
        logger.warning(f"Found {len(issues)} issues")
        for issue in issues[:10]:
            logger.warning(f"  - {issue}")
    else:
        logger.info("Dataset verified successfully!")

    return result


def check_class_distribution(labels_dir: Path) -> Dict:
    """Check class distribution in labels"""

    class_counts = {}

    for label_file in labels_dir.rglob("*.txt"):
        with open(label_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                class_id = int(parts[0])
                class_counts[class_id] = class_counts.get(class_id, 0) + 1

    return class_counts


def main():
    """Main setup function"""
    logger.info("=== YOLOv8 Dataset Setup ===")

    # Step 1: Find and extract dataset
    zip_file = find_zip_file()

    if zip_file:
        extract_dataset(zip_file, DATASETS_DIR / "temp")

        # Find actual dataset folder
        temp_contents = list((DATASETS_DIR / "temp").iterdir())
        if temp_contents:
            source_dir = temp_contents[0]
            if source_dir.is_dir():
                organize_dataset(source_dir, TRAIN_DIR)
    else:
        logger.warning("No RDD2022 zip found. Please place it in the project folder.")
        logger.info("Expected: RDD2022.zip or similar")

    # Step 2: Create data.yaml
    create_data_yaml(TRAIN_DIR, VALID_DIR, DATASETS_DIR / "data.yaml")

    # Step 3: Verify
    if TRAIN_DIR.exists():
        verify_dataset(TRAIN_DIR, VALID_DIR)
        logger.info(
            f"Class distribution: {check_class_distribution(TRAIN_DIR / 'labels')}"
        )

    logger.info("=== Setup Complete ===")
    logger.info(f"Dataset: {DATASETS_DIR}")
    logger.info(f"Config: {DATASETS_DIR / 'data.yaml'}")
    logger.info("")
    logger.info("To train:")
    logger.info(
        f"  yolo detect train data={DATASETS_DIR / 'data.yaml'} model=yolov8n.pt epochs=50 imgsz=640"
    )


if __name__ == "__main__":
    main()
