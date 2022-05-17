import os
from ..tmp import compute_iou, create_dict, ill_acc_dict, ill_map
import pandas as pd


ill_precision = ill_acc_dict.copy()  # 包含该疾病的pre，用于计算类别的precision
ill_recall = ill_acc_dict.copy()  # 包含该疾病的gt，用于计算类别的precision
ill_TP = ill_acc_dict.copy()  # 均包含该疾病的图片数
box_precision = ill_acc_dict.copy()  # 标注框的precision
box_recall = ill_acc_dict.copy()  # 标注框的recall

size_dict = ill_map.copy()
for key in size_dict.keys():
    size_dict[key] = {}


def compare_illness(dict1, dict2):
    for k1 in dict1.keys():
        ill_precision[k1] += 1
        if k1 in dict2.keys():
            ill_TP[k1] += 1
    for k2 in dict2.keys():
        ill_recall[k2] += 1


# 计算该张图中，都出现的病灶的一致度
def compare_box(dict1, dict2):
    # 对都出现的病灶，去计算标注框的一致度
    for k in dict2.keys():
        if k in dict1.keys():  # 标注中有该病灶
            gt = len(dict2[k])
            pre = len(dict1[k])
            TP = 0
            for i in range(len(dict2[k])):
                iou_list = []
                for j in range(len(dict1[k])):
                    iou = float('%.2f' % compute_iou(dict2[k][i], dict1[k][j], 'iou'))
                    iou_list.append(iou)
                iou_list.sort(reverse=True)
                if iou_list[0] >= 0.5:
                    TP += 1
            precision = float(TP / pre)
            recall = float(TP / gt)
            box_precision[k] += precision
            box_recall[k] += recall


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

    for k in ill_TP.keys():
        ill_precision[k] = -1 if ill_precision[k] == 0 else float(ill_TP[k] / ill_precision[k] * 100)
        ill_recall[k] = -1 if ill_recall[k] == 0 else float(ill_TP[k] / ill_recall[k] * 100)
        box_precision[k] = 0 if ill_TP[k] == 0 else float(box_precision[k] / ill_TP[k] * 100)
        box_recall[k] = 0 if ill_TP[k] == 0 else float(box_recall[k] / ill_TP[k] * 100)

    new_record = pd.DataFrame(None, columns=['病灶', '病灶类型精确度', '病灶类型召回率', '病灶定位精确度', '病灶定位召回率'])
    index = 0
    for k in ill_TP.keys():
        name = ill_map[k].split('：')[-1]
        if ill_precision[k] % 1 != 0:
            ill_precision[k] = round(ill_precision[k], 2)
        if ill_recall[k] % 1 != 0:
            ill_recall[k] = round(ill_recall[k], 2)
        if box_precision[k] % 1 != 0:
            box_precision[k] = round(box_precision[k], 2)
        if box_recall[k] % 1 != 0:
            box_recall[k] = round(box_recall[k], 2)

        new_record.loc[index] = [name, ill_precision[k], ill_recall[k], box_precision[k], box_recall[k]]
        index += 1
    new_record.to_excel(record_path)
    print('图片数：', img_num)
