import os
import csv
import shutil
from pathlib import Path
from ultralytics import YOLO

def calculate_iou(box1, box2):
    """
    计算两个归一化边界框的 IoU
    box: [x_center, y_center, width, height]
    """
    # 转换为 [x_min, y_min, x_max, y_max]
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
        print("请检查 dataset_yolo 目录结构是否正确。")
        return

    # 加载模型
    print(f"正在加载模型: {weights_path}")
    model = YOLO(str(weights_path))

    # 输出目录配置
    output_dir = Path("suspicious_dataset")
    out_images_dir = output_dir / "images"
    out_labels_dir = output_dir / "labels"
    out_preds_dir = output_dir / "predictions"
    
    # 自动创建目录
    for d in [out_images_dir, out_labels_dir, out_preds_dir]:
        d.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "report.csv"
    splits = ["train", "val"]
    
    total_checked = 0
    total_suspicious = 0
    
    # 存放所有可疑数据的列表，用于后续排序
    results_list = []

    print("开始筛查数据集...")
    for split in splits:
        images_dir = base_dir / "images" / split
        labels_dir = base_dir / "labels" / split
        
        if not images_dir.exists():
            print(f"警告: 找不到目录 {images_dir}，已跳过")
            continue
            
        # 遍历所有图片
        for img_path in images_dir.glob("*.*"):
            if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                continue
                
            total_checked += 1
            label_path = labels_dir / f"{img_path.stem}.txt"
            
            # 运行模型推理 (verbose=False 避免控制台输出过多)
            results = model(str(img_path), verbose=False)
            result = results[0]
            
            # 读取对应的 GT (Ground Truth)
            gt_classes = []
            gt_boxes = []
            if label_path.exists():
                with open(label_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            gt_classes.append(int(parts[0]))
                            gt_boxes.append([float(x) for x in parts[1:5]])
                            
            # 提取预测结果
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
            
            # 检查条件 1: 原始 label 有框，但模型完全没预测到
            if len(gt_boxes) > 0 and len(pred_boxes) == 0:
                suspicious = True
                reasons.add("gt_exist_pred_none")
                
            # 检查条件 4: 原始 label 为空但模型高置信度检测到目标 (conf > 0.7)
            if len(gt_boxes) == 0 and len(pred_boxes) > 0 and max_conf_overall > 0.7:
                suspicious = True
                reasons.add("gt_empty_pred_exist")
                
            # 当预测框和 GT 框都存在时，计算交并比 (IoU) 进行详细比对
            if len(gt_boxes) > 0 and len(pred_boxes) > 0:
                # 遍历每个预测框，寻找匹配的 GT 框
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
                        
                    # 检查条件 3: 预测框和原始框的最大 IoU < 0.5 (中/高风险)
                    if max_iou_for_pred < 0.5:
                        suspicious = True
                        reasons.add("low_iou")
                        
                    # 检查条件 2: 置信度 conf > 0.7，且找到了重合框 (IoU >= 0.2)，但类别不一致
                    if p_conf > 0.7 and max_iou_for_pred >= 0.2 and p_cls != matched_gt_cls:
                        suspicious = True
                        reasons.add("class_mismatch")
                        
                # 遍历每个 GT 框，检查是否有漏检 (该 GT 框与所有预测框的 IoU 都 < 0.5)
                for j, g_box in enumerate(gt_boxes):
                    max_iou_for_gt = 0.0
                    for i, p_box in enumerate(pred_boxes):
                        iou = calculate_iou(p_box, g_box)
                        if iou > max_iou_for_gt:
                            max_iou_for_gt = iou
                    
                    if max_iou_for_gt < 0.5:
                        suspicious = True
                        reasons.add("low_iou")
                        
            # 如果判定为可疑数据，计算严重程度和优先级得分
            if suspicious:
                total_suspicious += 1
                
                # 1. 判定 severity
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

                # 4. 计算 priority_score
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
                    "max_iou_overall": max_iou_overall,
                    "max_conf_overall": max_conf_overall,
                    "result": result
                })

    # 6. 按 priority_score 从高到低排序
    results_list.sort(key=lambda x: x["priority_score"], reverse=True)

    # 准备 CSV 报告并保存文件
    with open(report_path, "w", newline="", encoding="utf-8-sig") as csv_file:
        csv_writer = csv.writer(csv_file)
        # 5. 写入表头
        csv_writer.writerow([
            "image_name", "split", "reason", "severity", 
            "priority_score", "gt_classes", "pred_classes", 
            "max_iou", "max_conf"
        ])
        
        for item in results_list:
            img_path = item["img_path"]
            label_path = item["label_path"]
            
            # 写入 CSV 记录
            csv_writer.writerow([
                img_path.name,
                item["split"],
                item["reason_str"],
                item["severity"],
                f"{item['priority_score']:.4f}",
                str(item["gt_classes"]),
                str(item["pred_classes"]),
                f"{item['max_iou_overall']:.4f}",
                f"{item['max_conf_overall']:.4f}"
            ])
            
            # 8. 复制图片和标签 (不自动删除)
            shutil.copy2(img_path, out_images_dir / img_path.name)
            if label_path.exists():
                shutil.copy2(label_path, out_labels_dir / label_path.name)
                
            # 7. 保存带预测框的可视化图片，文件名包含 severity 和 reason
            safe_reason = item["reason_str"].replace(" | ", "_").replace(" ", "_")
            pred_filename = f"{item['severity']}_{safe_reason}_{img_path.name}"
            pred_img_path = out_preds_dir / pred_filename
            item["result"].save(filename=str(pred_img_path))

    print("\n" + "="*40)
    print("筛查及分析完成！")
    print(f"共检查图片: {total_checked} 张")
    print(f"发现可疑图片: {total_suspicious} 张")
    print(f"报告已按优先度得分排序，结果保存在:\n {output_dir.absolute()}")
    print("="*40)

if __name__ == "__main__":
    main()
