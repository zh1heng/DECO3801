import os
import csv
import shutil
from pathlib import Path
import cv2
from ultralytics import YOLO

def calculate_iou(box1, box2):
    """
    计算两个归一化边界框的 IoU
    box: [x_center, y_center, width, height]
    """
    b1_x1 = box1[0] - box1[2] / 2
    b1_y1 = box1[1] - box1[3] / 2
    b1_x2 = box1[0] + box1[2] / 2
    b1_y2 = box1[1] + box1[3] / 2
    
    b2_x1 = box2[0] - box2[2] / 2
    b2_y1 = box2[1] - box2[3] / 2
    b2_x2 = box2[0] + box2[2] / 2
    b2_y2 = box2[1] + box2[3] / 2
    
    inter_x1 = max(b1_x1, b2_x1)
    inter_y1 = max(b1_y1, b2_y1)
    inter_x2 = min(b1_x2, b2_x2)
    inter_y2 = min(b1_y2, b2_y2)
    
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    b1_area = box1[2] * box1[3]
    b2_area = box2[2] * box2[3]
    
    union_area = b1_area + b2_area - inter_area
    if union_area == 0:
        return 0
    return inter_area / union_area

def main():
    # 路径配置
    base_dir = Path("dataset_yolo")
    weights_path = base_dir / "runs" / "detect" / "train" / "weights" / "best.pt"
    
    if not weights_path.exists():
        print(f"错误: 找不到模型权重文件: {weights_path}")
        return

    # 加载模型
    print(f"正在加载模型: {weights_path}")
    model = YOLO(str(weights_path))

    # 输出目录配置
    output_dir = Path("suspicious_dataset")
    out_images_dir = output_dir / "images"
    out_labels_dir = output_dir / "labels"
    out_preds_dir = output_dir / "visualizations"  # 改名为可视化文件夹更准确
    
    # 自动创建目录
    for d in [out_images_dir, out_labels_dir, out_preds_dir]:
        d.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "report.csv"
    splits = ["train", "val"]
    
    total_checked = 0
    total_suspicious = 0
    
    results_list = []

    print("开始筛查数据集...")
    for split in splits:
        images_dir = base_dir / "images" / split
        labels_dir = base_dir / "labels" / split
        
        if not images_dir.exists():
            continue
            
        for img_path in images_dir.glob("*.*"):
            if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                continue
                
            total_checked += 1
            label_path = labels_dir / f"{img_path.stem}.txt"
            
            results = model(str(img_path), verbose=False)
            result = results[0]
            
            # 读取 Ground Truth (人工原始标注)
            gt_classes = []
            gt_boxes = []
            if label_path.exists():
                with open(label_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            gt_classes.append(int(parts[0]))
                            gt_boxes.append([float(x) for x in parts[1:5]])
                            
            # 提取模型预测
            pred_classes = []
            pred_boxes = []
            pred_confs = []
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    pred_classes.append(int(box.cls[0].item()))
                    pred_confs.append(float(box.conf[0].item()))
                    pred_boxes.append(box.xywhn[0].tolist())
                    
            suspicious = False
            reasons = set()
            max_iou_overall = 0.0
            max_conf_overall = max(pred_confs) if pred_confs else 0.0
            
            if len(gt_boxes) > 0 and len(pred_boxes) == 0:
                suspicious = True
                reasons.add("gt_exist_pred_none")
                
            if len(gt_boxes) == 0 and len(pred_boxes) > 0 and max_conf_overall > 0.7:
                suspicious = True
                reasons.add("gt_empty_pred_exist")
                
            if len(gt_boxes) > 0 and len(pred_boxes) > 0:
                for i, p_box in enumerate(pred_boxes):
                    p_cls = pred_classes[i]
                    p_conf = pred_confs[i]
                    
                    max_iou_for_pred = 0.0
                    matched_gt_cls = -1
                    
                    for j, g_box in enumerate(gt_boxes):
                        iou = calculate_iou(p_box, g_box)
                        if iou > max_iou_for_pred:
                            max_iou_for_pred = iou
                            matched_gt_cls = gt_classes[j]
                            
                    if max_iou_for_pred > max_iou_overall:
                        max_iou_overall = max_iou_for_pred
                        
                    if max_iou_for_pred < 0.5:
                        suspicious = True
                        reasons.add("low_iou")
                        
                    if p_conf > 0.7 and max_iou_for_pred >= 0.2 and p_cls != matched_gt_cls:
                        suspicious = True
                        reasons.add("class_mismatch")
                        
                for j, g_box in enumerate(gt_boxes):
                    max_iou_for_gt = 0.0
                    for i, p_box in enumerate(pred_boxes):
                        iou = calculate_iou(p_box, g_box)
                        if iou > max_iou_for_gt:
                            max_iou_for_gt = iou
                    if max_iou_for_gt < 0.5:
                        suspicious = True
                        reasons.add("low_iou")
                        
            if suspicious:
                total_suspicious += 1
                severity = "low"
                if "class_mismatch" in reasons or "gt_empty_pred_exist" in reasons:
                    severity = "high"
                elif len(gt_boxes) > 0 and len(pred_boxes) > 0:
                    if max_iou_overall < 0.2:
                        severity = "high"
                    elif 0.2 <= max_iou_overall < 0.5:
                        severity = "medium"
                    else:
                        severity = "low"
                elif "gt_exist_pred_none" in reasons:
                    severity = "low"

                base_score = max_conf_overall * (1 - max_iou_overall)
                priority_score = base_score
                if "class_mismatch" in reasons:
                    priority_score += 1.0
                if "gt_empty_pred_exist" in reasons:
                    priority_score += 0.8
                if severity == "high":
                    priority_score += 0.5
                    
                reason_str = " | ".join(reasons)
                
                results_list.append({
                    "img_path": img_path,
                    "label_path": label_path,
                    "split": split,
                    "reason_str": reason_str,
                    "severity": severity,
                    "priority_score": priority_score,
                    "gt_classes": gt_classes,
                    "pred_classes": pred_classes,
                    "gt_boxes": gt_boxes,
                    "pred_boxes": pred_boxes,
                    "pred_confs": pred_confs,
                    "max_iou_overall": max_iou_overall,
                    "max_conf_overall": max_conf_overall
                })

    results_list.sort(key=lambda x: x["priority_score"], reverse=True)

    with open(report_path, "w", newline="", encoding="utf-8-sig") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "image_name", "split", "reason", "severity", 
            "priority_score", "gt_classes", "pred_classes", 
            "max_iou", "max_conf"
        ])
        
        for item in results_list:
            img_path = item["img_path"]
            label_path = item["label_path"]
            
            csv_writer.writerow([
                img_path.name, item["split"], item["reason_str"], item["severity"],
                f"{item['priority_score']:.4f}", str(item["gt_classes"]), str(item["pred_classes"]),
                f"{item['max_iou_overall']:.4f}", f"{item['max_conf_overall']:.4f}"
            ])
            
            shutil.copy2(img_path, out_images_dir / img_path.name)
            if label_path.exists():
                shutil.copy2(label_path, out_labels_dir / label_path.name)
                
            # 绘制对比图
            img_cv = cv2.imread(str(img_path))
            if img_cv is not None:
                h, w, _ = img_cv.shape
                
                # 画你的原始标注 (绿色 GT)
                for gt_cls, gt_box in zip(item["gt_classes"], item["gt_boxes"]):
                    x_c, y_c, bw, bh = gt_box
                    x1, y1 = int((x_c - bw/2)*w), int((y_c - bh/2)*h)
                    x2, y2 = int((x_c + bw/2)*w), int((y_c + bh/2)*h)
                    cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img_cv, f"GT:{gt_cls}", (x1, max(15, y1 - 5)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # 画模型预测 (红色 Pred)
                for p_cls, p_conf, p_box in zip(item["pred_classes"], item["pred_confs"], item["pred_boxes"]):
                    # 仅画出置信度大于 0.25 的预测框，避免杂乱
                    if p_conf > 0.25:
                        x_c, y_c, bw, bh = p_box
                        x1, y1 = int((x_c - bw/2)*w), int((y_c - bh/2)*h)
                        x2, y2 = int((x_c + bw/2)*w), int((y_c + bh/2)*h)
                        cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(img_cv, f"Pred:{p_cls}({p_conf:.2f})", (x1, min(h-5, y2 + 20)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                safe_reason = item["reason_str"].replace(" | ", "_").replace(" ", "_")
                pred_filename = f"{item['severity']}_{safe_reason}_{img_path.name}"
                cv2.imwrite(str(out_preds_dir / pred_filename), img_cv)

    print("\n" + "="*40)
    print("筛查完成！")
    print(f"在 {total_checked} 张图片中，找到了 {total_suspicious} 张可疑数据。")
    print(f"请去 {out_preds_dir} 文件夹查看对比图。")
    print("图中：[绿色框] 为你的原始人工标注，[红色框] 为模型预测。")
    print("="*40)

if __name__ == "__main__":
    main()
