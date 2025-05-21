import pydicom
import numpy as np
import os
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from PyQt5 import QtWidgets, QtCore
import SimpleITK as sitk
import time

class nifti_2_dicom():
    def nii_to_dcm(self, in_dir, path_out):
        if in_dir:
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

    def convert_all(self, in_dir, path_out):
        indir = os.listdir(in_dir)
        if ".DS_Store" in indir:
            in_dir.remove(".DS_Store")

        for i, file in enumerate(indir):
            input_path = os.path.join(in_dir, file)
            output_path = os.path.join(path_out, file.split('.', 1)[0])
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            self.nifti_converter.nii_to_dcm(input_path, output_path)

    def convert_single(self, in_dir, path_out):
        self.nifti_converter.nii_to_dcm(in_dir, path_out)

def resample_q(self):
    choice = ["1/2", "1/3", "1/4"]
    reciprocal_choices = [str(eval(choice_item) ** -1) for choice_item in choice]
    selected_item, ok = QInputDialog.getItem(None, "請選擇欲重採樣倍率", "倍率:", choice)
    if ok and selected_item:  # 如果使用者選擇了一個項目
        if selected_item == "1/2":
            num = 2
        elif selected_item == "1/3":
            num = 3
        else:
            num = 4
        resample_itk(self, num)
    else:
        #跳出函式
        return

def resample_itk(self, rate):
    def resize_image_itk(ori_img, output_path, shrink_factor, resamplemethod=sitk.sitkLinear):
        # 使用simpleitk讀取dicom序列影像
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(ori_img)
        reader.SetFileNames(dicom_names)
        image = reader.Execute()

        # 取得dicom影像中的資料
        size = list(image.GetSize())
        spacing = list(image.GetSpacing())
        origin = image.GetOrigin()
        direction = image.GetDirection()

        # 設定resample比例
        size[0] = int(size[0] / shrink_factor)
        size[1] = int(size[1] / shrink_factor)
        size[2] = int(size[2] / shrink_factor)
        # size[0] = int(size[0])
        # size[1] = int(size[1])
        # size[2] = int(size[1])

        spacing[0] = float(spacing[0] * shrink_factor)
        spacing[1] = float(spacing[1] * shrink_factor)
        spacing[2] = float(spacing[2] * shrink_factor)
        # spacing[0] = float(spacing[0])
        # spacing[1] = float(spacing[1])
        # spacing[2] = float(spacing[1])

        # 以simpleitk的方法进行resample
        resampler = sitk.ResampleImageFilter()
        resampler.SetReferenceImage(image)  # 需要重採樣的目標圖像

        # 設置目標圖像資料
        resampler.SetSize(size)  # 大小
        resampler.SetOutputOrigin(origin)  # 原點
        resampler.SetOutputDirection(direction)  # 方向
        resampler.SetOutputSpacing(spacing)  # 間隔距離

        # 根据需要重採樣圖像的情况設置不同的編碼形式
        if resamplemethod == sitk.sitkNearestNeighbor:
            resampler.SetOutputPixelType(sitk.sitkUInt8)  # 鄰近插值法用于mask的，保存uint8
        else:
            resampler.SetOutputPixelType(sitk.sitkInt32)  # 線性插值用于PET/CT/MRI之类的，保存Int32

        resampler.SetTransform(sitk.Transform(3, sitk.sitkIdentity))
        resampler.SetInterpolator(resamplemethod)

        itk_img_resampled = resampler.Execute(image)  # 得到重採樣後的圖像

        if itk_img_resampled.GetPixelIDTypeAsString() == '32-bit signed integer':
            # 如果像素類型是Int32，則將像素值加上最小像素質（1000）後，將它轉為能夠直接存擋的UInt16編碼
            arr = sitk.GetArrayViewFromImage(image)
            min_val = abs(np.amin(arr))  # 尋找像素最小值
            print(min_val)
            image_new = sitk.Cast(itk_img_resampled + min_val, sitk.sitkUInt16)

        # Save the resampled image as DICOM
        writer = sitk.ImageFileWriter()
        # Set the output file format to DICOM
        writer.SetImageIO("GDCMImageIO")
        # Set the file name for the output DICOM file
        output_filename = os.path.join(output_path, os.path.basename(ori_img) + ".dcm")
        writer.KeepOriginalImageUIDOn()
        writer.SetFileName(output_filename)
        # Write the resampled image to the output DICOM file
        writer.Execute(image_new)

        # 使用pydicom轉換modality
        ds = pydicom.dcmread(output_filename)
        ds.Modality = "CT"
        ds.save_as(output_filename)

    folder_path = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Documents')
    if folder_path:
        self.ui.statusbar.showMessage("讀取 : "+ folder_path)
        input_files = os.listdir(folder_path)
        output_path = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Documents/andy_college/about_my_lab_life/CT_data')
        self.ui.statusbar.showMessage("存入 : "+ output_path)
        if output_path:
            if ".DS_Store" in input_files:
                input_files.remove(".DS_Store")

            for i, file in enumerate(input_files):
                input_file = os.path.join(folder_path, file)
                print(input_file)
                self.ui.statusbar.showMessage("讀取 : "+input_file)
                output_file = os.path.join(output_path, file)
                if not os.path.exists(output_file):
                    os.makedirs(output_file)
                resize_image_itk(input_file, output_file, rate)
                print(output_file)

            QtWidgets.QMessageBox.about(self, "finish", "處理完成")


def dicomcrop(self):
    self.ui.statusbar.showMessage("請選擇欲裁減之整體資料夾", 10000)
    in_path = QFileDialog.getExistingDirectory(self, "input folder", '/Users/andy/Desktop')
    if in_path:
        self.ui.statusbar.showMessage("讀取 : "+ in_path, 10000)
        self.ui.statusbar.showMessage("請選擇存檔位置", 10000)
        outpath = QFileDialog.getExistingDirectory(self, "output folder", '/Users/andy/Desktop')
        if outpath:
            self.ui.statusbar.showMessage("存入 : "+ outpath, 10000)
            
            def createnewdicom(cropped_side, infolder, outfolder, crop_ratio):
                # 讀取Dicom影像
                ds = pydicom.dcmread(infolder)

                # 轉換為影像
                image = ds.pixel_array.astype(float)  # 轉換為float型NumPy陣列

                # 裁剪影像
                height, width = image.shape
                crop_width = int(width * crop_ratio)
                if cropped_side == "right":
                    cropped_image = image[:, crop_width:]
                elif cropped_side == "left":
                    cropped_image = image[:, :crop_width]

                # 創建新的Dicom檔案
                output_filename = os.path.join(outfolder, i)
                new_ds = pydicom.dataset.FileDataset(output_filename, {}, file_meta=ds.file_meta, preamble=b"\0" * 128)

                # 設定元數據
                # new_ds.SpecificCharacterSet = ds.SpecificCharacterSet
                new_ds.ImageType = ds.ImageType
                new_ds.PatientName = ds.PatientName
                new_ds.PatientID = ds.PatientID
                new_ds.Modality = ds.Modality
                new_ds.ImagePositionPatient = ds.ImagePositionPatient
                new_ds.ImageOrientationPatient = ds.ImageOrientationPatient
                new_ds.StudyInstanceUID = ds.StudyInstanceUID
                new_ds.SeriesInstanceUID = ds.SeriesInstanceUID
                new_ds.SOPClassUID = ds.SOPClassUID
                new_ds.SOPInstanceUID = pydicom.uid.generate_uid()
                new_ds.SamplesPerPixel = ds.SamplesPerPixel
                new_ds.PhotometricInterpretation = ds.PhotometricInterpretation
                new_ds.StudyID = ds.StudyID
                new_ds.InstanceNumber = ds.InstanceNumber
                new_ds.SeriesNumber = 1
                new_ds.SamplePerPixel = 1
                new_ds.Rows = height
                new_ds.Columns = width - crop_width
                new_ds.PixelSpacing = ds.PixelSpacing
                #new_ds.SliceThickness = ds.SliceThickness
                new_ds.BitsAllocated = ds.BitsAllocated
                new_ds.BitsStored = ds.BitsStored
                new_ds.HighBit = ds.HighBit
                new_ds.PixelRepresentation = ds.PixelRepresentation
                # new_ds.SmallestImagePixelValue = int(np.min(cropped_image))
                # new_ds.LargestImagePixelValue = int(np.max(cropped_image))
                new_ds.SOPClassUID = ds.SOPClassUID
                new_ds.StudyDate = ds.StudyDate
                new_ds.SeriesDate = ds.SeriesDate
                #new_ds.ContentDate = ds.ContentDate
                new_ds.StudyTime = ds.StudyTime
                new_ds.SeriesTime = ds.SeriesTime
                #new_ds.ContentTime = ds.ContentTime
                # new_ds.AccessionNumber = ds.AccessionNumber
                #new_ds.Manufacturer = ds.Manufacturer
                # new_ds.ReferringPhysicianName = ds.ReferringPhysicianName

                # 設定像素數據
                pixel_data = cropped_image.astype(np.uint16)
                new_ds.PixelData = pixel_data.tobytes()

                # 儲存Dicom檔案
                pydicom.filewriter.write_file(output_filename, new_ds, write_like_original=False)

            def cropleftpart(input_folder, output_folder_L):
                # 讀取輸入資料夾中的所有Dicom影像並依次處理
                if input_folder.endswith('.dcm'):
                    createnewdicom("left", input_folder, output_folder_L, 0.5)

            def croprightpart(input_folder, output_folder_R):
                # 讀取輸入資料夾中的所有Dicom影像並依次處理
                if input_folder.endswith('.dcm'):
                    createnewdicom("right", input_folder, output_folder_R, 0.5)

            # 設定輸入和輸出Dicom檔案的路徑
            input_folder = in_path


            root_folders = os.listdir(input_folder)
            if ".DS_Store" in root_folders:
                root_folders.remove(".DS_Store")

            # 對檔案中的所有檔案進行動作
            for filename in root_folders:
                input_1 = os.path.join(input_folder, filename)
                folders = os.listdir(input_1)
                if ".DS_Store" in folders:
                    folders.remove(".DS_Store")

                output_folder_left = os.path.join(outpath, "Left")
                output_folder_right = os.path.join(outpath, "right")
                # 確定輸出Dicom檔案存在
                if not os.path.exists(output_folder_left):
                    os.makedirs(output_folder_left)
                if not os.path.exists(output_folder_right):
                    os.makedirs(output_folder_right)

                for i in folders:
                    input2 = os.path.join(input_1, i)
                    self.ui.statusbar.showMessage(input2)
                    output_folder_L = os.path.join(output_folder_left, filename)
                    print(output_folder_L)
                    output_folder_R = os.path.join(output_folder_right, filename)
                    # 確定輸出Dicom檔案存在
                    if not os.path.exists(output_folder_L):
                        os.makedirs(output_folder_L)
                    if not os.path.exists(output_folder_R):
                        os.makedirs(output_folder_R)
                    cropleftpart(input2, output_folder_L)
                    croprightpart(input2, output_folder_R)
            QtWidgets.QMessageBox.about(self, "finish", "轉檔完成")

def dcminfo(self):
    filename, filetype = QFileDialog.getOpenFileName(self, "Open folder", '/Users/andy/Documents')
    if 'dcm' in filename:
        from pydicom import dcmread
        filepath = filename
        print(filepath)
        information = {}
        ds = dcmread(filepath)
        information['Manufacturer'] = ds.Manufacturer
        info = ds.Manufacturer
        print(info)
        self.ui.statusbar.showMessage("請選擇單一dcm切片資料", 10000)
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.cmdlabel.setText("設備廠商 : "+info)
        self.ui.statusbar.showMessage("設備廠商 : "+info, 30000)
    else:
        QtWidgets.QMessageBox.about(self, "finish", "檔案錯誤")