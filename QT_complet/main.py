import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QTableWidgetItem, QInputDialog
from PyQt5.QtGui import QIcon, QPalette, QBrush, QColor, QPen, QPainter
from PyQt5.QtWidgets import *
from test0301 import Ui_MainWindow
import vtk
import time
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkCommonTransforms import vtkTransform
import platform
import display
import datatransform
import data_augmentation
import st_model
import usevtk
import processdiocm
import os
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import oneshot
import getjson
import run_command
import style
import set_up
import openfile
import contorl
import display_dicom


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # set_up.install_request(self)
        self.setup_control()
        self.nifti_converter = processdiocm.nifti_2_dicom()
        contorl.home(self)
        
        self.list = [] # 用於動態新增

        # 設定vtk視窗，讓其顯示於tab_vtkwidget中
        self.vtkWidget = QVTKRenderWindowInteractor(self.ui.tab_vtkwidget, width=1000, height=801)
        # 設定vtk視窗，讓其顯示於tab_vtkwidget中
        self.vtkWidget_new = QVTKRenderWindowInteractor(self.ui.tab_vtkwidget, width=1000, height=841)

        # 設定vtk視窗，讓其顯示於tab_dicom中
        self.vtkWidget_dicom = QVTKRenderWindowInteractor(self.ui.tab_dicom, width=1000, height=801)
        # 設定vtk視窗，讓其顯示於tab_dicom中
        self.vtkWidget_dicom_1 = QVTKRenderWindowInteractor(self.ui.tab_dicom, width=1000, height=801)
        # 設定vtk視窗，讓其顯示於tab_dicom中
        self.vtkWidget_dicom_2 = QVTKRenderWindowInteractor(self.ui.tab_dicom, width=1000, height=801)
        # 設定vtk視窗，讓其顯示於tab_dicom中
        self.vtkWidget_dicom_3 = QVTKRenderWindowInteractor(self.ui.tab_dicom, width=1000, height=801)
        # 設定vtk視窗，讓其顯示於tab_dicom_zoom中
        self.vtkWidget_dicom_zoom = QVTKRenderWindowInteractor(self.ui.tab_dicom_zoom, width=1000, height=801)

        # 設定 VTK Widget 在 Z 軸上處於較低的位置
        self.vtkWidget_dicom.lower()
        self.vtkWidget_dicom_1.lower()
        self.vtkWidget_dicom_2.lower()
        self.vtkWidget_dicom_3.lower()
        self.vtkWidget_dicom_zoom.lower()

        # 設置初始渲染器為空值
        self.renderer = vtk.vtkRenderer()
        #設置背景讓他看起來透明
        hex_color_code = "#e5e5e5"  # 背景色的16進制顏色代碼
        r, g, b = tuple(int(hex_color_code[i:i+2], 16)/255.0 for i in (1, 3, 5))  # 將16進制的顏色代碼轉換為RGB顏色值
        self.renderer.SetBackground(r, g, b)  # 設定渲染器的背景色為16進制的顏色代碼所對應的RGB值
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)  # 在vtkwidget中新增渲染器

        self.renderer_new = None
        self.renderer_dicom = None

        # 設置mapper為空值
        self.mapper_1 = vtk.vtkPolyDataMapper()
        self.mapper_2 =None
        self.mapper_dicom =None
        self.mapper_dicom_seg =None
        self.mapper_dicom_3d =None

        self.actor = vtk.vtkActor()

        # 設定當前模型顯示狀態
        self.status = 0

        # 創建一個米白色的材質
        white = vtk.vtkNamedColors()
        whiteColor = white.GetColor3d('antiquewhite')  #顏色調整
        self.whiteProperty = vtk.vtkProperty()
        self.whiteProperty.SetColor(whiteColor)

        # 設定交互器，用來監聽鼠標的設定
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        # 建立點選器，並綁定到渲染器
        self.picker = vtk.vtkCellPicker()
        self.iren.SetPicker(self.picker)
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera()) # 變更模型移動方式
        self.iren.AddObserver("LeftButtonPressEvent", self.onMouseDown)
        # 連接vtkWidget的MouseMove事件到事件處理函数
        self.iren.AddObserver("MouseMoveEvent", self.mouseMoveEvent_)

        self.iren_new = self.vtkWidget_new.GetRenderWindow().GetInteractor()

        self.iren_dicom = self.vtkWidget_dicom.GetRenderWindow().GetInteractor()
        self.iren_dicom.SetInteractorStyle(vtk.vtkInteractorStyleImage())

        self.iren_dicom_zoom = self.vtkWidget_dicom_zoom.GetRenderWindow().GetInteractor()
        self.iren_dicom_zoom.SetInteractorStyle(vtk.vtkInteractorStyleImage())
        # 設定dicom_3d的渲染視窗和渲染器
        display_dicom.setup_dicom_3d(self)

        self.window_level_filter = vtk.vtkImageMapToWindowLevelColors()
        
        # self.iren.Initialize()
        
        # self.iren.AddObserver("LeftButtonPressEvent", self.on_left_button_press)
        # self.iren.AddObserver("LeftButtonReleaseEvent", self.on_left_button_release)

        # --------------------匡選畫線工具---------------------
        # self.scene = QGraphicsScene(self)
        # self.ui.graphicsView.setScene(self.scene)

        # self.ui.graphicsView.mousePressEvent = self.on_left_button_press
        # self.ui.graphicsView.mouseMoveEvent = self.on_mouse_move
        # self.ui.graphicsView.mouseReleaseEvent = self.on_left_button_release

        # 設定dicom影像匡選工具的起始與結束點
        self.start_point = None
        self.end_point = None
        self.rect_item = None
        self.rectangle = None
        # --------------------匡選畫線工具---------------------
    
        # -------------------針對各vtk視窗進行佈局---------------------
        #建立stl模型的vtk視窗
        self.layout = QtWidgets.QHBoxLayout(self.ui.tab_vtkwidget) # 建立一個水平佈局
        self.layout.addWidget(self.vtkWidget)

        # 建立dicom顯示之vtk視窗
        self.layout_dicom = QtWidgets.QVBoxLayout(self.ui.tab_dicom) # 建立一個垂直佈局
        layout_row_1 = QtWidgets.QHBoxLayout() # 建立第一排的水平佈局
        # 加入兩個vtk視窗到layout_row_1
        layout_row_1.addWidget(self.vtkWidget_dicom)
        layout_row_1.addWidget(self.vtkWidget_dicom_1)
        layout_row_2 = QtWidgets.QHBoxLayout()# 建立第二排的水平佈局
        # 加入兩個vtk視窗到layout_row_2
        layout_row_2.addWidget(self.vtkWidget_dicom_2)
        layout_row_2.addWidget(self.vtkWidget_dicom_3)
        # 把第一、第二排的水平佈局加入到垂直佈局中
        self.layout_dicom.addLayout(layout_row_1)
        self.layout_dicom.addLayout(layout_row_2)

        #建立放大的vtk視窗
        self.layout_row_zoom = QtWidgets.QHBoxLayout(self.ui.tab_dicom_zoom)
        self.layout_row_zoom.addWidget(self.vtkWidget_dicom_zoom)
        # -------------------針對各vtk視窗進行佈局---------------------
        
        self.ui.mean_reliability.textChanged.connect(self.update_button_text_mean_reliability)
        self.ui.top_persent.textChanged.connect(self.update_button_text_top_persent)
        self.ui.save_reliability_data_path.textChanged.connect(lambda: self.ui.btn_save_top_data.setEnabled(True))
        

        # 连接 itemClicked 信号到槽函数
        self.ui.checkpoint_lst.itemClicked.connect(self.on_item_clicked)

        
        # 設定隱藏物件
        contorl.set_hide(self)

        #設定所有btn形式
        self.set_stytle()

        if platform.system() == 'Darwin':
            self.ui.actionPredict.setEnabled(True)

        #設定開啟默認頁面
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.statusbar.showMessage("Ready!", 4500)

    def on_item_clicked(self, item):
        # 获取所点击的 item 的文本数据
        selected_item_text = item.text()
        self.ui.label_10.setVisible(True)
        self.ui.checkpoint_path.setVisible(True)
        self.ui.label_14.setVisible(True)
        self.ui.checkpoint_input_path.setVisible(True)
        self.ui.btn_checkpoint_input_path.setVisible(True)
        
        self.ui.checkpoint_path.setText(os.path.join(self.ui.result_path.toPlainText(), selected_item_text))
        print(f"Selected item: {selected_item_text}")

    def update_button_text_mean_reliability(self):
        self.ui.btn_mean_reliability.setEnabled(True)
        if self.ui.mean_reliability.toPlainText().strip():
            self.ui.btn_mean_reliability.setText(f"Auto Choose better than {self.ui.mean_reliability.toPlainText()}")
    
    def update_button_text_top_persent(self):
        self.ui.btn_top_persent.setEnabled(True)
        if self.ui.top_persent.toPlainText().strip():
            self.ui.btn_top_persent.setText(f"Select Top {self.ui.top_persent.toPlainText()}%")
            

    def mouseMoveEvent_(self, obj, event):
        # 取得鼠標在vtkWidget中的位置
        x, y = obj.GetEventPosition()
        # width, height = self.vtkWidget.GetRenderWindow().GetSize()
        # x = int(x * width)
        # y = int((1 - y) * height)

        # 更新statusBar文字
        self.ui.statusbar.showMessage(f"Mouse Position: X={int(x/2)}, Y={int(y/2)}", 1000)

    def onMouseDown(self, obj, event):
        # 取得鼠標點擊的位置
        click_pos = self.iren.GetEventPosition()

        self.picker.Pick(click_pos[0]/2, click_pos[1]/2, 0, self.renderer) # 除2才能轉換為vtkwidget正確的位置
        print("X:",click_pos[0]/2 ,"Y:",click_pos[1]/2)
        self.picker.AddPickList(self.actor)
        
        # 取得被點選的actor
        picked_actor = self.picker.GetActor()
        if picked_actor:
            print("鎖定目標")
            # 取得當前演員颜色
            current_color = picked_actor.GetProperty().GetDiffuseColor()
            # 取得當前ｒｇｂ值
            r = current_color[0]
            g = current_color[1]
            b = current_color[2]
            print(r,g,b)
            new_Property = vtk.vtkProperty()
            new_Property.SetColor(r-0.1, g-0.1, b-0.1)
            picked_actor.SetProperty(new_Property)

            actor_property = vtk.vtkProperty()
            dlg = QColorDialog(self)
            dlg.setCurrentColor(QtCore.Qt.white)
            # 添加自定義的顏色選項
            custom_colors = [QtGui.QColor(135, 206, 235),  # 天空藍
                            QtGui.QColor(235, 153, 153),  # 肉紅色
                            QtGui.QColor(0, 0, 255)]  # 蘭色

            for custom_color in custom_colors:
                dlg.setCustomColor(custom_colors.index(custom_color), custom_color)
            if dlg.exec_():
                # Set actor color
                color = dlg.selectedColor()
            actor_property.SetColor(color.redF(), color.greenF(), color.blueF())
            actor_property.SetOpacity(int(self.ui.opacity_level.text()) / 100)
            picked_actor.SetProperty(actor_property)
            actor_property = picked_actor
            self.vtkWidget.GetRenderWindow().Render()
        return
    
    #-----------------------選取方匡繪製-----------------------
    # def on_left_button_press(self, event):
    #     click_pos = event.pos()
    #     scene_pos = self.ui.graphicsView.mapToScene(click_pos)
    #     self.start_point = scene_pos
    #     print(self.start_point.x(), self.start_point.y())
        
    # def on_left_button_release(self, event):
    #     click_pos = event.pos()
    #     scene_pos = self.ui.graphicsView.mapToScene(click_pos)
    #     self.end_point = scene_pos
    #     print(self.end_point.x(), self.end_point.y())
        
    #     display_dicom.draw_rectangle(self)

    # def on_mouse_move(self, event):
    #     if self.start_point is not None:
    #         if self.rectangle:
    #             self.scene.removeItem(self.rectangle)
    #             self.rectangle = None
    #         click_pos = event.pos()
    #         scene_pos = self.ui.graphicsView.mapToScene(click_pos)
    #         # 更新矩形項目的座標和大小
    #         x = min(self.start_point.x(), scene_pos.x())
    #         y = min(self.start_point.y(), scene_pos.y())
    #         width = abs(scene_pos.x() - self.start_point.x())
    #         height = abs(scene_pos.y() - self.start_point.y())
    #         pen = QPen(QColor(255, 0, 0,200))  # 設定筆刷顏色為紅色
    #         pen.setWidth(2)  # 設定筆刷寬度為2
    #         pen.setCosmetic(True)  # 設定筆刷為 cosmetic style，以便適應變換

            
    #         brush = QBrush(QtCore.Qt.NoBrush)  # 設定填滿方式為無填滿
            
    #         self.rectangle = self.scene.addRect(x, y, width, height, pen, brush)  # 在場景中新增方框
    #-----------------------選取方匡繪製-----------------------

    #設定GUI's style
    def set_stytle(self):
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QtCore.Qt.white)
        self.ui.enterimagets.setPalette(palette)
        self.ui.enteroutput.setPalette(palette)
        self.ui.enteroutput_3D.setPalette(palette)
        self.ui.set_smooth_level.setPalette(palette)
        self.ui.smooth_level.setPalette(palette)
        self.ui.current_Threshold.setPalette(palette)

    def updatethreshold(self, value):
        self.threshold_values = value
        self.surface.SetValue(0, self.threshold_values)    
        self.surface.Update() # 執行Marching Cubes演算法，生成表面
        # 創建顏色色組
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)  # RGB颜色
        colors.SetName("Colors")

        # 設定所有点的颜色
        for j in range(self.surface.GetOutput().GetNumberOfPoints()):
            # 根據罰值設定颜色
            if self.threshold_values < 30:
                colors.InsertNextTuple3(255, 214, 170)  # 肉色
            else:
                colors.InsertNextTuple3(190, 190, 190)  # 骨白色

        # 將顏色資料與 vtkPolyData 綁定
        self.surface.GetOutput().GetPointData().SetScalars(colors)
        self.surface.Update()

        self.triangles.SetInputConnection(self.surface.GetOutputPort())  # 將 Marching Cubes 的輸出連接到 Triangle Filter
        self.triangles.Update()  # 更新Triangle Filter

        # 取得三角形數量
        number_of_triangles = self.triangles.GetOutput().GetNumberOfCells()
        self.ui.statusbar.showMessage("number_of_triangles:%d"%number_of_triangles, 4500)

        self.vtkWidget_dicom_1.GetRenderWindow().Render()
        self.vtkWidget_dicom_zoom.GetRenderWindow().Render()
    
    def updateSlice_raw(self, value):
        # 更新顯示的切片
        slice = value
        self.mapper_dicom.SetSliceNumber(slice)

        if self.mapper_dicom_seg:
            self.mapper_dicom_seg.SetSliceNumber(slice)
        self.vtkWidget_dicom.GetRenderWindow().Render()
        self.vtkWidget_dicom_zoom.GetRenderWindow().Render()
    
    def updateSlice_coronal(self, value):
        # 更新顯示的切片
        slice = value
        self.resliceAxes_coronal.SetElement(1, 3, slice* self.spacing[1]) # self.center2 + slice* self.spacing[1]
       
        if self.mapper_dicom_seg:
            self.mapper_dicom_seg.SetSliceNumber(slice)
        
        self.vtkWidget_dicom_2.GetRenderWindow().Render()
        self.vtkWidget_dicom_zoom.GetRenderWindow().Render()
        

    def updateSlice_sagitta(self, value):
        # 更新顯示的切片
        slice = value
        self.mapper_dicom.SetSliceNumber(slice)
        self.resliceAxes_sagitta.SetElement(0, 3, slice* self.spacing[0]) # self.center1 + slice * self.spacing[0]

        if self.mapper_dicom_seg:
            self.mapper_dicom_seg.SetSliceNumber(slice)
        self.vtkWidget_dicom_3.GetRenderWindow().Render()
        self.vtkWidget_dicom_zoom.GetRenderWindow().Render()
    
    def on_window_slider_value_changed(self, value):
        # 當Level值的滑桿數值改變時，設定window_level_filter的window值
        self.window_level_filter.SetWindow(value)
        # 更新vtk pipeline，使更改生效
        self.window_level_filter.Update()

        # 更新顯示的切片
        self.mapper_dicom.Update()
        if self.mapper_dicom_seg:
            self.mapper_dicom_seg.Update()
        self.vtkWidget_dicom.GetRenderWindow().Render()  
        self.vtkWidget_dicom_2.GetRenderWindow().Render()
        self.vtkWidget_dicom_3.GetRenderWindow().Render()
        self.vtkWidget_dicom_zoom.GetRenderWindow().Render()
    
    def on_level_slider_value_changed(self, value):
        # 當Level值的滑桿數值改變時，設定window_level_filter的Level值
        self.window_level_filter.SetLevel(value)
        # 更新vtk pipeline，使更改生效
        self.window_level_filter.Update()

        # 更新顯示的切片
        self.mapper_dicom.Update()
        if self.mapper_dicom_seg:
            self.mapper_dicom_seg.Update()
        self.vtkWidget_dicom.GetRenderWindow().Render() 
        self.vtkWidget_dicom_2.GetRenderWindow().Render()
        self.vtkWidget_dicom_3.GetRenderWindow().Render()   
        self.vtkWidget_dicom_zoom.GetRenderWindow().Render()   

    def on_opacity_level_slider_value_changed(self, value):

        # 取得當前演員颜色
        current_color = self.actor.GetProperty().GetDiffuseColor()

        # 取得當前ｒｇｂ值
        r = current_color[0]
        g = current_color[1]
        b = current_color[2]
        
        new_Property = vtk.vtkProperty()
        new_Property.SetColor(r, g, b)
        new_Property.SetOpacity(value/100)
        # 更新顯示的切片
        self.actor.SetProperty(new_Property)
        self.renderer.AddActor(self.actor)
        self.vtkWidget.GetRenderWindow().Render()
    
    



    def setup_control(self):
        # -------------------------------------------------------目錄頁button-------------------------------------------------------------    
        self.ui.btn_cropdicom.clicked.connect(lambda: processdiocm.dicomcrop(self))
        self.ui.btn_resampledicom.clicked.connect(lambda: processdiocm.resample_q(self))
        self.ui.btn_dicom2nii.clicked.connect(lambda: datatransform.dcm_to_nii_q(self))
        self.ui.btn_nii2dicom.clicked.connect(lambda: datatransform.nii_to_dcm_q(self))

        self.ui.btn_viewdicom.clicked.connect(lambda: display_dicom.view(self, openfile.get_folder(self, "開啟Dicom資料夾")))
        self.ui.btn_viewnii.clicked.connect(lambda: display.read_nii(self))

        self.ui.btn_3d_reconstruction.clicked.connect(lambda: usevtk.vtk_3d(self, openfile.get_folder(self, "開啟Dicom資料夾")))
        self.ui.btn_openmodel.clicked.connect(lambda: usevtk.view(self, openfile.open_stl_data(self,"請選擇stl模型檔")))
        self.ui.btn_smooth.clicked.connect(lambda: usevtk.modelsmooth(self))
        
        

        # self.ui.btn_DCM_resample.clicked.connect(lambda: processdiocm.resample_itk(self, 2))
        # self.ui.btn_getjson.clicked.connect(lambda: getjson.make_json(self))
        # self.ui.btn_open_NII.clicked.connect(lambda: display.read_nii(self))
        # self.ui.btn_dicom_info.clicked.connect(lambda: processdiocm.dcminfo(self))
        # self.ui.btn_calculatearea.clicked.connect(lambda: usevtk.vtkcalculatearea_campare_singel(self))
        # self.ui.btn_cropdicom.clicked.connect(lambda: processdiocm.dicomcrop(self))
        # self.ui.btn_drawloss.clicked.connect(lambda: display.lossimage(self))
        self.ui.btn_add_model.clicked.connect(lambda: usevtk.add_model(self))
        self.ui.btn_new_model.clicked.connect(lambda: usevtk.new_model(self))

        # 疊加標註影像
        self.ui.btn_add_dcm_seg.clicked.connect(lambda: display_dicom.add_seg(self))
        self.ui.btn_display_single_slice.clicked.connect(lambda: display_dicom.display_slice(self, self.in_path))
        # self.ui.btn_capture.toggled.connect(lambda: self.detection_mouse())
        
        # -------------------------------------------------------以下為選單列-------------------------------------------------------------
        # self.ui.menubar.enterEvent = lambda event: self.ui.stackedWidget.setCurrentIndex(0)

        # dicom process
        # -- display dicom
        self.in_path = ""
        self.ui.actionDisplay_Dicom.triggered.connect(lambda: display_dicom.view(self, openfile.get_folder(self, "開啟Dicom資料夾")))
        self.ui.checkBox_see_3d.stateChanged.connect(lambda: display_dicom.dicom_3d(self,self.in_path))
        # -- resample
        self.ui.actionhalf.triggered.connect(lambda: processdiocm.resample_itk(self, 2))  # half
        self.ui.action1_3.triggered.connect(lambda: processdiocm.resample_itk(self, 3))  # 1/3
        self.ui.action1_4.triggered.connect(lambda: processdiocm.resample_itk(self, 4))  # 1/4
        # -- corp
        self.ui.actioncorp.triggered.connect(lambda: processdiocm.dicomcrop(self))
        # -- format converter
        self.ui.actionDP_D2N_Entry_Folder.triggered.connect(lambda: datatransform.dcm_to_nii_all(self))  # dicom 2 nii whole folder
        self.ui.actionDP_N2D_Entry_Folder.triggered.connect(lambda: datatransform.nii_2_dcm_convert_all(self))  # nii 2 dicom whole folder
        self.ui.actionDP_D2N_Single_Data.triggered.connect(lambda: datatransform.dcm_to_nii(self))  # dicom 2 nii single data
        self.ui.actionDP_N2D_Single_Data.triggered.connect(lambda: datatransform.nii_2_dcm_convert_single(self))  # nii 2 dicom single data
        # -- view Manufacturer
        self.ui.actionView_Meanufeter.triggered.connect(lambda: processdiocm.dcminfo(self))        

        # To make Task Dir
        # -- Generate Json
        self.ui.actionGenerate_Json.triggered.connect(lambda: getjson.make_json(self))
        # -- dicom 2 nii
        self.ui.actiontmtd_Entry_Folder.triggered.connect(lambda: datatransform.dcm_to_nii_all(self))  # dicom 2 nii whole folder
        self.ui.actiontmtd_Single_data.triggered.connect(lambda: datatransform.dcm_to_nii(self))  # dicom 2 nii single data
        # -- read nii
        self.ui.actionRead_NIFTI.triggered.connect(lambda: display.read_nii(self))

        # 3D construction
        # -- Create 3D Mode
        self.ui.actionCreat_3D_Model.triggered.connect(lambda: usevtk.vtk_3d(self))
        # -- Model Smoothing
        self.ui.actionModel_Smoothing.triggered.connect(lambda: usevtk.modelsmooth(self))

        # Compare Result
        # -- read nii
        self.ui.actionView_NIFTI.triggered.connect(lambda: display.read_nii(self))
        # -- view 3D model
        self.ui.actionView_3D_model.triggered.connect(lambda: usevtk.openstl(self))
        # -- calculate difference into raw and prediction
        self.ui.actionSingle.triggered.connect(lambda: usevtk.vtkcalculatearea_campare_singel(self))
        # -- calculate difference into raw and prediction(whole folder)
        self.ui.actionBatch.triggered.connect(lambda: usevtk.vtkcalculatearea_campare_batch(self))
        # -- calculate 3Dmodel
        self.ui.actionCalculate_Model.triggered.connect(lambda: usevtk.vtkcalculatearea(self))
        # --draw loss function image
        self.ui.actionDraw_LossImage.triggered.connect(lambda: display.single_getloss_draw(self, openfile.openfile(self, "開啟整體txt檔案")))

        # nnU-Net
        # preprocess
        self.ui.actionPreprocess.triggered.connect(lambda: run_command.preprocess(self, "convert"))
        # train
        self.ui.actionTrain.triggered.connect(lambda: run_command.preprocess(self, "train"))
        # predict
        self.ui.actionPredict.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.btn_imagets.clicked.connect(lambda: openfile.in_folder_imagsts(self))
        self.ui.btn_inferstr.clicked.connect(lambda: openfile.out_folder_inferstr(self))
        self.ui.btn_go_predict.clicked.connect(lambda: run_command.nnunet_infer(self, self.ui.imagets_path.toPlainText(), self.ui.inferstr_path.toPlainText()))
        self.ui.checkBox_generate_model.stateChanged.connect(lambda: contorl.checkbox_generate_model_changed(self))
        self.ui.btn_model.clicked.connect(lambda: openfile.in_folder_model(self))

        

        # ST++ Model
        self.ui.actionGet_nifti_in_Folder.triggered.connect(lambda: st_model.get_nifti_infolder(self, openfile.get_folder(self, "開啟模型result檔案"), openfile.get_folder(self, "選擇輸出資料夾")))
        # -- TXT process
        self.ui.actionOne_txt_.triggered.connect(lambda: display.single_getloss_draw(self, openfile.openfile(self, "開啟整體txt檔案")))
        self.ui.actionMul_txt_.triggered.connect(lambda: display.mul_getloss_draw(self, openfile.get_folder(self, "開啟整體txt檔案"), openfile.get_folder(self, "選擇輸出資料夾")))
        self.ui.actionCompare_Difference.triggered.connect(lambda: display.run_2_difference(self, openfile.openfile(self, "開啟 Before 整體txt檔案")))

        # -- Data_Augmentation
        self.ui.actionWDA_.triggered.connect(lambda: data_augmentation.conduct_all_WDA(self))
        self.ui.actionS_WDA_.triggered.connect(lambda: data_augmentation.conduct_all_SWDA(self))
        self.ui.actionsingle_display_.triggered.connect(lambda: data_augmentation.choice(self))
        # -- Calculate reliabilty
        self.ui.actionCalculate_Reliability.triggered.connect(lambda: st_model.set_up_reliability_window(self))
        self.ui.actionDo_it.triggered.connect(lambda: st_model.set_up_predict_checkpoint(self))

        # ------- 設定路徑位址按鈕連動-------
        self.ui.btn_gt_path.clicked.connect(lambda: st_model.open_gt_folder(self, openfile.get_folder(self))) # 開啟資料夾(btn_gt_path)
        self.ui.btn_pseudo_path.clicked.connect(lambda: st_model.open_pseudo_folder(self, openfile.get_folder(self))) # 開啟資料夾(btn_pseudo_path)
        self.ui.btn_save_reliability_data_path.clicked.connect(lambda: st_model.open_out_folder(self)) # 開啟資料夾(btn_save_reliability_data_path)
        self.ui.btn_result_folder.clicked.connect(lambda: st_model.open_result_folder(self, openfile.get_folder(self))) # 開啟資料夾(btn_gt_path)
        self.ui.btn_checkpoint_output_path.clicked.connect(lambda: st_model.open_out_folder_checkpont(self))
        self.ui.btn_checkpoint_input_path.clicked.connect(lambda: st_model.open_in_folder_checkpont(self))
        self.ui.btn_images_tr_path.clicked.connect(lambda: st_model.open_tr_folder(self))
        self.ui.btn_oversample_path.clicked.connect(lambda: st_model.open_out_folder_oversample(self))
        self.ui.btn_labels_tr_path.clicked.connect(lambda: st_model.open_label_tr_folder(self))
        # ------- 設定路徑位址按鈕連動-------

        #設定當滑桿狀態改變時
        self.ui.checkBox_smooth_model.stateChanged.connect(lambda: contorl.checkbox_smooth_model_changed(self))
        self.ui.checkBox_save_excel.stateChanged.connect(lambda: contorl.checkBox_save_excel_changed(self))
        #self.ui.horizontalSlider_smooth_level.valueChanged.connect(lambda value: self.ui.smooth_level.setText(str(value)))
        
        # 設定Slider與lineEdit綁定
        # 將QSlider的valueChanged信號連接到槽函數
        self.ui.horizontalSlider_smooth_level.valueChanged.connect(lambda: contorl.sliderMoved(self, "smoothing"))
        # 將QlineEdit的textChanged信號連接到另一個槽函數
        self.ui.smooth_level.textChanged.connect(lambda: contorl.textChanged(self,"smoothing"))
        
        # 將QSlider的valueChanged信號連接到槽函數
        self.ui.horizontalSlider_threshold .valueChanged.connect(lambda: contorl.sliderMoved(self, "slice"))
        # 將QlineEdit的textChanged信號連接到另一個槽函數
        self.ui.threshold.textChanged.connect(lambda: contorl.textChanged(self, "slice"))

        # 將QSlider的valueChanged信號連接到槽函數
        self.ui.horizontalSlider_window .valueChanged.connect(lambda: contorl.sliderMoved(self, "window"))
        # 將QlineEdit的textChanged信號連接到另一個槽函數
        self.ui.value_window.textChanged.connect(lambda: contorl.textChanged(self, "window"))

        # 將QSlider的valueChanged信號連接到槽函數
        self.ui.horizontalSlider_level .valueChanged.connect(lambda: contorl.sliderMoved(self, "level"))
        # 將QlineEdit的textChanged信號連接到另一個槽函數
        self.ui.value_level.textChanged.connect(lambda: contorl.textChanged(self, "level"))

        # 將QSlider的valueChanged信號連接到槽函數
        self.ui.horizontalSlider_opacity_level .valueChanged.connect(lambda: contorl.sliderMoved(self, "opacity"))
        # 將QlineEdit的textChanged信號連接到另一個槽函數
        self.ui.opacity_level.textChanged.connect(lambda: contorl.textChanged(self, "opacity"))
        

        # 隱藏按鈕
        # 設定選擇按鈕指令
        self.ui.btn_exchange_model.clicked.connect(lambda: run_command.choose_to_display(self, self.ui.inferstr_path.toPlainText()))
        
        # Help information
        #self.ui.actionHome.triggered.connect(lambda: contorl.home(self))
        self.ui.actionHome.triggered.connect(lambda: contorl.home(self))
        
        #test
        self.ui.actionTest.triggered.connect(lambda: usevtk.overlap(self))
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon/application_office_word_proccesser_12788.png"))
    # app.setStyle('windows')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
