from PyQt5.QtWidgets import QFileDialog, QInputDialog
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
import nibabel as nib
import glob
import matplotlib.pyplot as plt
import io
import re
import os
import openfile
from PIL import Image, ImageQt
from main import MainWindow

# def calldata(self):
#     data_path, filetype = QFileDialog.getOpenFileName(self, "Open folder", '/Users/andy/Documents')
#     return data_path

def read_nii(self):
    self.ui.cmdlabel.setText("")
    plt.clf()
    self.ui.label.setPixmap(QPixmap("icon/5.png"))
    self.ui.tabWidget.setCurrentIndex(0)
    nii_path, filetype = QFileDialog.getOpenFileName(self, "Open folder", '/Users/andy/Documents')
    if nii_path and 'nii' in nii_path:
        self.ui.statusbar.showMessage("讀取 : "+ nii_path, 10000)
        self.ui.label.setPixmap(QPixmap("影像顯示區域"))
        print(nii_path)
        img = nib.load(nii_path).get_fdata()
        print(img.shape)
        weigth = int(img.shape[2] ** 0.5 + 1)
        long = weigth
        print(weigth, long)

        for i in range(img.shape[2]):
            plt.subplot(long, weigth, i + 1)
            plt.imshow(img[:, :, i])
            plt.gcf().set_size_inches(10, 10)

        # Save the plot as a PNG file
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image = Image.open(buf)

        # Display the image on the label
        pixmap = QPixmap.fromImage(ImageQt.toqimage(image))
        self.ui.label.setPixmap(pixmap)
        buf.truncate()

    elif nii_path and 'nii' not in nii_path:
        self.ui.label.setPixmap(QPixmap("影像顯示區域"))
        QtWidgets.QMessageBox.about(self, "Erro", "檔案錯誤")

class Draw_loss(MainWindow):
    def __init__(self, all_txt_folder_1, all_txt_folder_2 = None, txt_folder_path = None):
        super(Draw_loss, self).__init__()
        self.txt_folder_path = txt_folder_path
        self.all_txt_folder_1 = all_txt_folder_1
        self.all_txt_folder_2 = all_txt_folder_2


    def merge_txt_files(self):
        files = os.listdir(self.all_txt_folder_1)
        if ".DS_Store" in files:
            files.remove(".DS_Store")
        txt_files = []
        for file_name in files:
            # Get all txt files
            txt_files.extend(glob.glob(os.path.join(self.all_txt_folder_1, file_name)))

        sorted_txt_files = sorted(txt_files)

        # 合併具有時間標記的資料
        merged_data = ''
        for txt_file in sorted_txt_files:
            with open(txt_file, 'r', encoding='utf-8') as file:
                file_data = file.read()
                merged_data += file_data

        out = os.path.join(self.txt_folder_path, "merged_data.txt")

        # 寫入合併的資料到新檔案
        with open(out, 'w', encoding='utf-8') as merged_file:
            merged_file.write(merged_data)

        QtWidgets.QMessageBox.about(self, "finish", f"資料合併完成並寫入 merged_data.txt。, path: {out}")

        return out

    def get_loss(self, txt_path):
        if txt_path and 'txt' in txt_path:
            # 定義一個字典，用來儲存資料
            self.data_dict = {'epoch': [], 'train loss': [], 'validation loss': [], 'Dice': []}
            
            # 讀取檔案
            with open(txt_path, 'r') as file:
                # 逐行讀取 
                lines = file.readlines()
                line_number = 0
                i=0
                while line_number < len(lines) and len(self.data_dict['epoch']) <= 1000:
                    line = lines[line_number]
                    epoch = re.search('Epoch (\d+)', line)

                    # 將數字加入對應的字典鍵值中
                    if epoch:
                        current_epoch = int(epoch.group(1))

                        if current_epoch == i and re.search('train_loss (-?\d+\.\d+)', lines[line_number + 2]):
                            self.data_dict['epoch'].append(current_epoch)
                            # Process lines after the current line
                            tl_match = re.search('train_loss (-?\d+\.\d+)', lines[line_number + 2])
                            if tl_match:
                                self.data_dict['train loss'].append(float(tl_match.group(1)))

                            vl_match = re.search('val_loss (-?\d+\.\d+)', lines[line_number + 3])
                            if vl_match:
                                self.data_dict['validation loss'].append(float(vl_match.group(1)))

                            lr_match = re.search('Pseudo dice \[(\d+\.\d+)\]', lines[line_number + 4])
                            if lr_match:
                                self.data_dict['Dice'].append(float(lr_match.group(1)))
                                
                            i += 1

                    line_number += 1
                
            # 取得train loss、validation loss和Dice的數值
            epoch = self.data_dict['epoch']
            train_loss = self.data_dict['train loss']
            val_loss = self.data_dict['validation loss']
            dice = self.data_dict['Dice']

            print(f"First Dice: {dice[0]}")
            print(f"Final Dice: {dice[-1]}")
            return epoch, train_loss, val_loss, dice
        else:
            return
        
    def draw_2_difference(self, txt_folder_path_1, txt_folder_path_2):
        x = range(1, 1001)
        # 建立一個subplot，共用x軸但有兩個y軸
        fig, ax1 = plt.subplots()

        # 選擇欲比對的線
        choice = ["Training Loss", "Validation Loss", "Dice score"]
        selected_item, ok = QInputDialog.getItem(None, "請選擇要比對之Loss值", ":", choice)


        if ok and selected_item:  # 如果使用者選擇了一個項目
            if selected_item == "Training Loss":
                epoch_a, train_loss_a, val_loss_a, dice_a = self.get_loss(txt_folder_path_1)
                epoch_b, train_loss_b, val_loss_b, dice_b = self.get_loss(txt_folder_path_2)

                ax1.plot(x, train_loss_a, label = "Training Loss Before", color= "#03045e")
                ax1.plot(x, train_loss_b, label = "Training Loss After", color='#0077b6', linestyle='--')
                # 設定圖例
                ax1.legend(loc='upper right', fontsize=12)

            elif selected_item == "Validation Loss":
                epoch_a, train_loss_a, val_loss_a, dice_a = self.get_loss(txt_folder_path_1)
        
                epoch_b, train_loss_b, val_loss_b, dice_b = self.get_loss(txt_folder_path_2)

                ax1.plot(x, val_loss_a, label = "Validation Loss Before", color= "#d00000")
                ax1.plot(x, val_loss_b, label = "Validation Loss After", color='#e85d04', linestyle='--')
                # 設定圖例
                ax1.legend(loc='upper right', fontsize=12)
                
            else:
                epoch_a, train_loss_a, val_loss_a, dice_a = self.get_loss(txt_folder_path_1)
        
                epoch_b, train_loss_b, val_loss_b, dice_b = self.get_loss(txt_folder_path_2)

                ax1.plot(x, dice_a, label = "Dice Before", color= "#008000")
                ax1.plot(x, dice_b, label = "Dice After", color='#9ef01a', linestyle='--')
                # 設定圖例
                ax1.legend(loc='lower right', fontsize=13)
            
            #設置刻度字體大小
            ax1.tick_params(axis='x', labelsize=14)
            ax1.tick_params(axis='y', labelsize=14)
            
            # 設定圖表的標題和軸標籤
            ax1.set_title(f"Compare {selected_item} between Before After", fontsize=16)
            ax1.set_xlabel('Epoch', fontsize=14)
            ax1.set_ylabel('Loss', fontsize=14)
            
            # Save the plot as a PNG file
            buf = io.BytesIO()
            plt.savefig(buf, format='jpeg')
            buf.seek(0)
            image = Image.open(buf)
            # Display the image on the label
            pixmap = QPixmap.fromImage(ImageQt.toqimage(image))
            scaled_pixmap = pixmap.scaled(1200, 700)
            return scaled_pixmap

        else: 
            return

    def draw(self, epoch, train_loss =None, val_loss =None, dice =None):
        self.ui.cmdlabel.setText("")
        self.ui.tabWidget.setCurrentIndex(0)
        # 設定x軸的數值
        x = range(1, len(epoch)+1)

        # 建立一個subplot，共用x軸但有兩個y軸
        fig, ax1 = plt.subplots()

        # 繪製train loss和validation loss的曲線
        if train_loss is not None:
            ax1.plot(x, train_loss, label='Train Loss', color='blue')

        if val_loss is not None:
            ax1.plot(x, val_loss, label='Validation Loss', color='red')

        # 調整區間上下限
        if train_loss and val_loss:
            ax1.set_ylim([min(train_loss)-0.05, max(val_loss)+0.3])

        if dice is not None:
            ax2 = ax1.twinx()

            # 繪製Dice的曲線
            ax2.plot(x, dice, label='DSC', color='green')

            # 調整區間上下限
            ax2.set_ylim([min(dice)-0.4, max(dice)+0.07])
            ax2.tick_params(axis='y', labelsize=16)
            ax2.set_ylabel('DSC', fontsize=14)
            ax2.legend(loc='upper left', fontsize=13) 

        #設置刻度字體大小
        ax1.tick_params(axis='x', labelsize=16)
        ax1.tick_params(axis='y', labelsize=16)
        

        # 設定圖表的標題和軸標籤
        ax1.set_title('Training and Validation Loss and DSC', fontsize=18)
        ax1.set_xlabel('Epoch', fontsize=14)
        ax1.set_ylabel('Loss', fontsize=14)

        # 設定圖例
        ax1.legend(loc='upper right', fontsize=13)
            
        # 建立一個 QPixmap 物件
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image = Image.open(buf)
        pixmap = QPixmap.fromImage(ImageQt.toqimage(image))

        # 顯示圖表
        scaled_pixmap = pixmap.scaled(1200, 700)
        return scaled_pixmap
        # self.ui.label.setPixmap(scaled_pixmap)
        # buf.truncate()
    
def mul_getloss_draw(self, txt_folder_path, merge_txt_output_folder):
    draw_loss_obj = Draw_loss(all_txt_folder_1 = txt_folder_path, txt_folder_path = merge_txt_output_folder)

    out = draw_loss_obj.merge_txt_files()
    epoch, train_loss, val_loss, dice = draw_loss_obj.get_loss(out)
    scaled_pixmap = draw_loss_obj.draw(epoch, train_loss, val_loss, dice)
    self.ui.label.setPixmap(scaled_pixmap)
    
def single_getloss_draw(self, merge_txt_output_folder):
    draw_loss_obj = Draw_loss(all_txt_folder_1 = merge_txt_output_folder)
    epoch, train_loss, val_loss, dice = draw_loss_obj.get_loss(merge_txt_output_folder)
    scaled_pixmap = draw_loss_obj.draw(epoch, train_loss, val_loss, dice)
    self.ui.label.setPixmap(scaled_pixmap)

def run_2_difference(self, input_1):
    if input_1 :
        input_2 = openfile.openfile(self, "開啟 After 整體txt檔案")
        if input_2: 
            draw_loss_obj = Draw_loss(all_txt_folder_1 = input_1, all_txt_folder_2 = input_2)
            scaled_pixmap = draw_loss_obj.draw_2_difference(input_1, input_2)
            self.ui.cmdlabel.setText("")
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.label.setPixmap(scaled_pixmap)
    else:
        return


    




    # self.ui.label.setPixmap(scaled_pixmap)
    # buf.truncate()

# def draw_two_differnet(self, merge_txt_output_folder_b, merge_txt_output_folder_a):
#     draw_loss_obj = Draw_loss(merge_txt_output_folder)
#     epoch, train_loss, val_loss, dice = draw_loss_obj.get_loss(merge_txt_output_folder)
#     scaled_pixmap = draw_loss_obj.draw(epoch, train_loss, val_loss, dice)
#     self.ui.label.setPixmap(scaled_pixmap)




# def lossimage(self):
#     self.ui.cmdlabel.setText("")
#     self.ui.tabWidget.setCurrentIndex(0)
#     txt_path, filetype = QFileDialog.getOpenFileName(self, "Get txt file", '/Users/andy/Documents')
#     if txt_path and 'txt' in txt_path:
#         self.ui.statusbar.showMessage("讀取文字資料 : "+ txt_path, 10000)
#         # 定義一個字典，用來儲存資料
#         data = {'train loss': [], 'validation loss': [], 'Dice': []}
#         count = 0
#         # 讀取檔案
#         with open(txt_path, 'r') as file:
#             # 逐行讀取
#             for line in file:
#                 tl_match = re.search('train loss : (-?\d+\.\d{4})', line)
#                 vl_match = re.search('validation loss: (-?\d+\.\d{4})', line)
#                 lr_match = re.search('Average global foreground Dice: \[(\d+\.\d+)\]', line)
#                 # 將數字加入對應的字典鍵值中
#                 if tl_match:
#                     data['train loss'].append(float(tl_match.group(1)))
#                     count += 1
#                 if vl_match:
#                     data['validation loss'].append(float(vl_match.group(1)))
#                 if lr_match:
#                     data['Dice'].append(float(lr_match.group(1)))


#         # 取得train loss、validation loss和Dice的數值
#         train_loss = data['train loss']
#         val_loss = data['validation loss']
#         dice = data['Dice']

#         # 設定x軸的數值
#         x = range(1, count + 1)

#         # 建立一個subplot，共用x軸但有兩個y軸
#         fig, ax1 = plt.subplots()
#         ax2 = ax1.twinx()

#         # 繪製train loss和validation loss的曲線
#         ax1.plot(x, train_loss, label='Train Loss', color='blue')
#         ax1.plot(x, val_loss, label='Validation Loss', color='red')

#         # 調整區間上下限
#         ax1.set_ylim([min(train_loss)-0.05, max(val_loss)+0.5])

#         # 繪製Dice的曲線
#         ax2.plot(x, dice, label='DSC', color='green')

#         # 調整區間上下限
#         ax2.set_ylim([min(dice)-0.6, max(dice)+0.2])

#         #設置刻度字體大小
#         ax1.tick_params(axis='x', labelsize=16)
#         ax1.tick_params(axis='y', labelsize=16)
#         ax2.tick_params(axis='y', labelsize=16)

#         # 設定圖表的標題和軸標籤
#         ax1.set_title('Training and Validation Loss and DSC', fontsize=18)
#         ax1.set_xlabel('Epoch', fontsize=14)
#         ax1.set_ylabel('Loss', fontsize=14)
#         ax2.set_ylabel('DSC', fontsize=14)


#         # 設定圖例
#         ax1.legend(loc='upper right', fontsize=13)
#         ax2.legend(loc='upper left', fontsize=13)   

#         # Save the plot as a PNG file
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png')
#         buf.seek(0)
#         image = Image.open(buf)

#         # Display the image on the label
#         pixmap = QPixmap.fromImage(ImageQt.toqimage(image))
#         scaled_pixmap = pixmap.scaled(1200, 600)
#         self.ui.label.setPixmap(scaled_pixmap)
#         buf.truncate()