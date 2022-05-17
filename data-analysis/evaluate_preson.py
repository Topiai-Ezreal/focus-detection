import os
from tools import compute_iou, create_dict


def compare_grade(dict1, dict2):
    if 'grade' in dict1.keys() and 'grade' in dict2.keys():
        if dict1['grade'] == dict2['grade']:
            return 1
    return 0


def compare_illness_others(dict1, dict2):
    ill_right_num = 0
    ill_acc = 1
    ill_num1, ill_num2 = 0, 0  # 两个note的病灶数
    for k1 in dict1.keys():
        if k1 not in [200, 'grade', 'illness']:
            ill_num1 += 1
            if k1 in dict2.keys():  # 两个note的交集
                ill_right_num += 1
    for k2 in dict2.keys():
        if k2 not in [200, 'grade', 'illness']:
            ill_num2 += 1

    ill_num_all = ill_num1 + ill_num2 - ill_right_num  # 两个note的并集
    if ill_num_all != 0:  # 并集为0则acc为1，否则计算交并比
        ill_acc = float(ill_right_num / ill_num_all)
    return ill_acc


def compare_illness_standard(dict1, dict2):
    pre_num, gt_num, TP = 0, 0, 0
    for k1 in dict1.keys():
        if k1 not in [200, 'grade', 'illness']:
            pre_num += 1
            if k1 in dict2.keys():  # 两个note的交集
                TP += 1
    for k2 in dict2.keys():
        if k2 not in [200, 'grade', 'illness']:
            gt_num += 1

    if gt_num == 0 and pre_num == 0:
        precision, recall = 1, 1
    elif gt_num == 0 and pre_num != 0:
        precision, recall = 0, 1
    elif gt_num != 0 and pre_num == 0:
        precision, recall = 1, 0
    else:
        precision = float(TP/pre_num)
        recall = float(TP/gt_num)

    return precision, recall


def compare_box_others_v2(dict1, dict2):
    box_acc = 0.0

    # 两个标注的病灶总类
    union_list, combine_list = [], []  # 交集和并集
    for k1 in dict1.keys():
        if k1 not in [200, 'grade', 'illness']:
            combine_list.append(k1)
            if k1 in dict2.keys():
                union_list.append(k1)
    for k2 in dict2.keys():
        if k2 not in [200, 'grade', 'illness'] and k2 not in combine_list:
            combine_list.append(k2)

    # 两个都有该病灶，再计算一致度，否则一致度为0
    for k in union_list:
        # arr用来记录该病灶的每个标注框对应的标签
        # 默认-1：没有相交框；0：有唯一相交框，且iou>0.5；1：有多个相交框或有唯一相交框，但iou<0.5
        arr1 = [-1 for _ in range(len(dict1[k]))]
        arr2 = [-1 for _ in range(len(dict2[k]))]
        right_num = 0
        all_num = len(dict1[k]) + len(dict2[k])
        for i in range(len(dict1[k])):
            for j in range(len(dict2[k])):
                iou = float('%.2f' % compute_iou(dict1[k][i], dict2[k][j], 'iou'))
                if iou > 0.5:
                    if arr1[i] == -1 and arr2[j] == -1:  # 此前没有相交框
                        arr1[i], arr2[j] = 0, 0
                    else:
                        arr1[i], arr2[j] = 1, 1
                elif 0 < iou <= 0.5:
                    arr1[i], arr2[j] = 1, 1
        for q in range(len(arr1)):
            if arr1[q] == 0:
                right_num += 1
                all_num -= 1
        box_acc += float(right_num / all_num)
    if len(combine_list) == 0:
        box_acc += 1
    else:
        box_acc = box_acc / len(combine_list)  # 所有病灶平均，作为该张图的acc
    return box_acc


def compare_box_others(dict1, dict2):
    # 总框数
    box_num_all = 0
    for k1 in dict1.keys():
        if k1 not in [200, 'grade', 'illness']:
            box_num_all += len(dict1[k1])
    for k2 in dict2.keys():
        if k2 not in [200, 'grade', 'illness']:
            box_num_all += len(dict2[k2])

    # 两个都有该病灶，计算合格框的数量
    right_num = 0
    for k in dict1.keys():
        if k not in [200, 'grade', 'illness'] and k in dict2.keys():
            iou_list = []
            for i in range(len(dict1[k])):
                for j in range(len(dict2[k])):
                    iou = float('%.2f' % compute_iou(dict1[k][i], dict2[k][j], 'iou'))
                    if iou >= 0.5:
                        iou_list.append(iou)
            for w in range(len(iou_list)):
                if iou_list[w] >= 0.5:
                    right_num += 1

    if box_num_all == 0:
        box_acc = 0
    else:
        box_acc = float(right_num / (box_num_all - right_num))

    return box_acc


def compare_box_standard(dict1, dict2):
    pre_num, gt_num, TP = 0, 0, 0
    for k2 in dict2.keys():
        if k2 not in [200, 'grade', 'illness']:
            gt_num += len(dict2[k2])  # standard中框的数量
    for k1 in dict1.keys():
        if k1 not in [200, 'grade', 'illness']:
            pre_num += len(dict1[k1])  # 标注中框的数量

    for k in dict2.keys():
        if k not in [200, 'grade', 'illness'] and k in dict1.keys():
            for i in range(len(dict2[k])):
                # 把该标注框对应的所有iou记录下来，并排序
                # 若存在iou>0.5的框，则该框为TP，其他框均为FP
                iou_list = []
                for j in range(len(dict1[k])):
                    iou = float('%.2f' % compute_iou(dict2[k][i], dict1[k][j], 'iou'))
                    iou_list.append(iou)
                iou_list.sort(reverse=True)
                if iou_list[0] > 0.5:
                    TP += 1

    if gt_num == 0 and pre_num == 0:
        precision, recall = 1, 1
    elif gt_num == 0 and pre_num != 0:
        precision, recall = 0, 1
    elif gt_num != 0 and pre_num == 0:
        precision, recall = 1, 0
    else:
        precision = TP / pre_num
        recall = TP / gt_num

    return precision, recall


def evaluate_with_others(txt_path1, txt_path2):
    img_num = 0  # 图片数
    ill_acc = 0.0  # 病灶类别
    box_acc = 0.0
    grade_right_num = 0  # 干预分级

    namelist1 = os.listdir(txt_path1)
    namelist2 = os.listdir(txt_path2)
    for name in namelist1:
        if name in namelist2:
            with open(os.path.join(txt_path1, name), 'r') as f1:
                dict1 = create_dict(f1)
            with open(os.path.join(txt_path2, name), 'r') as f2:
                dict2 = create_dict(f2)
            img_num += 1
            ill_acc += compare_illness_others(dict1, dict2)
            box_acc += compare_box_others(dict1, dict2)
            grade_right_num += compare_grade(dict1, dict2)
    grade_acc = grade_right_num / img_num
    box_acc = box_acc / img_num
    ill_acc = ill_acc / img_num

    print('图片数：', img_num)
    print('病灶类别准确率：', ill_acc)
    print('病灶定位准确率：', box_acc)
    print('干预分级准确率：', grade_acc)


def evaluate_with_standard(txt_path1, txt_path2):
    img_num = 0  # 图片数
    ill_precision, ill_recall = 0, 0  # 病灶类别
    box_precision, box_recall = 0, 0
    grade_right_num = 0  # 干预分级
    namelist1 = os.listdir(txt_path1)
    namelist2 = os.listdir(txt_path2)
    for name in namelist1:
        if name in namelist2:
            with open(os.path.join(txt_path1, name), 'r') as f1:
                dict1 = create_dict(f1)
            with open(os.path.join(txt_path2, name), 'r') as f2:
                dict2 = create_dict(f2)
            img_num += 1
            ip, ir = compare_illness_standard(dict1, dict2)
            ill_precision += ip
            ill_recall += ir
            bp, br = compare_box_standard(dict1, dict2)
            box_precision += bp
            box_recall += br
            grade_right_num += compare_grade(dict1, dict2)
    grade_acc = grade_right_num / img_num
    ill_precision = ill_precision / img_num
    ill_recall = ill_recall / img_num
    box_precision = box_precision / img_num
    box_recall = box_recall / img_num
    ill_f1_score = 2 * ill_recall * ill_precision / (ill_recall + ill_precision)
    box_f1_score = 2 * box_recall * box_precision / (box_recall + box_precision)

    print('图片数：', img_num)
    print('病灶类别精确度：', ill_precision, '  召回率：', ill_recall, '  F1 score：', ill_f1_score)
    print('病灶定位精确度：', box_precision, '  召回率：', box_recall, '  F1 score：', box_f1_score)
    print('干预分级准确率：', grade_acc)


def evaluate_on_person(txt_path1, txt_path2, mode):
    if mode == 0:
        evaluate_with_others(txt_path1, txt_path2)
    elif mode == 1:
        evaluate_with_standard(txt_path1, txt_path2)
