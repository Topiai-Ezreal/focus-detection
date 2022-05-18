"""
按病灶类别计算标注一致度
"""

import os
from utils import compute_iou, create_dict, ill_acc_dict, ill_map
import pandas as pd
import numpy as np


ill_precision = ill_acc_dict.copy()  # 包含该疾病的pre，用于计算类别的precision
ill_recall = ill_acc_dict.copy()  # 包含该疾病的gt，用于计算类别的precision
ill_TP = ill_acc_dict.copy()  # 均包含该疾病的图片数
box_precision = ill_acc_dict.copy()  # 标注框的precision
box_recall = ill_acc_dict.copy()  # 标注框的recall
box_TP = ill_acc_dict.copy()


def compare_illness(dict1, dict2):
    for k1 in dict1.keys():
        ill_precision[k1] += 1
        if k1 in dict2.keys():
            ill_TP[k1] += 1
    for k2 in dict2.keys():
        ill_recall[k2] += 1


def compare_box(dict1, dict2):
    for k in box_TP.keys():
        if k in dict1.keys():
            box_precision[k] += len(dict1[k])
        if k in dict2.keys():
            box_recall[k] += len(dict2[k])
        if k in dict1.keys() and k in dict2.keys():
            for i in range(len(dict2[k])):
                iou_list = []
                for j in range(len(dict1[k])):
                    iou = float('%.2f' % compute_iou(dict2[k][i], dict1[k][j], 'iou'))
                    iou_list.append(iou)
                iou_list.sort(reverse=True)
                if iou_list[0] >= 0.5:
                    box_TP[k] += 1


def evaluate_on_illness(txt_path1, txt_path2, record_path):
    img_num = 0  # 图片数

    label_list = os.listdir(txt_path1)
    standard_list = os.listdir(txt_path2)
    for name in label_list:
        if name in standard_list:
            with open(os.path.join(txt_path1, name), 'r') as f1:
                dict1 = create_dict(f1)
            with open(os.path.join(txt_path2, name), 'r') as f2:
                dict2 = create_dict(f2)
            for i in [200, 'grade', 'illness']:
                if i in dict1.keys():
                    del dict1[i]
                if i in dict2.keys():
                    del dict2[i]

            img_num += 1
            compare_illness(dict1, dict2)
            compare_box(dict1, dict2)

    eps = np.finfo(np.float32).eps
    for k in ill_TP.keys():
        box_precision[k] += eps
        box_recall[k] += eps
        box_precision[k] = box_TP[k] / box_precision[k] * 100
        box_recall[k] = box_TP[k] / box_recall[k] * 100

        ill_precision[k] += eps
        ill_recall[k] += eps
        ill_precision[k] = ill_TP[k] / ill_precision[k] * 100
        ill_recall[k] = ill_TP[k] / ill_recall[k] * 100

    new_record = pd.DataFrame(None, columns=['病灶', '病灶类型精确度', '病灶类型召回率', '病灶定位精确度', '病灶定位召回率'])
    index = 0
    for k in ill_TP.keys():
        name = ill_map[k].split('：')[-1]
        ill_precision[k] = round(ill_precision[k], 2) if ill_precision[k] % 1 != 0 else ill_precision[k]
        ill_recall[k] = round(ill_recall[k], 2) if ill_recall[k] % 1 != 0 else ill_recall[k]
        box_precision[k] = round(box_precision[k], 2) if box_precision[k] % 1 != 0 else box_precision[k]
        box_recall[k] = round(box_recall[k], 2) if box_recall[k] % 1 != 0 else box_recall[k]

        new_record.loc[index] = [name, ill_precision[k], ill_recall[k], box_precision[k], box_recall[k]]
        index += 1
    new_record.to_excel(record_path)
    print('图片数：', img_num)


annotations1 = ''   # 标注文件储存路径
annotations2 = ''
record = ''
evaluate_on_illness(annotations1, annotations2, record)
