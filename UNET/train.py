import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["MPLBACKEND"] = "Agg"

from pathlib import Path
import random
import gc
import math

import numpy as np
from PIL import Image

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# =========================
# 1. 配置
# =========================
DATA_ROOT = Path(r"C:\Users\21590\3801 pro14\unet\segmentation mask 1.1\unet_dataset")

TRAIN_IMAGE_DIR = DATA_ROOT / "images" / "train"
TRAIN_MASK_DIR = DATA_ROOT / "masks" / "train"
VAL_IMAGE_DIR = DATA_ROOT / "images" / "val"
VAL_MASK_DIR = DATA_ROOT / "masks" / "val"

SAVE_DIR = Path(r"C:\Users\21590\3801 pro14\unet\checkpoints_8gb_safe_v2")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

NUM_CLASSES = 4
BATCH_SIZE = 1
EPOCHS = 25
LEARNING_RATE = 1e-3
NUM_WORKERS = 0
IMAGE_SIZE = (256, 256)   # 8GB 显卡先用这个
RANDOM_SEED = 42

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE_TYPE = "cuda" if torch.cuda.is_available() else "cpu"
USE_AMP = DEVICE_TYPE == "cuda"

# 类别权重：按你的类别顺序改
# 0=background, 1=Main Content, 2=Navigation, 3=Secondary
# 背景通常太多，所以给小一点；小类给大一点
CLASS_WEIGHTS = [0.4, 1.0, 1.8, 1.8]

# Loss 权重
CE_WEIGHT = 0.6
DICE_WEIGHT = 0.4

# 是否每个 epoch 保存一张验证预测图
SAVE_PREVIEW_EACH_EPOCH = True


# =========================
# 2. 随机种子
# =========================
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# =========================
# 3. 数据集
# =========================
class WebSegDataset(Dataset):
    def __init__(self, image_dir: Path, mask_dir: Path, image_size=(256, 256), augment=False):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.image_size = image_size
        self.augment = augment

        self.image_files = sorted([
            p for p in self.image_dir.iterdir()
            if p.is_file() and p.suffix.lower() in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]
        ])

        if not self.image_files:
            raise ValueError(f"在 {self.image_dir} 没找到图片。")

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_path = self.image_files[idx]
        mask_path = self.mask_dir / f"{img_path.stem}.png"

        if not mask_path.exists():
            raise FileNotFoundError(f"找不到对应 mask: {mask_path}")

        image = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")

        if self.image_size is not None:
            image = image.resize(self.image_size, Image.BILINEAR)
            mask = mask.resize(self.image_size, Image.NEAREST)

        image = np.array(image, dtype=np.uint8)
        mask = np.array(mask, dtype=np.uint8)

        # 轻量数据增强，省显存
        if self.augment:
            if random.random() < 0.5:
                image = np.fliplr(image).copy()
                mask = np.fliplr(mask).copy()

            if random.random() < 0.2:
                image = np.flipud(image).copy()
                mask = np.flipud(mask).copy()

            # 轻微亮度扰动
            if random.random() < 0.3:
                factor = random.uniform(0.85, 1.15)
                image = np.clip(image.astype(np.float32) * factor, 0, 255).astype(np.uint8)

        image = image.astype(np.float32) / 255.0
        mask = mask.astype(np.int64)

        # HWC -> CHW
        image = np.transpose(image, (2, 0, 1))

        image = torch.tensor(image, dtype=torch.float32)
        mask = torch.tensor(mask, dtype=torch.long)

        return image, mask


# =========================
# 4. U-Net（缩小版）
# =========================
class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),

            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.block(x)


class UNet(nn.Module):
    def __init__(self, in_channels=3, num_classes=4, features=(16, 32, 64, 128)):
        super().__init__()

        self.downs = nn.ModuleList()
        self.ups = nn.ModuleList()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        current_in = in_channels
        for feature in features:
            self.downs.append(DoubleConv(current_in, feature))
            current_in = feature

        self.bottleneck = DoubleConv(features[-1], features[-1] * 2)

        rev_features = features[::-1]
        current_in = features[-1] * 2

        for feature in rev_features:
            self.ups.append(
                nn.ConvTranspose2d(current_in, feature, kernel_size=2, stride=2)
            )
            self.ups.append(DoubleConv(feature * 2, feature))
            current_in = feature

        self.final_conv = nn.Conv2d(features[0], num_classes, kernel_size=1)

    def forward(self, x):
        skip_connections = []

        for down in self.downs:
            x = down(x)
            skip_connections.append(x)
            x = self.pool(x)

        x = self.bottleneck(x)
        skip_connections = skip_connections[::-1]

        for idx in range(0, len(self.ups), 2):
            x = self.ups[idx](x)
            skip = skip_connections[idx // 2]

            if x.shape[2:] != skip.shape[2:]:
                x = F.interpolate(x, size=skip.shape[2:], mode="bilinear", align_corners=False)

            x = torch.cat((skip, x), dim=1)
            x = self.ups[idx + 1](x)

        return self.final_conv(x)


# =========================
# 5. Loss
# =========================
class DiceLoss(nn.Module):
    """
    多分类 Dice Loss
    输入:
      logits: [B, C, H, W]
      targets: [B, H, W]
    """
    def __init__(self, num_classes, smooth=1e-6):
        super().__init__()
        self.num_classes = num_classes
        self.smooth = smooth

    def forward(self, logits, targets):
        probs = torch.softmax(logits, dim=1)  # [B, C, H, W]

        # [B, H, W] -> [B, H, W, C] -> [B, C, H, W]
        targets_one_hot = F.one_hot(targets, num_classes=self.num_classes).permute(0, 3, 1, 2).float()

        dims = (0, 2, 3)
        intersection = torch.sum(probs * targets_one_hot, dims)
        cardinality = torch.sum(probs + targets_one_hot, dims)

        dice_per_class = (2.0 * intersection + self.smooth) / (cardinality + self.smooth)
        dice_loss = 1.0 - dice_per_class.mean()

        return dice_loss


class CombinedLoss(nn.Module):
    def __init__(self, num_classes, class_weights=None, ce_weight=0.6, dice_weight=0.4):
        super().__init__()
        self.ce_weight = ce_weight
        self.dice_weight = dice_weight

        if class_weights is not None:
            weight_tensor = torch.tensor(class_weights, dtype=torch.float32)
        else:
            weight_tensor = None

        self.ce = nn.CrossEntropyLoss(weight=weight_tensor)
        self.dice = DiceLoss(num_classes=num_classes)

    def forward(self, logits, targets):
        # 确保 ce 的权重在同设备上
        if self.ce.weight is not None and self.ce.weight.device != logits.device:
            self.ce.weight = self.ce.weight.to(logits.device)

        ce_loss = self.ce(logits, targets)
        dice_loss = self.dice(logits, targets)
        total = self.ce_weight * ce_loss + self.dice_weight * dice_loss
        return total, ce_loss.detach(), dice_loss.detach()


# =========================
# 6. 指标
# =========================
@torch.no_grad()
def pixel_accuracy(preds, masks):
    pred_labels = torch.argmax(preds, dim=1)
    correct = (pred_labels == masks).sum().item()
    total = masks.numel()
    return correct / total


@torch.no_grad()
def mean_iou(preds, masks, num_classes):
    pred_labels = torch.argmax(preds, dim=1)
    ious = []

    for cls in range(num_classes):
        pred_cls = (pred_labels == cls)
        mask_cls = (masks == cls)

        intersection = (pred_cls & mask_cls).sum().item()
        union = (pred_cls | mask_cls).sum().item()

        if union == 0:
            continue

        ious.append(intersection / union)

    if not ious:
        return 0.0

    return sum(ious) / len(ious)


# =========================
# 7. 训练 / 验证
# =========================
def train_one_epoch(model, loader, optimizer, criterion, scaler, device):
    model.train()

    total_loss = 0.0
    total_ce = 0.0
    total_dice = 0.0
    total_acc = 0.0
    total_iou = 0.0

    for images, masks in loader:
        images = images.to(device, non_blocking=True)
        masks = masks.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        with torch.amp.autocast(device_type=DEVICE_TYPE, enabled=USE_AMP):
            outputs = model(images)
            loss, ce_loss, dice_loss = criterion(outputs, masks)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        total_loss += loss.item()
        total_ce += ce_loss.item()
        total_dice += dice_loss.item()
        total_acc += pixel_accuracy(outputs.detach(), masks)
        total_iou += mean_iou(outputs.detach(), masks, NUM_CLASSES)

        del images, masks, outputs, loss, ce_loss, dice_loss

    n = len(loader)
    return (
        total_loss / n,
        total_ce / n,
        total_dice / n,
        total_acc / n,
        total_iou / n,
    )


@torch.no_grad()
def validate_one_epoch(model, loader, criterion, device):
    model.eval()

    total_loss = 0.0
    total_ce = 0.0
    total_dice = 0.0
    total_acc = 0.0
    total_iou = 0.0

    for images, masks in loader:
        images = images.to(device, non_blocking=True)
        masks = masks.to(device, non_blocking=True)

        with torch.amp.autocast(device_type=DEVICE_TYPE, enabled=USE_AMP):
            outputs = model(images)
            loss, ce_loss, dice_loss = criterion(outputs, masks)

        total_loss += loss.item()
        total_ce += ce_loss.item()
        total_dice += dice_loss.item()
        total_acc += pixel_accuracy(outputs, masks)
        total_iou += mean_iou(outputs, masks, NUM_CLASSES)

        del images, masks, outputs, loss, ce_loss, dice_loss

    n = len(loader)
    return (
        total_loss / n,
        total_ce / n,
        total_dice / n,
        total_acc / n,
        total_iou / n,
    )


# =========================
# 8. 可视化
# =========================
@torch.no_grad()
def save_prediction_sample(model, dataset, save_path, device, idx=0):
    if len(dataset) == 0:
        return

    idx = min(idx, len(dataset) - 1)
    image, mask = dataset[idx]
    input_tensor = image.unsqueeze(0).to(device)

    model.eval()
    with torch.amp.autocast(device_type=DEVICE_TYPE, enabled=USE_AMP):
        output = model(input_tensor)

    pred = torch.argmax(output, dim=1).squeeze(0).cpu().numpy()
    image_np = image.permute(1, 2, 0).cpu().numpy()
    mask_np = mask.cpu().numpy()

    fig = plt.figure(figsize=(12, 4))

    ax1 = fig.add_subplot(1, 3, 1)
    ax1.imshow(image_np)
    ax1.set_title("Image")
    ax1.axis("off")

    ax2 = fig.add_subplot(1, 3, 2)
    ax2.imshow(mask_np, vmin=0, vmax=NUM_CLASSES - 1)
    ax2.set_title("Ground Truth")
    ax2.axis("off")

    ax3 = fig.add_subplot(1, 3, 3)
    ax3.imshow(pred, vmin=0, vmax=NUM_CLASSES - 1)
    ax3.set_title("Prediction")
    ax3.axis("off")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)

    del input_tensor, output


def plot_history(history, save_dir: Path):
    epochs = range(1, len(history["train_loss"]) + 1)

    plt.figure(figsize=(8, 5))
    plt.plot(epochs, history["train_loss"], label="Train Loss")
    plt.plot(epochs, history["val_loss"], label="Val Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Total Loss Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_dir / "loss_curve.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(epochs, history["train_iou"], label="Train mIoU")
    plt.plot(epochs, history["val_iou"], label="Val mIoU")
    plt.xlabel("Epoch")
    plt.ylabel("mIoU")
    plt.title("mIoU Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_dir / "iou_curve.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(epochs, history["train_ce"], label="Train CE")
    plt.plot(epochs, history["val_ce"], label="Val CE")
    plt.plot(epochs, history["train_dice"], label="Train Dice")
    plt.plot(epochs, history["val_dice"], label="Val Dice")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("CE / Dice Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_dir / "ce_dice_curve.png")
    plt.close()


# =========================
# 9. 主程序
# =========================
def main():
    set_seed(RANDOM_SEED)

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    print("Using device:", DEVICE)
    print("AMP enabled:", USE_AMP)

    train_dataset = WebSegDataset(
        TRAIN_IMAGE_DIR,
        TRAIN_MASK_DIR,
        image_size=IMAGE_SIZE,
        augment=True,
    )

    val_dataset = WebSegDataset(
        VAL_IMAGE_DIR,
        VAL_MASK_DIR,
        image_size=IMAGE_SIZE,
        augment=False,
    )

    print("Train samples:", len(train_dataset))
    print("Val samples:", len(val_dataset))

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=(DEVICE_TYPE == "cuda"),
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=1,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=(DEVICE_TYPE == "cuda"),
    )

    model = UNet(
        in_channels=3,
        num_classes=NUM_CLASSES,
        features=(16, 32, 64, 128)
    ).to(DEVICE)

    criterion = CombinedLoss(
        num_classes=NUM_CLASSES,
        class_weights=CLASS_WEIGHTS,
        ce_weight=CE_WEIGHT,
        dice_weight=DICE_WEIGHT,
    )

    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scaler = torch.amp.GradScaler(device=DEVICE_TYPE, enabled=USE_AMP)

    best_val_iou = -1.0

    history = {
        "train_loss": [],
        "train_ce": [],
        "train_dice": [],
        "train_acc": [],
        "train_iou": [],
        "val_loss": [],
        "val_ce": [],
        "val_dice": [],
        "val_acc": [],
        "val_iou": [],
    }

    for epoch in range(1, EPOCHS + 1):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        train_loss, train_ce, train_dice, train_acc, train_iou = train_one_epoch(
            model, train_loader, optimizer, criterion, scaler, DEVICE
        )

        val_loss, val_ce, val_dice, val_acc, val_iou = validate_one_epoch(
            model, val_loader, criterion, DEVICE
        )

        history["train_loss"].append(train_loss)
        history["train_ce"].append(train_ce)
        history["train_dice"].append(train_dice)
        history["train_acc"].append(train_acc)
        history["train_iou"].append(train_iou)

        history["val_loss"].append(val_loss)
        history["val_ce"].append(val_ce)
        history["val_dice"].append(val_dice)
        history["val_acc"].append(val_acc)
        history["val_iou"].append(val_iou)

        print(
            f"Epoch [{epoch}/{EPOCHS}] | "
            f"Train Loss: {train_loss:.4f} (CE {train_ce:.4f}, Dice {train_dice:.4f}), "
            f"Acc: {train_acc:.4f}, mIoU: {train_iou:.4f} | "
            f"Val Loss: {val_loss:.4f} (CE {val_ce:.4f}, Dice {val_dice:.4f}), "
            f"Acc: {val_acc:.4f}, mIoU: {val_iou:.4f}"
        )

        # 每轮都保存
        torch.save(model.state_dict(), SAVE_DIR / "last_model.pth")

        if val_iou > best_val_iou:
            best_val_iou = val_iou
            torch.save(model.state_dict(), SAVE_DIR / "best_model.pth")
            print(f"保存最佳模型，Val mIoU = {best_val_iou:.4f}")

        # 每轮尝试存一张预测图，避免最后报错导致一张都没有
        if SAVE_PREVIEW_EACH_EPOCH:
            try:
                preview_path = SAVE_DIR / f"preview_epoch_{epoch:03d}.png"
                save_prediction_sample(model, val_dataset, preview_path, DEVICE, idx=0)
            except Exception as e:
                print(f"[警告] 第 {epoch} 轮预览图保存失败: {e}")

    plot_history(history, SAVE_DIR)

    # 训练结束后再额外存几张
    try:
        for i in range(min(3, len(val_dataset))):
            save_prediction_sample(
                model,
                val_dataset,
                SAVE_DIR / f"final_sample_{i}.png",
                DEVICE,
                idx=i,
            )
    except Exception as e:
        print(f"[警告] 最终样例图保存失败: {e}")

    print("训练完成。")
    print("最佳模型:", SAVE_DIR / "best_model.pth")
    print("最新模型:", SAVE_DIR / "last_model.pth")
    print("结果目录:", SAVE_DIR)


if __name__ == "__main__":
    main()