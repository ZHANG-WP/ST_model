import random
import numpy as np
import torch
import SimpleITK as sitk
import cv2
from typing import Union, Tuple
import matplotlib.pyplot as plt
import pydicom
from PIL import Image, ImageOps, ImageFilter
from torchvision import transforms
import os
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from PyQt5 import QtWidgets
import openfile
import display_dicom
from skimage import exposure

from scipy.ndimage import median_filter
from scipy.ndimage import gaussian_filter
from scipy.signal import convolve
from typing import Union, Tuple, Callable


from batchgenerators.augmentations.color_augmentations import augment_contrast, augment_brightness_additive, augment_gamma
from batchgenerators.augmentations.utils import create_zero_centered_coordinate_mesh, elastic_deform_coordinates, \
    interpolate_img,rotate_coords_2d, rotate_coords_3d, scale_coords
from batchgenerators.augmentations.spatial_transformations import augment_resize
from batchgenerators.augmentations.resample_augmentations import augment_linear_downsampling_scipy
from batchgenerators.augmentations.noise_augmentations import augment_blank_square_noise
from batchgenerators.augmentations.crop_and_pad_augmentations import random_crop as random_crop_aug
from batchgenerators.augmentations.crop_and_pad_augmentations import center_crop as center_crop_aug
from batchgenerators.augmentations.utils import get_range_val

data_dict = {"data" : [],
             "label" : []}


def display_2d(img, title='image'):
    plt.imshow(img)
    plt.title(title)
    plt.axis('off')
    plt.show()

def clear_folder(folder_path):
    # 遍历文件夹中的每个文件和子文件夹
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # 如果是文件，则删除
        if os.path.isfile(item_path):
            os.remove(item_path)
        # 如果是文件夹，则递归清空文件夹
        elif os.path.isdir(item_path):
            clear_folder(item_path)

def choice(self):
    self.oh = None
    self.ow = None
    data_dict["data"].clear()
    data_dict["label"].clear()
    choice = ["Resize", "Randomflip", "Blur", "Nosie", "GammaTransform", "BrightnessTransform ", "ContrastAugmentation"]
    selected_item, ok = QInputDialog.getItem(None, "請選擇資料擴增形式", ":", choice)
    if ok and selected_item:  # 如果使用者選擇了一個項目
        img_folder = openfile.get_folder(self, "開啟Dicom資料夾")
        if img_folder: 

            def save_as_dicom(pixel_array, output_folder):
                i = 0
                for slice in sorted(os.listdir(img_folder)):
                    dicom_file_path = os.path.join(img_folder, slice)
                    dicom_data = pydicom.dcmread(dicom_file_path)
                    dicom_data.PixelData = pixel_array[i]
                    if self.ow is not None:
                        dicom_data.Rows = self.ow
                        dicom_data.Columns = self.oh
                        print(f"Rows: {dicom_data.Rows}, Columns: {dicom_data.Columns}")
                        self.ui.statusbar.showMessage(f"New rows: {dicom_data.Rows}, New Columns: {dicom_data.Columns}", 10000)

                    # 保存DICOM文件
                    dicom_file_path = os.path.join(output_folder, slice)
                    dicom_data.save_as(dicom_file_path)
                    i += 1
                    # print(f'DICOM file saved: {dicom_file_path}')
            
            # 根据选择的项目确定输出文件夹路径
            if selected_item == "Resize":
                out_folder_path = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/augmentation_test/resize'
            elif selected_item == "Randomflip":
                out_folder_path = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/augmentation_test/randomflip'
            elif selected_item == "Blur":
                out_folder_path = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/augmentation_test/blur'
            elif selected_item == "Nosie":
                out_folder_path = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/augmentation_test/nosie'
            elif selected_item == "GammaTransform":
                out_folder_path = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/augmentation_test/gammaTransform'
            elif selected_item == "BrightnessTransform":
                out_folder_path = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/augmentation_test/brightnessTransform'
            elif selected_item == "ContrastAugmentation":
                out_folder_path = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/augmentation_test/contrastAugmentation'
            
            if not os.path.exists(out_folder_path):
                os.makedirs(out_folder_path)
            
            # 清空输出文件夹
            clear_folder(out_folder_path)

            # 讀取 DICOM 資料夾
            for slice in sorted(os.listdir(img_folder)):
                dicom_file_path = os.path.join(img_folder, slice)
                self.dicom_data = pydicom.dcmread(dicom_file_path)

                if dicom_file_path.endswith('.dcm'):
                    dicom_image = self.dicom_data.pixel_array
                    data_dict["data"].append(np.array(dicom_image))

            # 根据选择的项目进行数据增强
            if selected_item == "Resize":
                do_resize(self)
            elif selected_item == "Randomflip":
                rot90Transform((0, 1, 2, 3), [1,2], data_key='data', p_per_sample=1)
            elif selected_item == "Blur":
                gaussianBlurTransform((3, 15), different_sigma_per_channel=True ,p_per_sample=1, p_per_channel=1)
            elif selected_item == "Nosie":
                gaussianNoiseTransform(p_per_sample=1)
            elif selected_item == "GammaTransform":
                gammaTransform((0.7, 1.5), invert_image=True, per_channel=True, retain_stats=True, p_per_sample=1)
            elif selected_item == "BrightnessTransform":
                brightnessTransform(0, 0.5, per_channel=True, p_per_sample=1, p_per_channel=1)
            elif selected_item == "ContrastAugmentation":
                contrastAugmentationTransform(contrast_range=(0.5, 2), per_channel=True, data_key='data',
                                               p_per_sample=1, p_per_channel=1, p = 0.5)
                
            save_as_dicom(data_dict["data"], out_folder_path)
            data_dict["data"] = []
            data_dict["label"] = []
                # self.dicom_data.PixelData = data_dict["data"]
                # print(self.dicom_data.PixelData)
            
            
                # # 生成输出文件路径
                # output_filename = os.path.join(out_folder_path, slice)
                # # 保存 DICOM 文件
                # self.dicom_data.save_as(output_filename)

            QtWidgets.QMessageBox.about(self, "finish", "轉檔完成")

            display_dicom.view(self, out_folder_path)
    else:
        #跳出函式
        return

# ------------------------------------------dicom sucessfuly------------------------------------------
# 先移除param: mask
def cutout(self, img, mask =None, p=0.5, size_min=0.02, size_max=0.4, ratio_1=0.3,
           ratio_2=1/0.3, value_min=0, value_max=255, pixel_level=True):
    # 檢查是否應用 cutout 資料增強，根據機率 p
    # if random.random() < p:
    # 將影像轉換成numpy數組
    img = np.array(img)
    if mask is not None:
        mask = np.array(mask) 

    # 取得影像的高度、寬度及通道數
    # img_h, img_w, img_c = img.shape
    img_h, img_w = img.shape

    # 循環直到找到合適的 cutout 區域
    while True:
        # 隨機生成cutout區域的面積
        size = np.random.uniform(size_min, size_max) * img_h * img_w

        # 隨機生成cutout區域的長寬比
        ratio = np.random.uniform(ratio_1, ratio_2)

        # 根據面積和長寬比計算 cutout 區域的寬度和高度
        erase_w = int(np.sqrt(size / ratio))
        erase_h = int(np.sqrt(size * ratio))

        # 隨機生成cutout區域的左上角座標
        x = np.random.randint(0, img_w)
        y = np.random.randint(0, img_h)

        # 檢查cutout區域是否存在於影像內
        if x + erase_w <= img_w and y + erase_h <= img_h:
            break


    # 根據像素等級和值範圍隨機產生 cutout 區域的值
    if pixel_level:
        value = np.random.uniform(value_min, value_max, (erase_h, erase_w))
    else:
        value = np.random.uniform(value_min, value_max)


    # 將影像中的 cutout 區域替換為隨機產生的值
    img[y:y + erase_h, x:x + erase_w] = value
    self.dicom_data.PixelData = img.tobytes()


    # 將mask中的 cutout 區域標記為白色（255）
    if mask is not None:
        mask[y:y + erase_h, x:x + erase_w] = value
        self.mask_data.PixelData = mask.tobytes()

        return self.dicom_data.PixelData, self.mask_data.PixelData
    else:
        return self.dicom_data.PixelData
    
"""WDA"""
# -------------------------------- Rot90 --------------------------------
def augment_rot90(sample_data, num_rot=(1, 2, 3), axes=(0, 1, 2), per_channel = False):
    """

    :param sample_data:
    :param sample_seg:
    :param num_rot: rotate by 90 degrees how often? must be tuple -> nom rot randomly chosen from that tuple
    :param axes: around which axes will the rotation take place? two axes are chosen randomly from axes.
    :return:
    """
    if per_channel is True:
        num_rot = np.random.choice(num_rot)
        axes = np.random.choice(axes, size=2, replace=False)
        axes = [(i + 1) % sample_data.ndim for i in axes]  # 保證 axes 在合法的範圍內
    else:
        num_rot = num_rot
        axes = axes
    print("num_rot :", num_rot)
    
    print("before:",sample_data.shape)
    print("axes:", axes)
    
    sample_data = np.rot90(sample_data, num_rot, axes)
    print("after:",sample_data.shape)
    return sample_data

def rot90Transform(num_rot=(1, 2, 3), axes=(0, 1, 2), data_key="data", label_key='label', p_per_sample=0.3, per_channel = False):
    data = np.array(data_dict.get(data_key))

    if data_dict[label_key]:
        label = np.array(data_dict.get(label_key))
    else:
        label = None


    if per_channel is False:
        num_rot = np.random.choice(num_rot)
        axes = np.random.choice(axes, size=2, replace=False)
        axes = [(i + 1) % data[0].ndim for i in axes]  # 保證 axes 在合法的範圍內

    for b in range(data.shape[0]): # b : 當前slice
        if np.random.uniform() < p_per_sample:
            d = data[b] # d : 當前slice的影像陣列
            d = augment_rot90(d , num_rot = num_rot, axes=axes) # 呼叫使用augment_rot90
            data[b] = d

            if label is not None:
                e = label[b] # d : 當前slice的影像陣列
                e = augment_rot90(e , num_rot = num_rot, axes=axes) # 呼叫使用augment_rot90
                label[b] = e

    data_dict[data_key] = data
    if label is not None:
        data_dict[label_key] = label

    return data_dict
# -------------------------------- Rot90 --------------------------------

# -------------------------------- Resize --------------------------------
def resize(data_sample: np.ndarray, ow, oh, p_per_sample=1, data_key="data", mask=None):
    if np.random.uniform() <= p_per_sample:
        # 直接修改 data_sample
        data_sample = cv2.resize(data_sample, (ow, oh), interpolation=cv2.INTER_LINEAR)
    return data_sample

def do_resize(self, ratio_range = (0.5, 2.0), data_key="data", label_key="label"):
    base_size = np.array(data_dict[data_key][0]).shape[1]
    h, w = np.array(data_dict[data_key][0]).shape  # Assuming data is a 2D array

    # 限制 long_side 的范围在 ratio_range 内
    long_side = random.randint(int(base_size * ratio_range[0]), int(base_size * ratio_range[1]))
    
    if h > w:
        self.oh = long_side
        self.ow = int(1.0 * w * long_side / h + 0.5)
    else:
        self.ow = long_side
        self.oh = int(1.0 * h * long_side / w + 0.5)

    print("before : ", np.array(data_dict[data_key]).shape)
    for b in range(len(np.array(data_dict[data_key]))):
        data_dict[data_key][b] = resize(data_dict[data_key][b], self.ow, self.oh)
        if data_dict[label_key]:
            data_dict[label_key][b] = resize(data_dict[label_key][b], self.ow, self.oh)

    print("after : ", np.array(data_dict[data_key]).shape)
    return data_dict
# -------------------------------- Resize --------------------------------
"""WDA"""



"""SDA"""
# -------------------------------- BLUR --------------------------------
def augment_gaussian_blur(data_sample: np.ndarray, sigma_range: Tuple[float, float], per_channel: bool = True,
                          p_per_channel: float = 1, different_sigma_per_axis: bool = False,
                          p_isotropic: float = 0) -> np.ndarray:
    """
    對輸入的資料樣本應用高斯模糊增強。

    Parameters:
    - data_sample: 輸入的資料樣本，numpy 陣列。     - sigma_range: 高斯濾波器的標準差範圍。
    - per_channel: 是否對每個通道套用不同的模糊參數。     - p_per_channel: 每個通道應用增強的機率。
    - different_sigma_per_axis: 是否在每個軸上使用不同的模糊參數。     - p_isotropic: 各軸上使用相同參數的機率。

    Returns:
    - np.ndarray: 增強後的資料樣本。
    """
    if not per_channel:
        # Godzilla Had a Stroke Trying to Read This and F***ing Died
        # https://i.kym-cdn.com/entries/icons/original/000/034/623/Untitled-3.png
        sigma = get_range_val(sigma_range) if ((not different_sigma_per_axis) or
                                               ((np.random.uniform() < p_isotropic) and
                                                different_sigma_per_axis)) \
            else [get_range_val(sigma_range) for _ in data_sample.shape[1:]]
    else:
        sigma = None
    for c in range(data_sample.shape[0]):
        if np.random.uniform() <= p_per_channel:
            if per_channel:
                sigma = get_range_val(sigma_range) if ((not different_sigma_per_axis) or
                                                       ((np.random.uniform() < p_isotropic) and
                                                        different_sigma_per_axis)) \
                    else [get_range_val(sigma_range) for _ in data_sample.shape[1:]]
            data_sample[c] = gaussian_filter(data_sample[c], sigma, order=0)
    return data_sample

def gaussianBlurTransform(blur_sigma: Tuple[float, float] = (1, 5), different_sigma_per_channel: bool = True,
                 different_sigma_per_axis: bool = False, p_isotropic: float = 0, p_per_channel: float = 1,
                 p_per_sample: float = 1, data_key: str = "data"):
    """
    對資料字典中的每個樣本應用高斯模糊增強。

    Parameters:
    - blur_sigma: 高斯濾波器的標準差範圍。     - different_sigma_per_channel: 是否對每個通道套用不同的模糊參數。
    - different_sigma_per_axis: 是否在每個軸上使用不同的模糊參數。     - p_isotropic: 各軸上使用相同參數的機率。
    - p_per_channel: 每個通道應用增強的機率。     - p_per_sample: 每個樣本應用增強的機率。
    - data_key: 資料字典中包含樣本的鍵。

    Returns:
    - dict: 增強後的資料字典。
    """
    for b in range(len(np.array(data_dict[data_key]))):
        if np.random.uniform() < p_per_sample:
            data_dict[data_key][b] = augment_gaussian_blur(data_dict[data_key][b], blur_sigma,
                                                                different_sigma_per_channel,
                                                                p_per_channel,
                                                                different_sigma_per_axis=different_sigma_per_axis,
                                                                p_isotropic=p_isotropic)
    return data_dict

# -------------------------------- BLUR --------------------------------

# -------------------------------- GaussianNoise --------------------------------
def augment_gaussian_noise(data_sample: np.ndarray, noise_variance: Tuple[float, float] = (0, 0.1),
                           p_per_channel: float = 1, per_channel: bool = False) -> np.ndarray:

    if not per_channel:
        if noise_variance[0] == noise_variance[1] :
            variance = noise_variance[0] 
        else:
            variance = random.uniform(noise_variance[0], noise_variance[1])
    else:
        variance = None
    print(data_sample.shape)
    for c in range(data_sample.shape[0]):
        if np.random.uniform() < p_per_channel:
            # lol good luck reading this
            variance_here = variance if variance is not None else \
                noise_variance[0] if noise_variance[0] == noise_variance[1] else \
                    random.uniform(noise_variance[0], noise_variance[1])
            # bug fixed: https://github.com/MIC-DKFZ/batchgenerators/issues/86
            data_sample[c] = data_sample[c] + np.random.normal(0.0, variance_here, size=data_sample[c].shape)
    return data_sample


def gaussianNoiseTransform(noise_variance=(0, 0.1), p_per_sample=1, p_per_channel: float = 1,
                 per_channel: bool = False, data_key="data"):
    print(len(np.array(data_dict[data_key])))
    for b in range(len(np.array(data_dict[data_key]))):
        if np.random.uniform() < p_per_sample:
            data_dict[data_key][b] = augment_gaussian_noise(data_dict[data_key][b], noise_variance,
                                                                    p_per_channel, per_channel)
    return data_dict

# -------------------------------- GaussianNoise --------------------------------


# -------------------------------- BrightnessTransform --------------------------------
def brightnessTransform(mu, sigma, per_channel=True, data_key="data", p_per_sample=1, p_per_channel=1):
    data = np.array(data_dict[data_key])
    print(data)
    for b in range(data.shape[0]):
        if np.random.uniform() < p_per_sample:
            data[b] = augment_brightness_additive(data[b], mu, sigma, per_channel,
                                                    p_per_channel=p_per_channel)

    data_dict[data_key] = data
    return data_dict
# -------------------------------- BrightnessTransform --------------------------------


# -------------------------------- ContrastAugmentationTransform --------------------------------
def contrastAugmentationTransform(contrast_range: Union[Tuple[float, float], Callable[[], float]] = (0.75, 1.25),
                 preserve_range: bool = True,
                 per_channel: bool = True,
                 data_key: str = "data",
                 p_per_sample: float = 1,
                 p_per_channel: float = 1, p : float =0.5):
        """
        Augments the contrast of data
        :param contrast_range:
            (float, float): range from which to sample a random contrast that is applied to the data. If
                            one value is smaller and one is larger than 1, half of the contrast modifiers will be >1
                            and the other half <1 (in the inverval that was specified)
            callable      : must be contrast_range() -> float
        :param preserve_range: if True then the intensity values after contrast augmentation will be cropped to min and
        max values of the data before augmentation.
        :param per_channel: whether to use the same contrast modifier for all color channels or a separate one for each
        channel
        :param data_key:
        :param p_per_sample:
        """
        if np.random.uniform() < p:
            preserve_range = True
        else:
            preserve_range = False

        for b in range(len(np.array(data_dict[data_key]))):
            if np.random.uniform() < p_per_sample:
                data_dict[data_key][b] = augment_contrast(data_dict[data_key][b],
                                                               contrast_range=contrast_range,
                                                               preserve_range=preserve_range,
                                                               per_channel=per_channel,
                                                               p_per_channel=p_per_channel)
        return data_dict
# -------------------------------- ContrastAugmentationTransform --------------------------------


# -------------------------------- GammaTransform --------------------------------
def gammaTransform(gamma_range=(0.5, 2), invert_image=False, per_channel=False, data_key="data",
                 retain_stats: Union[bool, Callable[[], bool]] = False, p_per_sample=1):
        """
        Augments by changing 'gamma' of the image (same as gamma correction in photos or computer monitors

        :param gamma_range: range to sample gamma from. If one value is smaller than 1 and the other one is
        larger then half the samples will have gamma <1 and the other >1 (in the inverval that was specified).
        Tuple of float. If one value is < 1 and the other > 1 then half the images will be augmented with gamma values
        smaller than 1 and the other half with > 1
        :param invert_image: whether to invert the image before applying gamma augmentation
        :param per_channel:
        :param data_key:
        :param retain_stats: Gamma transformation will alter the mean and std of the data in the patch. If retain_stats=True,
        the data will be transformed to match the mean and standard deviation before gamma augmentation. retain_stats
        can also be callable (signature retain_stats() -> bool)
        :param p_per_sample:
        """
        for b in range(len(np.array(data_dict[data_key]))):
            if np.random.uniform() < p_per_sample:
                data_dict[data_key][b] = augment_gamma(data_dict[data_key][b], gamma_range,
                                                            invert_image,
                                                            per_channel=per_channel,
                                                            retain_stats=retain_stats)
        return data_dict
# -------------------------------- GammaTransform --------------------------------
"""SDA"""

def conduct_all_WDA(self):
    self.oh = None
    self.ow = None
    
    img_folder = openfile.get_folder(self, "選擇要進行資料擴增之Tr資料夾")
    mask_folder = openfile.get_folder(self, "選擇要進行資料擴增之Label資料夾")
    out_folder_img = r'/Volumes/andy_SSD/dicom/Task32_tsinus/dicom/imageTr_wda'
    out_folder_mask = r'/Volumes/andy_SSD/dicom/Task32_tsinus/dicom/labelsTr_wda'

    def save(output_folder_dicom, output_folder_label, data_key = "data", label_key = "label"):
        if not os.path.exists(output_folder_dicom):
                os.makedirs(output_folder_dicom)
        else:
            clear_folder(output_folder_dicom)

        if not os.path.exists(output_folder_label):
                os.makedirs(output_folder_label)
        else:
            clear_folder(output_folder_label)

        i = 0
        for slice in self.dicom_file:
            dicom_file_path = os.path.join(self.dicom_folder_path, slice)
            dicom_data = pydicom.dcmread(dicom_file_path)
            dicom_data.PixelData = data_dict[data_key][i]

            mask_file_path = os.path.join(self.mask_folder_path , slice)
            mask_data = pydicom.dcmread(mask_file_path)
            mask_data.PixelData = data_dict[label_key][i]

            if self.ow is not None:
                dicom_data.Rows = self.ow
                dicom_data.Columns = self.oh

                mask_data.Rows = self.ow
                mask_data.Columns = self.oh

                print(f"Rows: {dicom_data.Rows}, Columns: {dicom_data.Columns}")
                self.ui.statusbar.showMessage(f"New rows: {dicom_data.Rows}, New Columns: {dicom_data.Columns}", 10000)

            # 保存DICOM文件
            dicom_file_path = os.path.join(output_folder_dicom, slice)
            dicom_data.save_as(dicom_file_path)

            mask_file_path = os.path.join(output_folder_label, slice)
            mask_data.save_as(mask_file_path)

            i += 1

        data_dict[data_key] = []
        data_dict[label_key] = []

    if img_folder:
        folder_list = os.listdir(img_folder)
        if ".DS_Store" in folder_list:
            folder_list.remove(".DS_Store")

        for time in range(1, 3): 
            # 讀取 DICOM 資料夾
            for file in sorted(folder_list):
                self.dicom_folder_path = os.path.join(img_folder, file) # 每個dicom資料夾位址
                print("dicom_folder_path :", self.dicom_folder_path)
                self.dicom_file = sorted(os.listdir(self.dicom_folder_path))
                if ".DS_Store" in self.dicom_file:
                    self.dicom_file.remove(".DS_Store")

                self.mask_folder_path = os.path.join(mask_folder, file)
                

                for slice_dicom in self.dicom_file:
                    img_slice_path = os.path.join(self.dicom_folder_path, slice_dicom) # 每張Tr切片位址
                    mask_slice_path = os.path.join(self.mask_folder_path , slice_dicom) # 每張label切片位址
                    if img_slice_path.endswith('.dcm') and mask_slice_path.endswith('.dcm'):
                        print(img_slice_path)
                        print(mask_slice_path)
                        self.dicom_data = pydicom.dcmread(img_slice_path)
                        # 获取 DICOM 图像数组
                        dicom_image = self.dicom_data.pixel_array
                        data_dict["data"].append(np.copy(dicom_image))

                        self.mask_data = pydicom.dcmread(mask_slice_path)
                        # 获取 mask 图像数组
                        dicom_mask = self.mask_data.pixel_array
                        data_dict["label"].append(np.copy(dicom_mask))
                
                if time == 1:
                    do_resize(self)

                    out_path_dicom = os.path.join(out_folder_img, f"{file}_{time}")
                    out_path_mask = os.path.join(out_folder_mask, f"{file}_{time}")
                    save(out_path_dicom, out_path_mask)
                elif time == 2:
                    self.oh = None
                    self.ow = None
                    rot90Transform((0, 1, 2, 3), [1,2], data_key='data', label_key='label', p_per_sample=1)
                    
                    out_path_dicom = os.path.join(out_folder_img, f"{file}_{time}")
                    out_path_mask = os.path.join(out_folder_mask, f"{file}_{time}")
                    save(out_path_dicom, out_path_mask)
                    
        openwindow = QtWidgets.QMessageBox()
        openwindow.setText("資料擴增已完成，是否需要檢視")
        openwindow.setWindowTitle("finish")
        openwindow.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        # 顯示視窗，等待使用者按下按鈕
        response = openwindow.exec_()
        if response == QtWidgets.QMessageBox.Yes:
            display_dicom.view(self, openfile.get_folder(self, "開啟欲顯示影像"))

    pass


def conduct_all_SWDA(self):
    self.oh = None
    self.ow = None
    
    img_folder = openfile.get_folder(self, "選擇要進行資料擴增之整體資料夾")
    # mask_folder = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/conduct_all/mask'
    out_folder_img = openfile.get_folder(self, "選擇要進行存檔之資料夾")
    # out_folder_mask = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/conduct_all/output/mask'

    def save(pixel_array, output_folder):
        if not os.path.exists(out_path):
                os.makedirs(out_path)
        else:
            clear_folder(out_path)
    
        i = 0
        for slice in self.dicom_file:
            dicom_file_path = os.path.join(self.dicom_folder_path, slice)
            dicom_data = pydicom.dcmread(dicom_file_path)
            dicom_data.PixelData = pixel_array[i]
            if self.ow is not None:
                dicom_data.Rows = self.ow
                dicom_data.Columns = self.oh
                print(f"Rows: {dicom_data.Rows}, Columns: {dicom_data.Columns}")
                self.ui.statusbar.showMessage(f"New rows: {dicom_data.Rows}, New Columns: {dicom_data.Columns}", 10000)

            # 保存DICOM文件
            dicom_file_path = os.path.join(output_folder, slice)
            dicom_data.save_as(dicom_file_path)
            i += 1
        data_dict["data"] = []

    if img_folder:
        folder_list = os.listdir(img_folder)
        if ".DS_Store" in folder_list:
            folder_list.remove(".DS_Store")
        
        folder_list = [filename for filename in folder_list if not filename.startswith("._")]

        for time in range(1, 11): 
            # 讀取 DICOM 資料夾
            for file in sorted(folder_list):
                self.dicom_folder_path = os.path.join(img_folder, file) # 每個dicom資料夾位址
                print("dicom_folder_path :", self.dicom_folder_path)
                self.dicom_file = sorted(os.listdir(self.dicom_folder_path))
                if ".DS_Store" in self.dicom_file:
                    self.dicom_file.remove(".DS_Store")

                for slice_dicom in self.dicom_file:
                    img_slice_path = os.path.join(self.dicom_folder_path, slice_dicom) # 每張切片位址
                    if img_slice_path.endswith('.dcm'):
                        self.dicom_data = pydicom.dcmread(img_slice_path)
                        # 获取 DICOM 图像数组
                        dicom_image = self.dicom_data.pixel_array
                        data_dict["data"].append(np.copy(dicom_image))

                # 取得每個dicom資料中所有array後
                if time <= 5:
                    do_resize(self)
                    if time == 1:
                        gaussianBlurTransform((0.5, 2.3), different_sigma_per_channel=True ,p_per_sample=1, p_per_channel=1)
                        out_path = os.path.join(out_folder_img, f"{file}_{time}_0000")
                        save(data_dict["data"], out_path)
                    elif time == 2:
                        gaussianNoiseTransform(p_per_sample=1)
                        out_path = os.path.join(out_folder_img, f"{file}_{time}_0000")
                        save(data_dict["data"], out_path)
                    elif time == 3:
                        gammaTransform((0.7, 1.5), invert_image=True, per_channel=True, retain_stats=True, p_per_sample=1)
                        out_path = os.path.join(out_folder_img, f"{file}_{time}_0000")
                        save(data_dict["data"], out_path)
                    elif time == 4:
                        brightnessTransform(0, 0.5, per_channel=True, p_per_sample=1, p_per_channel=1)
                        out_path = os.path.join(out_folder_img, f"{file}_{time}_0000")
                        save(data_dict["data"], out_path)
                    elif time == 5:
                        contrastAugmentationTransform(contrast_range=(0.5, 2), per_channel=True, data_key='data',
                                               p_per_sample=1, p_per_channel=1, p = 0.5)
                        out_path = os.path.join(out_folder_img, f"{file}_{time}_0000")
                        save(data_dict["data"], out_path)
                else:
                    self.oh = None
                    self.ow = None
                    rot90Transform((0, 1, 2, 3), [1,2], data_key='data', p_per_sample=1)
                    if time == 6:
                        gaussianBlurTransform((0.5, 2.3), different_sigma_per_channel=True ,p_per_sample=1, p_per_channel=1)
                        out_path = os.path.join(out_folder_img, f"{file}_{time}_0000")
                        save(data_dict["data"], out_path)
                    elif time == 7:
                        gaussianNoiseTransform(p_per_sample=1)
                        out_path = os.path.join(out_folder_img, f"{file}_{time}_0000")
                        save(data_dict["data"], out_path)
                    elif time == 8:
                        gammaTransform((0.7, 1.5), invert_image=True, per_channel=True, retain_stats=True, p_per_sample=1)
                        out_path = os.path.join(out_folder_img, f"{file}_{time}")
                        save(data_dict["data"], out_path)
                    elif time == 9:
                        brightnessTransform(0, 0.5, per_channel=True, p_per_sample=1, p_per_channel=1)
                        out_path = os.path.join(out_folder_img, f"{file}_{time}_0000")
                        save(data_dict["data"], out_path)
                    elif time == 10:
                        contrastAugmentationTransform(contrast_range=(0.5, 2), per_channel=True, data_key='data',
                                               p_per_sample=1, p_per_channel=1, p = 0.5)
                        out_path = os.path.join(out_folder_img, f"{file}_{time}_0000")
                        save(data_dict["data"], out_path)

        openwindow = QtWidgets.QMessageBox()
        openwindow.setText("資料擴增已完成，是否需要檢視")
        openwindow.setWindowTitle("finish")
        openwindow.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        # 顯示視窗，等待使用者按下按鈕
        response = openwindow.exec_()
        if response == QtWidgets.QMessageBox.Yes:
            display_dicom.view(self, openfile.get_folder(self, "開啟欲顯示影像"))
        

                
        
                


    # def save(augmentation):
    #     if not os.path.exists(os.path.join(out_folder_img, augmentation)):
    #         os.makedirs(os.path.join(out_folder_img, augmentation))
    #     if not os.path.exists(os.path.join(os.path.join(out_folder_img, augmentation), file)):
    #         os.makedirs(os.path.join(os.path.join(out_folder_img, augmentation), file))
        
    #     # 生成输出文件路径
    #     output_filename_dicom = os.path.join(os.path.join(os.path.join(out_folder_img, augmentation), file),slice_dicom)

    #     if not os.path.exists(os.path.join(out_folder_mask, augmentation)):
    #         os.makedirs(os.path.join(out_folder_mask, augmentation))
    #     if not os.path.exists(os.path.join(os.path.join(out_folder_mask, augmentation), file)):
    #         os.makedirs(os.path.join(os.path.join(out_folder_mask, augmentation), file))
    #     output_filename_mask = os.path.join(os.path.join(os.path.join(out_folder_mask, augmentation), file),slice_mask)
    #     # 保存 DICOM 文件
    #     self.dicom_data.save_as(output_filename_dicom)
    #     self.mask_data.save_as(output_filename_mask)



        
                    # # resize(self,dicom_image, dicom_image.shape[0], (2.0, 2.0), mask_image)

                    # hflip(self, dicom_image, mask_image)
                    # save("hflip")

                    # cutout(self, dicom_image, mask_image)
                    # save("cutout")

                    # blur(self, dicom_image, mask_image)
                    # save("blur")

                    # colorjitter_dicom(self, dicom_image, mask_image)
                    # save("colorjitter")

                    # normalize(self, dicom_image, mask_image)
                    # save("normalize")
                    
                    

       