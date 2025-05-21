#對大部分的按鈕設定形式
# most_button_style = '''
# /* 按鈕基本形式 */
# QPushButton {
#     background-color: #d4e5f0;  /* 設置背景顏色 */
#     border-style: outset;  /* 設置邊框形式：外邊框 */
#     border-width: 2px;  /* 設置邊框粗度 */
#     border-radius: 10px;  /* 設置邊框圓滑程度 */
#     border-color: white;  /* 設置邊框顏色 */
#     font-size: 15px;  /* 設置文字大小 */
#     font-family: BiauKai;  /* 設置標楷體 */
#     font-weight: 900;  /* 設置文字粗體 */
#     color: black;   /* 設置文字顏色 */
# }
# /* 按鈕被選取時形式 */
# QPushButton:hover { 
#     background-color: #186ca0;  
#     color: white;  

# }
# /* 按鈕被點下後形式 */
# QPushButton:pressed {
#     background-color: #000000;  
# }
# '''

# contorlvtk_buttn_style = '''
# QPushButton {
#     background-color: #f4a261;  
#     border-style: outset;
#     border-width: 2px;
#     border-radius: 10px;
#     font-size: 14px;
#     font-family: BiauKai;
#     font-weight: bold;  
#     color: white;
#     padding: 3px;
# }

# QPushButton:hover {
#     background-color: #e76f51;  
# }

# QPushButton:pressed {
#     background-color: #880000;  
# }
# '''

# closevtk_button_style = '''
# QPushButton {
#     background-color: #d72c15;  
#     border-style: outset;
#     border-width: 2px;
#     border-radius: 10px;
#     font-size: 14px;
#     font-family: BiauKai;
#     font-weight: bold;  
#     color: white;
#     padding: 3px;
# }

# QPushButton:hover {
#     background-color: #AA0000;  
# }

# QPushButton:pressed {
#     background-color: #880000;  
# }
# '''

# combobox_style = '''
# QComboBox {
#         background-color: #d4e5f0; 
#         border: 2px solid white;
#         border-radius: 10px;
#         text-align: center;
#         color: black;
#         font-size: 15px;
#         font-family: BiauKai;
#         font-weight: bolder;
#     }
# '''

# slider_style = """
# /*橫向滑軌，設定無邊框、背景色、高度和圓角*/
# QSlider::groove:horizontal {
#     border: none;
#     background: #ddd;
#     height: 10px;
#     border-radius: 5px;
# }

# /*橫向滑塊，設定背景色、無邊框、高度、寬度、位移和圓角*/
# QSlider::handle:horizontal {
#     background: #e63946;
#     border: none;
#     height: 20px;
#     width: 20px;
#     margin: -5px 0;
#     border-radius: 10px;
# }

# /*橫向滑塊滑鼠懸停時，設定背景色*/
# QSlider::handle:horizontal:hover {
#     background: #e76f51;
# }

# /*橫向滑軌前景，設定背景色和圓角*/
# QSlider::add-page:horizontal {
#     background: #e5e5e5;
#     border: none;
#     height: 10px;
#     border-radius: 5px;
# }

# /*橫向滑軌背景，設定背景色和圓角*/
# QSlider::sub-page:horizontal {
#     background: #ffb4a2;
#     border: none;
#     height: 10px;
#     border-radius: 5px;
# }
# """

# menu_bar_style = """
# QMenuBar {
#     background-color: #e5e5e5;
#     font-size: 15px;
#     font-family: Arial;
#     font-weight: bold;
#     color: black;
# }
# QMenuBar::item {
#     padding: 2px 10px;
#     background-color: #e5e5e5;
# }
# QMenuBar::item:selected {
#     background-color: #242f40;
#     color: white;
# }
# """

# status_bar_style ="""
# QStatusBar {
#     background-color: #bfbfbf; /*设置背景颜色*/
#     color: black; /*设置文字颜色*/
#     font-size: 12px; /*设置字体大小*/
#     font-family: BiauKai;
#     font-weight: bold;
    
# }

# QStatusBar::item {
#     border: none; /*去掉边框*/
# }

# QStatusBar QToolTip {
#     background-color: #fff; /*设置提示的背景颜色*/
#     color: #333; /*设置提示文字颜色*/
#     border: 1px solid #aaa; /*设置提示边框*/
#     font-size: 12px; /*设置提示字体大小*/
# } 

# QStatusBar QLabel {
#     padding: 3px; /*设置标签的内边距*/
# } 

# QStatusBar::busy {
#     image: url(busy.gif); /*设置忙时状态图标*/
# } 

# QStatusBar::permanent {
#     border: none; /*设置永久部件的边框*/
# } 

# QStatusBar::temporary {
#     border: none; /*设置临时部件的边框*/
#     border-top: 1px solid #aaa; /*设置临时部件顶部的边框*/
#     padding: 2px; /*设置临时部件的内边距*/
# } 

# QStatusBar::message {
#     font-weight: bold; /*设置消息的字体粗细*/
# }
# """

# textedit_style = """
# QTextEdit {
#     font-family: "Arial";
#     font-size: 9px;
#     color: black;
#     background-color: rgba(255, 255, 255, 0.35);
#     border: 1px solid #ccc;
#     padding: 5px;
# }

# QTextEdit:focus {
#     border: 1px solid #0078d7;
#     outline: none;
# }

# QTextEdit::placeholder {
#     color: #999;
# }

# QTextEdit::disabled {
#     color: #ccc;
#     background-color: #f7f7f7;
#     border: 1px solid #eee;
# }

# QScrollBar:vertical {
#     width: 12px;
#     margin: 12px 0 12px 0;
# }

# QScrollBar::handle:vertical {
#     background-color: #ccc;
#     min-height: 20px;
#     border-radius: 6px;
# }

# QScrollBar::handle:vertical:hover {
#     background-color: #999;
# }

# QScrollBar::add-line:vertical {
#     height: 12px;
#     width: 12px;
#     border-image: url(add.png);
#     subcontrol-position: bottom;
#     subcontrol-origin: margin;
# }

# QScrollBar::add-line:vertical:hover {
#     border-image: url(add_hover.png);
# }

# QScrollBar::sub-line:vertical {
#     height: 12px;
#     width: 12px;
#     border-image: url(sub.png);
#     subcontrol-position: top;
#     subcontrol-origin: margin;
# }

# QScrollBar::sub-line:vertical:hover {
#     border-image: url(sub_hover.png);
# }
# """

# lineedit_style = """
# QLineEdit {
#     text-align: center;
#     font-family: "Arial";
#     font-size: 14px;
#     color: black;
#     background-color: rgba(255, 255, 255, 0.35);
#     border: 1px solid #ccc;
#     padding: 5px;
# }

# QLineEdit::focus {
#     border: 1px solid #0078d7;
#     outline: none;
# }
# """

checkbox_style = """
QCheckBox {
    border: 2px solid gray;
    border-radius: 10px;
    padding: 0px 0px 0px 3px;
    color: white;
    font-size: 14px;
    font-family: BiauKai;
    font-weight: bold;
}

QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border-radius: 7px;
}

QCheckBox::indicator:unchecked {
    border: 2px solid #3b3b3b;
    background-color: #fff;
}

QCheckBox::indicator:checked {
    background-color: #da291c;
    border: 2px solid gray;
}

QCheckBox::indicator:checked:disabled {
    border: 2px solid #afafaf;
    background-color: #afafaf;
}

QCheckBox::indicator:unchecked:disabled {
    border: 2px solid #afafaf;
    background-color: #fff;
}
"""
slider_raw_style = """
QSlider::groove:horizontal {
    border: none;
    background: #ddd;
    height: 5px;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    background: #343a40;
    border: none;
    height: 20px;
    width: 10px;
    margin: -5px 0;
    border-radius: 0px;
}

QSlider::handle:horizontal:hover {
    background: #370617;
}

QSlider::add-page:horizontal {
    background: #00000;
    border: none;
    height: 10px;
    border-radius: 5px;
}

QSlider::sub-page:horizontal {
    background: #fec5bb;
    border: none;
    height: 10px;
    border-radius: 5px;
}"""

slider_coronal_style = """
QSlider::groove:horizontal {
    border: none;
    background: #ddd;
    height: 5px;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    background: #343a40;
    border: none;
    height: 20px;
    width: 10px;
    margin: -5px 0;
    border-radius: 0px;
}

QSlider::handle:horizontal:hover {
    background: #081c15;
}

QSlider::add-page:horizontal {
    background: #00000;
    border: none;
    height: 10px;
    border-radius: 5px;
}

QSlider::sub-page:horizontal {
    background: #95d5b2;
    border: none;
    height: 10px;
    border-radius: 5px;
}"""

slider_sagitta_style = """
QSlider::groove:horizontal {
    border: none;
    background: #ddd;
    height: 5px;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    background: #343a40;
    border: none;
    height: 20px;
    width: 10px;
    margin: -5px 0;
    border-radius: 0px;
}

QSlider::handle:horizontal:hover {
    background: #f3722c;
}

QSlider::add-page:horizontal {
    background: #00000;
    border: none;
    height: 10px;
    border-radius: 5px;
}

QSlider::sub-page:horizontal {
    background: #ffee9d;
    border: none;
    height: 10px;
    border-radius: 5px;
}"""