import os
from tools import compute_iou, create_dict, ill_num_dict, ill_acc_dict, ill_map
import pandas as pd

grade_all = ill_num_dict.copy()  # 每个病灶对应的图片数
grade_right = ill_num_dict.copy()  #
box_all = ill_num_dict.copy()
box_right = ill_num_dict.copy()
box_accs = ill_acc_dict.copy()
grade_accs = ill_acc_dict.copy()
ill_names = ill_map.copy()

def set_zero(dict1):
    for i in dict1.keys():
        dict1[i] = 0


class CompareNoteOnPerson:
    def __init__(self, dict1, dict2, mode):
        self.dict1 = dict1
        self.dict2 = dict2
        self.mode = mode

    def compare_grade(self):
        dict1 = self.dict1
        dict2 = self.dict2
        index = 0
        if 'grade' in dict1.keys() and 'grade' in dict2.keys():
            if dict1['grade'] == dict2['grade']:
                index = 1
        return index

    def compare_illness(self):
        dict1 = self.dict1
        dict2 = self.dict2
        ill_right_num = 0  # 交集
        ill_acc = 1
        ill_num1, ill_num2 = 0, 0  # 两个note的病灶数
        for k1 in dict1.keys():
            if k1 not in [200, 'grade', 'illness']:
                ill_num1 += 1
                if k1 in dict2.keys():
                    ill_right_num += 1
        for k2 in dict2.keys():
            if k2 not in [200, 'grade', 'illness']:
                ill_num2 += 1
        ill_num_all = ill_num1 + ill_num2 - ill_right_num  # 两个note中的所有病灶数
        if self.mode == 0:
            if ill_num_all != 0:
                ill_acc = float(ill_right_num / ill_num_all)
        else:
            if ill_num2 == 0 and ill_num1 == 0:
                ill_acc = 1
            elif ill_num2 == 0 and ill_num1 != 0:
                ill_acc = 0
            else:
                ill_acc = float(ill_right_num / ill_num2)

        return ill_acc

    def all_box(self):
        dict1 = self.dict1
        dict2 = self.dict2
        mode = self.mode
        num1, num2 = 0, 0
        for k1 in dict1.keys():
            if k1 not in [200, 'grade', 'illness']:
                num1 += len(dict1[k1])
        for k2 in dict2.keys():
            if k2 not in [200, 'grade', 'illness']:
                num2 += len(dict2[k2])
        all_box_num = num1 + num2 if mode == 0 else num2

        return all_box_num, num1

    def right_box(self, all_box_num):
        dict1 = self.dict1
        dict2 = self.dict2
        mode = self.mode
        right_num = 0
        for k2 in dict2.keys():
            if k2 not in [200, 'grade', 'illness']:
                if k2 in dict1.keys():
                    arr1 = [-1 for i in range(len(dict1[k2]))]
                    arr2 = [-1 for i in range(len(dict2[k2]))]
                    # arr用来表示每个标注框对应的标签
                    # -1：没有iou>0.5的相交框  0：有唯一iou>0.5的相交框 1：有多个iou>0.5的相交框
                    # 计算所有框对应的iou,并把标签记录到arr中
                    for i in range(len(dict1[k2])):
                        for j in range(len(dict2[k2])):
                            iou = float('%.2f' % compute_iou(dict1[k2][i], dict2[k2][j], 'iou'))
                            if iou > 0.5:
                                if arr1[i] == -1 and arr2[j] == -1:
                                    arr1[i], arr2[j] = 0, 0
                                else:
                                    arr1[i], arr2[j] = 1, 1
                            elif 0 < iou <= 0.5:
                                arr1[i], arr2[j] = 1, 1

                    for i in range(len(dict1[k2])):
                        if arr1[i] == 0:
                            right_num += 1
                            if mode == 0:
                                all_box_num -= 1
        return right_num, all_box_num


def evaluate_on_person(loaddir1, loaddir2, mode):
    new_record = pd.DataFrame(columns=['name', 'ill_acc', 'box_acc'])
    index = 0
    img_names1 = os.listdir(loaddir1)
    img_names2 = os.listdir(loaddir2)
    ill_acc = 0.0  # 病灶类别
    img_num = 0  # 图片数
    grade_right_num = 0  # 干预分级
    box_acc = 0  # 病灶定位
    for img_name in img_names1:
        if img_name in img_names2:
            with open(os.path.join(loaddir1, img_name), 'r') as f1:
                dict1 = create_dict(f1)
            with open(os.path.join(loaddir2, img_name), 'r') as f2:
                dict2 = create_dict(f2)
            cnote = CompareNoteOnPerson(dict1, dict2, mode)
            grade_right_num += cnote.compare_grade()
            ill_acc += cnote.compare_illness()
            all_box_num, note1_box_num = cnote.all_box()
            right_box_num, all_box_num = cnote.right_box(all_box_num)
            if mode == 0:
                box_acc += 1 if all_box_num == 0 else right_box_num/all_box_num
            elif mode == 1:
                if all_box_num == 0 and note1_box_num == 0:
                    box_acc += 1
                elif all_box_num != 0:
                    box_acc += right_box_num/all_box_num
            img_num += 1
            new_record.loc[index] = [img_name, ill_acc, box_acc]
            index += 1
    # new_record.to_excel('E:\\0726_ai_annotation\phase2\标注\\标注整合\\tmp.xlsx')
    ill_acc = ill_acc/img_num         # 病灶类型交并比
    grade_acc = grade_right_num/img_num     # 干预分级准确率
    box_acc = box_acc/img_num         # 病灶框交并比，合格的框算作一个

    print('图片数：', img_num)
    print('病灶类别准确率：', ill_acc)
    print('病灶定位准确率：', box_acc)
    print('干预分级准确率：', grade_acc)


class CompareNoteOnIllness:
    def __init__(self, dict1, dict2, mode):
        self.dict1 = dict1
        self.dict2 = dict2
        self.mode = mode

    def compare_grade(self):
        dict1 = self.dict1
        dict2 = self.dict2
        for k in grade_all.keys():
            if k in dict1.keys() and k in dict2.keys():
                grade_all[k] += 1

        if 'grade' in dict1.keys() and 'grade' in dict2.keys():  # 首先两个人对这张图都有评级
            for k in grade_all.keys():  # 两个人必须都认为有该病灶，总数+1
                if k in dict1.keys() and k in dict2.keys():
                    grade_all[k] += 1
            if dict1['grade'] == dict2['grade']:  # 评级一致，一致数+1
                for k in grade_right.keys():
                    if k in dict1.keys() and k in dict2.keys():
                        grade_right[k] += 1

    def all_box(self):
        dict1 = self.dict1
        dict2 = self.dict2
        mode = self.mode
        for k2 in dict2.keys():
            if k2 not in [200, 'grade', 'illness']:
                box_all[k2] += len(dict2[k2])
        if mode == 0:
            for k1 in dict1.keys():
                if k1 not in [200, 'grade', 'illness']:
                    box_all[k1] += len(dict1[k1])

    def right_box(self):
        dict1 = self.dict1
        dict2 = self.dict2
        mode = self.mode
        for k2 in dict2.keys():
            if k2 not in [200, 'grade', 'illness']:
                if k2 in dict1.keys():
                    arr1 = [-1 for i in range(len(dict1[k2]))]
                    arr2 = [-1 for i in range(len(dict2[k2]))]
                    # arr用来表示每个标注框对应的标签
                    # -1：没有iou>0.5的相交框  0：有唯一iou>0.5的相交框 1：有多个iou>0.5的相交框
                    # 计算所有框对应的iou,并把标签记录到arr中
                    for i in range(len(dict1[k2])):
                        for j in range(len(dict2[k2])):
                            iou = float('%.2f' % compute_iou(dict1[k2][i], dict2[k2][j], 'iou'))
                            if iou > 0.5:
                                if arr1[i] == -1 and arr2[j] == -1:
                                    arr1[i], arr2[j] = 0, 0
                                else:
                                    arr1[i], arr2[j] = 1, 1
                            elif 0 < iou <= 0.5:
                                arr1[i], arr2[j] = 1, 1
                    for i in range(len(dict1[k2])):
                        if arr1[i] == 0:
                            box_right[k2] += 1
                            if mode == 0:
                                box_all[k2] -= 1


def evaluate_on_illness(loaddir1, loaddir2, mode, record_path):
    labels = os.listdir(loaddir1)
    standards = os.listdir(loaddir2)
    img_num = 0  # 图片数

    for img_name in labels:
        if img_name in standards:
            img_num += 1
            with open(os.path.join(loaddir1, img_name), 'r') as f1:
                dict1 = create_dict(f1)
            with open(os.path.join(loaddir2, img_name), 'r') as f2:
                dict2 = create_dict(f2)
            cnote = CompareNoteOnIllness(dict1, dict2, mode)
            cnote.compare_grade()
            cnote.all_box()
            cnote.right_box()

            for k in box_right.keys():
                if box_all[k] != 0:
                    box_accs[k] += box_right[k] / box_all[k]
        set_zero(box_all)
        set_zero(box_right)

    new_record = pd.DataFrame(None, columns=['病灶', '干预分级', '标注框'])
    index = 0
    for k in grade_right.keys():
        name = ill_names[k].split('：')[-1]
        box_accs[k] = box_accs[k] / img_num
        if grade_all[k] != 0:
            grade_accs[k] = grade_right[k] / grade_all[k]
        else:
            grade_accs[k] = 'none'

        new_record.loc[index] = [name, grade_accs[k], box_accs[k]]
        index += 1
    new_record.to_excel(record_path)
    print('图片数：', img_num)
