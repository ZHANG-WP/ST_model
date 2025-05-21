import subprocess
from PyQt5.QtWidgets import QFileDialog, QInputDialog
import nibabel as nib
import numpy as np
import os
import SimpleITK as sitk
from PyQt5 import QtWidgets
import platform
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
from PIL import Image, ImageQt
import usevtk
import set_up
import processdiocm

#宣告變數：設定暫存資料夾存放預測後的dicom檔案
path_out = set_up.set_temp_folder()
#清空暫存資料夾
set_up.clear_temp_folder(path_out)

def preprocess(self, function):
    #設置功能（資料轉換, 前處理, 訓練）
    #資料轉換
    if function == "convert": 
        #在UI的狀態列上顯示
        self.ui.statusbar.showMessage("請選擇資料夾", 10000) 
        #使用者選取欲處裡資料夾
        convert_path = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Desktop/git-respostory/QT_complet/DataSet')
        if convert_path:
            #命令cmd執行
            docmd(self, function, convert_path) #convert
            docmd(self, "preprocess", convert_path) #preprocess
    #模型訓練
    if function == "train":
            task_id, ok = QInputDialog.getInt(None, "輸入欲訓練ID", "請輸入任務ID:") #跳出詢問框填選欲訓練之任務ID
            if ok:
                #命令cmd,模型訓練指令執行
                docmd(self, "train", task_id) 

def docmd(self, function, input):
    #當使用mac os 系統時才設置環境變數
    if platform.system() == 'Darwin':
        # 設置 nnU-Net 環境變數：原始數據路徑
        os.environ['nnUNet_raw'] = '/Users/andy/Desktop/git-respostory/QT_complet/DataSet/nnUnet_raw'

        # 設置 nnU-Net 環境變數：預處理數據路徑
        os.environ['nnUNet_preprocessed'] = '/Users/andy/Desktop/git-respostory/QT_complet/DataSet/nnUnet_preprocessed'

        # 設置 nnU-Net 環境變數：結果路徑
        os.environ['nnUNet_results'] = '/Users/andy/Desktop/git-respostory/QT_complet/DataSet/nnUnet_trained_models'
    

    #指定CMD執行之資料夾目錄
    # if platform.system() == 'Windows':
    #         cwd = r"C:\Users\User\Desktop"
    # elif platform.system() == 'Darwin':
    #         cwd = r"/Users/andy/Desktop/git-respostory/QT_complet"

    #判斷執行動作（convert, preprocess, train）
    if function == 'convert':
        #取得資料夾路徑的檔案名稱
        file_name = os.path.basename(input)
        #取得file_name中的第5個和第6個字，作為任務id
        task_id = file_name[4:6]
        print(task_id)
        if platform.system() == 'Windows':
            command = f'cmd.exe /k call conda activate nnunetV2 && nnUNetv2_convert_MSD_dataset -i {input} -overwrite_id {task_id}'
            print(command)
            # os.system(f'start {command}')
        elif platform.system() == 'Darwin':
            #資料轉換cmd指令
            convert = 'nnUNetv2_convert_MSD_dataset -i '+input

        #狀態列顯示運行指令
        self.ui.statusbar.showMessage(convert, 10000)

    if function == 'preprocess':
        #取得資料夾路徑的檔案名稱
        file_name = os.path.basename(input)
        #取得file_name中的第5個和第6個字，作為任務id
        task_id = file_name[4:6]
        print(task_id)
        if platform.system() == 'Windows':
            command = f'cmd.exe /k call conda activate nnunetV2 && nnUNetv2_plan_and_preprocess -d {task_id} --verify_dataset_integrity'
            print(command)
            # os.system(f'start {command}')
            # #資料前處理cmd指令
            # preprocess = 'nnUNet_plan_and_preprocess -t '+ task_id
        elif platform.system() == 'Darwin':
            #資料前處理cmd指令
            preprocess = 'nnUNetv2_plan_and_preprocess -d '+ task_id
        
        #狀態列顯示運行指令
        self.ui.statusbar.showMessage(preprocess, 10000)

        # #進入cmd中運行preprocess指令
        # if platform.system() == 'Windows':
        #     process = subprocess.Popen(['cmd.exe', '/c', preprocess], shell=False, stdout=subprocess.PIPE, cwd=cwd)
        # elif platform.system() == 'Darwin':
        #     process = subprocess.Popen(['/bin/zsh', '-c', preprocess], shell=False, stdout=subprocess.PIPE, cwd=cwd)
        
        # #蒐集cmd運行後的輸出（bytes形式）
        # output, _ = process.communicate()
        # #將 bytes 形式轉換為相應的 str 形式輸出顯示
        # print(output.decode())

    if function == 'train':
        if platform.system() == 'Windows':
            command = f'cmd.exe /k call conda activate nnunetV2 && nnUNetv2_train 0{str(input)} 3d_fullres 4'
            os.system(f'start {command}')
            # #模型訓練cmd指令
            # train = 'nnUNet_train 3d_fullres nnUNetTrainerV2' +str(input)+ ' 4' 
        elif platform.system() == 'Darwin':
            #模型訓練cmd指令
            train = 'nnUNetv2_train ' +str(input)+ ' 3d_fullres 0 -device mps' #-device mps用於mac
        
        #狀態列顯示運行指令
        self.ui.statusbar.showMessage(train, 10000)
        # #進入cmd中運行train指令
        # if platform.system() == 'Windows':
        #     process = subprocess.Popen(['cmd.exe', '-c', train], shell=False, stdout=subprocess.PIPE, cwd=cwd)
        # elif platform.system() == 'Darwin':
        #     process = subprocess.Popen(['/bin/zsh', '-c', train], shell=False, stdout=subprocess.PIPE, cwd=cwd)
        # #蒐集cmd運行後的輸出（bytes形式）
        # output, _ = process.communicate()
        # #將 bytes 形式轉換為相應的 str 形式輸出顯示
        # print(output.decode())

    self.ui.tabWidget.setCurrentIndex(0)
    # #將cmd的輸出顯示於label中
    # self.ui.cmdlabel.setText(output.decode())
    #跳出完成對話框
    QtWidgets.QMessageBox.about(self, "finish", "完成")
    # #將label清空
    # self.ui.cmdlabel.setText("")


#nnunet運行推理(單一檔案推理並檢視預測成果)
def nnunet_infer (self, in_path, out_path):   
    if in_path and out_path:
        # #狀態列顯示
        # self.ui.statusbar.showMessage("處理中", 10000)
        # #切換到父目錄
        # dir_name = os.path.dirname(in_path)
        # #取得附目錄中最後一個檔案名稱，在此為任務名稱
        # data_name = os.path.basename(dir_name)
        # #選取data_name中的第5和第6個字作為task_no
        
        # task_no = data_name[5:7]
        # #若為windows系統
        # if platform.system() == 'Windows':
        #     #nnunet模型推理指令
        #     command = 'nnUNet_predict -i ' +in_path+ ' -o ' +out_path+ ' -t ' + task_no + ' -m 3d_fullres -f 4'  # Replace with your command
        #     #指定cmd執行資料夾
        #     cwd = r"C:\Users\User\Desktop\nnUNetframe\nnUNetframe"
        #     #進入cmd中運行command指令
        #     process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, cwd=cwd)
        #     #蒐集cmd運行後的輸出（bytes形式）
        #     output, _ = process.communicate()
        #     self.ui.statusbar.showMessage(command, 10000)
        #     output = output.decode()
        # #若為mac os系統
        # elif platform.system() == 'Darwin':
        #     output = predict_model_mac.predict(in_path, out_path, task_no)
        
        
        # #將cmd的輸出顯示於label中
        # self.ui.tabWidget.setCurrentIndex(1)
        # self.ui.cmdlabel.setText(output)
        # QtWidgets.QMessageBox.about(self, "finish", "推理完成")
        # self.ui.cmdlabel.setText("")

        
        #---------------------------------------------------顯示推理成果---------------------------------------------------
        #清空暫存資料
        set_up.clear_temp_folder(path_out)
        #選擇欲顯示的預測成果並檢視
        choose_to_display(self, out_path)

        #--------------------儲存stl檔案--------------------
        #確認暫存資料夾中資料量
        dcm_folders = os.listdir(path_out)
        
        #如果多檔案且勾選列被勾選
        if len(os.listdir(out_path)) > 1 and self.ui.checkBox_generate_model.isChecked():
            for folder in dcm_folders:
                folder_path = os.path.join(path_out, folder) # 重新設定資料路徑
                if self.ui.model_path.toPlainText(): # 如果輸出資料夾有填上輸出位址
                    try:
                        out_put = os.path.join(self.ui.model_path.toPlainText(), folder) # 將輸出路徑加上檔案名稱作為新的路徑
                        usevtk.vtk_3d(self, folder_path, out_put) # 進行3D檔案的存檔
            
                    except:
                        #顯示狀態列
                        self.ui.statusbar.showMessage("請輸入3D模型輸出位址", 10000)
        #如果只有單一檔案且勾選列被勾選
        elif len(os.listdir(out_path)) == 1 and self.ui.checkBox_generate_model.isChecked():
            out_put = os.path.join(self.ui.model_path.toPlainText(), os.listdir(out_path)[0]) # 將輸出路徑加上檔案名稱作為新的路徑
            usevtk.vtk_3d(self, path_out, out_put) # 進行3D檔案的存檔


        # #--------------------檢視nii.gz影像--------------------
        # #讀取輸入影像
        # img = nib.load(result_path).get_fdata()
        # #取得輸入影像之大小
        # print(img.shape)
        # #計算如何能取得最佳plt子圖排列方式
        # weigth = int(img.shape[2] ** 0.5 + 1)
        # long = weigth
        # print(weigth, long)

        # for i in range(img.shape[2]):
        #     plt.subplot(long, weigth, i + 1)
        #     plt.imshow(img[:, :, i])
        #     plt.gcf().set_size_inches(10, 10)

        # # Save the plot as a PNG file
        # buf = io.BytesIO()
        # plt.savefig(buf, format='png')
        # buf.seek(0)
        # image = Image.open(buf)

        # # Display the image on the label
        # pixmap = QPixmap.fromImage(ImageQt.toqimage(image))
        # self.ui.label.setPixmap(pixmap)
        # buf.truncate()
        # #--------------------檢視nii.gz影像--------------------
        self.ui.stackedWidget.setCurrentIndex(0)


def choose_to_display(self, in_path):
    #關閉VTK視窗
    usevtk.vtkclose(self)
    #顯示狀態列
    self.ui.statusbar.showMessage("讀取推理成果", 10000)
    
    #將上一段輸出作為本段輸入，並刪除不必要檔案
    if os.path.exists(os.path.join(in_path, "plans.pkl")):
        os.remove(os.path.join(in_path, "plans.pkl"))
    if os.path.exists(os.path.join(in_path, ".DS_Store")):
        os.remove(os.path.join(in_path, ".DS_Store"))
    if os.path.exists(os.path.join(in_path, "prediction_time.txt")):
        os.remove(os.path.join(in_path, "prediction_time.txt"))
        
    #列出in_path路經中所有檔案
    outcome_data = os.listdir(in_path)
    print(outcome_data)

    #偵測若輸入資料為多個檔案
    if len(outcome_data) > 1:
        #為避免每次呼叫時，都進行轉檔，會先偵測暫存資料夾內是否已經有資料
        if len(os.listdir(path_out)) == 0:
            #轉檔nii to dicom(全部)
            processdiocm.nifti_2_dicom.convert_all(self, in_path, path_out)
        #列出暫存資料夾中所有檔案
        dcm_folders = os.listdir(path_out) 

        #刪除mac默認檔
        if ".DS_Store" in dcm_folders:
            dcm_folders.remove(".DS_Store")
        
        # 設定tabWidget至第二頁（輸出成果頁）
        self.ui.tabWidget.setCurrentIndex(1)
        # 顯示輸出成果
        self.ui.cmdlabel.setText("當前預測資料：" + str(dcm_folders))
        dcm_folders = sorted(dcm_folders, key=lambda x: int(x))

        while True:
            # 跳出下拉式選單對話視窗
            selected_item, ok = QInputDialog.getItem(None, "選擇病患檔案預測結果", "請選擇病患:", dcm_folders)
            if ok and selected_item:  # 如果使用者選擇了一個項目
                try:
                    index_no = dcm_folders.index(selected_item)
                    #以num檔案，重新整理整輸入路徑
                    result_path = os.path.join(path_out, dcm_folders[index_no])
                    # 設定選擇按鈕: 顯示
                    self.ui.btn_exchange_model.setVisible(True) # ！debug功臣！
                    break
                #如果輸入值不在資料夾中則重新輸入
                except ValueError:
                    print(f"不存在 {index_no} 資料")
            else:
                #將label重置
                self.ui.cmdlabel.setText("")
                #調整tabＷidget回到主頁面
                self.ui.tabWidget.setCurrentIndex(0)
                #關閉vtk視窗
                usevtk.vtkclose(self)
                #跳出函式
                return
            
    #若是單一檔案
    else:
        # 設定選擇按鈕: 顯示
        self.ui.btn_exchange_model.setVisible(False)
        #轉檔nii to dicom(單一)
        processdiocm.nifti_2_dicom.convert_single(self, os.path.join(in_path, outcome_data[0]), path_out)
        #重新整理整輸入路徑
        result_path = path_out
    
    #清空cmdlabel
    self.ui.cmdlabel.setText("")

    if result_path:
        print(result_path)
        #vtk檢視3D模型
        usevtk.view_after_infer(self, result_path)   
        #最終將輸入路徑清除
        result_path = ""
    

