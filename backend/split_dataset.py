import os
import shutil
import random
from pathlib import Path

# ===== CONFIGURATION =====
# Using the absolute path found in the workspace
DATASET_PATH = Path(r"C:\project folder\resume project\civic-ai\backend\datasets")
TRAIN_IMG = DATASET_PATH / "train" / "images"
TRAIN_LBL = DATASET_PATH / "train" / "labels"

VAL_IMG = DATASET_PATH / "val" / "images"
VAL_LBL = DATASET_PATH / "val" / "labels"

SPLIT_RATIO = 0.2  # 20% for validation
RANDOM_SEED = 42

def split_dataset():
    # 1. Ensure directories exist
    os.makedirs(VAL_IMG, exist_ok=True)
    os.makedirs(VAL_LBL, exist_ok=True)

    # 2. Get list of all images
    all_images = [f for f in os.listdir(TRAIN_IMG) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"Total training images found: {len(all_images)}")

    # 3. Shuffle and split
    random.seed(RANDOM_SEED)
    random.shuffle(all_images)
    
    num_val = int(len(all_images) * SPLIT_RATIO)
    val_files = all_images[:num_val]
    
    print(f"Moving {len(val_files)} images and their labels to validation set...")

    # 4. Move files
    moved_count = 0
    label_missing_count = 0
    
    for img_name in val_files:
        # Define paths
        src_img = TRAIN_IMG / img_name
        dst_img = VAL_IMG / img_name
        
        # Determine label filename (assumed .txt for YOLO)
        lbl_name = Path(img_name).stem + ".txt"
        src_lbl = TRAIN_LBL / lbl_name
        dst_lbl = VAL_LBL / lbl_name

        try:
            # Move image
            shutil.move(str(src_img), str(dst_img))
            
            # Move label if it exists
            if src_lbl.exists():
                shutil.move(str(src_lbl), str(dst_lbl))
            else:
                label_missing_count += 1
            
            moved_count += 1
        except Exception as e:
            print(f"Error moving {img_name}: {e}")

    print("\n" + "="*30)
    print("DONE: SPLIT COMPLETED SUCCESSFULLY!")
    print(f"Total images moved: {moved_count}")
    print(f"Images without labels (Background): {label_missing_count}")
    print(f"New Train size: {len(os.listdir(TRAIN_IMG))}")
    print(f"New Val size: {len(os.listdir(VAL_IMG))}")
    print("="*30)

if __name__ == "__main__":
    split_dataset()
