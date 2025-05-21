import os
import subprocess
import importlib
import platform
import style
from PyQt5 import QtWidgets

def predict(in_path, out_path, task_no):
    if os.name == 'nt':
       # 設置 nnunet_raw_data_base 路徑
        nnunet_raw_data_base = r'E:\nnUNet-master\nnUNetFrame\DATASET\nnUnet_raw'
        # 若找不到 nnunet_raw_data_base 路徑，就新建一個
        if not os.path.exists(nnunet_raw_data_base):
            print("No fround nnunet_raw_data_base!")
            os.makedirs(nnunet_raw_data_base)
            # 設置 nnU-Net 環境變數：原始數據路徑
            command = f"cmd.exe /c set nnUNet_raw_data_base= {nnunet_raw_data_base}"
            os.system(f'start {command}')
            # process = subprocess.Popen(['cmd.exe', '/c', command], shell=False, stdout=subprocess.PIPE, cwd=cwd)

        # 設置 nnunet_preprocessed 路徑
        nnunet_preprocessed = r'E:\nnUNet-master\nnUNetFrame\DATASET\nnUnet_preprocessed'
        # 若找不到 nnunet_preprocessed 路徑，就新建一個
        if not os.path.exists(nnunet_preprocessed):
            print("No fround nnunet_preprocessed!")
            os.makedirs(nnunet_preprocessed)
            # 設置 nnU-Net 環境變數：原始數據路徑
            command = f"cmd.exe /c set nnUNet_preprocessed= {nnunet_preprocessed}"
            os.system(f'start {command}')
            # process = subprocess.Popen(['cmd.exe', '/c', command], shell=False, stdout=subprocess.PIPE, cwd=cwd)

        # 設置 results_folder 路徑
        results_folder = r'E:\nnUNet-master\nnUNetFrame\DATASET\nnUNet_results'
        # 若找不到 results_folder 路徑，就新建一個
        if not os.path.exists(results_folder):
            print("No fround results_folder!")
            os.makedirs(results_folder)
            # 設置 nnU-Net 環境變數：原始數據路徑
            command = f"cmd.exe /c set RESULTS_FOLDER= {results_folder}"
            os.system(f'start {command}')
            # process = subprocess.Popen(['cmd.exe', '/c', command], shell=False, stdout=subprocess.PIPE, cwd=cwd)

        # cwd = r'C:\Users\User\Desktop'
    else:
        # 設置 nnU-Net 環境變數：原始數據路徑
        os.environ['nnUNet_raw_data_base'] = '/Users/andy/Desktop/DataSet/nnUnet_raw'

        # 設置 nnU-Net 環境變數：預處理數據路徑
        os.environ['nnUNet_preprocessed'] = '/Users/andy/Desktop/DataSet/nnUnet_preprocessed'

        # 設置 nnU-Net 環境變數：結果路徑
        os.environ['RESULTS_FOLDER'] = '/Users/andy/Desktop/DataSet/nnUnet_trained_models'

        # 設置 cmd 執行位址
        cwd = '/Users/andy/Desktop'

 
    command = f'start cmd.exe /c nnUNetv2_predict -i {in_path} -o {out_path} -d {task_no} -c 3d_fullres -f 4 '
    print(command)
    # os.system(f'start {command}')
    # 使用 subprocess.run 调用命令，等待其完成
    result = subprocess.run(command, shell=True)

    return result

   

    # # 宣告變數：模型推理指令
    # infer = 'nnUNet_predict -i ' +in_path+ ' -o ' +out_path+ ' -t ' + task_no + ' -m 3d_fullres -f 4'
    # print(infer)

    # if os.name == "nt":
    #     # 呼叫cmd執行infer指令
    #     process = subprocess.Popen(['cmd.exe', '-c', infer], shell=False, stdout=subprocess.PIPE, cwd=cwd)
    # else:
    #     # 呼叫cmd執行infer指令
    #     process = subprocess.Popen(['/bin/zsh', '-c', infer], shell=False, stdout=subprocess.PIPE, cwd=cwd)
    
    # #蒐集cmd運行後的輸出（bytes形式）
    # output, _ = process.communicate()
    # #將 bytes 形式轉換為相應的 str 形式輸出顯示
    # output = output.decode()
    # return output
