import vtk
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QFileDialog, QApplication, QGraphicsView, QGraphicsScene
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.qt.QVTKRenderWindowInteractor import vtkGenericRenderWindowInteractor
from PyQt5.QtWidgets import *
import math
import numpy as np
from natsort import natsorted
from pathlib import Path
from PyQt5.QtCore import QEventLoop, QObject, Qt
from PyQt5.QtGui import QBrush, QColor, QPen
import os
import usevtk
import openfile
import style
import pydicom
import contorl
import matplotlib.pyplot as plt
from collections import Counter
import shutil

# 設定wl值控制滑桿
def set_wl(self, in_path):
    # 選擇資料夾中第1個資料路徑
    third_subfolder = os.path.join(in_path, os.listdir(in_path)[0])

    # 讀取third_subfolder標頭檔資料
    ds = pydicom.dcmread(third_subfolder)

    # 讀取若dicom標頭檔中有WindowCenter值時
    if hasattr(ds, 'WindowCenter'):
        # 獲取影響window值
        window_center = ds.WindowCenter # 此值就等同於level值
        window_width = ds.WindowWidth

        try:
            window_max_value = window_center + window_width / 2
            window_min_value = window_center - window_width / 2
        except Exception as e:
            window_max_value = 6000
            window_min_value = -1000
            window_center = 1000

        # 設定wl值的滑桿值
        self.ui.horizontalSlider_window.setMinimum(window_min_value) # 設定滑桿最小值
        self.ui.horizontalSlider_window.setMaximum(window_max_value) # 設定滑桿最大值為window_max_value
        self.ui.horizontalSlider_window.setValue(int("2592")) # 設定滑桿初始值

        # 設定當widow滑桿值改變時動作
        self.ui.horizontalSlider_window.valueChanged.connect(self.on_window_slider_value_changed)

        self.ui.horizontalSlider_level.setMinimum(0) # 設定滑桿最小值
        self.ui.horizontalSlider_level.setMaximum(window_center) # 設定滑桿最大值為window_center
        self.ui.horizontalSlider_level.setValue(int("365")) # 設定滑桿初始值

        # 設定當widow滑桿值改變時動作
        self.ui.horizontalSlider_level.valueChanged.connect(self.on_level_slider_value_changed)
    else:
        self.ui.horizontalSlider_window.setValue(int("2592"))
        self.ui.horizontalSlider_level.setValue(int("365"))

# 取得當前切片之路徑
def get_current_slice_path(self, in_path):
    current_slice = self.mapper_dicom.GetSliceNumber() # 取得當前切片數
    files = natsorted(os.listdir(in_path)) # 對in_path進行排序
    current_path = os.path.join(in_path, files[current_slice]) # 取得當前切片之路徑位置
    print(current_path)
    return current_path

def setSlider(self, in_path, num_slices):
    slice_path = get_current_slice_path(self, in_path)
    print("path:", slice_path)
    ds = pydicom.dcmread(slice_path)
    # 取得像素資料
    pixel_data = ds.pixel_array

    # 尋找最大像素值
    max_pixel_value = np.max(pixel_data)
    min_pixel_value = np.min(pixel_data)
    print("min_pixel_value:", min_pixel_value)

    # -------------------------設定所有滑桿基本設置-------------------------
    self.ui.horizontalSlider_threshold.setMinimum(min_pixel_value)
    self.ui.horizontalSlider_threshold.setMaximum(max_pixel_value)
    self.ui.horizontalSlider_threshold.setValue(480)

    self.ui.horizontalSlider_dicom_raw.setMinimum(0)
    self.ui.horizontalSlider_dicom_raw.setMaximum(num_slices - 1)
    self.ui.horizontalSlider_dicom_raw.setValue(self.mid_slice)

    self.ui.horizontalSlider_dicom_coronal.setMinimum(0)
    self.ui.horizontalSlider_dicom_coronal.setMaximum(ds.Rows-1)
    self.ui.horizontalSlider_dicom_coronal.setValue(ds.Rows/2)

    self.ui.horizontalSlider_dicom_sagitta.setMinimum(0)
    self.ui.horizontalSlider_dicom_sagitta.setMaximum(ds.Columns-1)
    self.ui.horizontalSlider_dicom_sagitta.setValue(ds.Columns/2)
    # -------------------------設定所有滑桿基本設置-------------------------

# 設定dicom的三維視窗
def setup_dicom_3d(self):
    self.renderer_dicom_3d = vtk.vtkOpenGLRenderer()
    self.renderer_dicom_3d.SetUseShadows(True)  # 啟用陰影
    self.renderer_dicom_3d.SetUseDepthPeeling(True)  # 深度剝離（用於半透明的模型物件）

    # 建立 vtkCubeSource 創建方框
    cube_source = vtk.vtkCubeSource()
    cube_source.SetCenter(0, 0, 0)  # 設置中心
    cube_source.SetXLength(38.0)      # 設置方框在 X 軸的長度
    cube_source.SetYLength(38.0)      # 設置方框在 Y 軸的長度
    cube_source.SetZLength(38.0)      # 設置方框在 Z 軸的長度

    # 建立 vtkPolyDataMapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube_source.GetOutputPort())

    # 建立 vtkActor 
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(1.0, 1.0, 1.0)  # 設置線為白色
    actor.GetProperty().SetRepresentationToWireframe()  # 表示方式設置為框線
    actor.GetProperty().SetLineWidth(2.0)  # 設置框線的粗度

    # 將 Actor 添加到渲染器
    self.renderer_dicom_3d.AddActor(actor)

    # 設置渲染器的背景颜色
    self.renderer_dicom_3d.SetBackground(0.7490, 0.7608, 0.9216)  # 底部颜色值
    self.renderer_dicom_3d.SetBackground2(0.4549, 0.4745, 0.7647);   # 頂部颜色值
    self.renderer_dicom_3d.SetGradientBackground(2)   # 使用上下漸層的背景

    
    self.iren_dicom.Start() # 啟用交互器

    self.renderer_dicom_3d.ResetCamera()

    self.vtkWidget_dicom_1.GetRenderWindow().AddRenderer(self.renderer_dicom_3d)
    self.vtkWidget_dicom_1.GetRenderWindow().Render()

# 設定視窗放大
def dicom_zoom_out(self, view):
    self.ui.tabWidget.setCurrentIndex(5)  # 設定tabwidget到tab_dicom_zoom頁面
    if view == "dicom_raw":
        # --------------------設定滑桿-------------------------
        self.ui.horizontalSlider_dicom_zoom_raw.setVisible(True)
        self.ui.horizontalSlider_dicom_zoom_raw.setMinimum(self.ui.horizontalSlider_dicom_raw.minimum())
        self.ui.horizontalSlider_dicom_zoom_raw.setMaximum(self.ui.horizontalSlider_dicom_raw.maximum())
        self.ui.horizontalSlider_dicom_zoom_raw.setValue(self.ui.horizontalSlider_dicom_raw.value())
        # 連接滑桿值更改訊號到槽函數
        self.ui.horizontalSlider_dicom_zoom_raw.valueChanged.connect(self.updateSlice_raw)
        # --------------------設定滑桿-------------------------
        self.ui.label_slider_zoom.setText("")
        self.ui.label_slider_zoom.setStyleSheet("color: white; background-color: #ff3320; ")
        self.vtkWidget_dicom.GetRenderWindow().RemoveRenderer(self.renderer_dicom)
        self.vtkWidget_dicom_zoom.GetRenderWindow().AddRenderer(self.renderer_dicom)  # 將原先的渲染器加到新的渲染視窗
        self.iren_dicom_zoom.SetInteractorStyle(vtk.vtkInteractorStyleImage()) # 變更渲染器操作方式
        self.iren_dicom_zoom.Start()  # 啟動交互器

        self.ui.pushButton_zoom_in.clicked.connect(lambda: dicom_zoom_in(self, "dicom_raw"))

    elif view == "dicom_3d":
        self.ui.label_slider_zoom.setStyleSheet("color: white; background-color: #5f6db5; padding-left: 32px;font-size: 16px; font-weight: bold;")
        self.ui.label_slider_zoom.setText("3D model")
        self.vtkWidget_dicom_1.GetRenderWindow().RemoveRenderer(self.renderer_dicom_3d)
        self.vtkWidget_dicom_zoom.GetRenderWindow().AddRenderer(self.renderer_dicom_3d)  # 將原先的渲染器加到新的渲染視窗
        self.iren_dicom_zoom.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera()) # 變更渲染器操作方式
        self.iren_dicom_zoom.Start()  # 啟動交互器

        self.ui.pushButton_zoom_in.clicked.connect(lambda: dicom_zoom_in(self, "dicom_3d"))

    elif view == "dicom_coronal":
        ## --------------------設定滑桿-------------------------
        self.ui.horizontalSlider_dicom_zoom_coronal.setVisible(True)
        self.ui.horizontalSlider_dicom_zoom_coronal.setMinimum(self.ui.horizontalSlider_dicom_coronal.minimum())
        self.ui.horizontalSlider_dicom_zoom_coronal.setMaximum(self.ui.horizontalSlider_dicom_coronal.maximum())
        self.ui.horizontalSlider_dicom_zoom_coronal.setValue(self.ui.horizontalSlider_dicom_coronal.value())
        # 連接滑桿值更改訊號到槽函數
        self.ui.horizontalSlider_dicom_zoom_coronal.valueChanged.connect(self.updateSlice_coronal)
        # --------------------設定滑桿-------------------------
        self.ui.label_slider_zoom.setText("")
        self.ui.label_slider_zoom.setStyleSheet("color: white; background-color: #55ad37; ")
        self.vtkWidget_dicom_2.GetRenderWindow().RemoveRenderer(self.renderer_dicom_coronal)
        self.vtkWidget_dicom_zoom.GetRenderWindow().AddRenderer(self.renderer_dicom_coronal)  # 將原先的渲染器加到新的渲染視窗
        self.iren_dicom_zoom.SetInteractorStyle(vtk.vtkInteractorStyleImage()) # 變更渲染器操作方式
        self.iren_dicom_zoom.Start()  # 啟動交互器

        self.ui.pushButton_zoom_in.clicked.connect(lambda: dicom_zoom_in(self, "dicom_coronal"))

    elif view == "dicom_sagitta":
        # --------------------設定滑桿-------------------------
        self.ui.horizontalSlider_dicom_zoom_sagitta.setVisible(True)
        self.ui.horizontalSlider_dicom_zoom_sagitta.setMinimum(self.ui.horizontalSlider_dicom_sagitta.minimum())
        self.ui.horizontalSlider_dicom_zoom_sagitta.setMaximum(self.ui.horizontalSlider_dicom_sagitta.maximum())
        self.ui.horizontalSlider_dicom_zoom_sagitta.setValue(self.ui.horizontalSlider_dicom_sagitta.value())
        # 連接滑桿值更改訊號到槽函數
        self.ui.horizontalSlider_dicom_zoom_sagitta.valueChanged.connect(self.updateSlice_sagitta)
        # --------------------設定滑桿-------------------------
        self.ui.label_slider_zoom.setText("")
        self.ui.label_slider_zoom.setStyleSheet("color: white; background-color: #eacd19; ")
        self.vtkWidget_dicom_3.GetRenderWindow().RemoveRenderer(self.renderer_dicom_sagitta)
        self.vtkWidget_dicom_zoom.GetRenderWindow().AddRenderer(self.renderer_dicom_sagitta)  # 將原先的渲染器加到新的渲染視窗
        self.iren_dicom_zoom.SetInteractorStyle(vtk.vtkInteractorStyleImage()) # 變更渲染器操作方式
        self.iren_dicom_zoom.Start()  # 啟動交互器

        self.ui.pushButton_zoom_in.clicked.connect(lambda: dicom_zoom_in(self, "dicom_sagitta"))

# 設定視窗縮小
def dicom_zoom_in(self, view):
    self.ui.tabWidget.setCurrentIndex(4)
    if view == "dicom_raw":
        self.ui.horizontalSlider_dicom_raw.setValue(self.ui.horizontalSlider_dicom_zoom_raw.value()) # 設定滑桿值與原滑桿相同
        self.ui.horizontalSlider_dicom_zoom_raw.setVisible(False) # 關閉滑桿
        self.ui.horizontalSlider_dicom_raw.valueChanged.connect(self.updateSlice_raw) # 設定滑桿連接的函式
        self.vtkWidget_dicom_zoom.GetRenderWindow().RemoveRenderer(self.renderer_dicom) # 移除zoom視窗的渲染器
        self.vtkWidget_dicom.GetRenderWindow().AddRenderer(self.renderer_dicom)  # 將原先的渲染器加到新的渲染視窗
    elif view == "dicom_3d":
        self.vtkWidget_dicom_zoom.GetRenderWindow().RemoveRenderer(self.renderer_dicom_3d)# 移除zoom視窗的渲染器
        self.vtkWidget_dicom_1.GetRenderWindow().AddRenderer(self.renderer_dicom_3d)  # 將原先的渲染器加到新的渲染視窗
    elif view == "dicom_coronal":
        self.ui.horizontalSlider_dicom_coronal.setValue(self.ui.horizontalSlider_dicom_zoom_coronal.value()) # 設定滑桿值與原滑桿相同
        self.ui.horizontalSlider_dicom_zoom_coronal.setVisible(False) # 關閉滑桿
        self.ui.horizontalSlider_dicom_coronal.valueChanged.connect(self.updateSlice_coronal) # 設定滑桿連接的函式
        self.vtkWidget_dicom_zoom.GetRenderWindow().RemoveRenderer(self.renderer_dicom_coronal)# 移除zoom視窗的渲染器
        self.vtkWidget_dicom_2.GetRenderWindow().AddRenderer(self.renderer_dicom_coronal)  # 將原先的渲染器加到新的渲染視窗
    elif view == "dicom_sagitta":
        self.ui.horizontalSlider_dicom_sagitta.setValue(self.ui.horizontalSlider_dicom_zoom_sagitta.value()) # 設定滑桿值與原滑桿相同
        self.ui.horizontalSlider_dicom_zoom_sagitta.setVisible(False) # 關閉滑桿
        self.ui.horizontalSlider_dicom_sagitta.valueChanged.connect(self.updateSlice_sagitta) # 設定滑桿連接的函式
        self.vtkWidget_dicom_zoom.GetRenderWindow().RemoveRenderer(self.renderer_dicom_sagitta)# 移除zoom視窗的渲染器
        self.vtkWidget_dicom_3.GetRenderWindow().AddRenderer(self.renderer_dicom_sagitta)  # 將原先的渲染器加到新的渲染視窗
    self.use_slider = True

def dicom_3d(self, in_path):
    if self.ui.checkBox_see_3d.isChecked():
        self.ui.threshold.setEnabled(True)
        self.ui.horizontalSlider_threshold.setEnabled(True)
        self.iren_dicom_3d = self.vtkWidget_dicom_1.GetRenderWindow().GetInteractor()
        self.iren_dicom_3d.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        # 建立 Dicom 讀取器
        reader = vtk.vtkDICOMImageReader()
        reader.SetDirectoryName(in_path)
        reader.Update()

        # 減少資料的體積
        shrink = vtk.vtkImageShrink3D()
        shrink.SetInputData(reader.GetOutput())
        shrink.AveragingOn()
        shrink.SetShrinkFactors(6,6,6) # 6：x軸縮小6倍、6：y軸縮小6倍、6:z軸縮小6倍
        shrink.Update()

        self.threshold_values = self.ui.horizontalSlider_threshold.value() # 綁定滑桿值

        # MarchingCubes三維重建
        self.surface = vtk.vtkMarchingCubes()
        self.surface.SetInputData(shrink.GetOutput())
        self.surface.SetValue(0, self.threshold_values)
        self.surface.Update() # 執行Marching Cubes演算法，生成表面

        # 創建顏色色組
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)  # RGB颜色
        colors.SetName("Colors")

        # 設定所有点的颜色
        for j in range(self.surface.GetOutput().GetNumberOfPoints()):
            # 依照閥值進行設定
            if self.threshold_values < 30:
                colors.InsertNextTuple3(255, 214, 170)  # 皮膚色
            else:
                colors.InsertNextTuple3(190, 190, 190)  # 骨白色

        # 將顏色資料和 vtkPolyData 綁定
        self.surface.GetOutput().GetPointData().SetScalars(colors)
        self.surface.Update()

        # 連接滑桿值更改訊號到槽函數
        self.ui.horizontalSlider_threshold.valueChanged.connect(self.updatethreshold)

        # 取得模型中三角形資訊
        self.triangles = vtk.vtkTriangleFilter()
        self.triangles.SetInputConnection(self.surface.GetOutputPort())  
        self.triangles.Update()  # 更新Triangle Filter

        # 取得模型中三角形的數量
        number_of_triangles = self.triangles.GetOutput().GetNumberOfCells()

        # 犧牲模型點數量，以加速處理速度
        deci=vtk.vtkDecimatePro()
        if number_of_triangles < 50000 :
            deci.SetTargetReduction(0.1) # 減少模型的點數量改為原來的 10%
        elif 50000 <= number_of_triangles < 70000:
            deci.SetTargetReduction(0.0001) # 減少模型的點數量改為原來的 0.1%
        elif 70000 <= number_of_triangles < 90000:
            deci.SetTargetReduction(0.00001) # 減少模型的點數量改為原來的 0.001%
        elif 90000 <= number_of_triangles < 150000:
            deci.SetTargetReduction(0.000001) # 減少模型的點數量改為原來的 0.001%
        elif 150000 <= number_of_triangles < 200000:
            deci.SetTargetReduction(0.0000001) # 減少模型的點數量改為原來的 0.0001%
        else:
            deci.SetTargetReduction(0.000000001) # 減少模型的點數量改為原來的 0.000001%

        deci.SetInputConnection(self.surface.GetOutputPort())

        # 取得模型法線
        skinNormals = vtk.vtkPolyDataNormals()
        skinNormals.SetInputConnection(deci.GetOutputPort())
        skinNormals.SetFeatureAngle(60.0)

        # 將各個模型點連接
        stripper = vtk.vtkStripper()
        stripper.SetInputConnection(skinNormals.GetOutputPort())

        # 綁定到Mapper上，從而生成可供VTK渲染的組件
        self.mapper_dicom_3d = vtk.vtkPolyDataMapper()
        self.mapper_dicom_3d.SetInputConnection(stripper.GetOutputPort())

        # 模型中心点
        model_center = self.mapper_dicom_3d.GetCenter()

        # 取得模型中心點座標
        translation = [-(model_center[0]), -(model_center[1]), -(model_center[2])]

        # 缩放因子（0.125 表示缩小到原尺寸的1/8）
        scale_factor = 0.125

        # 設定轉換座標
        transform = vtk.vtkTransform()
        transform.Scale(scale_factor, scale_factor, scale_factor) # 縮小影像
        transform.Translate(translation) # 設定模型中心點座標為視窗原點

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper_dicom_3d)
        self.actor.GetProperty().SetAmbient(0.4) # 控制物體在沒有直接光源照射時的颜色和亮度(環境光)
        self.actor.GetProperty().SetDiffuse(0.7) # 控制物體在受到直射光源照射時的颜色和反射(漫反射)
        self.actor.GetProperty().SetSpecular(0.1) # 控制物体表面的镜面高光反射效果(鏡面反射)
        self.actor.SetUserTransform(transform)

        self.renderer_dicom_3d.AddActor(self.actor)

        # 模型邊界框
        bounds = self.mapper_dicom_3d.GetBounds()

        mean_x = (bounds[0] + bounds[1])/2
        mean_y = (bounds[2] + bounds[3])/2
        mean_z = (bounds[4] + bounds[5])/2
        mean_all = (mean_x+mean_y+mean_z)/3

        # 設定相機位置
        camera = vtk.vtkCamera()
        camera.SetPosition(0, mean_all/1.6 + 38, 1) # 設定相機位置
        camera.SetFocalPoint(0, 0, 0)  # 設定相機觀看的焦點
        camera.Zoom(1.5)
        self.renderer_dicom_3d.SetActiveCamera(camera)  # 設定渲染器的相機

        # 啟動交互器，偵測滑鼠動作
        self.iren_dicom_3d.Initialize()
        self.iren_dicom_3d.Start()
        self.vtkWidget_dicom_1.GetRenderWindow().Render()
        self.ui.pushButton_zoom_3d.clicked.connect(lambda: dicom_zoom_out(self, "dicom_3d"))
    else:
        self.ui.threshold.setEnabled(False)
        self.ui.horizontalSlider_threshold.setEnabled(False)
        setup_dicom_3d(self)

def view_other(self, in_path):
    self.iren_dicom_coronal = self.vtkWidget_dicom_2.GetRenderWindow().GetInteractor()
    self.iren_dicom_sagitta = self.vtkWidget_dicom_3.GetRenderWindow().GetInteractor()
    self.iren_dicom_coronal.SetInteractorStyle(vtk.vtkInteractorStyleImage()) 
    self.iren_dicom_sagitta.SetInteractorStyle(vtk.vtkInteractorStyleImage())  
    # 設置dicom讀取器
    reader = vtk.vtkDICOMImageReader()
    # 設置dicom讀取器讀取位址
    reader.SetDirectoryName(in_path)
    # 更新dicom讀取器
    reader.Update()

    # 設定wl值滑桿數值
    set_wl(self, in_path)

    # 創建渲染視窗和渲染器
    self.renderer_dicom_coronal = vtk.vtkRenderer()
    self.renderer_dicom_sagitta = vtk.vtkRenderer()
    self.vtkWidget_dicom_2.GetRenderWindow().AddRenderer(self.renderer_dicom_coronal)
    self.vtkWidget_dicom_3.GetRenderWindow().AddRenderer(self.renderer_dicom_sagitta)

    self.extent = reader.GetOutput().GetExtent()  # 取得圖像範圍
    self.spacing = reader.GetOutput().GetSpacing()    # 取得各像素間隔
    self.origin = reader.GetOutput().GetOrigin()   # 取得原點

    self.center1 = self.origin[0] + self.spacing[0] * 0.5 *(self.extent[0] + self.extent[1])
    self.center2 = self.origin[1] + self.spacing[1] * 0.5 *(self.extent[2] + self.extent[3])
    self.center3 = self.origin[2] + self.spacing[2] * 0.5 *(self.extent[4] + self.extent[5])

    coronalElements = [1, 0, 0, 0,
                    0, 0, 1, 0,
                    0, -1, 0, 0,
                    0, 0, 0, 1]     # 取得平行於XZ平面的轉換矩陣
    
    sagittalElements = [0, 0, -1, 0,
                        -1, 0, 0, 0,
                        0, -1, 0, 0,
                        0, 0, 0, 1]     # 取得平行於YZ平面的轉換矩陣
            
    self.resliceAxes_coronal = vtk.vtkMatrix4x4()
    self.resliceAxes_coronal.DeepCopy(coronalElements)
    self.resliceAxes_coronal.SetElement(0, 3, self.center1)
    self.resliceAxes_coronal.SetElement(1, 3, self.center2)
    self.resliceAxes_coronal.SetElement(2, 3, self.center3)

    self.reslice_coronal = vtk.vtkImageReslice()      # 取得影像切面
    self.reslice_coronal.SetInputConnection(self.window_level_filter.GetOutputPort())
    self.reslice_coronal.SetOutputDimensionality(2)    # 指定輸出為二維影像
    self.reslice_coronal.SetResliceAxes(self.resliceAxes_coronal)    # 設定轉換矩陣
    self.reslice_coronal.SetOutputExtent(self.extent[0], self.extent[1], self.extent[4], self.extent[5], 0, 0)
    self.reslice_coronal.SetInterpolationModeToLinear()   # 線性插值

    # 使用 vtkImageSliceMapper 和 vtkImageSlice 顯示影像
    self.mapper_dicom_coronal = vtk.vtkImageSliceMapper()
    self.mapper_dicom_coronal.SetInputConnection(self.reslice_coronal.GetOutputPort())
    self.slice_coronal = vtk.vtkImageSlice()
    self.slice_coronal.SetMapper(self.mapper_dicom_coronal)


    self.resliceAxes_sagitta = vtk.vtkMatrix4x4()
    self.resliceAxes_sagitta.DeepCopy(sagittalElements)
    self.resliceAxes_sagitta.SetElement(0, 3, self.center1)
    self.resliceAxes_sagitta.SetElement(1, 3, self.center2)
    self.resliceAxes_sagitta.SetElement(2, 3, self.center3)

    self.reslice_sagitta = vtk.vtkImageReslice()      # 取得影像切面
    self.reslice_sagitta.SetInputConnection(self.window_level_filter.GetOutputPort())
    self.reslice_sagitta.SetOutputDimensionality(2)    # 指定輸出為二維影像
    self.reslice_sagitta.SetResliceAxes(self.resliceAxes_sagitta)    # 設定轉換矩陣
    self.reslice_sagitta.SetInterpolationModeToLinear()   # 線性插值

    # 使用 vtkImageSliceMapper 和 vtkImageSlice 顯示影像
    self.mapper_dicom_sagitta = vtk.vtkImageSliceMapper()
    self.mapper_dicom_sagitta.SetInputConnection(self.reslice_sagitta.GetOutputPort())

    self.slice_sagitta = vtk.vtkImageSlice()
    self.slice_sagitta.SetMapper(self.mapper_dicom_sagitta)

     # 連接滑桿值更改訊號到槽函數
    self.ui.horizontalSlider_dicom_coronal.valueChanged.connect(self.updateSlice_coronal)
    self.ui.horizontalSlider_dicom_sagitta.valueChanged.connect(self.updateSlice_sagitta)

    # 將 VTK Widget 和 QGraphicsView 添加到相同的父容器中
    self.ui.tab_dicom.setLayout(self.layout_dicom)

    # 將影像加入到渲染器並更新渲染視窗
    self.renderer_dicom_coronal.AddViewProp(self.slice_coronal)
    # 調整透明度
    self.slice_coronal.GetProperty().SetOpacity(1)

    # 將影像加入到渲染器並更新渲染視窗
    self.renderer_dicom_sagitta.AddViewProp(self.slice_sagitta)
    # 調整透明度
    self.slice_sagitta.GetProperty().SetOpacity(1)

    self.renderer_dicom_coronal.ResetCamera()
    self.renderer_dicom_coronal.GetActiveCamera().Zoom(1.5)
    self.renderer_dicom_sagitta.ResetCamera()
    self.renderer_dicom_sagitta.GetActiveCamera().Zoom(1.5)


    # 啟動交互器，偵測滑鼠動作
    self.iren_dicom_coronal.Initialize()
    self.iren_dicom_coronal.Start()

    # 啟動交互器，偵測滑鼠動作
    self.iren_dicom_sagitta.Initialize()
    self.iren_dicom_sagitta.Start()

    
    self.vtkWidget_dicom_2.GetRenderWindow().Render()
    self.vtkWidget_dicom_3.GetRenderWindow().Render()

    self.ui.pushButton_zoom_coronal.clicked.connect(lambda: dicom_zoom_out(self, "dicom_coronal"))
    self.ui.pushButton_zoom_sagitta.clicked.connect(lambda: dicom_zoom_out(self, "dicom_sagitta"))

def is_dicom_file(file_path):
    try:
        with pydicom.dcmread(file_path, force=True):
            return True
    except pydicom.errors.InvalidDicomError:
        return False

# 取得同類別數量最多之資料
def get_max_files(folder_path):
    # file_sizes_dict_dict：每個資料對應其文件大小的dict
    # size_count：檔案大小計數器
    file_sizes_dict = {}  
    size_count = []
    size_lst = []

    # 跑遍輸入資料夾中的所有檔案
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file) # 取得檔案大小
            size = round(os.path.getsize(file_path) / 1000) # 取得檔案大小

            # 檢查size是否已有相同，並將檔案路徑加入file_sizes_dict
            if size in file_sizes_dict:
                file_sizes_dict[size].append(file_path)
            else:
                file_sizes_dict[size] = [file_path]
                size_lst.append(size) # 記錄有幾種不同的檔案大小
            
            size_count.append(size) # 記錄檔案大小

    # 若大於兩種檔案大小才執行
    if len(size_lst)>= 2:
        # ------------- 取得size_count中最多重複資料 -------------
        counter = Counter(size_count) 
        most_common_value = counter.most_common(1)[0][0]
        # ------------- 取得size_count中最多重複資料 -------------
        
        # 取出最多重複資料中的所有文件path
        files_we_need = [paths for paths in file_sizes_dict[most_common_value]]

        # ------------------ 設置暫存資料夾 ------------------
        temp_dicom = os.path.join(folder_path, "temp")
        if os.path.exists(temp_dicom):
            shutil.rmtree(temp_dicom)
            os.makedirs(temp_dicom, exist_ok=True)
        else:
            os.makedirs(temp_dicom, exist_ok=True)
        # ------------------ 設置暫存資料夾 ------------------

        # 將每個資料複製到所建立暫存資料夾中
        for file in files_we_need:
            file_name = os.path.basename(file)  # 取得檔案名稱
            new_file_path = os.path.join(temp_dicom , file_name) # 設置新存檔路徑至暫存資料夾下
            shutil.copy(file, new_file_path) # 將原本檔案複製到暫存資料夾中
    else:
        temp_dicom = folder_path

    return temp_dicom # 回傳暫存資料夾位址

# # 用法示例
# folder_path = '/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/虎科林彥昆老師/非正常版/01'
# files = get_max_files(folder_path)
# print(files)
    
def view(self, in_path):
    # ---------確認是否為dicom資料夾-----------
    if in_path:
        data = os.listdir(in_path)
        # 原先偵測是否為dicom檔案之方式
        # if Path(os.path.join(in_path, data[1])).suffix == ".dcm": 

        if is_dicom_file(os.path.join(in_path, data[1])):
    # ---------確認是否為dicom資料夾-----------
            self.in_path = in_path
            contorl.home(self)
            self.ui.tabWidget.setCurrentIndex(4)  # 設定tabwidget到tab_dicom頁面
            self.ui.stackedWidget.setCurrentIndex(2) # 設置按鈕介面至切片控制頁

            # 若vtk視窗已被關閉就重啟一個
            if self.vtkWidget_dicom is None:
                self.vtkWidget_dicom = QVTKRenderWindowInteractor(self.ui.tab_dicom)

            self.vtkWidget_dicom.show()

            # 設置dicom讀取器
            reader = vtk.vtkDICOMImageReader()

            # 刪除默認檔案
            if os.path.exists(os.path.join(in_path, ".DS_Store")):
                os.remove(os.path.join(in_path, ".DS_Store"))

            new_path = get_max_files(in_path)
            

            # 設置dicom讀取器讀取位址
            reader.SetDirectoryName(new_path)
            # 更新dicom讀取器
            reader.Update()

            # 設定滑桿的範圍和初始值
            num_slices = reader.GetOutput().GetDimensions()[2]
            self.mid_slice = math.ceil(num_slices/2)
            
            # 設定wl值滑桿數值
            set_wl(self, in_path)

            # 創建渲染視窗和渲染器
            self.renderer_dicom = vtk.vtkRenderer()
            self.vtkWidget_dicom.GetRenderWindow().AddRenderer(self.renderer_dicom)

            self.window_level_filter = vtk.vtkImageMapToWindowLevelColors()
            self.window_level_filter.SetInputConnection(reader.GetOutputPort())
            self.window_level_filter.SetWindow(2596)   # 設定預設window值
            self.window_level_filter.SetLevel(365)   # 設定預設level值

            # 使用 vtkImageSliceMapper 和 vtkImageSlice 顯示圖像
            self.mapper_dicom = vtk.vtkImageSliceMapper()
            self.mapper_dicom.SetSliceNumber(self.mid_slice)
            self.mapper_dicom.SetInputConnection(self.window_level_filter.GetOutputPort())

            self.slice = vtk.vtkImageSlice()
            self.slice.SetMapper(self.mapper_dicom)

            setSlider(self, in_path, num_slices)
            if self.ui.horizontalSlider_threshold.maximum()+abs(self.ui.horizontalSlider_threshold.minimum()) <= 500:
                # 建立顏色映射
                color_map = vtk.vtkLookupTable()
                color_map.SetNumberOfTableValues(2)  # 設定顏色映射的值數量

                # 第一个颜色：背景颜色－黑色
                color_map.SetTableValue(0, 0.0, 0.0, 0.0, 1.0)  # 背景顏色設為黑色

                # 第二个颜色以後：是標註區域的颜色
                color_map.SetTableValue(1, 1.0, 1.0, 1.0, 1.0)  # 設定標註區域為白色

                # 設定顏色的映射範圍
                color_map.SetTableRange(0, 1)  # 根據標註的數量值調整

                # 设置颜色映射范围
                color_map.SetRange(0, 1)  # 根据标记的像素值范围进行调整

                # 使用颜色映射
                self.window_level_filter.SetLookupTable(color_map)
                # 更新渲染視窗
                self.mapper_dicom.Update()
                self.vtkWidget_dicom.GetRenderWindow().Render()
                self.vtkWidget_dicom_2.GetRenderWindow().Render()
                self.vtkWidget_dicom_3.GetRenderWindow().Render()

            # 連接滑桿值更改信號到槽函數
            self.ui.horizontalSlider_dicom_raw.valueChanged.connect(self.updateSlice_raw)

            # 將 VTK Widget 和 QGraphicsView 添加到相同的父容器中
            self.ui.tab_dicom.setLayout(self.layout_dicom)

            # 將圖像添加到渲染器並更新渲染視窗
            self.renderer_dicom.AddViewProp(self.slice)
            # 调整透明度
            self.slice.GetProperty().SetOpacity(1)

            self.renderer_dicom.ResetCamera()
            self.renderer_dicom.GetActiveCamera().Zoom(1.5)

                
            self.vtkWidget_dicom.GetRenderWindow().SetInteractor(self.iren_dicom)

            # 啟動交互器，偵測滑鼠動作
            self.iren_dicom.Initialize()
            self.iren_dicom.Start()
            
            self.vtkWidget_dicom.GetRenderWindow().Render()

            self.ui.pushButton_zoom_raw.clicked.connect(lambda: dicom_zoom_out(self, "dicom_raw"))

            # 設定關閉視窗按鈕
            self.ui.btn_close_dcm.setVisible(True)
            self.ui.btn_close_dcm.clicked.connect(lambda: usevtk.dicomclose(self))  # 關閉按鈕連接關閉指令

            # 設定不同的wl值樣式
            def wlstyle(num):
                if num == 1 :
                    self.ui.horizontalSlider_window.setValue(int("1000")) # 設定預設window值
                    self.ui.horizontalSlider_level.setValue(int("400")) # 設定預設level值
                elif num == 2 :
                    self.ui.horizontalSlider_window.setValue(int("1000")) # 設定預設window值
                    self.ui.horizontalSlider_level.setValue(int("-426")) # 設定預設level值
                elif num == 3 :
                    self.ui.horizontalSlider_window.setValue(int("100")) # 設定預設window值
                    self.ui.horizontalSlider_level.setValue(int("50")) # 設定預設level值
                elif num == 4 :
                    self.ui.horizontalSlider_window.setValue(int("350")) # 設定預設window值
                    self.ui.horizontalSlider_level.setValue(int("40")) # 設定預設level值
                elif num == 5 :
                    self.ui.horizontalSlider_window.setValue(int("1400")) # 設定預設window值
                    self.ui.horizontalSlider_level.setValue(int("-500")) # 設定預設level值

            def calculate_rainbow_color(pixel_value):
                # 假設像素值的範圍在 0 到 255 之間
                r = g = b = 0  # 初始化rgb通道值
                
                if pixel_value < 85:  # 對應彩虹的紅、橙、黃顏色
                    r = int(pixel_value / 85 * 255)  # 從紅到橙到黃的過渡
                    g = int(255 - pixel_value / 85 * 255)  # 從綠到橙到黃的過渡
                elif pixel_value < 170:  # 對應彩虹的綠、藍綠顏色
                    g = int((pixel_value - 85) / 85 * 255)  # 從綠到青的過渡
                    b = int(255 - (pixel_value - 85) / 85 * 255)  # 從藍綠到青的過渡
                else:  # 對應彩虹的藍、紫顏色
                    b = int((pixel_value - 170) / 85 * 255)  # 從藍到紫的過渡
                    r = int(255 - (pixel_value - 170) / 85 * 255)  # 從紅到紫的過渡
                
                return r, g, b

            def rainbow():
                # 创建颜色映射
                color_map = vtk.vtkLookupTable()
                color_map.SetNumberOfTableValues(2)  # 您可以根据需要设置颜色映射的值数量

                # 第一个颜色是背景颜色，可以是黑色
                color_map.SetTableValue(0, 0.0, 0.0, 0.0, 1.0)  # 设置背景颜色为黑色

                # 第二个颜色是标记区域的颜色，可以是白色
                color_map.SetTableValue(1, 1.0, 1.0, 1.0, 1.0)  # 设置标记区域的颜色为白色

                # 设置颜色映射范围
                color_map.SetTableRange(0, 1)  # 根据标记的像素值范围进行调整

                # 设置颜色映射范围
                color_map.SetRange(0, 1)  # 根据标记的像素值范围进行调整

                # 使用颜色映射
                self.window_level_filter.SetLookupTable(color_map)
                # current_path = get_current_slice_path(self, in_path)
                # ds = pydicom.dcmread(current_path)
                
                # # 提取影像資料並轉換為NumPy數組
                # image_array = ds.pixel_array.astype(np.uint16)  # 將像素數組轉換為無符號16位整數
                
                # # 創建一個VTK影像資料對象
                # vtk_image = vtk.vtkImageData()
                # vtk_image.SetDimensions(image_array.shape[1], image_array.shape[0], 1)
                # vtk_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 3)
                
                # # 取得VTK影像的像素資料
                # vtk_pixel_array = vtk_image.GetPointData().GetScalars()
                
                # # 將NumPy中的像素數據複製到VTK圖像數據對像中
                # for y in range(image_array.shape[0]):
                #     for x in range(image_array.shape[1]):
                #         pixel_value = image_array[y, x]
                #         vtk_pixel_index = vtk_image.ComputePointId([x, y, 0])
                #         vtk_pixel_array.SetComponent(vtk_pixel_index, 0, pixel_value)
                #         vtk_pixel_array.SetComponent(vtk_pixel_index, 1, pixel_value)
                #         vtk_pixel_array.SetComponent(vtk_pixel_index, 2, pixel_value)
                
                # # 創建一個顏色映射器
                # color_map = vtk.vtkColorTransferFunction()
                
                # # 設置彩虹顏色成像
                # for i in range(256):  # 假設像素值範圍在 0 到 255 之間
                #     r, g, b = calculate_rainbow_color(i)
                #     color_map.AddRGBPoint(i, r, g, b)
                
                # # 將顏色映射器應用在窗口級別過濾器
                # self.window_level_filter.SetLookupTable(color_map)
                
                # 更新渲染視窗
                self.mapper_dicom.Update()
                self.vtkWidget_dicom.GetRenderWindow().Render()
                self.vtkWidget_dicom_2.GetRenderWindow().Render()
                self.vtkWidget_dicom_3.GetRenderWindow().Render()

            view_other(self, in_path)


            # 設定不同既有樣式WL值按鈕連接
            self.ui.btn_wlstyle_1.clicked.connect(lambda: wlstyle(1))
            self.ui.btn_wlstyle_2.clicked.connect(lambda: wlstyle(2))
            self.ui.btn_wlstyle_3.clicked.connect(lambda: wlstyle(3))
            self.ui.btn_wlstyle_4.clicked.connect(lambda: wlstyle(4))
            self.ui.btn_wlstyle_5.clicked.connect(lambda: wlstyle(5))
            self.ui.btn_wlstyle_6.clicked.connect(lambda: rainbow())
            print(in_path)
            
        else:
            QMessageBox.about(self, "Erro", "Open the correct folder od Dicom, Please!")

def display_slice(self, input):
    choice = []
    for i, slice in enumerate (sorted(os.listdir(input))):
        choice.append(slice)
        
    selected_item, ok = QInputDialog.getItem(None, "請選擇資料擴增形式", ":", choice)
    if ok and selected_item:  # 如果使用者選擇了一個項目
        input_file = os.path.join(input, selected_item)
        if input_file:
            dicom_data = pydicom.dcmread(input_file)
            # 获取 DICOM 图像数组
            dicom_image = dicom_data.pixel_array
            plt.imshow(dicom_image, cmap='gray')
            plt.title("Dicom single slice")
            plt.axis('off')
            plt.show()
        return
    else:
        return



def add_seg(self):
    # in_path = openfile.get_folder(self, "開啟Dicom資料夾")
    in_path = r'/Users/andy/Documents/andy_college/about_my_lab_life/CT_data/有哲標註完成/2'

    if in_path:
        self.ui.btn_get_3dmodel.setVisible(True)
        # 設置dicom讀取器
        reader = vtk.vtkDICOMImageReader()
        # 刪除默認檔案
        if os.path.exists(os.path.join(in_path, ".DS_Store")):
            os.remove(os.path.join(in_path, ".DS_Store"))
        # 設置dicom讀取器讀取位址
        reader.SetDirectoryName(in_path)
        # 更新dicom讀取器
        reader.Update()

        self.window_level_filter_seg = vtk.vtkImageMapToWindowLevelColors()
        self.window_level_filter_seg.SetInputConnection(reader.GetOutputPort())
        self.window_level_filter_seg.SetWindow(2596)   # 設定預設window值
        self.window_level_filter_seg.SetLevel(365)   # 設定預設level值
        # 使用 vtkImageSliceMapper 和 vtkImageSlice 顯示圖像
        self.mapper_dicom_seg = vtk.vtkImageSliceMapper()
        self.mapper_dicom_seg.SetSliceNumber(self.mid_slice)
        self.mapper_dicom_seg.SetInputConnection(self.window_level_filter_seg.GetOutputPort())

        self.slice_seg = vtk.vtkImageSlice()
        self.slice_seg.SetMapper(self.mapper_dicom_seg)

        # 調整透明度
        self.slice_seg.GetProperty().SetOpacity(0.3)

        # 建立顏色映射
        color_map = vtk.vtkLookupTable()
        color_map.SetNumberOfTableValues(2)  # 設定顏色映射的值數量

        # 第一个颜色：背景颜色－黑色
        color_map.SetTableValue(0, 0.0, 0.0, 0.0, 0.0)  # 背景顏色設為黑色

        # 第二个颜色以後：是標註區域的颜色
        color_map.SetTableValue(1, 0.0, 1.0, 0.0, 1.0)  # 設定標註區域為綠色

        # 設定顏色的映射範圍
        color_map.SetTableRange(0, 1)  # 根據標註的數量值調整

        # 设置颜色映射范围
        color_map.SetRange(0, 1)  # 根据标记的像素值范围进行调整

        # 使用颜色映射
        self.window_level_filter_seg.SetLookupTable(color_map)
        # 將圖像添加到渲染器並更新渲染視窗
        self.renderer_dicom.AddViewProp(self.slice_seg)
        self.renderer_dicom_coronal.AddViewProp(self.slice_seg)
        self.renderer_dicom_sagitta.AddViewProp(self.slice_seg)
        # 更新渲染視窗
        self.mapper_dicom_seg.Update()
        self.vtkWidget_dicom.GetRenderWindow().Render()
        self.vtkWidget_dicom_2.GetRenderWindow().Render()
        self.vtkWidget_dicom_3.GetRenderWindow().Render()
        self.ui.btn_get_3dmodel.clicked.connect(lambda: usevtk.view(self, in_path))

        # # 清除所有视图属性
        # self.renderer_dicom.RemoveAllViewProps()

        # # 读取DICOM文件
        # reader = vtk.vtkDICOMImageReader()
        # reader.SetDirectoryName(in_path)  # 替换为您的DICOM文件目录
        # # 更新读取器
        # reader.Update()

        # # 删除默认文件
        # if os.path.exists(os.path.join(in_path, ".DS_Store")):
        #     os.remove(os.path.join(in_path, ".DS_Store"))
        
        # # 创建颜色映射器和查找表
        # color_map = vtk.vtkLookupTable()
        # color_map.SetNumberOfTableValues(3)  # 设置查找表中的颜色数量为2，对应两种颜色

        # # 第一种颜色
        # color_map.SetTableValue(0, 1.0, 1.0, 1.0, 0.0)  # 黑色不顯示
        # # 第二种颜色
        # color_map.SetTableValue(1, 0.0, 0.0, 1.0, 1.0)  # 蓝色
        # # 第三种颜色
        # color_map.SetTableValue(2, 0.0, 1.0, 0.0, 1.0)  # 綠色
        

        # # 设置颜色映射器范围
        # color_map.SetRange(reader.GetOutput().GetScalarRange())

        # self.window_level_filter = vtk.vtkImageMapToWindowLevelColors()
        # self.window_level_filter.SetInputConnection(reader.GetOutputPort())
        # self.window_level_filter.SetWindow(2596)   # 設定預設window值
        # self.window_level_filter.SetLevel(365)   # 設定預設level值


        # # 使用vtkImageSliceMapper和vtkImageSlice显示图像
        # self.mapper_dicom_seg = vtk.vtkImageSliceMapper()
        # self.mapper_dicom_seg.SetSliceNumber(mid_slice)
        # self.mapper_dicom_seg.SetInputConnection(self.window_level_filter.GetOutputPort())

        # # 创建图像分割滤波器
        # color_filter = vtk.vtkImageMapToColors()
        # color_filter.SetInputConnection(self.mapper_dicom_seg.GetOutputPort())
        # color_filter.SetLookupTable(color_map)

        # self.slice_seg = vtk.vtkImageSlice()
        # self.slice_seg.SetMapper(self.mapper_dicom_seg)
        # self.slice_seg.GetMapper().SetInputConnection(color_filter.GetOutputPort())

        # # 连接滑块值更改信号到槽函数
        # self.ui.horizontalSlider_threshold.valueChanged.connect(self.updatethreshold)

        # # 將圖像添加到渲染器並更新渲染視窗
        # self.renderer_dicom.AddViewProp(self.slice_seg)

        # # 调整透明度
        # self.slice_seg.GetProperty().SetOpacity(0.7)
        # self.slice.GetProperty().SetOpacity(1)

        # # 重置相机
        # self.renderer_dicom.ResetCamera()
        # self.vtkWidget_dicom.GetRenderWindow().Render()

# def draw_rectangle(self):
#     # if self.start_point and self.end_point:
#     if self.rectangle:
#         self.scene.removeItem(self.rectangle)
    
#     # 取得方框的座標和大小
#     x = min(self.start_point.x(), self.end_point.x())
#     y = min(self.start_point.y(), self.end_point.y())
#     width = abs(self.end_point.x() - self.start_point.x())
#     height = abs(self.end_point.y() - self.start_point.y())
    
#     pen = QPen(QColor(255, 0, 0))  # 設定筆刷顏色為紅色
#     pen.setWidth(3)  # 設定筆刷寬度為2
#     pen.setCosmetic(True)  # 設定筆刷為 cosmetic style，以便適應變換
    
#     brush = QBrush(Qt.NoBrush)  # 設定填滿方式為無填滿
    
#     self.rectangle = self.scene.addRect(x, y, width, height, pen, brush)  # 在場景中新增方框
#     self.rectangle.setZValue(1)
    
#     self.start_point = None
#     self.end_point = None
    
#     # 強制更新場景
#     self.scene.update()




    # 切割影像
#     crop_image(self, x, y, width, height)

# def crop_image(self, x, y, width, height):
#     # 取得切割區域的座標和大小
#     crop_region = [x, y, width, height]
    
#     # 取得 DICOM 影像資料
#     dcm_reader = vtk.vtkDICOMImageReader()
#     dcm_reader.SetFileName(file_path)
#     dcm_reader.Update()
#     dcm_data = dcm_reader.GetOutput()
    
#     # 建立切割過濾器
#     crop_filter = vtk.vtkImageClip()
#     crop_filter.SetInputData(dcm_data)
#     crop_filter.SetOutputWholeExtent(*dcm_data.GetExtent())
#     crop_filter.SetClipData(True)
#     crop_filter.SetClipBox(crop_region)
#     crop_filter.Update()
    
#     # 取得切割後的影像
#     cropped_image = crop_filter.GetOutput()
    
#     # 儲存切割後的 DICOM 檔案
#     cropped_dcm = pydicom.dcmread(file_path)
#     cropped_dcm.PixelData = cropped_image.GetPointData().GetArray(0).tostring()
#     cropped_dcm.Rows, cropped_dcm.Columns = cropped_image.GetDimensions()
#     cropped_dcm.PixelSpacing = (dcm_reader.GetPixelSpacing()[0], dcm_reader.GetPixelSpacing()[1])
#     cropped_dcm.save_as(output_file_path)
    
# def view3positon(self, in_path):
#     if in_path:
#         self.ui.tabWidget.setCurrentIndex(2)  # 設定tabwidget到vtkwidget頁面
#         self.ui.stackedWidget_vtk.setCurrentIndex(1) # 設置按鈕介面至切片控制頁

#         # 若vtk視窗已被關閉就重啟一個
#         if self.vtkWidget is None:
#             self.vtkWidget = QVTKRenderWindowInteractor(self.ui.tab_vtkwidget)

#         self.vtkWidget.show()

#         # 設置dicom讀取器
#         reader = vtk.vtkDICOMImageReader()

#         # 刪除默認檔案
#         if os.path.exists(os.path.join(in_path, ".DS_Store")):
#             os.remove(os.path.join(in_path, ".DS_Store"))

#         # 設置dicom讀取器讀取位址
#         reader.SetDirectoryName(in_path)
#         # 更新dicom讀取器
#         reader.Update()

#         # 設定滑桿的範圍和初始值
#         num_slices = reader.GetOutput().GetDimensions()[2]
#         mid_slice = math.ceil(num_slices/2)
#         self.ui.horizontalSlider_slice_num.setMinimum(0)
#         self.ui.horizontalSlider_slice_num.setMaximum(num_slices - 1)
#         self.ui.horizontalSlider_slice_num.setValue(mid_slice)

#         # 創建渲染視窗和渲染器
#         renderWindow = vtkGenericRenderWindowInteractor()
#         self.renderer = vtk.vtkRenderer()
#         renderWindow.SetRenderWindow(self.vtkWidget.GetRenderWindow())
#         self.vtkWidget.SetRenderWindow(renderWindow.GetRenderWindow())

#         # 創建渲染視窗和渲染器
#         self.renderer_axial = vtk.vtkRenderer()
#         self.renderer_coronal = vtk.vtkRenderer()
#         self.renderer_sagittal = vtk.vtkRenderer()

#         # 2. Set up three different orientations
#         # Axial orientation
#         axial_position = reader.GetOutput().GetExtent()[5] // 2
#         self.axial = vtk.vtkImageSliceMapper()
#         self.axial.SetInputConnection(reader.GetOutputPort())
#         self.axial.SetSliceNumber(axial_position)
#         self.axial.Update()

#         # Coronal orientation
#         coronal_position = reader.GetOutput().GetExtent()[3] // 2
#         self.coronal = vtk.vtkImageSliceMapper()
#         self.coronal.SetInputConnection(reader.GetOutputPort())
#         self.coronal.SetSliceNumber(coronal_position)
#         self.coronal.Update()

#         # Sagittal orientation
#         sagittal_position = reader.GetOutput().GetExtent()[1] // 2
#         self.sagittal = vtk.vtkImageSliceMapper()
#         self.sagittal.SetInputConnection(reader.GetOutputPort())
#         self.sagittal.SetSliceNumber(sagittal_position)
#         self.sagittal.Update()

#         self.axial_actor = vtk.vtkImageActor()
#         self.axial_actor.SetMapper(self.axial)
#         self.axial_actor.SetPosition(0, 0, 0)

#         self.coronal_actor = vtk.vtkImageActor()
#         self.coronal_actor.SetMapper(self.coronal)
#         self.coronal_actor.SetPosition(0, 0, 0)

#         self.sagittal_actor = vtk.vtkImageActor()
#         self.sagittal_actor.SetMapper(self.sagittal)
#         self.sagittal_actor.SetPosition(0, 0, 0)

#         # 設定 vtkWidget 為 tab_vtkwidget 的中心部件
#         layout = QVBoxLayout(self.ui.tab_vtkwidget)
#         self.ui.tab_vtkwidget.setLayout(layout)

#         # 將圖像添加到渲染器並更新渲染視窗
#         self.renderer_axial.AddViewProp(self.axial_actor)
#         self.renderer_coronal.AddViewProp(self.coronal_actor)
#         self.renderer_sagittal.AddViewProp(self.sagittal_actor)

#         self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer_axial)
#         self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer_coronal)
#         self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer_sagittal)

#         self.vtkWidget.GetRenderWindow().Render()

#         # 連接滑桿值更改信號到槽函數
#         self.ui.horizontalSlider_slice_num.valueChanged.connect(self.updateSlice)

#         # 設定 vtkWidget 為 tab_vtkwidget 的中心部件
#         layout = QVBoxLayout(self.ui.tab_vtkwidget)
#         layout.addWidget(self.vtkWidget)
#         self.ui.tab_vtkwidget.setLayout(layout)


#         # 設定關閉視窗按鈕
#         self.ui.btn_close_dcm.setVisible(True)
#         self.ui.btn_close_dcm.clicked.connect(lambda: usevtk.vtkclose(self))  # 關閉按鈕連接關閉指令



