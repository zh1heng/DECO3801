from pathlib import Path
from collections import defaultdict

root = Path(r"C:\Users\21590\Downloads\segmentation mask 1.1")
jpeg_dir = root / "JPEGImages"
mask_dir = root / "SegmentationClass"

jpeg_dict = defaultdict(list)
mask_dict = defaultdict(list)

for f in jpeg_dir.iterdir():
    if f.is_file():
        jpeg_dict[f.stem].append(f.name)

for f in mask_dir.iterdir():
    if f.is_file():
        mask_dict[f.stem].append(f.name)

jpeg_names = set(jpeg_dict.keys())
mask_names = set(mask_dict.keys())

only_in_jpeg = sorted(jpeg_names - mask_names)
only_in_mask = sorted(mask_names - jpeg_names)

print("=== 只在 JPEGImages 里有的文件 ===")
for stem in only_in_jpeg:
    print(jpeg_dict[stem])

print("\n=== 只在 SegmentationClass 里有的文件 ===")
for stem in only_in_mask:
    print(mask_dict[stem])

print("\n=== 统计 ===")
print(f"JPEGImages 数量: {len(jpeg_names)}")
print(f"SegmentationClass 数量: {len(mask_names)}")
print(f"只在 JPEGImages: {len(only_in_jpeg)}")
print(f"只在 SegmentationClass: {len(only_in_mask)}")