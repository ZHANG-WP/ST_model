from PyQt5 import QtWidgets
import os 
import platform
import subprocess
import shutil
import nibabel as nib
import contorl
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
import openfile
import predict_model_mac
import numpy as np
import pandas as pd
import time
from pathlib import Path
from sklearn.metrics import confusion_matrix

def get_nifti_infolder(self, result_folder, out_folder):
    nii_gz_files = [file for file in os.listdir(result_folder) if file.endswith(".nii.gz")]
    for data in nii_gz_files :
        print(data)
        nifti_path = os.path.join(result_folder, data)
        out_folder_path = os.path.join(out_folder, data)
        shutil.copyfile(nifti_path, out_folder_path)
    QtWidgets.QMessageBox.about(self, "finish", "成功提取NifTi檔案")

def meanIOU(image1, image2, num_classes=3):
    # 使用 nibabel 讀取影像
    image1 = nib.load(image1)
    image2 = nib.load(image2)

    # 將影像的像素值轉換為多類別標籤
    image1 = image1.get_fdata().astype(np.int32)
    image2 = image2.get_fdata().astype(np.int32)

    # 將像素值轉換為一維數組
    image1_flat = image1.flatten()
    image2_flat = image2.flatten()

    # 計算 Jaccard Index（IOU）值
    ious = []
    for class_label in range(num_classes -1):
        class_mask1 = (image1_flat == class_label +1)
        class_mask2 = (image2_flat == class_label +1)

        intersection = np.sum(class_mask1 & class_mask2)
        union = np.sum(class_mask1 | class_mask2)

        iou = intersection / union if union > 0 else 0
        ious.append(iou)

    # 計算所有 IOU 值的平均值
    return np.mean(ious)

def compute_confusion_mat(gt_path, pseudo_path, seg_region = [0, 1, 2]):
     # 讀取第二个.nii.gz檔案
    image_gt = nib.load(gt_path)
    data_gt = image_gt.get_fdata()

    image_pseudo = nib.load(pseudo_path)
    data_pseudo = image_pseudo.get_fdata()

    # # 將 NumPy 數組轉換為 PyTorch Tensor
    # if os.name == 'nt':
    #     torch.device('gpu')
    #     data_gt_tensor = torch.from_numpy(data_gt).float().to('cuda')
    #     data_pseudo_tensor = torch.from_numpy(data_pseudo).float().to('cuda')
    # else:
    #     torch.device('mps')
    #     data_gt_tensor = torch.from_numpy(data_gt).float().to('mps')
    #     data_pseudo_tensor = torch.from_numpy(data_pseudo).float().to('mps')

    # 將資料攤平為一維數組
    data_gt_flat = data_gt.flatten()
    data_pseudo_flat = data_pseudo.flatten()

    # data_gt_flat = torch.flatten(data_gt_tensor)
    # data_pseudo_flat = torch.flatten(data_pseudo_tensor)

    if len(seg_region) == 2:
        # segmentation "1" 
        # 計算混淆矩陣
        confusion_mat = confusion_matrix(data_gt_flat, data_pseudo_flat)
        # confusion_mat = confusion_matrix(data_gt_flat.cpu().numpy(), data_pseudo_flat.cpu().numpy(), labels=[0, 1, 2])

        tp = confusion_mat[1, 1] # correct 
        fp = confusion_mat[0, 1] # correct 
        tn = confusion_mat[0, 0] # correct
        fn = confusion_mat[1, 0] # correct

        dice = round(2 * tp / (2 * tp + fp + fn), 6)
        iou = round(tp / (tp + fp + fn), 6)
        accuracy = round((tp + tn) / (tp + tn + fp + fn), 6)
        recall = round(tp / (tp + fn), 6)
        precesion = round(tp / (tp + fp), 6)

        return dice, iou, accuracy, recall, precesion

    elif len(seg_region) == 3:
        matrix ={
            "tp": [],
            "fp": [], 
            "tn": [],
            "fn":[]
        }

        loss = {
            "Dice" : [],
            "meanIoU" : [],
            "Accuracy" : [],
            "Recall" : [],
            "Precesion" : []
        }

        # segmentation "1" 
        # 計算混淆矩陣
        confusion_mat = confusion_matrix(data_gt_flat, data_pseudo_flat, labels= seg_region)
        # confusion_mat = confusion_matrix(data_gt_flat.cpu().numpy(), data_pseudo_flat.cpu().numpy(), labels=[0, 1, 2])
        
        tp = confusion_mat[1, 1] # correct 
        fp = confusion_mat[0, 1] + confusion_mat[2, 1] # correct 
        tn = confusion_mat[0, 0] + confusion_mat[2, 2] + confusion_mat[0, 2] + confusion_mat[2, 0] # correct
        fn = confusion_mat[1, 0] + confusion_mat[1, 2] # correct
        matrix["tp"].append(tp)
        matrix["fp"].append(fp)
        matrix["tn"].append(tn)
        matrix["fn"].append(fn)

        # segmentation "2" 
        tp = confusion_mat[2, 2] # correct 
        fp = confusion_mat[0, 2] + confusion_mat[1, 2] # correct 
        tn = confusion_mat[0, 0] + confusion_mat[1, 1] + confusion_mat[0, 1] + confusion_mat[1, 0] # correct
        fn = confusion_mat[2, 0] + confusion_mat[2, 1] # correct
        matrix["tp"].append(tp)
        matrix["fp"].append(fp)
        matrix["tn"].append(tn)
        matrix["fn"].append(fn)

        for i in range(len(seg_region)-1):
            dice = round(2 * matrix["tp"][i] / (2 * matrix["tp"][i] + matrix["fp"][i] + matrix["fn"][i]), 6)
            iou = round(matrix["tp"][i] / (matrix["tp"][i] + matrix["fp"][i] + matrix["fn"][i]), 6)
            accuracy = round((matrix["tp"][i] + matrix["tn"][i]) / (matrix["tp"][i] + matrix["tn"][i] + matrix["fp"][i] + matrix["fn"][i]), 6)
            recall = round(matrix["tp"][i] / (matrix["tp"][i] + matrix["fn"][i]), 6)
            precesion = round(matrix["tp"][i] / (matrix["tp"][i] + matrix["fp"][i]), 6)

            loss["Dice"].append(dice)
            loss["meanIoU"].append(iou)
            loss["Accuracy"].append(accuracy)
            loss["Recall"].append(recall)
            loss["Precesion"].append(precesion)
        
        dice = sum(loss["Dice"]) / len(loss["Dice"])
        iou = sum(loss["meanIoU"]) / len(loss["meanIoU"])
        accuracy = sum(loss["Accuracy"]) / len(loss["Accuracy"])
        recall = sum(loss["Recall"]) / len(loss["Recall"])
        precesion = sum(loss["Precesion"]) / len(loss["Precesion"])
    
        return dice, iou, accuracy, recall, precesion


def set_up_reliability_window(self):
    contorl.home(self)
    self.ui.tabWidget.setCurrentIndex(6)  # 設定tabwidget到tab_reliablity頁面
    self.ious = []

    # ------- 設定各值得初始值-------
    self.ui.gt_data_lst.clear()
    self.ui.pseudo_data_lst.clear()
    self.ui.gt_path.setText("")
    self.ui.pseudo_path.setText("")
    self.ui.mean_reliability.setText("")
    self.ui.top_persent.setText("")
    self.ui.save_reliability_data_path.setText("")
    self.ui.reliability_lst.clear()
    self.ui.check_label_raw.setText("")
    # ------- 設定各值得初始值-------

    # ------- 設定頁面初始狀態，讓一些依不同階段進行顯示之功能關閉 -------
    self.ui.gt_data_lst.setVisible(False)
    self.ui.pseudo_data_lst.setVisible(False)
    self.ui.btn_evaluate.setVisible(False)
    self.ui.btn_calculate_reliablity.setVisible(False)
    self.ui.mean_reliability.setVisible(False)
    self.ui.btn_mean_reliability.setVisible(False)
    self.ui.label_12.setVisible(False)
    self.ui.label_9.setVisible(False)
    self.ui.background_out_folder.setVisible(False)
    self.ui.save_reliability_data_path.setVisible(False)
    self.ui.btn_save_reliability_data_path.setVisible(False)
    self.ui.btn_save_top_data.setVisible(False)
    self.ui.df_display_reliability.setVisible(False)
    self.ui.reliability_lst.setVisible(False)
    self.ui.btn_log_reliability.setVisible(False)
    self.ui.btn_clear_reliability.setVisible(False)
    self.ui.top_persent.setVisible(False)
    self.ui.btn_top_persent.setVisible(False)
    self.ui.label_15.setVisible(False)
    self.ui.label_16.setVisible(False)
    self.ui.check_label_raw.setVisible(False)
    # ------- 設定頁面初始狀態，讓一些依不同階段進行顯示之功能關閉 -------
    self.ui.btn_evaluate.clicked.connect(lambda: evaluate_model()) # 評估模型表現
    def evaluate_model():
        # import torch
        # import torch.nn.functional as F

        self.ui.df_display_reliability.clear() # 清空表格顯示視窗

        # 讀取 .nii.gz 檔案
        gt_folder = self.ui.gt_path.toPlainText()
        pseudo_folder = self.ui.pseudo_path.toPlainText()
        
        result_dict = {
                        "Data" : [],
                        "Dice" : [],
                        "meanIoU" : [],
                        "Accuracy" : [],
                        "Recall" : [],
                        "Precesion" : []
                        }
        
        for data in self.gt_data:
            gt_path = os.path.join(gt_folder, data)
            pseudo_path = os.path.join(pseudo_folder, data)
            dice, iou, accuracy, recall, precesion = compute_confusion_mat(gt_path, pseudo_path, seg_region = [0, 1, 2])

            result_dict["Data"].append(str(data.split(".")[0]))
            result_dict["Dice"].append(round(dice, 6))
            result_dict["meanIoU"].append(round(iou, 6))
            result_dict["Accuracy"].append(round(accuracy, 6))
            result_dict["Recall"].append(round(recall, 6))
            result_dict["Precesion"].append(round(precesion, 6))

        # 計算所有驗證分數平均
        result_dict["Data"].append("Total Avg.")
        result_dict["Dice"].append(round(sum(result_dict["Dice"])/ len(result_dict["Dice"]), 6))
        result_dict["meanIoU"].append(round(sum(result_dict["meanIoU"])/ len(result_dict["meanIoU"]), 6))
        result_dict["Accuracy"].append(round(sum(result_dict["Accuracy"])/ len(result_dict["Accuracy"]), 6))
        result_dict["Recall"].append(round(sum(result_dict["Recall"])/ len(result_dict["Recall"]), 6))
        result_dict["Precesion"].append(round(sum(result_dict["Precesion"])/ len(result_dict["Precesion"]), 6))

        dfs = []  # Create an empty list to store DataFrames
        data = []
        dice = []
        meaniou = []
        accuracy = []
        recall =[]
        precesion = []

        for i in range(len(result_dict["Data"])):
            data.append(result_dict["Data"][i])
            dice.append(result_dict["Dice"][i])
            meaniou.append(result_dict["meanIoU"][i])
            accuracy.append(result_dict["Accuracy"][i])
            recall.append(result_dict["Recall"][i])
            precesion.append(result_dict["Precesion"][i])
        
        df = pd.DataFrame({
            "Dice": dice,
            "meanIoU": meaniou,
            "Accuracy": accuracy,
            "Recall": recall,
            "Precesion": precesion,
        }, index = data)
        dfs.append(df)
        
        result_df = pd.concat(dfs)
        self.ui.df_display_reliability.setRowCount(result_df.shape[0]) # 設定列數量
        self.ui.df_display_reliability.setColumnCount(result_df.shape[1]) # 設定欄數量
        self.ui.df_display_reliability.setHorizontalHeaderLabels(result_df.columns.tolist()) # 使用欄名稱作為列標籤
        self.ui.df_display_reliability.setVerticalHeaderLabels(result_df.index.tolist())  # 使用索引作為行標籤

        column_widths = [100, 180, 180, 180, 180, 180]   # Specify the width for each column
        # Set column widths
        for col, width in enumerate(column_widths):
            self.ui.df_display_reliability.setColumnWidth(col, width)

        # 设置列头字体大小
        header_font = QtGui.QFont()
        header_font.setPointSize(18)  # 设置字体大小为24
        self.ui.df_display_reliability.horizontalHeader().setFont(header_font)

        # 设置行头字体大小
        vertical_header_font = QtGui.QFont()
        vertical_header_font.setPointSize(18)  # 设置字体大小为24
        self.ui.df_display_reliability.verticalHeader().setFont(vertical_header_font)

        for i, row in enumerate(result_df.values):  # 使用 enumerate 獲取索引和行數據
            for j, val in enumerate(row):  # 使用 enumerate 獲取索引和列數據
                item = QTableWidgetItem(str(val))
                self.ui.df_display_reliability.setItem(i, j, item) # 設置表格顯示視窗顯示之資料
        
        # 將整個表格中的文字置中
        for i in range(self.ui.df_display_reliability.rowCount()): # 掃描所有列
            for j in range(self.ui.df_display_reliability.columnCount()): # 掃描所有欄
                item = self.ui.df_display_reliability.item(i, j)
                item.setTextAlignment(QtCore.Qt.AlignCenter) # 文字置中

        self.ui.df_display_reliability.resizeRowsToContents() # 自動調整行高以顯示完整的行標籤文字
        # 開啟表格顯示視窗
        self.ui.df_display_reliability.show() 
        self.ui.df_display_reliability.setVisible(True)

        openwindow = QtWidgets.QMessageBox()
        openwindow.setText("是否要存成Excel?")
        openwindow.setWindowTitle("finish")
        openwindow.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        # 顯示視窗，等待使用者按下按鈕
        response = openwindow.exec_()
        if response == QtWidgets.QMessageBox.Yes:
            # transposed_df = df.transpose()  # 對DataFrame進行轉置(行列轉換)
            excel_path = r"/Users/andy/Downloads/model_difference.xlsx"
            for df in dfs:
                df.to_excel(excel_path, index=True) # 將轉置後的DataFrame保存為Excel文件
            if platform.system() == 'Darwin':
                subprocess.run(['open', excel_path]) # 使用cmd打開所生成的excel檔案
            elif platform.system() == 'Windows':
                subprocess.run(['open', excel_path], shell=False) # 使用cmd打開所生成的excel檔案

    
    # 設定計算按鈕連動
    self.ui.btn_calculate_reliablity.clicked.connect(lambda: calculate()) # 計算信度
    def calculate():
        # 讀取 .nii.gz 檔案
        gt_folder = self.ui.gt_path.toPlainText()
        pseudo_folder = self.ui.pseudo_path.toPlainText()
        

        self.iou_dict = {}
        for data in self.gt_data:
            gt_path = os.path.join(gt_folder, data)
            pseudo_path = os.path.join(pseudo_folder, data)
            #　dice, iou, accuracy, recall, precesion = compute_confusion_mat(gt_path, pseudo_path, seg_region = [0, 1, 2])
            # 計算 mean IOU
            mean_iou = meanIOU(pseudo_path, gt_path, num_classes=3)
            self.iou_dict[str(data.split(".")[0])] = mean_iou

        # 全部的meanIoU平均
        total = 0
        for file, value in self.iou_dict.items():
            total += value

        self.data_dict = {
            "Data name" : [], # 設置檔案名稱的空陣列
            "Data Path" : [], # 設置檔案路徑的空陣列
            "meanIoU" : [] # 設置meaniou的空陣列
            }
        

        for data, value in self.iou_dict.items():
            path = os.path.join(gt_folder, f"{data}.nii.gz")
            self.data_dict["Data name"].append(data)
            self.data_dict["Data Path"].append(path)
            self.data_dict["meanIoU"].append(value)
        
        dfs = []  # Create an empty list to store DataFrames

        for i in range(len(self.data_dict["Data Path"])):
            df = pd.DataFrame({
                "Data name": [self.data_dict["Data name"][i]],
                "Data Path": [self.data_dict["Data Path"][i]],
                "meanIoU": [self.data_dict["meanIoU"][i]]
            })
            dfs.append(df)

        # Concatenate all DataFrames in the list
        self.result_df = pd.concat(dfs)

        self.ui.df_display_reliability.clear() # 清空表格顯示視窗
        self.ui.df_display_reliability.setRowCount(self.result_df.shape[0]) # 設定列數量
        self.ui.df_display_reliability.setColumnCount(self.result_df.shape[1]) # 設定欄數量
        self.ui.df_display_reliability.setHorizontalHeaderLabels(self.result_df.columns.tolist()) # 使用欄名稱作為列標籤

        column_widths = [130, 560, 290]   # Specify the width for each column
        # Set column widths
        for col, width in enumerate(column_widths):
            self.ui.df_display_reliability.setColumnWidth(col, width)

        # 设置列头字体大小
        header_font = QtGui.QFont()
        header_font.setPointSize(18)  # 设置字体大小为24
        self.ui.df_display_reliability.horizontalHeader().setFont(header_font)

        # 设置行头字体大小
        vertical_header_font = QtGui.QFont()
        vertical_header_font.setPointSize(18)  # 设置字体大小为24
        self.ui.df_display_reliability.verticalHeader().setFont(vertical_header_font)

        for i, row in enumerate(self.result_df.values):  # 使用 enumerate 獲取索引和行數據
            for j, val in enumerate(row):  # 使用 enumerate 獲取索引和列數據
                item = QTableWidgetItem(str(val))
                self.ui.df_display_reliability.setItem(i, j, item) # 設置表格顯示視窗顯示之資料
        
        # 將整個表格中的文字置中
        for i in range(self.ui.df_display_reliability.rowCount()): # 掃描所有列
            for j in range(self.ui.df_display_reliability.columnCount()): # 掃描所有欄
                item = self.ui.df_display_reliability.item(i, j)
                item.setTextAlignment(QtCore.Qt.AlignCenter) # 文字置中

        self.ui.df_display_reliability.resizeRowsToContents() # 自動調整行高以顯示完整的行標籤文字

        # 開啟表格顯示視窗
        self.ui.df_display_reliability.show() 
        self.ui.df_display_reliability.setVisible(True)
        
        # 開啟選取趴數
        self.ui.mean_reliability.setVisible(True)
        self.ui.label_9.setVisible(True)
        self.ui.btn_mean_reliability.setEnabled(False)
        self.ui.btn_mean_reliability.setVisible(True)
        self.ui.label_16.setVisible(True)

        # 開啟信度記錄列
        self.ui.reliability_lst.setVisible(True)
        self.ui.btn_log_reliability.setVisible(True)
        self.ui.btn_log_reliability.setEnabled(True)
        self.ui.btn_clear_reliability.setVisible(True)
        
    
    self.ui.btn_log_reliability.clicked.connect(lambda: log_value()) 
    def log_value():
        for item_text in self.data_dict["meanIoU"]:
            self.ious.append(item_text)
            item = QListWidgetItem(f"[{len(self.ious)}]  {str(round(item_text, 8))}")
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.ui.reliability_lst.addItem(item)
        self.ui.btn_log_reliability.setEnabled(False)
        self.ui.btn_clear_reliability.setEnabled(True)
        
        iou_mean = round(sum(self.ious)/len(self.ious), 6)
        self.ui.mean_reliability.setText(str(iou_mean))

    
    self.ui.btn_clear_reliability.clicked.connect(lambda: clear_log()) 
    def clear_log():
        self.ui.reliability_lst.clear()
        self.ious.clear()
        self.ui.mean_reliability.setText("0")
        self.ui.btn_clear_reliability.setEnabled(False)
        self.ui.btn_mean_reliability.setEnabled(False)
            
        
    # 設定計算按鈕連動
    self.ui.btn_mean_reliability.clicked.connect(lambda: get_better_data()) # 提鎖定％數資料
    def get_better_data():
        if self.ui.mean_reliability.toPlainText():
            self.ui.btn_mean_reliability.setEnabled(True)
            # 取得 s 分數
            mean_reliability = self.ui.mean_reliability.toPlainText()
            # Sort the DataFrame by "meanIoU" in descending order
            sorted_df = self.result_df.sort_values(by="meanIoU", ascending=False)

            self.better_mean_reliability_df = sorted_df[sorted_df['meanIoU'] >= float(mean_reliability)]

            # print(self.better_mean_reliability_df)
            self.ui.df_display_reliability.clear() # 清空表格顯示視窗
            self.ui.df_display_reliability.setRowCount(self.better_mean_reliability_df.shape[0]) # 設定列數量
            self.ui.df_display_reliability.setColumnCount(self.better_mean_reliability_df.shape[1]) # 設定欄數量
            self.ui.df_display_reliability.setHorizontalHeaderLabels(self.better_mean_reliability_df.columns.tolist()) # 使用欄名稱作為列標籤

            column_widths = [130, 560, 290]    # Specify the width for each column
            # Set column widths
            for col, width in enumerate(column_widths):
                self.ui.df_display_reliability.setColumnWidth(col, width)

            # 设置列头字体大小
            header_font = QtGui.QFont()
            header_font.setPointSize(18)  # 设置字体大小为24
            self.ui.df_display_reliability.horizontalHeader().setFont(header_font)

            # 设置行头字体大小
            vertical_header_font = QtGui.QFont()
            vertical_header_font.setPointSize(18)  # 设置字体大小为24
            self.ui.df_display_reliability.verticalHeader().setFont(vertical_header_font)

            for i, row in enumerate(self.better_mean_reliability_df.values):  # 使用 enumerate 獲取索引和行數據
                for j, val in enumerate(row):  # 使用 enumerate 獲取索引和列數據
                    item = QTableWidgetItem(str(val))
                    self.ui.df_display_reliability.setItem(i, j, item) # 設置表格顯示視窗顯示之資料
            
            # 將整個表格中的文字置中
            for i in range(self.ui.df_display_reliability.rowCount()): # 掃描所有列
                for j in range(self.ui.df_display_reliability.columnCount()): # 掃描所有欄
                    item = self.ui.df_display_reliability.item(i, j)
                    item.setTextAlignment(QtCore.Qt.AlignCenter) # 文字置中

            self.ui.df_display_reliability.resizeRowsToContents() # 自動調整行高以顯示完整的行標籤文字

            # 開啟表格顯示視窗
            self.ui.df_display_reliability.show() 

            # 開啟存檔
            self.ui.label_12.setVisible(True)
            self.ui.save_reliability_data_path.setVisible(True)
            self.ui.btn_save_reliability_data_path.setVisible(True)
            self.ui.btn_save_top_data.setVisible(True)
            self.ui.btn_save_top_data.setEnabled(False)
            self.ui.background_out_folder.setVisible(True)

            self.ui.top_persent.setVisible(True)
            self.ui.btn_top_persent.setVisible(True)
            self.ui.btn_top_persent.setEnabled(False)
            self.ui.label_15.setVisible(True)
        else:
            return
        
    self.ui.btn_top_persent.clicked.connect(lambda: get_top_data()) 
    def get_top_data():
        self.ui.btn_top_persent.setEnabled(False)
        top_percent = self.ui.top_persent.toPlainText()
        # Select the top 50% of the data
        self.better_mean_reliability_df = self.better_mean_reliability_df.head(round(int(top_percent)/100 * len(self.data_dict["meanIoU"])))
        self.ui.df_display_reliability.clear() # 清空表格顯示視窗
        self.ui.df_display_reliability.setRowCount(self.better_mean_reliability_df.shape[0]) # 設定列數量
        self.ui.df_display_reliability.setColumnCount(self.better_mean_reliability_df.shape[1]) # 設定欄數量
        self.ui.df_display_reliability.setHorizontalHeaderLabels(self.better_mean_reliability_df.columns.tolist()) # 使用欄名稱作為列標籤

        column_widths = [130, 560, 290]   # Specify the width for each column
        # Set column widths
        for col, width in enumerate(column_widths):
            self.ui.df_display_reliability.setColumnWidth(col, width)

        # 设置列头字体大小
        header_font = QtGui.QFont()
        header_font.setPointSize(18)  # 设置字体大小为24
        self.ui.df_display_reliability.horizontalHeader().setFont(header_font)

        # 设置行头字体大小
        vertical_header_font = QtGui.QFont()
        vertical_header_font.setPointSize(18)  # 设置字体大小为24
        self.ui.df_display_reliability.verticalHeader().setFont(vertical_header_font)

        for i, row in enumerate(self.better_mean_reliability_df.values):  # 使用 enumerate 獲取索引和行數據
            for j, val in enumerate(row):  # 使用 enumerate 獲取索引和列數據
                item = QTableWidgetItem(str(val))
                self.ui.df_display_reliability.setItem(i, j, item) # 設置表格顯示視窗顯示之資料
        
        # 將整個表格中的文字置中
        for i in range(self.ui.df_display_reliability.rowCount()): # 掃描所有列
            for j in range(self.ui.df_display_reliability.columnCount()): # 掃描所有欄
                item = self.ui.df_display_reliability.item(i, j)
                item.setTextAlignment(QtCore.Qt.AlignCenter) # 文字置中

        self.ui.df_display_reliability.resizeRowsToContents() # 自動調整行高以顯示完整的行標籤文字

        # 開啟表格顯示視窗
        self.ui.df_display_reliability.show() 


    # 設定輸出按鈕連動
    self.ui.btn_save_top_data.clicked.connect(lambda: save_top_data()) 
    def save_top_data():
        self.ui.btn_save_reliability_data_path.setEnabled(True)
        out_folder = self.ui.save_reliability_data_path.toPlainText()

        out_folder_tr = os.path.join(out_folder, "imagesTr")
        if not os.path.exists(out_folder_tr):
            os.makedirs(out_folder_tr)

        if os.path.exists(self.ts_path):
            out_folder_label = os.path.join(out_folder, "labelsTr")
            if not os.path.exists(out_folder_label):
                os.makedirs(out_folder_label)

        top_50_dict = self.better_mean_reliability_df.to_dict(orient='records')
        ts_lst = os.listdir(self.ts_path)
        if ".DS_Store" in  ts_lst:
            ts_lst.remove(".DS_Store")

        for record in top_50_dict:
            name = record["Data name"]
            path = record["Data Path"] # pseudo label的資料夾
            print("path : ", path)
            shutil.copyfile(path, os.path.join(out_folder_label, f"{str(name)}.nii.gz"))
            if os.path.exists(self.ts_path) and f"{name}_0000.nii.gz" in ts_lst:
                shutil.copyfile(os.path.join(self.ts_path, f"{str(name)}_0000.nii.gz"), os.path.join(out_folder_tr, f"{str(name)}_0000.nii.gz"))

        QtWidgets.QMessageBox.about(self, "finish", f"成功提取信度大於{self.ui.mean_reliability.toPlainText()}%檔案，並偵測到Ts資料夾。")

        # # 計算總數量
        # total_data_count = len(self.iou_dict)
        # # 取得前 50% 的數量
        # top_percent = 0.5
        # top_data_count = int(total_data_count * top_percent)

        # # 取得前 50% 的 key-value pairs
        # sorted_iou_pairs = sorted(self.iou_dict.items(), key=lambda item: item[1], reverse=True)
        # top_data_pairs = sorted_iou_pairs[:top_data_count]

        # out_folder = r'/Users/andy/Desktop/loss_compute/best50'
        # for file_name, value in top_data_pairs:
        #     source_path = os.path.join(pseudo_folder, f"{file_name}.nii.gz")
        #     out_folder_path = os.path.join(out_folder, f"{file_name}.nii.gz") 
        #     shutil.copy2(source_path, out_folder_path)
        #     print("finish!")
    
def open_gt_folder(self, input_folder):
    if input_folder:
        self.ui.gt_data_lst.clear()
        self.ui.gt_path.setText(input_folder) # 設定gt_path顯示資料夾之路徑

        files = os.listdir(input_folder) # 讀取input_foldery資料夾內資料
        if ".DS_Store" in files:
            files.remove(".DS_Store")
            
        self.ui.statusbar.showMessage("Loading : " + input_folder) # 狀態列顯示
            
        self.gt_data =[]
        for file in sorted(files):
            if os.path.splitext(file)[-1] == ".gz":
                self.gt_data.append(file)
        self.gt_data = sorted(self.gt_data)

        i = 0
        for item_text in self.gt_data:
            item = QListWidgetItem(str(i+1)+ '.    ' + '[ ' + str(item_text) + ' ]')
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.ui.gt_data_lst.addItem(item)
            i+=1
        
        # # 設定gt_data_lst顯示排序後資料
        # for i in range(len(self.gt_data)):
        #     self.ui.gt_data_lst.setText(self.ui.gt_data_lst.toPlainText() + str(i+1)+ '. ' + '[' + str(self.gt_data[i]) + ']' + '    ')
        
        self.ui.gt_data_lst.setVisible(True) # 開啟gt_data_lst顯示

       

        floder_path = input_folder.split(os.path.basename(input_folder))[0]
        self.ts_path = os.path.join(floder_path, "imagesTs")

        if os.path.exists(self.ts_path):
            self.ui.check_label_raw.setText("* Fround imagesTs Folder")
            self.ui.check_label_raw.setStyleSheet("color: #affc41")
        else:
            self.ui.check_label_raw.setText("* ImagesTs Folder is Not Fround !!")
            self.ui.check_label_raw.setStyleSheet("color: red")

        self.ui.check_label_raw.setVisible(True)

         # 如果pseudo_data_lst中已有文字，開啟計算按鈕與確認是否存檔
        if self.ui.pseudo_data_lst.count() > 0: 
            self.ui.btn_calculate_reliablity.setVisible(True)
            self.ui.btn_evaluate.setVisible(True)
    else:
        return
    
def open_pseudo_folder(self, input_folder):
    if input_folder:
        self.ui.pseudo_data_lst.clear()
        self.ui.pseudo_path.setText(input_folder) # 設定gt_path顯示資料夾之路徑

        files = os.listdir(input_folder) # 讀取input_foldery資料夾內資料
        if ".DS_Store" in files:
            files.remove(".DS_Store")
            
        self.ui.statusbar.showMessage("Loading : " + input_folder) # 狀態列顯示
            
        self.pseudo_data =[]
        for file in sorted(files):
            if os.path.splitext(file)[-1] == ".gz":
                self.pseudo_data.append(file)
        
        self.pseudo_data = sorted(self.pseudo_data)

        i = 0
        for item_text in self.pseudo_data:
            item = QListWidgetItem(str(i+1)+ '.    ' + '[ ' + str(item_text) + ' ]')
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.ui.pseudo_data_lst.addItem(item)
            i+=1

        # # 設定pseudo_data_lst顯示排序後資料
        # for i in range(len(self.pseudo_data)):
        #     self.ui.pseudo_data_lst.setText(self.ui.pseudo_data_lst.toPlainText() + str(i+1)+ '. ' + '[' + str(self.pseudo_data[i]) + ']' + '    ')
        
        self.ui.pseudo_data_lst.setVisible(True) # 開啟pseudo_data_lst顯示

        if self.ui.gt_data_lst.count() > 0:
            self.ui.btn_calculate_reliablity.setVisible(True)
            self.ui.btn_evaluate.setVisible(True)
    else:
        return
    
def open_out_folder(self):
        output_folder = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Desktop') # 開啟資料夾
        self.ui.save_reliability_data_path.setText(output_folder) #設定save_path顯示資料夾之路徑
        if output_folder is not None:
            self.ui.statusbar.showMessage("Going to save to : " + output_folder) # 狀態列顯示
        return output_folder # 回傳存檔路徑位置



def set_up_predict_checkpoint(self):
    contorl.home(self)
    self.ui.tabWidget.setCurrentIndex(7)  # 設定tabwidget到tab_reliablity頁面

    # ------- 設定各值得初始值-------
    self.ui.result_path.setText("")
    self.ui.checkpoint_lst.clear()
    self.ui.checkpoint_path.setText("")
    self.ui.checkpoint_output_path.setText("")
    self.ui.images_tr_path.setText("")
    self.ui.oversample_path.setText("")
    self.ui.num_ts.setText("Ts Num. :")
    self.ui.num_tr.setText("Tr Num. :")
    self.ui.oversample_times.setText("Times :")
    self.ui.target_num.setText("Target :")
    # ------- 設定各值得初始值-------

    # ------- 設定頁面初始狀態，讓一些依不同階段進行顯示之功能關閉 -------
    self.ui.btn_get_checkpoint.setVisible(False)
    self.ui.checkpoint_lst.setVisible(False)
    self.ui.label_10.setVisible(False)
    self.ui.checkpoint_path.setVisible(False)
    self.ui.label_14.setVisible(False)
    self.ui.checkpoint_input_path.setVisible(False)
    self.ui.btn_checkpoint_input_path.setVisible(False)
    self.ui.label_13.setVisible(False)
    self.ui.checkpoint_output_path.setVisible(False)
    self.ui.btn_checkpoint_output_path.setVisible(False)
    self.ui.btn_checkpointpredict.setVisible(False)
    self.ui.btn_to_calculate_reliability.setVisible(False)
    # oversample介面
    self.ui.background_12.setVisible(False)
    self.ui.label_19.setVisible(False)
    self.ui.label_17.setVisible(False)
    self.ui.label_18.setVisible(False)
    self.ui.images_tr_path.setVisible(False)
    self.ui.oversample_path.setVisible(False)
    self.ui.btn_images_tr_path.setVisible(False)
    self.ui.btn_oversample_path.setVisible(False)
    self.ui.btn_oversample.setVisible(False)
    self.ui.num_ts.setVisible(False)
    self.ui.num_tr.setVisible(False)
    self.ui.oversample_times.setVisible(False)
    self.ui.label_20.setVisible(False)
    self.ui.labels_tr_path.setVisible(False)
    self.ui.btn_labels_tr_path.setVisible(False)
    self.ui.target_num.setVisible(False)
    # ------- 設定頁面初始狀態，讓一些依不同階段進行顯示之功能關閉 -------

    
    self.ui.btn_get_checkpoint.clicked.connect(lambda: get_checkpoint_item())
    def get_checkpoint_item():
        self.ui.checkpoint_lst.clear()
        self.checkpoint_final_path = os.path.join(self.ui.result_path.toPlainText(), "checkpoint_final.pth")
        if os.path.exists(self.checkpoint_final_path):
            temp_folder = os.path.join(self.ui.result_path.toPlainText(), "temp") # 请替换为你的临时文件夹路径
            os.makedirs(temp_folder, exist_ok=True)
            # 构建目标文件的完整路径
            target_path = os.path.join(temp_folder, "checkpoint_final.pth")
            # 剪切文件到临时文件夹
            shutil.move(self.checkpoint_final_path, target_path)
            self.checkpoint_final_path = target_path # 設定checkpoint_final_path新路徑
            
        self.checkpoint =[]
        files = os.listdir(self.ui.result_path.toPlainText())
        if ".DS_Store" in files:
                files.remove(".DS_Store")
        for file in sorted(files):
            if os.path.splitext(file)[-1] == ".pth":
                self.checkpoint.append(file)
        self.checkpoint = sorted(self.checkpoint)

        for item_text in self.checkpoint:
            item = QListWidgetItem(item_text)
            self.ui.checkpoint_lst.addItem(item)
        self.ui.checkpoint_lst.setVisible(True) 
        self.ui.btn_get_checkpoint.setEnabled(False)
    
    self.ui.btn_checkpointpredict.clicked.connect(lambda: checkpoint_process())
    def checkpoint_process():
        checkpoint_path = self.ui.checkpoint_path.toPlainText()
        checkpoint_new_name = os.path.join(self.ui.result_path.toPlainText(), "checkpoint_final.pth")
        os.rename(checkpoint_path, checkpoint_new_name)
        # 找到 'Dataset' 后的位置
        index = self.ui.result_path.toPlainText().find('Dataset')

        if index != -1:
            # 提取数字部分
            number = self.ui.result_path.toPlainText()[index + len('Dataset'):].split('_')[0].lstrip('0')
            print(number)
        result = predict_model_mac.predict(self.ui.checkpoint_input_path.toPlainText(), self.ui.checkpoint_output_path.toPlainText(), number)

         # 检查返回代码，如果为 0 表示成功完成
        if result.returncode == 0:
            time.sleep(10)
            print("nnUNetv2_predict completed successfully")
            # 继续执行后续代码，比如 os.rename()
            os.rename(checkpoint_new_name, checkpoint_path)
            self.ui.btn_to_calculate_reliability.setVisible(True)
        else:
            print(f"nnUNetv2_predict failed with error: {result.stderr}")

    self.ui.btn_oversample.clicked.connect(lambda: oversample_tr(self))
    def oversample_tr(self):
        # 讀取Ts資料夾中檔案數量
        ts_num = self.ts_num

        # 讀取Tr資料夾中檔案數量
        tr_path = self.ui.images_tr_path.toPlainText()
        tr_num = len(self.tr_lst)

        # 讀取labelsTr資料夾中檔案數量
        labels_path = self.ui.labels_tr_path.toPlainText()

        out_path = self.ui.oversample_path.toPlainText()

        # 取得需要oversample的倍數
        if ts_num % tr_num == 0:
            target_num = ts_num // tr_num
        else:
            target_num = ts_num // tr_num + 1

        for i in range(target_num + 1):
            for data in self.tr_lst:
                raw_data = os.path.join(tr_path, data)
                label_data = os.path.join(labels_path, data)

                out_path_raw = os.path.join(out_path, "imagesTr")
                out_path_label = os.path.join(out_path, "labelsTr")

                if not os.path.exists(out_path_raw):
                    os.makedirs(out_path_raw)
                if not os.path.exists(out_path_label):
                    os.makedirs(out_path_label)
                

                data_name = data.split(".nii.gz")[0]
                if i == 0:
                    new_raw_data = os.path.join(out_path_raw, data)
                    new_label_data = os.path.join(out_path_label, data)
                else:
                    new_raw_data = os.path.join(out_path_raw, f"{data_name}_{i}.nii.gz")
                    new_label_data = os.path.join(out_path_label, f"{data_name}_{i}.nii.gz")

                print(new_raw_data)
                shutil.copyfile(raw_data, new_raw_data)
                shutil.copyfile(label_data, new_label_data)
        QtWidgets.QMessageBox.about(self, "finish", f"成功將Tr資料oversample至 {target_num} 倍")
            
    self.ui.btn_to_calculate_reliability.clicked.connect(lambda: set_up_reliability_window(self))

def open_result_folder(self, input_folder):
    if input_folder:
        self.ui.checkpoint_lst.clear()
        self.ui.result_path.setText(input_folder) # 設定gt_path顯示資料夾之路徑
        self.ui.statusbar.showMessage("Loading : " + input_folder) # 狀態列顯示

        self.ui.btn_get_checkpoint.setEnabled(True)
        self.ui.btn_get_checkpoint.setVisible(True)
    else:
        return

def open_in_folder_checkpont(self):
    input_folder = openfile.get_folder(self) # 開啟資料夾
    if input_folder:
        self.ui.checkpoint_input_path.setText(input_folder) #設定save_path顯示資料夾之路徑
        self.ui.statusbar.showMessage("Going to save to : " + input_folder) # 狀態列顯示
        self.ui.label_13.setVisible(True)
        self.ui.checkpoint_output_path.setVisible(True)
        self.ui.btn_checkpoint_output_path.setVisible(True)

        self.ui.background_12.setVisible(True)
        self.ui.label_19.setVisible(True)
        self.ui.label_17.setVisible(True)
        self.ui.label_18.setVisible(True)
        self.ui.images_tr_path.setVisible(True)
        self.ui.oversample_path.setVisible(True)
        self.ui.btn_images_tr_path.setVisible(True)
        self.ui.btn_oversample_path.setVisible(True)
        self.ui.btn_oversample.setVisible(True)
        self.ui.num_ts.setVisible(True)
        self.ui.num_tr.setVisible(True)
        self.ui.oversample_times.setVisible(True)
        self.ui.label_20.setVisible(True)
        self.ui.labels_tr_path.setVisible(True)
        self.ui.btn_labels_tr_path.setVisible(True)
        self.ui.target_num.setVisible(True)

        ts_lst = os.listdir(input_folder)
        if ".DS_Store" in ts_lst:
            ts_lst.remove(".DS_Store")
        self.ts_num = len(ts_lst)
        self.ui.num_ts.setText(f"Ts Num. : {self.ts_num} data")

        return input_folder # 回傳存檔路徑位置
    
def open_out_folder_checkpont(self):
    output_folder = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Desktop') # 開啟資料夾
    if output_folder:
        self.ui.checkpoint_output_path.setText(output_folder) #設定save_path顯示資料夾之路徑
        if output_folder is not None:
            self.ui.statusbar.showMessage("Going to save to : " + output_folder) # 狀態列顯示
            self.ui.btn_checkpointpredict.setVisible(True)
            return output_folder # 回傳存檔路徑位置
    
def open_tr_folder(self):
    input_folder = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Desktop') # 開啟資料夾
    if input_folder:
        self.ui.images_tr_path.setText(input_folder) #設定save_path顯示資料夾之路徑
        self.tr_lst = os.listdir(input_folder)
        if ".DS_Store" in self.tr_lst:
            self.tr_lst.remove(".DS_Store")
        tr_num = len(self.tr_lst)
        self.ui.num_tr.setText(f"Ts Num. : {tr_num} data")

        # 取得需要oversample的倍數
        if self.ts_num % tr_num == 0:
            target_num = self.ts_num // tr_num
        else:
            target_num = self.ts_num // tr_num + 1
        self.ui.oversample_times.setText(f"Times : {target_num}")
        self.ui.target_num.setText(f"Target : {tr_num * target_num} data")

        file_name = os.path.basename(input_folder)
        folder_path = input_folder.split(f"/{file_name}")[0]
        labels_path = os.path.join(folder_path, "labelsTr")
        if os.path.exists(labels_path):
            self.ui.labels_tr_path.setText(labels_path) #設定labels_tr_path顯示資料夾之路徑

        self.ui.statusbar.showMessage("imagesTr folder path  : " + input_folder) # 狀態列顯示
        return input_folder # 回傳存檔路徑位置

def open_label_tr_folder(self):
    input_folder = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Desktop') # 開啟資料夾
    if input_folder:
        labels_lst = os.listdir(input_folder)
        if ".DS_Store" in labels_lst:
            labels_lst.remove(".DS_Store")
        if sorted(self.tr_lst) == sorted(labels_lst):
            self.ui.labels_tr_path.setText(input_folder) #設定labels_tr_path顯示資料夾之路徑
        else:
            QtWidgets.QMessageBox.about(self, "Error", f"Tr資料與labels資料不對等，請檢查資料夾")
            self.ui.labels_tr_path.setText("") 
        return input_folder

    
    
def open_out_folder_oversample(self):
    output_folder = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Desktop') # 開啟資料夾
    if output_folder:
        self.ui.oversample_path.setText(output_folder) #設定save_path顯示資料夾之路徑
        if self.ui.images_tr_path.toPlainText() is not None:
            self.ui.statusbar.showMessage("Going to save to : " + output_folder) # 狀態列顯示
            return output_folder # 回傳存檔路徑位置
        

