import os
import shutil
from pathlib import Path
import random

def main():
    dataset_dir = Path(r"d:\Desktop\DECO3801\DataSet")
    output_dir = Path(r"d:\Desktop\DECO3801\dataset_yolo")
    
    # Setup YOLO directory structure
    for split in ['train', 'val']:
        (output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)
        
    print("Finding all .png files...")
    # 排除 dataset_yolo 自己，以防互相干扰
    all_png_files = []
    for f in dataset_dir.rglob("*.png"):
        # We also want to exclude dataset_yolo if it was inside, but here dataset_yolo is outside (sibling of DataSet or in root of project)
        # Actually, let's just make sure it's not inside output_dir
        if output_dir not in f.parents:
            all_png_files.append(f)
            
    # Also look for .jpg just in case? User said .png, so sticking to .png.
    
    print(f"Found {len(all_png_files)} .png files.")
    
    site_groups = {} # site_id -> list of (png_path, txt_path)
    missing_labels = []
    
    for png_path in all_png_files:
        name_parts = png_path.stem.split('_')
        if len(name_parts) >= 2:
            site_id = name_parts[-2]
        else:
            print(f"Skipping {png_path.name}, doesn't match expected naming format.")
            continue
            
        txt_path = png_path.with_suffix('.txt')
        if not txt_path.exists():
            missing_labels.append(png_path)
            continue
            
        if site_id not in site_groups:
            site_groups[site_id] = []
        site_groups[site_id].append((png_path, txt_path))

    if missing_labels:
        print("\n[WARNING] The following images are missing corresponding .txt label files:")
        for missing in missing_labels:
            print(f"  - {missing}")
        print(f"Total missing labels: {len(missing_labels)}\n")
        
    site_ids = list(site_groups.keys())
    site_ids.sort() # For reproducibility
    random.seed(42)
    random.shuffle(site_ids)
    
    num_train_sites = int(len(site_ids) * 0.8)
    train_sites = site_ids[:num_train_sites]
    val_sites = site_ids[num_train_sites:]
    
    train_count = 0
    val_count = 0
    
    print("\nCopying files to train split...")
    for site_id in train_sites:
        for png_path, txt_path in site_groups[site_id]:
            shutil.copy2(png_path, output_dir / 'images' / 'train' / png_path.name)
            shutil.copy2(txt_path, output_dir / 'labels' / 'train' / txt_path.name)
            train_count += 1
            
    print("Copying files to val split...")
    for site_id in val_sites:
        for png_path, txt_path in site_groups[site_id]:
            shutil.copy2(png_path, output_dir / 'images' / 'val' / png_path.name)
            shutil.copy2(txt_path, output_dir / 'labels' / 'val' / txt_path.name)
            val_count += 1
            
    print("\n" + "="*40)
    print("DATASET SPLIT SUMMARY")
    print("="*40)
    print(f"Total sites: {len(site_ids)}")
    print(f"Total valid images with labels: {train_count + val_count}")
    print("\n--- TRAIN ---")
    print(f"Site IDs ({len(train_sites)}): {', '.join(train_sites)}")
    print(f"Total Images: {train_count}")
    
    print("\n--- VAL ---")
    print(f"Site IDs ({len(val_sites)}): {', '.join(val_sites)}")
    print(f"Total Images: {val_count}")
    print("="*40)
    print(f"Output directory: {output_dir}")

if __name__ == '__main__':
    main()
