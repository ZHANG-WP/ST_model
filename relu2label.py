import SimpleITK as sitk
import os
import pydicom
import numpy as np
import os
import copy
import nibabel as nib

def split_multiframe_dicom(dicom_file, output_dir=None):
    """
    將多幀DICOM轉換為多個單幀DICOM文件
    """
    ds = pydicom.dcmread(dicom_file)
    
    if not hasattr(ds, 'NumberOfFrames') or ds.NumberOfFrames <= 1:
        raise ValueError("這不是多幀DICOM。")

    num_frames = ds.NumberOfFrames
    frame_array = ds.pixel_array  # 會是 (frames, rows, cols)
    print(f'總帧數: {num_frames}，尺寸: {frame_array.shape[1]} x {frame_array.shape[2]}')

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(dicom_file), 'single_frame')
    os.makedirs(output_dir, exist_ok=True)

    for i in range(num_frames):
        new_ds = copy.deepcopy(ds)

        # 提取單帧
        single_frame = frame_array[i, :, :]
        new_ds.PixelData = single_frame.tobytes()
        new_ds.Rows, new_ds.Columns = single_frame.shape

        # 移除 NumberOfFrames
        if 'NumberOfFrames' in new_ds:
            del new_ds.NumberOfFrames

        # 生成新的 SOPInstanceUID
        new_ds.SOPInstanceUID = pydicom.uid.generate_uid()

        # 調整 InstanceNumber（可選）
        new_ds.InstanceNumber = i + 1

        # 更新 ImagePositionPatient（可選，若存在）
        if hasattr(new_ds, 'ImagePositionPatient') and hasattr(new_ds, 'SliceThickness'):
            ipp = list(new_ds.ImagePositionPatient)
            ipp[2] = new_ds.ImagePositionPatient[2] + i * new_ds.SliceThickness
            new_ds.ImagePositionPatient = ipp

        # 更新 WindowCenter / WindowWidth（可選）
        center = np.mean(single_frame)
        width = np.max(single_frame) - np.min(single_frame)
        new_ds.WindowCenter = int(center)
        new_ds.WindowWidth = int(width) if width > 0 else 1

        # 儲存
        output_file = os.path.join(output_dir, f'IMG{i+1:04d}.dcm')
        new_ds.save_as(output_file)
    print(f'✅ 儲存 {output_dir} 資料夾，包含 {num_frames} 個單幀 DICOM 檔案。')

# 讀取 DICOM 資料夾
def read_dicom_series(folder):
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(folder)
    reader.SetFileNames(dicom_names)
    image = reader.Execute()
    return image

# 主流程：使用 SimpleITK.Resample
def resample_label_to_ct_space(original_dcm_path, label_dcm_path, output_label_path):
    # 讀取原始 CT
    ct_image = read_dicom_series(original_dcm_path)
    # 讀取標註
    label_image = read_dicom_series(label_dcm_path)

    # 重採樣：以 CT 為參考，label 重投影到 CT 空間
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(ct_image)  # 以 CT 為基準
    resampler.SetInterpolator(sitk.sitkNearestNeighbor)  # 保持二值或分割類型不失真
    resampler.SetDefaultPixelValue(0)  # 背景填 0

    # 執行重採樣
    resampled_label = resampler.Execute(label_image)

    # 儲存為 NIfTI
    sitk.WriteImage(resampled_label, output_label_path)
    print(f"已完成 Label 重投影，輸出至 {output_label_path}")

# ==== 修改以下路徑 ====
path = "F:\\Grace\\nnunet_tmp\\ST_model\\dataset\\Dataset001_All\\train_data\\relu10person\\"

# 取得資料夾內所有資料夾
folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

# 遍歷所有資料夾
for folder in folders:
    original_dcm_path = path + folder + '\\ct'
    label_dcm_path = path + folder + '\\label'
    output_label_path = path + folder + f'\\{folder}.nii.gz'

    print(f"處理資料夾: {path + folder}")

    # 執行
    # split_multiframe_dicom(label_dcm_path + ".dcm", label_dcm_path)
    resample_label_to_ct_space(original_dcm_path, label_dcm_path, output_label_path)