import os
import shutil
import cv2

font = cv2.FONT_HERSHEY_SIMPLEX

# 6:(172,50,59),24:(217,192,34),
color_maps = {1:(104,221,230),2:(153,255,153),3:(254,0,0),4:(193,18,28),5:(209,91,143),
              7:(213,109,86),8:(250,166,155),9:(255,220,164),10:(255,192,0),11:(146,209,79),
              12:(255,255,0),13:(166,94,47),14:(250,132,43),15:(198,54,120),16:(251,138,226),
              17:(114,159,178),18:(226,240,217),19:(219,226,254),20:(1,32,96),21:(0,247,0),
              22:(33,136,143),23:(135,115,161),25:(204,197,143),26:(175,138,84),27:(190,78,32),
              28:(183,217,177),29:(158,160,161),30:(52,129,184),31:(152,64,225),32:(56,154,90),
              33:(254,94,47),34:(47,166,94),35:(94,47,166),36:(166,94,166),37:(220,11,200),
              38:(22,11,150), 100:(255,0,0),200:(255,0,0)}
cls_map = {'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'11':11,'12':12,'13':13,'14':14,'15':15,'16':16,
           '17':17,'18':18,'19':19,'20':20,'21':21,'22':22,'23':23,'24':24,'25':25,'26':26,'27':27,'28':28,'29':29,'30':30,
           '31':31,'32':32,'33':33,'34':34,'35':35,'36':36,'37':37,'38':38,'100':100,'有效区域':200}
ill_map = {1:' 1：视网膜前膜',2:' 2：视网膜裂孔',3:' 3：玻璃体黄斑牵拉',4:' 4：视网膜囊性变样',5:' 5：视网膜劈裂',
           7:' 7：黄斑水肿（非囊性）',8:' 8：视网膜内液',9:' 9：视网膜下积液',10:'10：弥漫性高反射病灶',11:'11：局部网膜内高反射点',
           12:'12：视网膜色素上皮（RPE）结构紊乱含玻璃疣',13:'13：瘢痕与机化',14:'14：视网膜神经纤维层（RNFL）萎缩',
           15:'15：脉络膜增厚',16:'16：圆顶状色素上皮层脱落（PED）',
           17:'17：视网膜萎缩',18:'18：纤维血管性色素上皮层脱离（含2型MNV）',19:'19：脉络膜曲度异常（例如肿瘤）',20:'20：双层征（扁平不规则PED，含1型MNV）',
           21:'21：后巩膜葡萄肿',22:'22：椭圆体带（IS/OS）缺失',23:'23：脉络膜变薄',25:'25：视盘水肿',26:'26：视神经萎缩（视盘处）',
           27:'27：视盘小凹',28:'28：神经节细胞层（GCL）萎缩',29:'29：有髓视神经纤维',30:'30：视网膜色素上皮（RPE）萎缩',
           31:'31：视网膜大血管瘤',32:'32：视网膜脱离',33:'33：视网膜前出血',34:'34：视网膜内出血',35:'35：视网膜下出血',36:'36：视盘凹陷扩大',
           37:'37：玻璃体后脱离',38:'38：玻璃体混浊（含玻璃体出血）', 100:'100：其它'}
grade_map = {0:'无治疗', 1:'干预并观察', 2:'手术', 3:' '}
ill_num_dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0,
              18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0,
              33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38:0, 100: 0}
ill_acc_dict = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0,
           14: 0.0, 15: 0.0, 16: 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0, 22: 0.0, 23: 0.0, 25: 0.0, 26: 0.0,
           27: 0.0, 28: 0.0, 29: 0.0, 30: 0.0, 31: 0.0, 32: 0.0, 33: 0.0, 34: 0.0, 35: 0.0, 36: 0.0, 37: 0.0, 38:0.0, 100: 0.0}


# 读取标注文件，并储存到字典中
def create_dict(file):
    lesion_dict = {}
    for line in file.readlines():
        mode = 2
        if line[0] == 'v':
            continue
        elif len(line) == 2:
            mode = 3
        elif line[0] == '有':
            mode = 1

        temp = line.split(';')

        # 有效区域
        if mode == 1:
            total_info = line.split(':')
            lesion_class = cls_map[total_info[0]]
            lesion_dict[lesion_class] = total_info[1][:-1]
        # 病灶识别
        if mode == 2:
            if len(temp) == 3:
                total_info = temp[1].split(':')
                pos = temp[2].split(',')
                lesion_dict['illness'] = temp[0]
            elif len(temp) == 2:
                total_info = temp[0].split(':')
                pos = temp[1].split(',')
            else:
                continue
            lesion_class = cls_map[total_info[0]]
            box_num = int(total_info[1])
            pos = [int(i) for i in pos]
            for j in range(box_num):
                box_pos = pos[j * 4:(j + 1) * 4]
                box_pos = [i for i in box_pos]
                if lesion_class not in lesion_dict:
                    lesion_dict[lesion_class] = []
                lesion_dict[lesion_class].append(box_pos)
        # 干预分级
        if mode == 3:
            lesion_dict['grade'] = line[0]

    return lesion_dict


def compute_iou(rec1, rec2, mode):
    """
    计算IoU
    :param rec1: (x0, y0, x1, y1), 标注框坐标信息
            分别代表左上角点横、纵坐标，右下角点横、纵坐标
    :param rec2: (x0, y0, x1, y1)
    :return: IoU
    """
    # 计算每个矩形框的面积
    S_rec1 = (rec1[2] - rec1[0]) * (rec1[3] - rec1[1])
    S_rec2 = (rec2[2] - rec2[0]) * (rec2[3] - rec2[1])

    # 计算并集
    sum_area = S_rec1 + S_rec2

    # 找到准交集的边际
    left_line = max(rec1[0], rec2[0])
    right_line = min(rec1[2], rec2[2])
    top_line = max(rec1[1], rec2[1])
    bottom_line = min(rec1[3], rec2[3])

    # 判断是否有交集，有则计算IoU
    if left_line >= right_line or top_line >= bottom_line:
        return 0
    else:
        intersect = (right_line - left_line) * (bottom_line - top_line)  # 交集
        result = (intersect / (sum_area - intersect)) * 1.0

        return result if mode == 'iou' else intersect
