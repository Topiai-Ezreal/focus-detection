# 统计每个病灶对应的图片数及标注框数

import os
import shutil
import pandas as pd
from .utils import ill_num_dict, create_dict, ill_map


img_num = ill_num_dict.copy()
box_num = ill_num_dict.copy()
other_img_num = {}
other_box_num = {}


def statistic_ill_num(note_path, record, new_path):
    excel_writer = pd.ExcelWriter(record)
    annotations = os.listdir(note_path)
    for name in annotations:
        with open(os.path.join(note_path, name), 'r') as f1:
            dict1 = create_dict(f1)
        for key in dict1.keys():  # 统计已有病灶
            if key not in ['grade', 'illness', '有效区域']:
                box_num[key] += len(dict1[key])
                img_num[key] += 1
        if 'illness' in dict1.keys():  # 统计其他病灶
            k = dict1['illness']
            if k in other_img_num.keys():
                other_img_num[k] += 1
                other_box_num[k] += len(dict1[100])
            else:
                other_img_num[k] = 1
                other_box_num[k] = len(dict1[100])
            # if k in ['玻璃体混浊', '玻璃体混浊,玻璃体混浊积血', '玻璃体混浊,玻璃体混浊']:
            #     shutil.copy(os.path.join(note_path, name), os.path.join(new_path, name))

    new_record = pd.DataFrame(columns=['编号', '病灶名称', '图片数', '标注框数'])
    index = 0
    for k in ill_map.keys():
        a = ill_map[k].split('：')[1]
        b = img_num[k]
        c = box_num[k]
        new_record.loc[index] = [k, a, b, c]
        index += 1
    new_record.to_excel(excel_writer, sheet_name='illness')

    other_record = pd.DataFrame(columns=['病灶名称', '图片数', '标注框数'])
    index = 0
    for k in other_img_num.keys():
        a = other_img_num[k]
        b = other_box_num[k]
        other_record.loc[index] = [k, a, b]
        index += 1
    other_record.to_excel(excel_writer, sheet_name='others')
    excel_writer.save()


note_path = 'E:\\0726_ai_annotation\\all_data\\note'
record = 'E:\\0726_ai_annotation\\all_data\\ill.xlsx'
new_path = 'E:\\0726_ai_annotation\\all_data\\renote'
statistic_ill_num(note_path, record, new_path)
