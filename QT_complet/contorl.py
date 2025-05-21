from PyQt5.QtGui import QPixmap
import vtk
# ----------------------回主要頁面----------------------
def home (self):
    self.ui.tabWidget.setCurrentIndex(0)
    self.ui.cmdlabel.setText("")
    self.ui.label.setPixmap(QPixmap("icon/5.png"))
    self.ui.stackedWidget.setCurrentIndex(0)
    self.ui.btn_close_vtk.setVisible(True)
    self.ui.checkBox_see_3d.setCheckState(0)
    # self.ui.btn_new_model.setVisible(False)
    self.ui.btn_add_model.setVisible(True)
    self.ui.btn_new_model.setEnabled(True)
    # self.ui.btn_exchange_model.setVisible(False)
    self.ui.btn_overlap.setVisible(False)
    self.ui.btn_overlap.setEnabled(True)
    self.ui.btn_get_3dmodel.setVisible(False)
    self.ui.horizontalSlider_dicom_zoom_raw.setVisible(False)
    self.ui.horizontalSlider_dicom_zoom_coronal.setVisible(False)
    self.ui.horizontalSlider_dicom_zoom_sagitta.setVisible(False)
    # self.ui.checkBox_smooth.setVisible(False)
    # self.ui.checkBox_hole.setVisible(False)
    # 在適當的位置添加以下程式碼以關閉 VTK 視窗並停止事件循環
    #self.iren.ExitCallback()
# ----------------------回主要頁面----------------------

def clear_dicom(self):
    self.renderer_dicom_3d.RemoveActor(self.actor)
    self.renderer_dicom_3d.RemoveAllLights()
    self.renderer_dicom_coronal.RemoveAllViewProps()
    self.renderer_dicom_coronal.RemoveAllLights()
    self.renderer_dicom_sagitta.RemoveAllViewProps()
    self.renderer_dicom_sagitta.RemoveAllLights()
    self.ui.checkBox_see_3d.setCheckState(0)

def clear_vtk(self):
    # 從渲染器中刪除演員
    self.renderer.RemoveActor(self.actor)
    self.renderer.RemoveAllViewProps()
    self.renderer.RemoveAllLights()
    self.renderer_dicom_3d.RemoveActor(self.actor)
    self.renderer_dicom_3d.RemoveAllLights()

    self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renderer)
    
    # 重新初始化渲染器
    self.renderer = vtk.vtkRenderer()
    #設置背景讓他看起來透明
    hex_color_code = "#e5e5e5"  # 背景色的16進制顏色代碼
    r, g, b = tuple(int(hex_color_code[i:i+2], 16)/255.0 for i in (1, 3, 5))  # 將16進制的顏色代碼轉換為RGB顏色值
    self.renderer.SetBackground(r, g, b)  # 設定渲染器的背景色為16進制的顏色代碼所對應的RGB值
    
    # 將渲染器添加回渲染窗口
    self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
    
    # 重置相機並重新渲染場景
    self.renderer.ResetCamera()
    self.vtkWidget.GetRenderWindow().Render()


# ----------------------設定slider與數值的連接----------------------
def sliderMoved(self, obeject):
    if obeject=="smoothing": # 當物件為smoothing時
        # 將QTextEdit的值設置為QSlider的值
        self.ui.smooth_level.setText(str(self.ui.horizontalSlider_smooth_level.value()))
    elif obeject=="slice": # 當物件為slice時
        # 將QTextEdit的值設置為QSlider的值
        self.ui.threshold.setText(str(self.ui.horizontalSlider_threshold.value()))
    elif obeject=="window": # 當物件為window時
        # 將QTextEdit的值設置為QSlider的值
        self.ui.value_window.setText(str(self.ui.horizontalSlider_window.value()))
    elif obeject=="level": # 當物件為level時
        # 將QTextEdit的值設置為QSlider的值
        self.ui.value_level.setText(str(self.ui.horizontalSlider_level.value()))
    elif obeject=="opacity": # 當物件為level時
        # 將QTextEdit的值設置為QSlider的值
        self.ui.opacity_level.setText(str(self.ui.horizontalSlider_opacity_level.value()))

# 設定與滑桿連接之數值  
def textChanged(self, obeject):
    if obeject=="smoothing": # 當物件為smoothing時
        try:
            value = self.ui.smooth_level.text() # 設置變數value等於lineEdit上的值
            value = int(value)
        except ValueError:
            return
        # 將數值映射到滑桿的範圍內
        min_value = self.ui.horizontalSlider_smooth_level.minimum() # 設置滑桿的最小值
        max_value = self.ui.horizontalSlider_smooth_level.maximum() # 設置華感得最大值
        value = min(max(value, min_value), max_value) # 確保值會在最大值與最小值之間
        # 將數值設置為滑桿的值
        self.ui.horizontalSlider_smooth_level.setValue(value)

    if obeject=="slice": # 當物件為slice時
        try:
            value = self.ui.threshold.text() # 設置變數value等於lineEdit上的值
            value = int(value)
        except ValueError:
            return
        # 將數值映射到滑桿的範圍內
        min_value = self.ui.horizontalSlider_threshold.minimum()
        max_value = self.ui.horizontalSlider_threshold.maximum()
        value = min(max(value, min_value), max_value)
        # 將數值設置為滑桿的值
        self.ui.horizontalSlider_threshold.setValue(value)
    
    if obeject=="window": # 當物件為window時
        try:
            value = self.ui.value_window.text() # 設置變數value等於lineEdit上的值
            value = int(value)
        except ValueError:
            return
        # 將數值映射到滑桿的範圍內
        min_value = self.ui.horizontalSlider_window.minimum()
        max_value = self.ui.horizontalSlider_window.maximum()
        value = min(max(value, min_value), max_value)
        # 將數值設置為滑桿的值
        self.ui.horizontalSlider_window.setValue(value)

    if obeject=="level": # 當物件為level時
        try:
            value = self.ui.value_level.text() # 設置變數value等於lineEdit上的值
            value = int(value)
        except ValueError:
            return
        # 將數值映射到滑桿的範圍內
        min_value = self.ui.horizontalSlider_level.minimum()
        max_value = self.ui.horizontalSlider_level.maximum()
        value = min(max(value, min_value), max_value)
        # 將數值設置為滑桿的值
        self.ui.horizontalSlider_level.setValue(value)

    if obeject=="opacity": # 當物件為opacity時
        try:
            value = self.ui.opacity_level.text() # 設置變數value等於lineEdit上的值
            value = int(value)
        except ValueError:
            return
        # 將數值映射到滑桿的範圍內
        min_value = self.ui.horizontalSlider_opacity_level.minimum()
        max_value = self.ui.horizontalSlider_opacity_level.maximum()
        value = min(max(value, min_value), max_value)
        # 將數值設置為滑桿的值
        self.ui.horizontalSlider_opacity_level.setValue(value)
# ----------------------設定slider與數值的連接----------------------


# ----------------------偵測checkbox事件----------------------
#偵測是否勾選儲存3D model後
def checkbox_generate_model_changed(self):
    if self.ui.checkBox_generate_model.isChecked():
        self.ui.enteroutput_3D.setVisible(True)
        self.ui.model_path.setVisible(True)
        self.ui.btn_model.setVisible(True)
    else:
        self.ui.enteroutput_3D.setVisible(False)
        self.ui.model_path.setVisible(False)
        self.ui.btn_model.setVisible(False)
        self.ui.model_path.setText("")

#偵測是否勾選平滑化後
def checkbox_smooth_model_changed(self):
    if self.ui.checkBox_smooth_model.isChecked():
        self.ui.horizontalSlider_smooth_level.setVisible(True)
        self.ui.set_smooth_level.setVisible(True)
        self.ui.smooth_level.setVisible(True)
    else:
        self.ui.horizontalSlider_smooth_level.setVisible(False)
        self.ui.set_smooth_level.setVisible(False)
        self.ui.smooth_level.setVisible(False)
        #將line edit設置為空
        self.ui.smooth_level.setText("")
        self.ui.horizontalSlider_smooth_level.setValue(0)

#偵測是否勾選excel檔案存檔
def checkBox_save_excel_changed(self):
    if self.ui.checkBox_save_excel.isChecked():
        self.ui.label_4.setVisible(True)
        self.ui.save_path.setVisible(True)
        self.ui.btn_save_path.setVisible(True)
        self.ui.background_excel.setVisible(True)
    else:
        self.ui.label_4.setVisible(False)
        self.ui.save_path.setVisible(False)
        self.ui.btn_save_path.setVisible(False)
        self.ui.background_excel.setVisible(False)
# ----------------------偵測checkbox事件----------------------

# ----------------------設置隱藏按鈕----------------------
def set_hide(self):
    # 設定關閉vtk視窗按鈕：不顯示
    self.ui.btn_close_vtk.setVisible(False)
    # 設定關閉vtk視窗按鈕：不顯示
    self.ui.btn_exchange_model.setVisible(False)
    self.ui.btn_add_model.setVisible(False)
    self.ui.enteroutput_3D.setVisible(False)
    self.ui.model_path.setVisible(False)
    self.ui.btn_model.setVisible(False)
    self.ui.btn_overlap.setVisible(False)
    self.ui.horizontalSlider_smooth_level.setVisible(False)
    self.ui.set_smooth_level.setVisible(False)
    self.ui.smooth_level.setVisible(False)
# ----------------------設置隱藏按鈕----------------------