import os
import shutil
import importlib
import subprocess
from PyQt5 import QtWidgets

# 程式運行初始化，為新裝置安裝所需套件
def install_request(self):
    try:
        # 偵測是否已安裝nibabel套件
        importlib.import_module('nibabel')
        print("nibabel is installed")
    except ImportError:
        print("nibabel is not installed. Installing...")
        # 呼叫cmd安裝nibabel
        subprocess.check_call(["pip", "install", "nibabel"])

    try:
        # 偵測是否已安裝SimpleITK套件
        importlib.import_module('SimpleITK')
        print("SimpleITK is installed")
    except ImportError:
        print("SimpleITK is not installed. Installing...")
        # 呼叫cmd安裝SimpleITK
        subprocess.check_call(["pip", "install", "SimpleITK"])

    try:
        # 偵測是否已安裝pydicom套件
        importlib.import_module('pydicom')
        print("pydicom is installed")
    except ImportError:
        print("pydicom is not installed. Installing...")
        # 呼叫cmd安裝pydicom
        subprocess.check_call(["pip", "install", "pydicom"])

    try:
        # 偵測是否已安裝PyQt5套件
        importlib.import_module('PyQt5')
        print("PyQt5 is installed")
    except ImportError:
        print("PyQt5 is not installed. Installing...")
        # 呼叫cmd安裝PyQt5
        subprocess.check_call(["pip", "install", "PyQt5"])

    try:
        # 偵測是否已安裝vtk套件
        importlib.import_module('vtk')
        print("vtk is installed")
    except ImportError:
        print("vtk is not installed. Installing...")
        # 呼叫cmd安裝vtk
        subprocess.check_call(["pip", "install", "vtk"])

    try:
        # 偵測是否已安裝nnUNet套件
        importlib.import_module('nnunet')
        print("nnunet is installed")
    except ImportError:
        print("nnunet is not installed. Installing...")
        # 呼叫cmd安裝nnUNet
        subprocess.check_call(["pip", "install", "nnunet"])
        # 跳出警告對話框
        QtWidgets.QMessageBox.about(self, "Warning", "若要使用nnUNet，請先設置好相關資料夾\n請將訓練模型放置於nnUnet_trained_models資料夾中")

    try:
        # 偵測是否已安裝tensorflow keras simpleitk套件
        importlib.import_module('tensorflow keras simpleitk')
        print("tensorflow keras simpleitk is installed")
    except ImportError:
        print("tensorflow keras simpleitk is not installed. Installing...")
        # 呼叫cmd安裝tensorflow keras simpleitk
        subprocess.check_call(["pip", "install", "tensorflow", "keras", 'simpleitk'])

    try:
        # 偵測是否已安裝tensorflow keras simpleitk套件
        importlib.import_module('batchgenerators')
        print("batchgenerators is installed")
    except ImportError:
        print("batchgenerators is not installed. Installing...")
        # 呼叫cmd安裝tensorflow keras simpleitk
        subprocess.check_call(["pip", "install", "batchgenerators==0.21"])

def set_temp_folder():
    #--------------------設定暫存資料夾--------------------   
    #設定暫存位址資料夾
    if os.name == 'nt':  #windows系統
        path_out = r'C:\Users\User\Desktop\test'
    else:  #windows系統以外
        path_out = '/Users/andy/Documents/test'

    #如果沒有path_out路徑就新增一個
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    #--------------------設定暫存資料夾--------------------
    return path_out 

def clear_temp_folder(input_path):
    #--------------------清空暫存資料--------------------
    #偵測暫存資料夾中檔案數量
    files_count = len(os.listdir(input_path))
    #偵測暫存資料夾中是否存有檔案
    if files_count > 0:
        files = os.listdir(input_path)  #列出路徑內所有檔案
        for file in files:
            file_path = os.path.join(input_path, file)  #重整檔案路徑
            #若該路徑為資料，則刪除資料
            if os.path.isfile(file_path):
                os.remove(file_path)
            #若該路徑為資料夾，則刪除資料夾
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path) #刪除整個目錄
    #--------------------清空暫存資料--------------------

def set_model_temp_folder():
    #--------------------設定stl暫存資料夾--------------------   
    #設定暫存位址資料夾
    if os.name == 'nt':  #windows系統
        path_out = r'C:\Users\User\Desktop\stl_test'
    else:
        path_out = '/Users/andy/Documents/stl_test'
    #如果沒有path_out路徑就新增一個
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    #--------------------設定stl暫存資料夾-------------------- 
    return path_out

def clear_model_temp_folder(input_path):
    #--------------------清空暫存資料--------------------
    #偵測暫存資料夾中檔案數量
    files_count = len(os.listdir(input_path))
    #偵測暫存資料夾中是否存有檔案
    if files_count > 0:
        files = os.listdir(input_path)  #列出路徑內所有檔案
        for file in files:
            file_path = os.path.join(input_path, file)  #重整檔案路徑
            os.remove(file_path)
    #--------------------清空暫存資料--------------------
