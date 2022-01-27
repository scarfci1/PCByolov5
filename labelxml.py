import xml.etree.ElementTree as ET
import pickle
import os

# os.listdir() 方法用于返回指定的文件夹包含的文件或文件夹的名字的列表

from os import listdir, getcwd
from os.path import join

sets = ['train', 'test', 'val']
classes = ['open', 'short', 'mousebite', 'spur', 'copper', 'pin-hole']
# open:0, short:1 mousebite:2 spur:3 copper:4 pin-hole:5

# 歸一化

def convert(size, box):  # size:(w1,h1) , box:(xmin,xmax,ymin,ymax)
    dw = 1. / size[0]  # 1/(w1)
    dh = 1. / size[1]  # 1/(h1)
    x = (box[0] + box[1]) / 2.0  # 該物體在圖中的中心(x,_)
    y = (box[2] + box[3]) / 2.0  # 該物體在圖中的中心(_,y)
    w = box[1] - box[0]  # 物體的寬度(xmax-xmin)
    h = box[3] - box[2]  # 物體的高度(ymax-ymin)
    x = x * dw  # 物體中心x的座標比(x/(w1))
    w = w * dw  # 物體的寬度比(w/(w1))
    y = y * dh  # 物體中心y的座標比(y/(h1))
    h = h * dh  # 物體的高度比(h/(h1)
    return (x, y, w, h)  # 返回 相對於原圖的x座標比,y座標比,寬度比,高度比


def convert_annotation(image_id):
    # 把xml文件轉成label文件
    in_file = open('data/PCBDatasets/xml/%s.xml' % (image_id), encoding='utf-8')
    # <object-class> <x> <y> <width> <height>
    out_file = open('data/PCBDatasets/label/%s.txt' % (image_id), 'w', encoding='utf-8')
    # 解析xml文件
    tree = ET.parse(in_file)
    root = tree.getroot()
    # 尺寸大小
    size = root.find('size')
    # 如果xml的標記為空，增加判斷條件
    if size != None:
        # 寬
        w = int(size.find('width').text)
        # 高
        h = int(size.find('height').text)
        # 目標obj
        for obj in root.iter('object'):
            # 獲得difficult ？？
            difficult = obj.find('difficult').text
            # 獲得類別 =string 類型
            cls = obj.find('name').text
            # 如果類別不是對應在預定好的class文件中，或difficult==1時跳過
            if cls not in classes or int(difficult) == 1:
                continue
            # 透過名稱找到id
            cls_id = classes.index(cls)
            # 找到bndbox 對象
            xmlbox = obj.find('bndbox')
            # 獲得bndbox的數組 = ['xmin','xmax','ymin','ymax']
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
                 float(xmlbox.find('ymax').text))
            print(image_id, cls, b)
            # 帶入
            # w = 寬, h = 高， b= bndbox的數組 = ['xmin','xmax','ymin','ymax']
            bb = convert((w, h), b)
            # bb (x,y,w,h)
            # 生成 class x y w h 在label文件中
            out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


# 返回工作目錄

wd = getcwd()
print(wd)

for image_set in sets:

    # 先找labels,不存在時創建
    if not os.path.exists('data/PCBDatasets/labels/'):
        os.makedirs('data/PCBDatasets/labels/')
    # 讀取在ImageSets/Main 中的train、test..等文件的内容
    # 包含對應文件名稱
    image_ids = open('data/PCBDatasets/dataSet/%s.txt' % (image_set)).read().strip().split()

    list_file = open('data/PCBDatasets/%s.txt' % (image_set), 'w')
    # 將對應的文件寫進去與換行
    for image_id in image_ids:
        list_file.write('data/PCBDatasets/image/%s.jpg\n' % (image_id))
        convert_annotation(image_id)
    # 關閉文件
    list_file.close()