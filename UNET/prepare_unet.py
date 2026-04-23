from pathlib import Path
import random
import shutil
import re

import numpy as np
from PIL import Image


# ========= 你可以改的设置 =========
ROOT = Path(r"C:\Users\21590\3801 pro14\unet\segmentation mask 1.1")
IMAGE_DIR = ROOT / "JPEGImages"
MASK_DIR = ROOT / "SegmentationClass"
LABELMAP_PATH = ROOT / "labelmap.txt"

OUTPUT_DIR = ROOT / "unet_dataset"

TRAIN_RATIO = 0.8
RANDOM_SEED = 42

# 是否统一缩放
RESIZE = False
TARGET_SIZE = (512, 512)  # (width, height)，只有 RESIZE=True 才生效

# 允许的图片后缀
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MASK_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
# ================================


def parse_labelmap(labelmap_path: Path):
    """
    读取 labelmap.txt
    格式示例：
    Main Content:148,64,93::
    Navigation:22,54,91::
    Secondary:29,39,150::
    background:0,0,0::
    """
    if not labelmap_path.exists():
        raise FileNotFoundError(f"找不到 labelmap.txt: {labelmap_path}")

    color_to_class = {}
    class_to_name = {}

    lines = labelmap_path.read_text(encoding="utf-8").splitlines()

    parsed = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        m = re.match(r"^(.*?):(\d+),(\d+),(\d+)::", line)
        if not m:
            print(f"[跳过] 无法解析这一行: {line}")
            continue

        class_name = m.group(1).strip()
        color = (int(m.group(2)), int(m.group(3)), int(m.group(4)))
        parsed.append((class_name, color))

    if not parsed:
        raise ValueError("labelmap.txt 没有解析出任何类别。")

    # 强制 background 为 0，其他按文件顺序编号
    next_class_id = 1
    for class_name, color in parsed:
        if class_name.lower() == "background":
            color_to_class[color] = 0
            class_to_name[0] = class_name

    for class_name, color in parsed:
        if class_name.lower() == "background":
            continue
        color_to_class[color] = next_class_id
        class_to_name[next_class_id] = class_name
        next_class_id += 1

    return color_to_class, class_to_name


def ensure_dirs():
    for p in [
        OUTPUT_DIR / "images" / "train",
        OUTPUT_DIR / "images" / "val",
        OUTPUT_DIR / "masks" / "train",
        OUTPUT_DIR / "masks" / "val",
    ]:
        p.mkdir(parents=True, exist_ok=True)


def collect_files_by_stem(folder: Path, allowed_exts: set[str]):
    files = {}
    for f in folder.iterdir():
        if f.is_file() and f.suffix.lower() in allowed_exts:
            files[f.stem] = f
    return files


def resize_image_if_needed(img: Image.Image, is_mask: bool):
    if not RESIZE:
        return img

    if is_mask:
        return img.resize(TARGET_SIZE, Image.NEAREST)
    return img.resize(TARGET_SIZE, Image.BILINEAR)


def rgb_mask_to_index_mask(mask_path: Path, color_to_class: dict):
    """
    把 RGB mask 转成单通道类别图
    """
    mask = Image.open(mask_path).convert("RGB")
    mask = resize_image_if_needed(mask, is_mask=True)
    mask_np = np.array(mask, dtype=np.uint8)

    h, w, _ = mask_np.shape
    class_mask = np.full((h, w), 255, dtype=np.uint8)

    unique_colors = set(map(tuple, mask_np.reshape(-1, 3)))

    for color, class_id in color_to_class.items():
        match = np.all(mask_np == np.array(color, dtype=np.uint8), axis=-1)
        class_mask[match] = class_id

    unknown_colors = [c for c in unique_colors if c not in color_to_class]
    if unknown_colors:
        raise ValueError(
            f"{mask_path.name} 出现未定义颜色：{unknown_colors}\n"
            f"请检查标注图是否有杂色、抗锯齿、JPEG压缩，或 labelmap.txt 没写全。"
        )

    if np.any(class_mask == 255):
        raise ValueError(f"{mask_path.name} 仍有未映射像素。")

    return Image.fromarray(class_mask, mode="L")


def process_image(img_path: Path):
    img = Image.open(img_path).convert("RGB")
    img = resize_image_if_needed(img, is_mask=False)
    return img


def main():
    if not IMAGE_DIR.exists():
        raise FileNotFoundError(f"找不到 JPEGImages: {IMAGE_DIR}")
    if not MASK_DIR.exists():
        raise FileNotFoundError(f"找不到 SegmentationClass: {MASK_DIR}")

    color_to_class, class_to_name = parse_labelmap(LABELMAP_PATH)

    print("=== 类别映射 ===")
    for class_id in sorted(class_to_name):
        print(f"{class_id}: {class_to_name[class_id]}")
    print()

    print("=== 颜色映射 ===")
    for color, class_id in color_to_class.items():
        print(f"{color} -> {class_id} ({class_to_name[class_id]})")
    print()

    image_files = collect_files_by_stem(IMAGE_DIR, IMAGE_EXTS)
    mask_files = collect_files_by_stem(MASK_DIR, MASK_EXTS)

    image_stems = set(image_files.keys())
    mask_stems = set(mask_files.keys())

    only_in_images = sorted(image_stems - mask_stems)
    only_in_masks = sorted(mask_stems - image_stems)

    if only_in_images:
        print("=== 只在 JPEGImages 里的文件 ===")
        for s in only_in_images:
            print(image_files[s].name)
        print()

    if only_in_masks:
        print("=== 只在 SegmentationClass 里的文件 ===")
        for s in only_in_masks:
            print(mask_files[s].name)
        print()

    common_stems = sorted(image_stems & mask_stems)

    if not common_stems:
        raise ValueError("没有找到任何同名 image-mask 配对文件。")

    print(f"成功配对数量: {len(common_stems)}")

    random.seed(RANDOM_SEED)
    random.shuffle(common_stems)

    train_count = int(len(common_stems) * TRAIN_RATIO)
    train_stems = common_stems[:train_count]
    val_stems = common_stems[train_count:]

    print(f"训练集数量: {len(train_stems)}")
    print(f"验证集数量: {len(val_stems)}")
    print()

    ensure_dirs()

    for subset_name, stems in [("train", train_stems), ("val", val_stems)]:
        print(f"=== 处理 {subset_name} ===")
        for stem in stems:
            img_path = image_files[stem]
            mask_path = mask_files[stem]

            out_img_path = OUTPUT_DIR / "images" / subset_name / f"{stem}.png"
            out_mask_path = OUTPUT_DIR / "masks" / subset_name / f"{stem}.png"

            img = process_image(img_path)
            img.save(out_img_path)

            class_mask = rgb_mask_to_index_mask(mask_path, color_to_class)
            class_mask.save(out_mask_path)

            print(f"已输出: {stem}.png")

    print("\n完成。")
    print(f"输出目录: {OUTPUT_DIR}")
    print("\nmask 像素值含义：")
    for class_id in sorted(class_to_name):
        print(f"{class_id} = {class_to_name[class_id]}")


if __name__ == "__main__":
    main()