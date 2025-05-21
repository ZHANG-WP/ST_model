from PyQt5.QtWidgets import QFileDialog, QInputDialog
import os 

def in_folder_imagsts(self):
    self.ui.statusbar.showMessage("選擇輸入資料夾", 10000)
    input_folder = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Desktop/DataSet')
    self.ui.imagets_path.setText(input_folder)

def in_folder_model(self):
    self.ui.statusbar.showMessage("選擇輸入模型資料夾", 10000)
    input_folder = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Desktop/STL')
    self.ui.model_path.setText(input_folder)

def out_folder_inferstr(self):
    self.ui.statusbar.showMessage("選擇輸出資料夾", 10000)
    output_folder = QFileDialog.getExistingDirectory(self, "Open folder")
    self.ui.inferstr_path.setText(output_folder)



# 設定選擇資料夾
def get_folder_showfiles(self,text=None):
    self.ui.statusbar.showMessage(text)
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    input_folder = QFileDialog.getExistingDirectory(self, "Open folder", r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/ST_test', options=options)
    if os.path.exists(os.path.join(input_folder, '.DS_Store')):
        os.remove(os.path.join(input_folder, '.DS_Store'))
    return input_folder

# 設定選擇資料夾
def get_folder(self,text=None):
    self.ui.statusbar.showMessage(text)
    input_folder = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Documents')
    if os.path.exists(os.path.join(input_folder, '.DS_Store')):
        os.remove(os.path.join(input_folder, '.DS_Store'))
    return input_folder
# 設定選擇檔案
def openfile(self,text =None):
    self.ui.statusbar.showMessage(text)
    input_file, filetype = QFileDialog.getOpenFileName(self, "Open folder", '/Users/andy/Documents')
    return input_file
# 設定儲存檔案
def get_save_file(self,text):
    self.ui.statusbar.showMessage(text)
    out_file, filetype = QFileDialog.getSaveFileName(self, 'Save File', '/Users/andy/Desktop')
    return out_file
# 設定選擇3D檔案
def open_stl_data(self,text):
    self.ui.statusbar.showMessage(text)
    input_file, filetype = QFileDialog.getOpenFileName(self, "Open STL file", '/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/1017_demo', "STL Files (*.stl);;All Files (*)")
    return input_file