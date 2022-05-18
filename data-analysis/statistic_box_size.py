import os
from utils import create_dict
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


ill_map = {1:' 1：视网膜前膜',2:' 2：视网膜裂孔',3:' 3：玻璃体黄斑牵拉',4:' 4：视网膜囊性变样',5:' 5：视网膜劈裂',
           7:' 7：黄斑水肿（非囊性）',8:' 8：视网膜内液',9:' 9：视网膜下积液',10:'10：弥漫性高反射病灶',11:'11：局部网膜内高反射点',
           12:'12：视网膜色素上皮（RPE）结构紊乱含玻璃疣',13:'13：瘢痕与机化',14:'14：视网膜神经纤维层（RNFL）萎缩',
           15:'15：脉络膜增厚',16:'16：圆顶状色素上皮层脱落（PED）',
           17:'17：视网膜萎缩',18:'18：纤维血管性色素上皮层脱离（含2型MNV）',19:'19：脉络膜曲度异常（例如肿瘤）',20:'20：双层征（扁平不规则PED，含1型MNV）',
           21:'21：后巩膜葡萄肿',22:'22：椭圆体带（ISOS）缺失',23:'23：脉络膜变薄',25:'25：视盘水肿',26:'26：视神经萎缩（视盘处）',
           27:'27：视盘小凹',28:'28：神经节细胞层（GCL）萎缩',29:'29：有髓视神经纤维',30:'30：视网膜色素上皮（RPE）萎缩',
           31:'31：视网膜大血管瘤',32:'32：视网膜脱离',33:'33：视网膜前出血',34:'34：视网膜内出血',35:'35：视网膜下出血',36:'36：视盘凹陷扩大',
           37:'37：玻璃体后脱离',38:'38：玻璃体混浊（含玻璃体出血）'}

size_width = np.zeros([38, 16])
size_height = np.zeros([38, 21])


# 绘制分布直方图
def draw_distribution(save_path, size_np):
    for key in ill_map.keys():
        size_dict = {}
        row = size_np[key-1]
        for i in range(len(row)):
            k = (i+1)*100
            size_dict[k] = row[i]

        c = {'section': size_dict.keys(), 'frequency': size_dict.values()}
        e = pd.DataFrame(c)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        ax = plt.figure(figsize=(10, 5))
        sns.barplot(x="section", y="frequency", data=e, palette="Set3")  # palette设置颜色
        plt.savefig(os.path.join(save_path,  str(ill_map[key]) + '.jpg'), dpi=500, bbox_inches='tight')
        plt.close(ax)


def write_excel(save_path):
    excel_writer = pd.ExcelWriter(save_path)
    record_w = pd.DataFrame(columns=[(i+1)*100 for i in range(16)])
    index1 = 1
    for row in size_width:
        record_w.loc[index1] = [row[j] for j in range(len(row))]
        index1 += 1
    record_w.to_excel(excel_writer, sheet_name='width')

    record_h = pd.DataFrame(columns=[(i + 1) * 100 for i in range(21)])
    index2 = 1
    for row in size_height:
        record_h.loc[index2] = [row[j] for j in range(len(row))]
        index2 += 1
    record_h.to_excel(excel_writer, sheet_name='height')

    excel_writer.save()


# 统计每个病灶标注框长宽分布
def state_box_size(txt_path):
    for file_name in os.listdir(txt_path):
        with open(os.path.join(txt_path, file_name), 'r') as w:
            file_dict = create_dict(w)
        for k in [200, 100, 'grade', 'illness']:
            if k in file_dict.keys():
                del file_dict[k]

        # img = cv2.imdecode(np.fromfile(os.path.join(img_path, file_name[:-3] + 'jpg'), dtype=np.uint8), 1)

        for illness in file_dict.keys():
            for box in file_dict[illness]:
                width = box[2] - box[0]
                height = box[3] - box[1]
                width_index = int(width / 100)
                height_index = int(height / 100)
                size_width[illness-1][width_index] += 1
                size_height[illness - 1][height_index] += 1


state_box_size(txt_path='E:\\0726_ai_annotation\\all_data\\note')
write_excel(save_path='E:\\0726_ai_annotation\\all_data\\size.xlsx')
draw_distribution(save_path='E:\\0726_ai_annotation\\all_data\\plot\\宽度分布', size_np=size_width)
draw_distribution(save_path='E:\\0726_ai_annotation\\all_data\\plot\\高度分布', size_np=size_height)
