import os 
import shutil
import nibabel as nib
import contorl
import numpy as np
import pandas as pd



def meanIOU(image1, image2):
    # 使用 nibabel 讀取影像
    image1 = nib.load(image1)
    image2 = nib.load(image2)

    # 將影像的像素值轉換為二進制值
    image1 = image1.get_fdata() > 0
    image2 = image2.get_fdata() > 0

    # 計算兩份影像的 IOU 值
    intersections = np.sum(image1 & image2)
    unions = np.sum(image1 | image2)
    ious = intersections / unions

    # 計算所有 IOU 值的平均值
    return np.mean(ious)

path_gt = r''
path_200 = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/ST_test/Smodel_T28/best_50/best_50_200'
path_400 = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/ST_test/Smodel_T28/best_50/best_50_400'
path_600 = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/ST_test/Smodel_T28/best_50/best_50_600'
path_800 = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/ST_test/Smodel_T28/best_50/best_50_800'


files_200 = os.listdir(path_200)
if ".DS_Store" in files_200:
    files_200.remove(".DS_Store")
files_400 = os.listdir(path_400)
if ".DS_Store" in files_400:
    files_400.remove(".DS_Store")
files_600 = os.listdir(path_600)
if ".DS_Store" in files_600:
    files_600.remove(".DS_Store")
files_800 = os.listdir(path_800)
if ".DS_Store" in files_800:
    files_800.remove(".DS_Store")

same_with_200 = []
same_with_400 = []
same_with_600 = []
same_with_total = [] # 51

for file in files_800:
    if file in os.listdir(path_200):
        same_with_200.append(file)
    if file in os.listdir(path_400):
        same_with_400.append(file)
    if file in os.listdir(path_600):
        same_with_600.append(file)
    if file in os.listdir(path_200) and file in os.listdir(path_400) and file in os.listdir(path_600):
        same_with_total.append(file)

print("200", len(same_with_200))
print("400", len(same_with_400))
print("600", len(same_with_600))
print("toatal:", len(same_with_total))


for file in same_with_total:
    if file in files_200:
        files_200.remove(file)
    if file in files_400:
        files_400.remove(file)
    if file in files_600:
        files_600.remove(file)
    if file in files_800:
        files_800.remove(file)

files_remaining = set(files_200 + files_400 + files_600 + files_800)
print(files_remaining)




iou_dict = {}
for file in files_remaining:
    file_gt = os.path.join(path_gt, file)
    file_200 = os.path.join(path_200, file)
    file_400 = os.path.join(path_400, file)
    file_600 = os.path.join(path_600, file)
    file_800 = os.path.join(path_800, file)
    
    
    file_name = str(file.split(".")[0])

    mean_iou_200 = meanIOU(file_200, file_gt)
    iou_dict[f"file_200_{file_name}"] = mean_iou_200
    






