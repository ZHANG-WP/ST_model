import json
import os
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

def make_json (self):
    self.ui.statusbar.showMessage("請選擇欲存入之任務資料夾", 10000)
    path, filetype = QFileDialog.getSaveFileName(self, 'Save File', 'dataset.json')
    task_num = os.path.dirname(path) #取得任務資料夾路徑
    folder_path_labeled = os.path.join(task_num, "dataset_labeled")  # dataset_labeled位置
    if os.path.exists(folder_path_labeled):
        labeled = os.listdir(folder_path_labeled)
        if ".DS_Store" in labeled:
            labeled.remove(".DS_Store")
    else:
        labeled = None

    folder_path_pseudo_labeled = os.path.join(task_num, "dataset_pseudo_labeled")  # dataset_labeled位置
    if os.path.exists(folder_path_pseudo_labeled):
        pseudo_labeled = os.listdir(folder_path_pseudo_labeled)
        if ".DS_Store" in pseudo_labeled:
            pseudo_labeled.remove(".DS_Store")
    else:
        pseudo_labeled = None

    if path:
        folder_path_tr = os.path.join(task_num, "imagesTr") #imageTr位置
        if os.path.exists(folder_path_tr):
            folder_path_ts = os.path.join(task_num, "imagesTs")  # imageTs位置
            if os.path.exists(folder_path_ts):
                name = os.listdir(folder_path_tr)
                if ".DS_Store" in name:
                    name.remove(".DS_Store")

                name_test = os.listdir(folder_path_ts)
                if ".DS_Store" in name_test:
                    name_test.remove(".DS_Store")

                with open(path, "w+", encoding="utf-8") as  f:
                    f.write('{\n')
                    f.write('"name": "Right Sinuse",\n')
                    f.write('"description": "Right sinuse segmentation",\n')
                    f.write('"reference": "groups/jiafucang",\n')
                    f.write('"licence": "CC-BY-SA 4.0",\n')
                    f.write('"release": "1.0 4/3/2020",\n')
                    f.write('"tensorImageSize": "3D",\n')
                    f.write('"modality": {\n')
                    f.write('"0": "CT"\n')
                    f.write('},\n\n')
                    f.write('"labels": {\n')
                    f.write('"0": "background",\n')
                    f.write('"1": "left Sinus"\n},\n')
                    f.write(f'"numTraining": {len(name)},\n')   #训练集个数
                    f.write(f'"numTest": {len(name_test)},\n')  #测试集个数
                    f.write('"training":[')
                    beforeI = '{"image":"./imagesTr/'
                    beforeL = '","label":"./labelsTr/'
                    for i in range(0,len(name)):
                        f.write(beforeI)
                        f.write(name[i][-24:])
                        f.write(beforeL)
                        f.write(name[i][-24:])
                        f.write('"}')
                        print(name[i][-24:])
                        if i<len(name)-1:
                            f.write(',')
                    f.write('],\n')
                    f.write('"test":[')
                    for i in range(0,len(name_test)):
                        f.write('"./imagesTs/'+name_test[i][-24:]+'"')  #測試文件名长度
                        if i<len(name_test)-1:
                            f.write(',')

                    if labeled == None:
                        f.write(']\n}')
                    else:
                        f.write('],\n')
                        f.write('"dataset_labeled":[')
                        for i in range(0,len(labeled)):
                            f.write('"./dataset_labeled/'+labeled[i][-24:]+'"')  #測試文件名长度
                            if i<len(labeled)-1:
                                f.write(',')
                        f.write('],\n')
                    
                        if pseudo_labeled is not None:
                            f.write('"dataset_pseudo_labeled":[')
                            for i in range(0,len(pseudo_labeled)):
                                f.write('"./dataset_labeled/'+pseudo_labeled[i][-24:]+'"')  #測試文件名长度
                                if i<len(pseudo_labeled)-1:
                                    f.write(',')
                            f.write(']\n}')

                openwindow = QtWidgets.QMessageBox()
                openwindow.setText("json檔已建立完成，是否需要檢視")
                openwindow.setWindowTitle("finish")
                openwindow.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                # 顯示視窗，等待使用者按下按鈕
                response = openwindow.exec_()
                if response == QtWidgets.QMessageBox.Yes:
                    # 使用QDesktopServices來開啟檔案
                    QDesktopServices.openUrl(QUrl.fromLocalFile(path))
            else:
                print("路徑中沒有符合“imageTs”的資料夾")
                QtWidgets.QMessageBox.about(self, "Erro", "路徑中沒有符合“imageTs”的資料夾")
        else:
            print("路徑中沒有符合“imageTr”的資料夾")
            QtWidgets.QMessageBox.about(self, "Erro", "路徑中沒有符合“imageTr”的資料夾")
