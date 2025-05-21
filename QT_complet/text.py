# import os 
# from collections import Counter
# import shutil

# def get_max_files(folder_path):
#     file_sizes = {}
#     size_count = []
#     temp_dicom = os.path.join(folder_path, "temp")
#     if os.path.exists(temp_dicom):
#         shutil.rmtree(temp_dicom)
#         os.makedirs(temp_dicom, exist_ok=True)
#     else:
#         os.makedirs(temp_dicom, exist_ok=True)
#     # 遍历文件夹中的文件
#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             size = round(os.path.getsize(file_path) / 1000)

#             # 检查大小是否已经在字典中
#             if size in file_sizes:
#                 file_sizes[size].append(file_path)
#             else:
#                 file_sizes[size] = [file_path]
#             size_count.append(size)

#     counter = Counter(size_count)
#     most_common_value = counter.most_common(1)[0][0]
    
#     # 取出文件path
#     files_we_need = [paths for paths in file_sizes[most_common_value]]

#     for file in files_we_need:
#         file_name = os.path.basename(file)
#         new_file_path = os.path.join(temp_dicom , file_name)
#         shutil.copy(file, new_file_path)
    


#     return files_we_need

# # 用法示例
# folder_path = '/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/虎科林彥昆老師/非正常版/01'
# file_sizes = get_max_files(folder_path)
# print(file_sizes)
from sklearn.metrics import confusion_matrix
import os
import nibabel as nib
# import torch
import numpy as np
from typing import Tuple, List, Union
from nnunetv2.utilities.plans_handling.plans_handler import PlansManager

def compute_tp_fp_fn_tn(mask_ref: np.ndarray, mask_pred: np.ndarray, ignore_mask: np.ndarray = None):
    if ignore_mask is None:
        use_mask = np.ones_like(mask_ref, dtype=bool)
    else:
        use_mask = ~ignore_mask
    tp = np.sum((mask_ref & mask_pred) & use_mask)
    fp = np.sum(((~mask_ref) & mask_pred) & use_mask)
    fn = np.sum((mask_ref & (~mask_pred)) & use_mask)
    tn = np.sum(((~mask_ref) & (~mask_pred)) & use_mask)
    return tp, fp, fn, tn

def region_or_label_to_mask(segmentation: np.ndarray, region_or_label: Union[int, Tuple[int, ...]]) -> np.ndarray:
    if np.isscalar(region_or_label):
        return segmentation == region_or_label
    else:
        mask = np.zeros_like(segmentation, dtype=bool)
        for r in region_or_label:
            mask[segmentation == r] = True
    return mask

gt_folder = r'/Volumes/andy_SSD/dicom/Task32_tsinus/result/summary_gt'
gt_lst = [file for file in  os.listdir(gt_folder) if file.endswith(".nii.gz")]
pseudo_folder = r'/Volumes/andy_SSD/dicom/Task32_tsinus/result/infers_summary'

result_dict = {
                "Data" : [],
                "Dice" : [],
                "meanIoU" : [],
                "Accuracy" : [],
                "Recall" : [],
                "Precesion" : []
                }

results = {}
results['metrics'] = {}

plans_file = r'/Volumes/andy_SSD/dicom/Task32_tsinus/result/plans.json'
dataset_json = r'/Volumes/andy_SSD/dicom/Task32_tsinus/result/dataset.json'
lm = PlansManager(plans_file).get_label_manager(dataset_json) # "plans_file" : plans.json, "dataset_json" : dataset.json
region_or_label = [lm.foreground_regions if lm.has_regions else lm.foreground_labels, lm.ignore_label]

for data in gt_lst:
    gt_path = os.path.join(gt_folder, data)
        # 讀取第二个.nii.gz檔案
    image_gt = nib.load(gt_path)
    data_gt = image_gt.get_fdata()

    pseudo_path = os.path.join(pseudo_folder, data)
    image_pseudo = nib.load(pseudo_path)
    data_pseudo = image_pseudo.get_fdata()

    mask_ref = region_or_label_to_mask(data_gt, region_or_label)
    mask_pred = region_or_label_to_mask(data_pseudo, region_or_label)

    

    for r in region_or_label:
        results['metrics'][r] = {}
        mask_ref = region_or_label_to_mask(data_gt, r)
        mask_pred = region_or_label_to_mask(data_pseudo, r)
        tp, fp, fn, tn = compute_tp_fp_fn_tn(mask_ref, mask_pred)
        if tp + fp + fn == 0:
            results['metrics'][r]['Dice'] = np.nan
            results['metrics'][r]['IoU'] = np.nan
        else:
            results['metrics'][r]['Dice'] = 2 * tp / (2 * tp + fp + fn)
            results['metrics'][r]['IoU'] = tp / (tp + fp + fn)
        results['metrics'][r]['FP'] = fp
        results['metrics'][r]['TP'] = tp
        results['metrics'][r]['FN'] = fn
        results['metrics'][r]['TN'] = tn
        results['metrics'][r]['n_pred'] = fp + tp
        results['metrics'][r]['n_ref'] = fn + tp

    

    print(results['metrics'][1])

    # # 將 NumPy 數組轉換為 PyTorch Tensor
    # if os.name == 'nt':
    #     torch.device('gpu')
    #     data_gt_tensor = torch.from_numpy(data_gt).float().to('cuda')
    #     data_pseudo_tensor = torch.from_numpy(data_pseudo).float().to('cuda')
    # else:
    #     torch.device('mps')
    #     data_gt_tensor = torch.from_numpy(data_gt).float().to('mps')
    #     data_pseudo_tensor = torch.from_numpy(data_pseudo).float().to('mps')

    # # 將資料攤平為一維數組
    # data_gt_flat = data_gt.flatten()
    # data_pseudo_flat = data_pseudo.flatten()

    # data_gt_flat = torch.flatten(data_gt_tensor)
    # data_pseudo_flat = torch.flatten(data_pseudo_tensor)

    # 計算混淆矩陣
    # confusion_mat = confusion_matrix(data_gt_flat, data_pseudo_flat, labels=[0, 1, 2])
    # confusion_mat = confusion_matrix(data_gt_flat.cpu().numpy(), data_pseudo_flat.cpu().numpy(), labels=[0, 1, 2])

    # tp_1 = confusion_mat[1, 1]
    # fp_1 = confusion_mat[0, 1]
    # tn_1 = confusion_mat[0, 0] + confusion_mat[1, 1] + confusion_mat[2, 2] - confusion_mat[0, 1]  # True negative for all classes
    # fn_1 = confusion_mat[1, 0] + confusion_mat[2, 0]  # False negative for class 1

    # # Extract values from the confusion matrix
    # tp_2 = confusion_mat[2, 2]  # True positive for class 2 (left sinus)
    # fp_2 = confusion_mat[0, 2]  # False positive for class 2
    # tn_2 = confusion_mat[0, 0] + confusion_mat[1, 1] + confusion_mat[2, 2] - confusion_mat[0, 2]  # True negative for all classes
    # fn_2 = confusion_mat[2, 0] + confusion_mat[1, 0]  # False negative for class 2

    # tp = (tp_1 + tp_2)/2
    # fp = (fp_1 + fp_2)/2
    # tn = (tn_1 + tn_2)/2
    # fn = (fn_1 + fn_2)/2

    # result_dict["Data"].append(str(data.split(".")[0]))
    # result_dict["Dice"].append(round(2*tp/(2*tp+fp+fn),6))
    # result_dict["meanIoU"].append(round(tp/(tp+fp+fn), 6))
    # result_dict["Accuracy"].append(round((tp+tn)/(tp+tn+fp+fn), 6))
    # result_dict["Recall"].append(round(tp/(tp+fn), 6))
    # result_dict["Precesion"].append(round(tp/(tp+fp), 6))

    # print(f"Dice_{data}_1:", 2*tp_1/(2*tp_1+fp_1+fn_1))
    # print(f"Dice_{data}_2:", 2*tp_2/(2*tp_2+fp_2+fn_2))
    # print(f"iou_{data}_1:", tp_1/(tp_1+fp_1+fn_1))
    # print(f"iou_{data}_2:", tp_2/(tp_2+fp_2+fn_2))

