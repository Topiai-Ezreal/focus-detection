import os
from database.focus_detection.data_analyse.utils import create_dict
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import seaborn as sns

# size_dict = {5: 0, 10: 0, 15: 0, 20: 0, 25: 0, 30: 0, 35: 0, 40: 0, 45: 0, 50: 0,
#              55: 0, 60: 0, 65: 0, 70: 0, 75: 0, 80: 0, 85: 0, 90: 0, 95: 0, 100: 0}



# zhfont1 = matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simsun.ttc')


# 按照固定区间长度绘制频率分布直方图
# bins_interval 区间的长度
# margin        设定的左边和右边空留的大小
def probability_distribution(data, bins_interval=1, margin=1):
    bins = range(min(data), max(data) + bins_interval - 1, bins_interval)
    print(len(bins))
    for i in range(0, len(bins)):
        print(bins[i])
    plt.xlim(min(data), max(data))
    plt.title("Probability-distribution")
    plt.xlabel('Interval')
    plt.ylabel('Probability')
    # 频率分布normed=True，频次分布normed=False
    prob,left,rectangle = plt.hist(x=data, bins=bins, histtype='bar', color=['r'])
    for x, y in zip(left, prob):
        # 字体上边文字
        # 频率分布数据 normed=True
        plt.text(x + bins_interval / 2, y + 0.003, '%.2f' % y, ha='center', va='top')
        # 频次分布数据 normed=False
        # plt.text(x + bins_interval / 2, y + 0.25, '%.2f' % y, ha='center', va='top')
    plt.show()


def distribution(data, ill):
    c = {'section': data.keys(), 'frequency': data.values()}
    e = pd.DataFrame(c)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    ax = plt.figure(figsize=(10, 5))
    sns.barplot(x="section", y="frequency", data=e, palette="Set3")  # palette设置颜色
    plt.savefig('E:\\0726_ai_annotation\\testcode\\plot\\' + str(ill) + '.jpg', dpi=500, bbox_inches='tight')
    # plt.show()
    plt.close(ax)


# data = [1, 1, 2, 2, 3, 4]
# probability_distribution(data)



def calculate_size(size_list, img_size):
    width = size_list[2] - size_list[0] + 1
    height = size_list[3] - size_list[1] + 1
    size = width*height/img_size*100
    # size = str(width) + ',' + str(height)
    return size


# 统计每个病灶标注框长宽分布
def state_box_size(txt_path, size_path, ill):
    size_dict = {}
    maxsize, minsize = 0, 100
    box_num = 0
    for name in os.listdir(txt_path):
        with open(os.path.join(txt_path, name), 'r') as f1:
            dict1 = create_dict(f1)
        img = cv2.imread(os.path.join('E:\\0726_ai_annotation\\1021_phase1\image', name[:-3] + 'jpg'))
        img_size = img.shape[0] * img.shape[1]
        if ill in dict1.keys():
            box_num += len(dict1[ill])
            for item in dict1[ill]:
                size = calculate_size(item, img_size)
                if size > maxsize:
                    maxsize = size
                if size < minsize:
                    minsize = size
                if size in size_dict.keys():
                    size_dict[size] += 1
                else:
                    size_dict[size] = 1

    # 至此，size_dict储存每个size的数量
    # print(ill, ':', box_num, len(size_dict.keys()), maxsize, minsize)
    # print(size_dict)
    # 大于12类的分为12个区间，小于12类的按原始区间
    axis_dict = {}
    if len(size_dict.keys()) > 12:
        bins_interval = (maxsize - minsize) / 12  # 间隔
        axis = minsize
        for k in range(11):
            axis += bins_interval

            axis_dict[int(axis)] = 0
        axis_dict[int(maxsize)] = 0
    else:
        for k in size_dict.keys():
            axis_dict[int(k)] = size_dict[k]
        # axis_dict = size_dict.copy()


    # print(axis_dict)
    # 将所有标注框分到这12个类里面
    for k in size_dict.keys():
        for j in axis_dict.keys():
            if k <= j:
                axis_dict[j] += size_dict[k]
                break
    if len(size_dict.keys()) != 0:
        distribution(axis_dict, ill)



txt_path1 = 'E:\\0726_ai_annotation\\1021_phase1\审核\check'
record_path = 'E:\\0726_ai_annotation\\1021_phase1\病灶\\ill_0214.xlsx'
for illness in range(34):
    illness = illness + 1
    state_box_size(txt_path1, record_path, illness)
