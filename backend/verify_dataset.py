#!/usr/bin/env python3
"""
Dataset Verification Script for YOLOv8

Verifies:
- Missing labels
- Incorrect formats
- Class distribution
- Image/label pairing
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def verify_dataset(datasets_dir: str = "datasets") -> Dict:
    """Verify dataset integrity"""

    datasets_dir = Path(datasets_dir)
    results = {"errors": [], "warnings": [], "info": []}

    for split in ["train", "valid"]:
        split_dir = datasets_dir / split
        if not split_dir.exists():
            results["warnings"].append(f"{split} directory not found")
            continue

        images_dir = split_dir / "images"
        labels_dir = split_dir / "labels"

        if not images_dir.exists():
            results["errors"].append(f"{split}/images not found")
            continue

        if not labels_dir.exists():
            results["errors"].append(f"{split}/labels not found")
            continue

        # Get files
        images = (
            list(images_dir.glob("*.jpg"))
            + list(images_dir.glob("*.png"))
            + list(images_dir.glob("*.jpeg"))
        )

        labels = list(labels_dir.glob("*.txt"))

        results["info"].append(f"{split}: {len(images)} images, {len(labels)} labels")

        # Check missing labels
        missing = 0
        for img in images:
            label_file = labels_dir / f"{img.stem}.txt"
            if not label_file.exists():
                missing += 1

        if missing > 0:
            results["warnings"].append(f"{split}: {missing} missing labels")

        # Check malformed labels
        malformed = 0
        class_counts = {}

        for label_file in labels:
            try:
                with open(label_file, "r") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue

                        parts = line.split()

                        # YOLO format: class x y w h
                        if len(parts) != 5:
                            results["errors"].append(
                                f"{label_file.name}:{line_num} - {len(parts)} values (expected 5)"
                            )
                            malformed += 1
                            continue

                        # Check class
                        try:
                            class_id = int(parts[0])
                            class_counts[class_id] = class_counts.get(class_id, 0) + 1
                        except ValueError:
                            results["errors"].append(
                                f"{label_file.name}:{line_num} - invalid class: {parts[0]}"
                            )

                        # Check normalized values
                        for val in parts[1:]:
                            try:
                                v = float(val)
                                if not (0 <= v <= 1):
                                    results["warnings"].append(
                                        f"{label_file.name}:{line_num} - value {v} not in [0,1]"
                                    )
                            except ValueError:
                                results["errors"].append(
                                    f"{label_file.name}:{line_num} - invalid float: {val}"
                                )
            except Exception as e:
                results["errors"].append(f"{label_file.name}: {e}")

        if class_counts:
            results["info"].append(f"{split} class distribution: {class_counts}")

    results["valid"] = len(results["errors"]) == 0

    return results


def check_class_in_labels(
    labels_dir: str, target_class: int = 0
) -> Tuple[int, List[str]]:
    """Check which class IDs exist in labels"""

    labels_dir = Path(labels_dir)
    class_ids = set()
    files_with_class = []

    for label_file in labels_dir.glob("*.txt"):
        with open(label_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    class_ids.add(int(parts[0]))
                    if int(parts[0]) == target_class:
                        files_with_class.append(label_file.name)

    return len(files_with_class), list(class_ids)


def main():
    """Main verification"""
    print("=== YOLOv8 Dataset Verifier ===\n")

    results = verify_dataset()

    print(f"Valid: {results['valid']}")
    print("")

    if results["info"]:
        print("Info:")
        for info in results["info"]:
            print(f"  - {info}")
        print("")

    if results["warnings"]:
        print("Warnings:")
        for w in results["warnings"]:
            print(f"  - {w}")
        print("")

    if results["errors"]:
        print("Errors:")
        for e in results["errors"]:
            print(f"  - {e}")
        print("")

    # Check class distribution
    for split in ["train", "valid"]:
        labels_dir = Path(f"datasets/{split}/labels")
        if labels_dir.exists():
            count, classes = check_class_in_labels(labels_dir)
            print(f"{split}: {count} pothole annotations, class IDs: {classes}")

    return 0 if results["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
