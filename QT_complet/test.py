import os 
import nibabel as nib
import numpy as np
from sklearn.metrics import confusion_matrix

gt_folder = r'/Volumes/andy_SSD/dicom/Task32_tsinus/t031_others/validation/gt_nii'
# gt_lst = [file for file in  os.listdir(gt_folder) if file.endswith(".nii.gz")]
pseudo_folder = r'/Volumes/andy_SSD/dicom/Task32_tsinus/result/infers_val'

gt_lst = ["29208671.nii.gz"]
result_dict = {
                "Data" : [],
                "Dice" : [],
                "meanIoU" : [],
                "Accuracy" : [],
                "Recall" : [],
                "Precesion" : []
                }

for data in gt_lst:
    gt_path = os.path.join(gt_folder, data)
    pseudi_path = os.path.join(pseudo_folder, data)

    image_gt = nib.load(gt_path)
    data_gt = image_gt.get_fdata()
    image_pseudo = nib.load(pseudi_path)
    data_pseudo = image_pseudo.get_fdata()
    

    # 將資料攤平為一維數組
    data_gt_flat = data_gt.flatten()
    data_pseudo_flat = data_pseudo.flatten()

    # confusion_mat = confusion_matrix(data_gt_flat, data_pseudo_flat, labels=[0, 1, 2])
    confusion_mat = confusion_matrix(data_gt_flat, data_pseudo_flat)

    # tp_1 = confusion_mat[1, 1] # correct 
    # fp_1 = confusion_mat[0, 1] + confusion_mat[2, 1] # correct 
    # tn_1 = confusion_mat[0, 0] + confusion_mat[2, 2] + confusion_mat[0, 2] + confusion_mat[2, 0] # correct
    # fn_1 = confusion_mat[1, 0] + confusion_mat[1, 2] # correct


    # tp_2 = confusion_mat[2, 2] # correct 
    # fp_2 = confusion_mat[0, 2] + confusion_mat[1, 2] # correct 
    # tn_2 = confusion_mat[0, 0] + confusion_mat[1, 1] + confusion_mat[0, 1] + confusion_mat[1, 0] # correct
    # fn_2 = confusion_mat[2, 0] + confusion_mat[2, 1] # correct

    tp_1 = confusion_mat[1, 1] # correct 
    fp_1 = confusion_mat[0, 1]
    tn_1 = confusion_mat[0, 0]
    fn_1 = confusion_mat[1, 0]

    dice = round(2 * tp_1 / (2 * tp_1 + fp_1 + fn_1), 6)
    iou = round(tp_1 / (tp_1 + fp_1 + fn_1), 6)
    accuracy = round((tp_1 + tn_1) / (tp_1 + tn_1 + fp_1 + fn_1), 6)
    recall = round(tp_1 / (tp_1 + fn_1), 6)
    precesion = round(tp_1 / (tp_1 + fp_1), 6)


    print(f"{data}_dice : {dice}")
    print(f"{data}_meanIoU : {iou}")
    print(f"{data}_accuracy : {accuracy}")
    print(f"{data}_recall : {recall}")
    print(f"{data}_precesion : {precesion}")
    
    # print(f"FN: {fn_2}")
    # print(f"FP: {fp_2}")
    # print(f"TN: {tn_2}")
    # print(f"TP: {tp_2}")

    