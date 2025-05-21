from PyQt5.QtWidgets import QFileDialog, QInputDialog
from PyQt5 import QtWidgets
import os
import SimpleITK as sitk
import time
import dicom2nifti
from natsort import natsorted


def handleComboChange(self):
    # This function will be called whenever the user changes the selected item in the combo box
    selected_text_1 = self.ui.comboBox_DCM2nii.currentText()
    if selected_text_1 == "單一檔案轉檔":
        self.ui.statusbar.showMessage("dicom to nii, 單一檔案轉檔", 10000)
        dcm_to_nii(self)
    elif selected_text_1 == "多檔案轉檔":
        self.ui.statusbar.showMessage("dicom to nii, 多檔案轉檔", 10000)
        dcm_to_nii_all(self)
    selected_text_2 = self.ui.comboBox_nii2DCM.currentText()
    if selected_text_2 == "單一檔案轉檔":
        self.ui.statusbar.showMessage("nii to dicom, 單一檔案轉檔", 10000)
        nii_2_dcm_convert_single(self)
    elif selected_text_2 == "多檔案轉檔":
        self.ui.statusbar.showMessage("nii to dicom, 多檔案轉檔", 10000)
        nii_2_dcm_convert_all(self)

def nii_to_dcm_q(self):
    choice = ["單一檔案", "多檔案（資料夾）"]
    selected_item, ok = QInputDialog.getItem(None, "請選擇資料形式", ":", choice)
    if ok and selected_item:  # 如果使用者選擇了一個項目
        if selected_item == "單一檔案":
            nii_2_dcm_convert_single(self)
        else:
            nii_2_dcm_convert_all(self)
    else:
        #跳出函式
        return

def nii_to_dcm(self, in_dir, path_out):
    if in_dir:
        self.ui.statusbar.showMessage("讀取 : "+ in_dir, 10000)
        self.ui.statusbar.showMessage("存入 : "+ path_out, 10000)
        def writeSlices(series_tag_values, new_img, i, out_dir):
            image_slice = new_img[:, :, i]
            writer = sitk.ImageFileWriter()
            writer.KeepOriginalImageUIDOn()

            # Tags shared by the series.
            list(map(lambda tag_value: image_slice.SetMetaData(tag_value[0], tag_value[1]), series_tag_values))

            # Slice specific tags.
            image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d"))  # Instance Creation Date
            image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S"))  # Instance Creation Time

            # Setting the type to CT preserves the slice location.
            image_slice.SetMetaData("0008|0060", "CT")  # set the type to CT so the thickness is carried over

            # (0020, 0032) image position patient determines the 3D spacing between slices.
            image_slice.SetMetaData("0020|0032", '\\'.join(
                map(str, new_img.TransformIndexToPhysicalPoint((0, 0, i)))))  # Image Position (Patient)
            image_slice.SetMetaData("0020,0013", str(i))  # Instance Number

            # Write to the output directory and add the extension dcm, to force writing in DICOM format.
            writer.SetFileName(os.path.join(out_dir, 'slice' + str(i).zfill(4) + '.dcm'))
            writer.Execute(image_slice)

        def convert_nifti_to_dicom(in_dir, out_dir):
            new_img = sitk.ReadImage(in_dir)
            modification_time = time.strftime("%H%M%S")
            modification_date = time.strftime("%Y%m%d")

            direction = new_img.GetDirection()
            series_tag_values = [("0008|0031", modification_time),  # Series Time
                                    ("0008|0021", modification_date),  # Series Date
                                    ("0008|0008", "DERIVED\\SECONDARY"),  # Image Type
                                    ("0020|000e",
                                    "1.2.826.0.1.3680043.2.1125." + modification_date + ".1" + modification_time),
                                    # Series Instance UID
                                    ("0020|0037", '\\'.join(
                                        map(str, (direction[0], direction[3], direction[6],  # Image Orientation (Patient)
                                                direction[1], direction[4], direction[7])))),
                                    ("0008|103e", "Created-SimpleITK")]  # Series Description
            # Write slices to output directory
            list(map(lambda i: writeSlices(series_tag_values, new_img, i, out_dir), range(new_img.GetDepth())))
        convert_nifti_to_dicom(in_dir, path_out)

def nii_2_dcm_convert_all(self):
    in_dir = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Documents')
    if in_dir:
        path_out = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Documents')
        if path_out:
                
            if os.path.exists(os.path.join(in_dir, ".DS_Store")):
                os.remove(os.path.join(in_dir, ".DS_Store"))
            if os.path.exists(os.path.join(in_dir, "plans.pkl")):
                os.remove(os.path.join(in_dir, "plans.pkl"))

            indir = os.listdir(in_dir)

            for i, file in enumerate(indir):
                input_path = os.path.join(in_dir, file)
                output_path = os.path.join(path_out, file.split('.', 1)[0])
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                nii_to_dcm(self, input_path, output_path)
            QtWidgets.QMessageBox.about(self, "Finish", "轉檔成功")

def nii_2_dcm_convert_single(self):
    in_dir, filetype = QFileDialog.getOpenFileName(self, "Open folder", '/Users/andy/Documents')
    if in_dir:
        path_out = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Documents')
        if path_out:
            nii_to_dcm(self, in_dir, path_out)
            QtWidgets.QMessageBox.about(self, "Finish", "轉檔成功")

def dcm_to_nii_q(self):
    choice = ["單一檔案", "多檔案（資料夾）"]
    selected_item, ok = QInputDialog.getItem(None, "請選擇資料形式", ":", choice)
    if ok and selected_item:  # 如果使用者選擇了一個項目
        if selected_item == "單一檔案":
            dcm_to_nii(self)
        else:
            dcm_to_nii_all(self)
    else:
        #跳出函式
        return

def dcm_to_nii(self):
    folder_path = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Documents')
    print(folder_path)
    if folder_path:
        self.ui.statusbar.showMessage("讀取 : "+ folder_path, 10000)
        path_out, filetype = QFileDialog.getSaveFileName(self, 'Save File', '/Users/andy/Documents')
        if path_out:
            self.ui.statusbar.showMessage("存入 : "+ path_out, 10000)
            path_one_patient = folder_path
            path_out_data = path_out + '.nii.gz'
            dicom2nifti.dicom_series_to_nifti(path_one_patient, path_out_data)
            QtWidgets.QMessageBox.about(self, "finish", "轉檔成功")
            # self.ui.comboBox_DCM2nii.setCurrentText("Dicom轉nii")
        else:
            QtWidgets.QMessageBox.about(self, "Erro", "錯誤")
            # self.ui.comboBox_DCM2nii.setCurrentText("Dicom轉nii")
    # else:
    #     # self.ui.comboBox_DCM2nii.setCurrentText("Dicom轉nii")

def dcm_to_nii_all(self):
    folder_path = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Documents')
    print(folder_path)
    if folder_path:
        self.ui.statusbar.showMessage("讀取資料夾 : "+ folder_path, 10000)
        files = os.listdir(folder_path)

        if ".DS_Store" in files:
            files.remove(".DS_Store")

        files = [filename for filename in files if not filename.startswith("._")]

        # def get_visible_files(folder_path):
        #     visible_files = []
        #     for filename in os.listdir(folder_path):
        #         # 排除 ".DS_Store" 和隱藏檔案（以 "._" 開頭的檔案）
        #         if filename != ".DS_Store" and not filename.startswith("._"):
        #             file_path = os.path.join(folder_path, filename)
        #             # 確認是檔案而非資料夾
        #             if os.path.isfile(file_path):
        #                 visible_files.append(file_path)
        #     return visible_files
        
        # files = get_visible_files(folder_path)
        # print(files)

        sort_files = natsorted(files)
        path_out = QFileDialog.getExistingDirectory(self, 'Select output directory', '/Users/andy/Documents')
        if path_out:
            self.ui.statusbar.showMessage("存入 : "+ path_out)
            for i, file in enumerate(sort_files):
                input = os.path.join(folder_path, file)
                print(input)
                output_name = os.path.splitext(file)[0] + '.nii.gz'
                output_path = os.path.join(path_out, output_name)
                dicom2nifti.dicom_series_to_nifti(input, output_path)
                print(output_path)

            QtWidgets.QMessageBox.about(self, "Finish", "轉檔成功")
            # self.ui.comboBox_DCM2nii.setCurrentText("Dicom轉nii")
        else:
            QtWidgets.QMessageBox.about(self, "Error", "錯誤")
            # self.ui.comboBox_DCM2nii.setCurrentText("Dicom轉nii")
    # else:
    #     self.ui.comboBox_DCM2nii.setCurrentText("Dicom轉nii")