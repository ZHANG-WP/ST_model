import vtk
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets,QtCore,QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import *
from pathlib import Path
from PyQt5.QtCore import Qt
import os
import main
import subprocess
import contorl
import pandas as pd
import random
import openfile
import set_up
import platform

def calculate_campare(input_1, input_2):
    # 創建stl讀取器 : reader1
    reader1 = vtk.vtkSTLReader()
    reader1.SetFileName(input_1)
    reader1.Update()

    # 創建stl讀取器 : reader2
    reader2 = vtk.vtkSTLReader()
    reader2.SetFileName(input_2)
    reader2.Update()

    # 計算小三角形面積_1
    triangleFilter1 = vtk.vtkTriangleFilter()
    triangleFilter1.SetInputData(reader1.GetOutput()) # 設定輸入為讀取器1的輸出
    triangleFilter1.Update()

    # 計算小三角形面積_2
    triangleFilter2 = vtk.vtkTriangleFilter()
    triangleFilter2.SetInputData(reader2.GetOutput()) # 設定輸入為讀取器2的輸出
    triangleFilter2.Update()

    # 計算表面積1
    mass1 = vtk.vtkMassProperties()
    mass1.SetInputConnection(triangleFilter1.GetOutputPort()) # 設定輸入為小三角形面積_1的輸出
    mass1.Update()

    # 計算表面積2
    mass2 = vtk.vtkMassProperties()
    mass2.SetInputConnection(triangleFilter2.GetOutputPort()) # 設定輸入為小三角形面積_2的輸出
    mass2.Update()

    # 計算模型的體積1
    mass_v1 = vtk.vtkMassProperties()
    mass_v1.SetInputData(reader1.GetOutput()) # 設定輸入為讀取器1的輸出
    mass_v1.Update()

    # 計算模型的體積2
    mass_v2 = vtk.vtkMassProperties()
    mass_v2.SetInputData(reader2.GetOutput()) # 設定輸入為讀取器2的輸出
    mass_v2.Update()

    raw_vol = round(mass_v1.GetVolume(),3) # 將原始體積取到小數點第三位
    raw_surf = round(mass1.GetSurfaceArea(),3) # 將原始表面積取到小數點第三位
    pre_vol = round(mass_v2.GetVolume(),3) # 將預測體積取到小數點第三位
    pre_surf = round(mass2.GetSurfaceArea(),3) # 將預測表面積取到小數點第三位
    difference_volume = round(abs(mass_v1.GetVolume() - mass_v2.GetVolume()) / mass_v1.GetVolume() * 100, 4) # 計算兩者的體積誤差
    difference_surf = round(abs(mass1.GetSurfaceArea() - mass2.GetSurfaceArea()) / mass1.GetSurfaceArea() * 100, 4) # 計算兩者的表面積誤差
    
    #self.ui.statusbar.showMessage("體積相差 : "+ str(difference_volume) + "%, 表面積相差 : " + str(difference_surf) + "%")
    return raw_vol, raw_surf, pre_vol, pre_surf, difference_volume, difference_surf # 回傳所有計算值

def vtkcalculatearea_campare_batch(self):
    contorl.home(self)
    self.ui.tabWidget.setCurrentIndex(3)  # 設定tabwidget到tab_process頁面

    # ------- 設定各值得初始值-------
    self.ui.manual_data_lst.setText("")
    self.ui.predict_data_lst.setText("")
    self.ui.manual_path.setText("")
    self.ui.predict_path.setText("")
    # ------- 設定各值得初始值-------

    # -------設定頁面初始狀態，讓一些依不同階段進行顯示之功能關閉-------
    self.ui.label_3.setVisible(False)
    self.ui.btn_openexcel.setVisible(False)
    self.ui.btn_home.setVisible(False)
    self.ui.btn_calculate.setVisible(False)
    self.ui.checkBox_save_excel.setVisible(False)
    self.ui.label_4.setVisible(False)
    self.ui.save_path.setVisible(False)
    self.ui.btn_save_path.setVisible(False)
    self.ui.manual_data_lst.setVisible(False)
    self.ui.predict_data_lst.setVisible(False)
    self.ui.df_display.setVisible(False)
    self.ui.background_excel.setVisible(False)
    self.ui.background_open.setVisible(False)
    # -------設定頁面初始狀態，讓一些依不同階段進行顯示之功能關閉-------

    def open_manual_folder(input_folder):
        if input_folder:
            self.ui.manual_data_lst.setText("")
            files = os.listdir(input_folder) # 讀取input_foldery資料夾內資料
            first_data = os.path.join(input_folder, files[0]) # 設定first_data為input_foldery資料夾內第一筆資料

            if ".stl" in first_data: # 如果frist_data為stl檔案
                self.ui.manual_path.setText(input_folder) # 設定manual_path顯示資料夾之路徑

                # 刪除mac默認檔
                if os.path.exists(os.path.join(input_folder,".DS_Store")): 
                    os.remove(os.path.join(input_folder,".DS_Store"))

                self.ui.statusbar.showMessage("Loading : " + input_folder) # 狀態列顯示
                stl_files = sorted(os.listdir(input_folder)) # 將資料夾內部資料案名稱順序進行排序

                # 設定manual_data_lst顯示排序後資料
                for i in range(len(stl_files)):
                    self.ui.manual_data_lst.setText(self.ui.manual_data_lst.text() + str(i+1)+ '. ' + '[' + str(stl_files[i]) + ']' + '   ') 

                self.ui.manual_data_lst.setVisible(True) # 開啟manual_data_lst顯示

                # 如果predict_data_lst中已有文字，開啟計算按鈕與確認是否存檔
                if self.ui.predict_data_lst.text().strip(): 
                    self.ui.btn_calculate.setVisible(True)
                    self.ui.checkBox_save_excel.setVisible(True)
            else: 
                QMessageBox.about(self, "Erro", "Open the correct .stl folder, Pleace!")
        else:
            return

    def open_predict_folder(input_folder):
        if input_folder:
            self.ui.predict_data_lst.setText("")
            files = os.listdir(input_folder) # 讀取input_foldery資料夾內資料
            first_data = os.path.join(input_folder, files[0]) # 設定first_data為input_foldery資料夾內第一筆資料
            if ".stl" in first_data: # 如果frist_data為stl檔案
                self.ui.predict_path.setText(input_folder) #設定predict_path顯示資料夾之路徑
                # 刪除mac默認檔
                if os.path.exists(os.path.join(input_folder,".DS_Store")): 
                    os.remove(os.path.join(input_folder,".DS_Store"))
                
                self.ui.statusbar.showMessage("Loading : " + input_folder) # 狀態列顯示
                stl_files = sorted(os.listdir(input_folder)) # 將資料夾內部資料案名稱順序進行排序

                # 設定predict_data_lst顯示排序後資料
                for i in range(len(stl_files)):
                    self.ui.predict_data_lst.setText(self.ui.predict_data_lst.text() + str(i+1)+ '. ' + '[' + str(stl_files[i]) + ']' + '    ') 
                
                self.ui.predict_data_lst.setVisible(True) # 開啟predict_data_lst顯示

                # 如果manual_data_lst中已有文字，開啟計算按鈕與確認是否存檔
                if self.ui.manual_data_lst.text().strip():
                    self.ui.btn_calculate.setVisible(True)
                    self.ui.checkBox_save_excel.setVisible(True)
            else: 
                QMessageBox.about(self, "Erro", "Open the correct .stl folder, Pleace!")
        else:
            return

    def open_save_folder():
        output_folder = QFileDialog.getExistingDirectory(self, "Open folder", '/Users/andy/Desktop/STL') # 開啟資料夾
        self.ui.save_path.setText(output_folder) #設定save_path顯示資料夾之路徑
        if output_folder is not None:
            self.ui.statusbar.showMessage("Calculating..., going to save to : " + output_folder) # 狀態列顯示
        return output_folder # 回傳存檔路徑位置

    #設定btn_manual_path按鈕連動
    self.ui.btn_manual_path.clicked.connect(lambda: open_manual_folder(openfile.get_folder(self))) # 開啟資料夾

    #設定btn_predict_path按鈕連動
    self.ui.btn_predict_path.clicked.connect(lambda: open_predict_folder(openfile.get_folder(self))) # 開啟資料夾
    
    #設定btn_save_path按鈕連動
    self.ui.btn_save_path.clicked.connect(lambda: open_save_folder())

    def calculate(output_folder = None):
        if self.ui.save_path.toPlainText():
            output_folder =self.ui.save_path.toPlainText() 
            # 對兩個in_path中的資料名稱從小到大排列
            files_1 = sorted(os.listdir(self.ui.manual_path.toPlainText()))
            files_2 = sorted(os.listdir(self.ui.predict_path.toPlainText()))

            print(files_1,files_2)

            # 若兩資料夾中資料數量相等
            if len(files_1) == len(files_2):
                vol_raw = [] # 設置原始體積的空陣列
                surf_raw = [] # 設置原始表面積的空陣列
                vol_pre = [] # 設置預測體積的空陣列
                surf_pre = [] # 設置預測表面積的空陣列
                diff_vol =[] # 設置體積誤差的空陣列
                diff_surf = [] # 設置表面積誤差的空陣列

                column = []  # 在for迴圈前定義column列表

                for file in files_1:
                    i = 0
                    if files_1[i] == files_2[i]: #判斷兩個模型檔名是否相同
                        column.append(file)  # 在column列表中追加欲比對項目名稱

                        folder_1 = os.path.join(self.ui.manual_path.toPlainText(), file) # 讀取資料夾中的檔案路徑
                        folder_2 = os.path.join(self.ui.predict_path.toPlainText(), file) # 讀取資料夾中的檔案路徑

                        raw_vol, raw_surf, pre_vol, pre_surf, difference_volume, difference_surf = calculate_campare(folder_1, folder_2) # 進行模型計算
                        
                        # ------------將計算結果加入陣列中------------
                        vol_raw.append(raw_vol) 
                        surf_raw.append(raw_surf)
                        vol_pre.append(pre_vol)
                        surf_pre.append(pre_surf)
                        diff_vol.append(difference_volume)
                        diff_surf.append(difference_surf)
                        # ------------將計算結果加入陣列中------------

                data = {
                    'Original Volume (mm^3) ': vol_raw,
                    'Original Surface (mm^2) ': surf_raw,
                    'Predict Volume (mm^3) ': vol_pre,
                    'Predict Surface (mm^2) ': surf_pre,
                    'Volume Error (%) ': diff_vol,
                    'Surface Error (%) ': diff_surf
                }

                df = pd.DataFrame(data, index=column) # 創建data的DataFrame，並切設置標籤為column

                selected_path = output_folder + '/model_difference.xlsx' # 設定存檔資料夾路徑
                print("輸出文件路径：", selected_path)

                transposed_df = df.transpose()  # 對DataFrame進行轉置(行列轉換)

                # 如果checkBox_save_excel被勾選
                if self.ui.checkBox_save_excel.isChecked():
                    transposed_df.to_excel(selected_path, index=True) # 將轉置後的DataFrame保存為Excel文件
                    
                    #--------開啟詢問使用者是否打開execl功能--------
                    self.ui.label_3.setVisible(True) 
                    self.ui.background_open.setVisible(True)
                    self.ui.btn_openexcel.setVisible(True)
                    self.ui.btn_home.setVisible(True)
                    #--------開啟詢問使用者是否打開execl功能--------

                self.ui.df_display.clear() # 清空表格顯示視窗
                self.ui.df_display.setRowCount(transposed_df.shape[0]) # 設定列數量
                self.ui.df_display.setColumnCount(transposed_df.shape[1]) # 設定欄數量
                self.ui.df_display.setHorizontalHeaderLabels(transposed_df.columns.tolist()) # 使用欄名稱作為列標籤
                self.ui.df_display.setVerticalHeaderLabels(transposed_df.index.tolist())  # 使用索引作為行標籤

                # 设置列头字体大小
                header_font = QtGui.QFont()
                header_font.setPointSize(20)  # 设置字体大小为24
                self.ui.df_display.horizontalHeader().setFont(header_font)

                # 设置行头字体大小
                vertical_header_font = QtGui.QFont()
                vertical_header_font.setPointSize(20)  # 设置字体大小为24
                self.ui.df_display.verticalHeader().setFont(vertical_header_font)

                for i, row in enumerate(transposed_df.values):  # 使用 enumerate 獲取索引和行數據
                    for j, val in enumerate(row):  # 使用 enumerate 獲取索引和列數據
                        item = QTableWidgetItem(str(val))
                        self.ui.df_display.setItem(i, j, item) # 設置表格顯示視窗顯示之資料
                
                # 將整個表格中的文字置中
                for i in range(self.ui.df_display.rowCount()): # 掃描所有列
                    for j in range(self.ui.df_display.columnCount()): # 掃描所有欄
                        item = self.ui.df_display.item(i, j)
                        item.setTextAlignment(QtCore.Qt.AlignCenter) # 文字置中

                self.ui.df_display.resizeRowsToContents() # 自動調整行高以顯示完整的行標籤文字

                # 開啟表格顯示視窗
                self.ui.df_display.show() 
                self.ui.df_display.setVisible(True)

                def open_excel():
                    if platform.system() == 'Darwin':
                        subprocess.run(['open', selected_path]) # 使用cmd打開所生成的excel檔案
                    elif platform.system() == 'Windows':
                        subprocess.run(['open', selected_path], shell=False) # 使用cmd打開所生成的excel檔案
                
                # 設定詢問使用者是否打開execl功能
                self.ui.btn_openexcel.clicked.connect(lambda: open_excel()) 
                self.ui.btn_home.clicked.connect(lambda: contorl.home()) 

            else:
                QtWidgets.QMessageBox.about(self, "Erro", "The data in the two folders are not equal, Please check the selected folder!")
        else:
            QtWidgets.QMessageBox.about(self, "Erro", "Please insert the saving path!")
    self.ui.btn_calculate.clicked.connect(lambda: calculate(self.ui.save_path.toPlainText())) # 設定計算誤差之按鈕

                

                
                
def vtkcalculatearea_campare_singel(self,in_path_1=None, in_path_2=None):
    if in_path_1 is None:
        in_path_1 = openfile.open_stl_data(self, "選擇stl模型檔案")
    if in_path_1:
        self.ui.statusbar.showMessage("Loading : " + in_path_1)
        if in_path_2 is None:
            in_path_2 = openfile.open_stl_data(self, "選擇stl模型檔案")
            if in_path_2:
                raw_vol,raw_surf,pre_vol,pre_surf,difference_volume,difference_surf = calculate_campare(in_path_1, in_path_2)
                QtWidgets.QMessageBox.about(self, "Result", "原始體積：%.3f，原始表面積：%.3f\n體積：%.3f，表面積%.3f\n體積相差：%.6f%%\n表面積相差：%.6f%%"%(raw_vol,raw_surf,pre_vol,pre_surf,difference_volume,difference_surf))
                    

                    

# 計算3D模型體積與表面積
def vtkcalculatearea(self, in_path=None):
    if in_path is None:
        in_path = openfile.open_stl_data(self, "選擇stl模型檔案")
        if in_path:
            self.ui.statusbar.showMessage("Path : "+in_path)
            # reader
            reader1 = vtk.vtkSTLReader()
            reader1.SetFileName(in_path)
            reader1.Update()

            # 計算小三角形面積_1
            triangleFilter1 = vtk.vtkTriangleFilter()
            triangleFilter1.SetInputData(reader1.GetOutput())
            triangleFilter1.Update()

            # 計算表面積1
            mass1 = vtk.vtkMassProperties()
            mass1.SetInputConnection(triangleFilter1.GetOutputPort())
            mass1.Update()

            # 計算模型的體積1
            mass_v1 = vtk.vtkMassProperties()
            mass_v1.SetInputData(reader1.GetOutput())
            mass_v1.Update()

            raw_vol = mass_v1.GetVolume()
            raw_surf = mass1.GetSurfaceArea()
            QtWidgets.QMessageBox.about(self, "Result", "Volume : " +str(raw_vol)+ " mm\nSurface Area : " +str(raw_surf)+ " mm")
            self.ui.statusbar.showMessage("Volume : " +str(raw_vol)+ "mm, Surface Area : " +str(raw_surf)+ "mm")

# 3D模型平滑化
def modelsmooth(self, in_path=None, out_path=None):
    if in_path is None:
        in_path = openfile.open_stl_data(self, "選擇stl模型檔案")
    if in_path:
        self.ui.statusbar.showMessage("Loading : " + in_path)
        if out_path is None:
            out_path = openfile.get_save_file(self, "儲存檔案")
        if out_path:
            self.ui.statusbar.showMessage("Finished, Saveing to : "+ out_path)
            # Create a VTK renderer
            renderer = vtk.vtkRenderer()

            # Create a VTK render window
            render_window = vtk.vtkRenderWindow()
            render_window.AddRenderer(renderer)

            # Create a VTK interactor
            interactor = vtk.vtkRenderWindowInteractor()
            interactor.SetRenderWindow(render_window)

            # Load STL file
            reader = vtk.vtkSTLReader()
            reader.SetFileName(in_path)
            reader.Update()

            # Smooth the surface
            smoother = vtk.vtkSmoothPolyDataFilter()
            smoother.SetInputConnection(reader.GetOutputPort())
            smoother.SetNumberOfIterations(100)  # Number of smoothing iterations
            smoother.SetRelaxationFactor(0.1)  # Controls the amount of smoothing
            smoother.FeatureEdgeSmoothingOff()  # Disable feature edge smoothing
            smoother.BoundarySmoothingOn()  # Enable boundary smoothing
            smoother.Update()

            # Save the smoothed surface as an STL file
            stl_writer = vtk.vtkSTLWriter()
            stl_writer.SetInputData(smoother.GetOutput())
            stl_writer.SetFileName(out_path + ".stl")
            stl_writer.Write()
            QtWidgets.QMessageBox.about(self, "finish", "The Model is smoothly now!")

global connectivity_Filter
connectivity_Filter= vtk.vtkConnectivityFilter()

def vtk_3d(self, in_path = None , out_path = None):
    choice = ["鼻竇", "氣管", "下顎骨"]
    selected_item, ok = QInputDialog.getItem(None, "三維模型重建", "選擇模型重建部位:", choice)
    if ok and selected_item:  # 如果使用者選擇了一個項目
        if in_path is None: # 若沒有指定in_path參數時
            in_path = openfile.get_folder(self, "選擇dicom資料夾") # 讓使用者開啟資料夾
        if in_path: # 有了in_path後
            self.ui.statusbar.showMessage("Loading : " + in_path) # 狀態列顯示
            if out_path is None: # 若沒有指定out_path參數時
                out_path = openfile.get_save_file(self, "儲存檔案") # 讓使用者開啟資料夾
            if out_path: # 有了out_path後
                self.ui.statusbar.showMessage("finished, Saveing to : " + out_path) # 狀態列顯示

                # vtk的dicom讀取器
                reader = vtk.vtkDICOMImageReader()
                reader.SetDirectoryName(in_path)
                reader.Update()

                # 設定三種針對氣管之閥值
                threshold_values = [1,2,3]

                # 設定兩種針對鼻竇之閥值
                sinus_values = [1,2]

                # 創建一個vtkAppendPolyData來合併模型
                append_filter = vtk.vtkAppendPolyData()

                if selected_item == "氣管":
                    for i, threshold_value in enumerate(threshold_values):
                        # 創建Marching Cubes物件
                        surface = vtk.vtkMarchingCubes()
                        surface.SetInputData(reader.GetOutput())
                        surface.SetValue(0, threshold_value)
                        surface.Update() # 執行Marching Cubes演算法，生成表面
                        # 創建顏色色組
                        colors = vtk.vtkUnsignedCharArray()
                        colors.SetNumberOfComponents(3)  # RGB颜色
                        colors.SetName("Colors")

                        # 设置所有点的颜色
                        for j in range(surface.GetOutput().GetNumberOfPoints()):
                            # 根据阈值设置颜色
                            if threshold_value == 1:
                                colors.InsertNextTuple3(123, 0, 0)  # 设置为红色
                            elif threshold_value == 2:
                                colors.InsertNextTuple3(0, 255, 0)  # 设置为绿色
                            elif threshold_value == 3:
                                colors.InsertNextTuple3(0, 0, 255)  # 设置为蓝色

                        # 将颜色数组与 vtkPolyData 关联
                        surface.GetOutput().GetPointData().SetScalars(colors)
                        surface.Update()

                        # 創建連接過濾器
                        # connectivity_Filter.SetInputConnection(surface.GetOutputPort()) # 設定輸入為Marching Cubes的輸出
                        # connectivity_Filter.SetExtractionModeToLargestRegion()  # 提取最大區域
                        # connectivity_Filter.Update() # 執行連接過濾器   

                        # 將模型添加到vtkAppendPolyData
                        append_filter.AddInputData(surface.GetOutput())

                    # 更新vtkAppendPolyData
                    append_filter.Update()
                    
                     
                    model_result = append_filter


                elif selected_item == "鼻竇":
                    for i, sinus_value in enumerate(sinus_values):
                        # 創建Marching Cubes物件
                        surface = vtk.vtkMarchingCubes()
                        surface.SetInputData(reader.GetOutput())
                        surface.SetValue(0, sinus_value)
                        surface.Update() # 執行Marching Cubes演算法，生成表面
                        # 將模型添加到vtkAppendPolyData
                        append_filter.AddInputData(surface.GetOutput())

                    # 更新vtkAppendPolyData
                    append_filter.Update()

                    input_model = append_filter.GetOutput() # 設定輸入為連接過濾器的輸出
                    fill_holes = vtk.vtkFillHolesFilter() # 創建填充孔洞濾波器物件
                    fill_holes.SetInputData(input_model)  # 設定輸入數據為input_model
                    fill_holes.SetHoleSize(1000.0) # 設定孔洞大小為1000
                    fill_holes.Update() # 執行填充孔洞濾波器
                    # 創建連接過濾器(為保留兩顆鼻竇站不使用)
                    model_result = fill_holes
                
                else:
                    # 創建Marching Cubes物件
                    surface = vtk.vtkMarchingCubes()
                    surface.SetInputData(reader.GetOutput())
                    surface.SetValue(0, 1)
                    surface.Update() # 執行Marching Cubes演算法，生成表面

                    # 創建連接過濾器(為保留兩顆鼻竇站不使用)
                    connectivity_Filter.SetInputConnection(surface.GetOutputPort()) # 設定輸入為Marching Cubes的輸出
                    connectivity_Filter.SetExtractionModeToLargestRegion()  # 提取最大區域
                    connectivity_Filter.Update() # 執行連接過濾器
                    model_result = connectivity_Filter # 執行連接過濾器    

                # 儲存為stl檔案
                output = out_path + '.stl' # 設置儲存檔案路徑
                stl_writer = vtk.vtkSTLWriter() # 創建stl儲存器

                # 當補洞按鈕被勾選
                if self.ui.checkBox_fill_holes.isChecked():
                    # 為3D模型進行補洞
                    input_model = model_result.GetOutput() # 設定輸入為連接過濾器的輸出
                    fill_holes = vtk.vtkFillHolesFilter() # 創建填充孔洞濾波器物件
                    fill_holes.SetInputData(input_model)  # 設定輸入數據為input_model
                    fill_holes.SetHoleSize(1000.0) # 設定孔洞大小為1000
                    fill_holes.Update() # 執行填充孔洞濾波器

                # 當平滑化被勾選與補洞同時被勾選
                if self.ui.checkBox_fill_holes.isChecked() and self.ui.checkBox_smooth_model.isChecked():
                    # 為3D模型進行平滑化
                    smoother = vtk.vtkSmoothPolyDataFilter() # 創建平滑器物件
                    smoother.SetInputConnection(fill_holes.GetOutputPort()) # 設定輸入為填充孔洞濾波器的輸出
                    smoother.SetNumberOfIterations(int(self.ui.smooth_level.text()))  # 平滑化程度
                    smoother.SetRelaxationFactor(0.1)  # 調整模型的收斂速度（鬆弛因子）
                    smoother.FeatureEdgeSmoothingOff()  # 關閉特徵邊緣平滑
                    smoother.BoundarySmoothingOn()  # 開啟邊界平滑
                    smoother.Update()

                    stl_writer.SetInputData(smoother.GetOutput()) # 設定stl儲存器輸入為平滑後的輸出
                    stl_writer.SetFileName(output) # 設置輸出路徑
                    stl_writer.Write() # 進行輸出

                # 當只有平滑化被勾選
                elif self.ui.checkBox_smooth_model.isChecked():
                    # 進行平滑化
                    smoother = vtk.vtkSmoothPolyDataFilter() # 創建平滑器物件
                    smoother.SetInputConnection(model_result.GetOutputPort()) # 設定輸入為最大連接過濾器的輸出
                    smoother.SetNumberOfIterations(int(self.ui.smooth_level.text()))  # 平滑化程度
                    smoother.SetRelaxationFactor(0.1)  # 調整模型的收斂速度（鬆弛因子）
                    smoother.FeatureEdgeSmoothingOff()  # 關閉特徵邊緣平滑
                    smoother.BoundarySmoothingOn()  # 開啟邊界平滑
                    smoother.Update()

                    stl_writer.SetInputData(smoother.GetOutput()) # 設定stl儲存器輸入為平滑後的輸出
                    stl_writer.SetFileName(output) # 設置輸出路徑
                    stl_writer.Write() # 進行輸出

                # 當什麼都沒勾選
                else:
                    stl_writer.SetInputData(model_result.GetOutput()) # 設定stl儲存器輸入為最大連接過濾器的輸出
                    stl_writer.SetFileName(output) # 設置輸出路徑
                    stl_writer.Write() # 進行輸出

                # 顯示重建後模型
                view(self, output)

                self.ui.statusbar.showMessage("Finished", 10000) # 狀態列顯示
                
    else:
        return #跳出函式

def vtkclose(self):
    contorl.clear_vtk(self)
    self.iren.TerminateApp()  # 關閉交互器
    self.iren_new.TerminateApp()  # 關閉交互器
    self.vtkWidget.hide()  # 隱藏vtkwidget
    self.vtkWidget_new.hide()  # 隱藏vtkwidget
    contorl.home(self)  # 回到主頁面

def dicomclose(self):
    contorl.clear_dicom(self)
    self.iren.TerminateApp()  # 關閉交互器
    self.iren_new.TerminateApp()  # 關閉交互器
    self.vtkWidget.hide()  # 隱藏vtkwidget
    self.vtkWidget_new.hide()  # 隱藏vtkwidget
    contorl.home(self)  # 回到主頁面

def change_style_smooth(self, input): #平滑化與補洞即時顯示
    # ------------------重置vtk渲染器-----------------
    if self.renderer is not None:  # 如果選染器已動作
        self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renderer)  # 移除渲染器

    self.vtkWidget.show()  # 開啟VTK視窗
    
    self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)  # 在vtkwidget中新增渲染器
    self.ui.horizontalSlider_opacity_level.setValue(100)
    # ------------------重置vtk炫染器-----------------
    if self.ui.checkBox_smooth.isChecked():
        smoother = vtk.vtkSmoothPolyDataFilter() # 創建平滑器物件
        smoother.SetInputConnection(input.GetOutputPort()) # 設定輸入為填充孔洞濾波器的輸出
        smoother.SetNumberOfIterations(100)  # 平滑化程度
        smoother.SetRelaxationFactor(0.1)  # 調整模型的收斂速度（鬆弛因子）
        smoother.FeatureEdgeSmoothingOff()  # 關閉特徵邊緣平滑
        smoother.BoundarySmoothingOn()  # 開啟邊界平滑
        smoother.Update()
        
        # 綁定到Mapper上，從而生成可供VTK渲染的組件
        self.mapper_1.SetInputConnection(smoother.GetOutputPort())
    else:
        # 綁定到Mapper上，從而生成可供VTK渲染的組件
        self.mapper_1.SetInputConnection(input.GetOutputPort())
    # 創建一個演員
    self.actor.SetMapper(self.mapper_1)
    # 取得當前演員颜色
    current_color = self.actor.GetProperty().GetDiffuseColor()

    # 取得當前ｒｇｂ值
    r = current_color[0]
    g = current_color[1]
    b = current_color[2]
    
    new_Property = vtk.vtkProperty()
    new_Property.SetColor(r, g, b)
    self.actor.SetProperty(new_Property)  # 將當前材質應用到演員上
    # 把演員加到渲染器
    self.renderer.AddActor(self.actor)
    # 使3D物件置中
    self.renderer.ResetCamera()
    # 立即更新渲染窗口
    self.vtkWidget.GetRenderWindow().Render()

def change_style_hole(self, input): #平滑化與補洞即時顯示
    # ------------------重置vtk渲染器-----------------
    if self.renderer is not None:  # 如果選染器已動作
        self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renderer)  # 移除渲染器

    self.vtkWidget.show()  # 開啟VTK視窗
   
    self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)  # 在vtkwidget中新增渲染器
    self.ui.horizontalSlider_opacity_level.setValue(100)
    # ------------------重置vtk渲染器-----------------
    if self.ui.checkBox_hole.isChecked():
        fill_holes = vtk.vtkFillHolesFilter() # 創建填充孔洞濾波器物件
        fill_holes.SetInputData(input.GetOutput())  # 設定輸入數據為input_model
        fill_holes.SetHoleSize(1000.0) # 設定孔洞大小為1000
        fill_holes.Update() # 執行填充孔洞濾波器
        
        # 綁定到Mapper上，從而生成可供VTK渲染的組件
        self.mapper_1.SetInputConnection(fill_holes.GetOutputPort())
    else:
        # 綁定到Mapper上，從而生成可供VTK渲染的組件
        self.mapper_1.SetInputConnection(input.GetOutputPort())
    # 創建一個演員
    self.actor.SetMapper(self.mapper_1)
    # 取得當前演員颜色
    current_color = self.actor.GetProperty().GetDiffuseColor()
    # 取得當前ｒｇｂ值
    r = current_color[0]
    g = current_color[1]
    b = current_color[2]
    
    new_Property = vtk.vtkProperty()
    new_Property.SetColor(r, g, b)
    self.actor.SetProperty(new_Property)  # 將當前材質應用到演員上
    # 把演員加到渲染器
    self.renderer.AddActor(self.actor)
    # 使3D物件置中
    self.renderer.ResetCamera()
    # 立即更新渲染窗口
    self.vtkWidget.GetRenderWindow().Render()

def view(self, input):
    if input:
        self.ui.tabWidget.setCurrentIndex(2)  # 設定tabwidget到vtkwidget頁面
        self.ui.stackedWidget.setCurrentIndex(3) # 設置按鈕介面至切片控制頁
        set_opacity(self)
        # 每次關閉後記得要開啟＊＊
        self.vtkWidget.show()

        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)  # 在vtkwidget中新增渲染器

        # 讀取STL模型
        if Path(input).suffix == ".stl":
            reader = vtk.vtkSTLReader()
            reader.SetFileName(input)
            reader.Update()

        # 創建PLY檔案讀取器
        if Path(input).suffix == ".ply":
            reader = vtk.vtkPLYReader()
            reader.SetFileName(input)  # 設置PLY檔案的文件名
            reader.Update()

        if Path(input).suffix == ".vtp":
            reader = vtk.vtkXMLPolyDataReader()
            reader.SetFileName(input)  # 設置PLY檔案的文件名
            reader.Update()

        # 綁定到Mapper上，從而生成可供VTK渲染的組件
        self.mapper_1.SetInputConnection(reader.GetOutputPort())

        # # 创建一个vtkTransform对象
        # transform = vtk.vtkTransform()

        # # 设置平移、旋转或缩放等操作，例如平移到世界坐标系的原点
        # transform.Translate(0, 0, 0)

        # # 将变换应用到模型
        # transformFilter = vtk.vtkTransformPolyDataFilter()
        # transformFilter.SetTransform(transform)
        # transformFilter.SetInputConnection(reader.GetOutputPort())  # 使用reader获取的数据
        # transformFilter.Update()

        # # 将变换后的数据设置给actor
        # self.mapper_1.SetInputData(transformFilter.GetOutput())
        
        # 设置模型的位置为世界坐标系的原点
        self.actor.SetPosition(0, 0, 0)
        # 創建一個演員
        self.actor.SetPickable(True)
        self.actor.SetMapper(self.mapper_1)
        

        # 获取vtkWidget的大小
        widget_width, widget_height = self.vtkWidget.width(), self.vtkWidget.height()

        # 获取self.actor的世界坐标中心点
        actor_center = self.actor.GetCenter()

        # 创建vtkRenderer的世界坐标系中心点的坐标
        world_coords = [actor_center[0], actor_center[1], actor_center[2]]

        # 使用vtkRenderer的GetActiveCamera方法获取相机
        camera = self.renderer.GetActiveCamera()

        # 使用vtkCamera的GetModelViewTransformObject方法获取ModelViewTransform对象
        modelview_transform = camera.GetModelViewTransformObject()

        # 使用ModelViewTransform对象将世界坐标转换为视口坐标
        viewport_coords = modelview_transform.TransformDoublePoint(world_coords)

        # 计算actor在vtkWidget中的坐标
        actor_x = int((viewport_coords[0] + 1) * 0.5 * widget_width)
        actor_y = int((1 - (viewport_coords[1] + 1) * 0.5) * widget_height)
        # 获取actor的z轴坐标
        actor_z = world_coords[2]

        print("Actor's x, y in vtkWidget:", actor_x, actor_y, actor_z)

        if Path(input).suffix == ".stl":
            self.actor.SetProperty(self.whiteProperty)  # 將米白色材質應用到演員上
        self.renderer.AddActor(self.actor)

        # 設定相機位置
        camera = vtk.vtkCamera()
        camera.SetPosition(0, 0, 2)  # 設定相機位置
        camera.SetFocalPoint(0, 0, 0)  # 設定相機觀看的焦點
        self.renderer.SetActiveCamera(camera)  # 設定渲染器的相機

        # 等比例縮放物體
        # bounds = self.actor.GetBounds()  #取得該物件在三個維度上的範圍
        # center = self.actor.GetCenter()  #取得該物件的中心座標
        # max_bound = max(bounds[i + 1] - bounds[i] for i in range(3))  #計算出物件在三個維度上的最大範圍，也就是其最長的邊長
        # self.actor.SetScale(1.0 / max_bound)  #設置縮放比例，讓物件顯示時大小合適
        # self.actor.SetPosition(-center[0] * max_bound, -center[1] * max_bound, -center[2] * max_bound)  #將該物件的位置做適當的平移

        # 使3D物件置中
        self.renderer.ResetCamera()

        # 啟動交互器，偵測滑鼠動作
        self.iren.Initialize()
        self.iren.Start()

        # 設定 vtkWidget 為 tab_vtkwidget 的中心部件
        self.ui.tab_vtkwidget.setLayout(self.layout)
        
        #設定模型疊合按鈕
        self.ui.btn_add_model.setVisible(True)
        #設定關閉視窗按鈕
        self.ui.btn_close_vtk.setVisible(True)  #顯示關閉按鈕
        self.ui.btn_close_vtk.clicked.connect(lambda: vtkclose(self))  #關閉按鈕連接關閉指令
        self.ui.checkBox_smooth.stateChanged.connect(lambda : change_style_smooth(self, reader))
        self.ui.checkBox_hole.stateChanged.connect(lambda : change_style_hole(self, reader))
    
def openstl(self):
    input_file, input_stytle = QFileDialog.getOpenFileName(self, "Open 3D file", '/Users/andy/Documents', "STL Files (*.stl);;VTP Files (*.vtp);;PLY Files (*.ply);;All Files (*)")
    if input_file:
        view(self, input_file)

def view_after_infer(self, input):
    self.ui.tabWidget.setCurrentIndex(2)  # 設定tabwidget到vtkwidget頁面
    self.ui.stackedWidget.setCurrentIndex(3) # 設置按鈕介面至切片控制頁
    self.ui.btn_exchange_model.setVisible(True)
    set_opacity(self)

    path_out = set_up.set_model_temp_folder() # 設置模型的暫存資料夾
    set_up.clear_model_temp_folder(path_out) # 清空暫存資料

    # 切換至vtkwidget頁面
    self.ui.tabWidget.setCurrentIndex(2) 

    # 如果選染器已動作
    if self.renderer is not None:
        self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renderer) # 移除選染器

    #設定狀態列
    self.ui.statusbar.showMessage("Display 3D Model", 10000)

    # 開啟VTK視窗
    self.vtkWidget.show()

    # self.renderer = vtk.vtkRenderer()
    # #設置背景讓他看起來透明
    # hex_color_code = "#e5e5e5"  # 背景色的16進制顏色代碼
    # r, g, b = tuple(int(hex_color_code[i:i+2], 16)/255.0 for i in (1, 3, 5))  # 將16進制的顏色代碼轉換為RGB顏色值
    # self.renderer.SetBackground(r, g, b)  # 設定渲染器的背景色為16進制的顏色代碼所對應的RGB值
    self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
    
    # 讀取dicom檔案
    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(input)
    reader.Update()

    # 調整選取的閥值區域
    threshold_value = 1

    # 進行3D重建
    surface = vtk.vtkMarchingCubes()
    surface.SetInputData(reader.GetOutput())
    surface.SetValue(0, threshold_value)
    surface.Update()

    # 創建連接過濾器，移除雜訊
    connectivityFilter = vtk.vtkConnectivityFilter()
    connectivityFilter.SetInputConnection(surface.GetOutputPort())
    # connectivityFilter.SetExtractionModeToLargestRegion()  # 提取最大區域
    
    connectivityFilter.SetExtractionModeToAllRegions() # 提取所有區域
    # 執行連接過濾器
    connectivityFilter.Update()

    # 獲取連接區域的數量
    numRegions = connectivityFilter.GetNumberOfExtractedRegions()

    # 如果有至少兩個區域，您可以通過迴圈進一步處理它們
    if numRegions >= 2:
        # 獲取每個區域的數據
        regionData = vtk.vtkPolyData()
        connectivityFilter.InitializeSpecifiedRegionList()
        connectivityFilter.AddSpecifiedRegion(0)
        connectivityFilter.Update()
        regionData.DeepCopy(connectivityFilter.GetOutput())

    # 存檔為stl檔，放置於暫存資料夾中
    output = os.path.join(path_out, "test.stl") #設定存檔位置
    stl_writer = vtk.vtkSTLWriter()
    stl_writer.SetInputData(regionData)
    stl_writer.SetFileName(output)
    stl_writer.Write()

    # 讀取剛存下的stl檔
    reader_new = vtk.vtkSTLReader()
    reader_new.SetFileName(output)
    reader_new.Update()

    # 當補洞被勾選
    if self.ui.checkBox_fill_holes.isChecked():
        # Fill the holes in the 3D model
        input_model = reader_new.GetOutput()
        fill_holes = vtk.vtkFillHolesFilter()
        fill_holes.SetInputData(input_model)
        fill_holes.SetHoleSize(1000.0)
        fill_holes.Update()

    # 當平滑化被勾選
    if self.ui.checkBox_fill_holes.isChecked() and self.ui.checkBox_smooth_model.isChecked():
        # 進行平滑化
        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetInputConnection(fill_holes.GetOutputPort())
        smoother.SetNumberOfIterations(int(self.ui.smooth_level.text()))  # 平滑化程度
        smoother.SetRelaxationFactor(0.1)  # 調整模型收斂速度（鬆弛因子）
        smoother.FeatureEdgeSmoothingOff()  # 關閉特徵邊緣平滑
        smoother.BoundarySmoothingOn()  # 開啟邊界平滑
        smoother.Update()
    elif self.ui.checkBox_smooth_model.isChecked():
        # 進行平滑化
        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetInputConnection(reader_new.GetOutputPort())
        smoother.SetNumberOfIterations(int(self.ui.smooth_level.text()))  # 平滑化程度
        smoother.SetRelaxationFactor(0.1)  # 調整模型收斂速度（鬆弛因子）
        smoother.FeatureEdgeSmoothingOff()  # 關閉特徵邊緣平滑
        smoother.BoundarySmoothingOn()  # 開啟邊界平滑
        smoother.Update()

    # 綁定到Mapper上，從而生成可供VTK渲染的組件
    mapper = vtk.vtkPolyDataMapper()
    # 當平滑化被勾選
    if self.ui.checkBox_smooth_model.isChecked():
        mapper.SetInputConnection(smoother.GetOutputPort())  # 選用平滑化後結果
    # 當補洞被勾選
    elif self.ui.checkBox_fill_holes.isChecked():
        mapper.SetInputConnection(fill_holes.GetOutputPort())  # 選用未平滑化後結果
    else:
        mapper.SetInputConnection(reader_new.GetOutputPort())  # 選用未平滑化後結果
    
    # 創建一個米白色的材質
    white = vtk.vtkNamedColors()
    whiteColor = white.GetColor3d('antiquewhite')
    whiteProperty = vtk.vtkProperty()
    whiteProperty.SetColor(whiteColor)

    # 創建演員讀取模型
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetProperty(whiteProperty)  # 將米白色材質應用到演員上
    self.renderer.AddActor(actor)

    # 設定相機位置
    camera = vtk.vtkCamera()
    camera.SetPosition(0, 0, 2)  # 設定相機位置
    camera.SetFocalPoint(0, 0, 0)  # 設定相機觀看的焦點
    self.renderer.SetActiveCamera(camera)  # 設定渲染器的相機

    # 對 vtkActor 物件進行縮放和平移，等比例縮放物體
    bounds = actor.GetBounds()  #取得該物件在三個維度上的範圍
    center = actor.GetCenter()  #取得該物件的中心座標
    max_bound = max(bounds[i + 1] - bounds[i] for i in range(3))  #計算出物件在三個維度上的最大範圍，也就是其最長的邊長
    actor.SetScale(1.0 / max_bound)  #設置縮放比例，讓物件顯示時大小合適
    actor.SetPosition(-center[0] * max_bound, -center[1] * max_bound, -center[2] * max_bound)  #將該物件的位置做適當的平移

    # 使3D物件置中
    self.renderer.ResetCamera()

    # 設定 vtkWidget 為 tab_vtkwidget 的中心部件
    # layout = QVBoxLayout(self.ui.tab_vtkwidget)
    # layout.addWidget(self.vtkWidget)
    self.iren.Initialize()
    self.iren.Start()
    self.ui.tab_vtkwidget.setLayout(self.layout)

    #設定模型疊合按鈕
    self.ui.btn_add_model.setVisible(True)
    
    # 設定關閉視窗: 顯示
    self.ui.btn_close_vtk.setVisible(True)

    # 設定關閉按鈕指令
    self.ui.btn_close_vtk.clicked.connect(lambda: vtkclose(self))

# 3D模型疊合
def add_model(self):
    # 使用者開啟資料夾
    in_path = openfile.open_stl_data(self, "開啟stl檔案")
    if in_path:
        self.vtkWidget_new.show()
        # 讀取stl模型
        reader = vtk.vtkSTLReader()
        reader.SetFileName(in_path)  # 設置讀取位址
        self.mapper_2= vtk.vtkPolyDataMapper()  # 綁定到Mapper上，從而生成可供VTK渲染的組件
        self.mapper_2.SetInputConnection(reader.GetOutputPort())
        actor_new = vtk.vtkActor() # 建置新演員
        actor_new.SetMapper(self.mapper_2)
        self.renderer_new = vtk.vtkRenderer()

        #設置背景讓他看起來透明
        hex_color_code = "#e5e5e5"  # 背景色的16進制顏色代碼
        r, g, b = tuple(int(hex_color_code[i:i+2], 16)/255.0 for i in (1, 3, 5))  # 將16進制的顏色代碼轉換為RGB顏色值
        self.renderer_new.SetBackground(r, g, b)  # 設定渲染器的背景色為16進制的顏色代碼所對應的RGB值
        
        self.vtkWidget_new.GetRenderWindow().AddRenderer(self.renderer_new)  # 在vtkwidget中新增渲染器
        self.renderer_new.AddActor(actor_new) # 將新演員渲染至視窗中

        # 設定相機位置
        camera = vtk.vtkCamera()
        camera.SetPosition(0, 0, 2)  # 設定相機位置
        camera.SetFocalPoint(0, 0, 0)  # 設定相機觀看的焦點
        self.renderer.SetActiveCamera(camera)  # 設定渲染器的相機

        # 等比例縮放物體
        bounds = actor_new.GetBounds()  #取得該物件在三個維度上的範圍
        center = actor_new.GetCenter()  #取得該物件的中心座標
        max_bound = max(bounds[i + 1] - bounds[i] for i in range(3))  #計算出物件在三個維度上的最大範圍，也就是其最長的邊長
        actor_new.SetScale(1.0 / max_bound)  #設置縮放比例，讓物件顯示時大小合適
        actor_new.SetPosition(-center[0] * max_bound, -center[1] * max_bound, -center[2] * max_bound)  #將該物件的位置做適當的平移
        
        # 使3D物件置中
        self.renderer.ResetCamera()
        self.renderer_new.ResetCamera()

        # 設定 vtkWidget 為 tab_vtkwidget 的中心部件
        self.layout.addWidget(self.vtkWidget_new)
        self.ui.tab_vtkwidget.setLayout(self.layout)

        # 啟動交互器，偵測滑鼠動作
        self.iren_new.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera()) # 變更模型移動方式
        self.iren_new.Initialize()
        self.iren_new.Start()

        self.ui.btn_overlap.setVisible(True)
        self.ui.btn_overlap.setEnabled(True)
        self.ui.btn_overlap.clicked.connect(lambda: overlap(self))

def overlap(self):
    self.ui.btn_overlap.setEnabled(False)
    self.ui.btn_new_model.setEnabled(False)
    
    # 創建ICP演算法
    icp = vtk.vtkIterativeClosestPointTransform()
    icp.SetSource(self.mapper_2.GetInput())  # 設定目標模型
    icp.SetTarget(self.mapper_1.GetInput())  # 設定参考模型
    icp.GetLandmarkTransform().SetModeToRigidBody()  # 使用剛性變換模式

    # 使用ICP演算法計算變換矩陣
    icp.Update()

    # 取得ICP計算後的變換矩陣
    transform = vtk.vtkTransform()
    transform.SetMatrix(icp.GetMatrix())

    # 將變換應用到目標模型
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(self.mapper_2.GetInput())
    transform_filter.SetTransform(transform)
    transform_filter.Update()
    aligned_model = transform_filter.GetOutput() # 取得變形後模型

    # 計算模型厚度差異並創建圖示
    thickness_array = vtk.vtkDoubleArray() # 創建一個vtkDoubleArray：存儲厚度數據
    thickness_array.SetNumberOfComponents(1) # 設置vtkDoubleArray的元素組成數
    thickness_array.SetName("Thickness") # 設置vtkDoubleArray的名稱

    aligned_points = aligned_model.GetPoints() # 從對齊後的模型獲取點數據
    reference_points = self.mapper_1.GetInput().GetPoints() # 從參考模型(self.mapper_1)中獲取點數據

    num_points = aligned_points.GetNumberOfPoints() # 取得對齊後模型的點數量

    for i in range(num_points):
        aligned_point = aligned_points.GetPoint(i) # 獲取對齊後模型中第i個點的坐標
        reference_point = reference_points.GetPoint(i) # 獲取參考模型中第i個點的坐標


        thickness = aligned_point[2] - reference_point[2]  # 計算對齊後模型和參考模型在z軸方向上的厚度差
        thickness_array.InsertNextValue(thickness) # 將計算得到的厚度差值插入到thickness_array中

    aligned_model.GetPointData().SetScalars(thickness_array) # 將厚度數據設置為對齊後模型的點數據的標量值

    # 創建分別映射器    
    # mapper1 = vtk.vtkPolyDataMapper()
    # mapper1.SetInputData(self.mapper_1.GetInput())

    # mapper2 = vtk.vtkPolyDataMapper()
    # mapper2.SetInputData(self.mapper_2.GetInput())

    # 創建合成映射器
    aligned_mapper = vtk.vtkPolyDataMapper()
    aligned_mapper.SetInputData(aligned_model) # 設置輸入為對齊後模型

    # 創建顏色映射器並設置範圍
    color_mapper = vtk.vtkLookupTable()
    color_mapper.SetHueRange(0.5, 0.0)  # 設定颜色範圍為綠色到红色

    scalar_range = aligned_model.GetPointData().GetScalars().GetRange() # 從對齊後模型的點數據中獲取標量值的範圍

    # 設置顏色映射器的顏色數量
    color_mapper.SetNumberOfTableValues(256)

    color_mapper.SetRange(scalar_range)

    # 設置顏色映射器的值範圍
    color_mapper.Build()

    # 設置顏色映射器
    aligned_mapper.SetLookupTable(color_mapper)

    # 設置標量範圍
    aligned_mapper.SetScalarRange(scalar_range)


    # 将颜色映射器应用于映射器
    # mapper1.SetLookupTable(color_mapper)
    # mapper1.SetScalarRange(scalar_range)

    # mapper2.SetLookupTable(color_mapper)
    # mapper2.SetScalarRange(scalar_range)

    # 將顏色映射器應用於合成映射器
    # aligned_mapper.SetLookupTable(color_mapper) 
    # aligned_mapper.SetScalarRange(scalar_range)

    # actor1 = vtk.vtkActor()
    # actor1.SetMapper(mapper1)

    # actor2 = vtk.vtkActor()
    # actor2.SetMapper(mapper2)

    # 設置演員以顯示對齊後模型
    aligned_actor = vtk.vtkActor()
    aligned_actor.SetMapper(aligned_mapper)

    # 創建顏色圖例
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(color_mapper)
    scalar_bar.SetTitle("Difference(mm)") # 設置圖例標題
    scalar_bar.GetTitleTextProperty().SetFontSize(8)  # 設置圖例標題字體大小
    scalar_bar.GetTitleTextProperty().SetColor(0, 0, 0)
    scalar_bar.SetNumberOfLabels(7)  # 設置顯示的標籤數量
    scalar_bar.GetLabelTextProperty().SetFontSize(5) # 設置圖例中標籤字體大小

    # 設置圖例的大小及位置
    scalar_bar.SetWidth(0.1)  # 設置寬度
    scalar_bar.SetHeight(0.9)  # 設置高度
    scalar_bar.SetPosition(0.05, 0.05)  # 設置位置：畫面最左邊
    
    # 創建渲染器並新增演員
    renderer = vtk.vtkRenderer()
    # renderer.AddActor(actor1)
    # renderer.AddActor(actor2)
    renderer.AddActor(aligned_actor)
    renderer.AddActor2D(scalar_bar)  # 將圖例添加到渲染器中

    # 清理交互器和額外的vtk視窗
    self.iren_new.TerminateApp()
    self.vtkWidget_new.hide()

    #設置背景讓他看起來透明
    hex_color_code = "#e5e5e5"  # 背景色的16進制顏色代碼
    r, g, b = tuple(int(hex_color_code[i:i+2], 16)/255.0 for i in (1, 3, 5))  # 將16進制的顏色代碼轉換為RGB顏色值
    renderer.SetBackground(r, g, b)  # 設定渲染器的背景色為16進制的顏色代碼所對應的RGB值

    # 在vtkWidget中添加渲染器
    self.vtkWidget.GetRenderWindow().AddRenderer(renderer)

    # 設置輸出位置
    self.layout.addWidget(self.vtkWidget)
    self.ui.tab_vtkwidget.setLayout(self.layout)

    # 重置相機並啟動交互器
    renderer.ResetCamera()
    self.iren.Initialize()
    self.iren.Start()

# 設定模型透明度
def set_opacity(self):
    self.ui.horizontalSlider_opacity_level.setMinimum(0) # 設定滑桿最小值
    self.ui.horizontalSlider_opacity_level.setMaximum(100) # 設定滑桿最大值為window_center
    self.ui.horizontalSlider_opacity_level.setValue(100)
    self.ui.horizontalSlider_opacity_level.valueChanged.connect(self.on_opacity_level_slider_value_changed)

# 新增模型
def new_model(self):
    # 使用者開啟資料夾
    in_path = openfile.open_stl_data(self, "開啟stl檔案")
    # 讀取stl模型
    if in_path:
        reader = vtk.vtkSTLReader()
        reader.SetFileName(in_path)  # 設置讀取位址
        reader.Update()

        # 建立新的 mapper 和 actor
        new_mapper = vtk.vtkPolyDataMapper()
        new_mapper.SetInputConnection(reader.GetOutputPort())

        actor_new = vtk.vtkActor()
        actor_new.SetMapper(new_mapper)
        

        actor_property = vtk.vtkProperty()
        dlg = QColorDialog(self)
        dlg.setCurrentColor(Qt.white)
        if dlg.exec_():
            # 設定演員顏色
            color = dlg.selectedColor()
            actor_property.SetColor(color.redF(), color.greenF(), color.blueF())
        actor_property.SetOpacity(0.5)
        actor_new.SetProperty(actor_property)

        # 建立vtkAssembly，將新舊演員合併
        assembly = vtk.vtkAssembly()
        assembly.AddPart(self.actor)  # 增加舊演員
        assembly.AddPart(actor_new)  # 增加新演員

        self.picker.AddPickList(actor_new)

        # 重新渲染
        self.renderer.AddActor(assembly) 

        self.renderer.ResetCamera()

        self.vtkWidget.GetRenderWindow().Render()
    




