import os
from database.focus_detection.data_analyse.utils import create_dict, ill_acc_dict
import cv2

size_dict = {50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 0, 350: 0, 400: 0, 450: 0, 500: 0,
             550: 0, 600: 0, 650: 0, 700: 0, 750: 0, 800: 0, 850: 0, 900: 0, 950: 0, 1000: 0}



ill_precision = ill_acc_dict.copy()  # 包含该疾病的pre，用于计算类别的precision
ill_recall = ill_acc_dict.copy()  # 包含该疾病的gt，用于计算类别的precision
ill_TP = ill_acc_dict.copy()  # 均包含该疾病的图片数
box_precision = ill_acc_dict.copy()  # 标注框的precision
box_recall = ill_acc_dict.copy()  # 标注框的recall


def calculate_size(size_list, img_size):
    width = size_list[2] - size_list[0] + 1
    height = size_list[3] - size_list[1] + 1
    size = width * height
    size_percent = float(size / img_size) * 100
    return size_percent





def double_dict(ill, size):
    if size in size_dict[ill].keys():
        size_dict[ill][size] += 1
    else:
        par = size_dict
        par = par.setdefault(ill, {})
        par[size] = 1


# 统计每个病灶标注框长宽分布
def state_box_size(txt_path, img_path, size_path, ill):
    for name in os.listdir(txt_path):
        with open(os.path.join(txt_path1, name), 'r') as f1:
            dict1 = create_dict(f1)

        img = cv2.imread(os.path.join(img_path, name[:-3] + 'jpg'))
        img_size = img.shape[0] * img.shape[1]
        if ill in dict1.keys():
            for item in dict1[ill]:
                size = calculate_size(item, img_size)
                # print(size)
                if size % 5 == 0:
                    a = size
                else:
                    a = (int(size / 5) + 1) * 5
                size_dict[a] += 1
    print(ill, size_dict)


txt_path1 = 'E:\\0726_ai_annotation\\testcode\\tag_doctor'
img_path = 'E:\\0726_ai_annotation\\testcode\image'
record_path = 'E:\\0726_ai_annotation\\1021_phase1\病灶\\ill_0214.xlsx'
for illness in range(30):
    illness = illness + 1
    state_box_size(txt_path1, img_path, record_path, illness)
