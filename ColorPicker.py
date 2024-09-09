import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PySide6.QtGui import QScreen, QPixmap, QPainter, QColor, QCursor, QIcon
from PySide6.QtCore import Qt, QPoint

from pyperclip import *
from screeninfo import get_monitors
import win32api


class Position(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(25)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.positionLabel_Color = QColor()
        self.positionLabel_Color.setRgb(0, 0, 0)

        self.positionLabel_BgColor = QColor()
        self.positionLabel_BgColor.setRgb(0, 0, 0)

        self.positionLabel = QLabel()
        self.positionLabel.setText("")

        style = f'''
        QLabel {{
            color: #FFFFFF;
            font-size: 14px;
            background-color: #FFFFFF;
            border-radius: 6px;
        }}
        '''
        self.positionLabel.setStyleSheet(style)

        self.alayout = QHBoxLayout()
        self.alayout.setContentsMargins(0,0,0,0)
        self.alayout.addWidget(self.positionLabel)

        self.setLayout(self.alayout)


    def update_position(self, pos, x, y, w, h, color_hex):
        self.bgcolor_hex = color_hex

        r,g,b = list(int(self.bgcolor_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        # 基于互补色方案实现
        # 互补色位于色轮上彼此相对的位置，可以提供良好的对比度
        # self.positionLabel_Color.setRgb(255-r, 255-g, 255-b)
        # 下面使用HSL（色相、饱和度、亮度）模型来动态计算亮度对比度
        # 确保字体颜色的亮度与背景色的亮度有足够的差异,以获得最佳的显示效果
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        if brightness < 128:
            self.positionLabel_Color.setRgb(255, 255, 255)
        else:
            self.positionLabel_Color.setRgb(0, 0, 0)

        self.color_hex = self.positionLabel_Color.name()
        
        style = f'''
        QLabel {{
            color: {self.color_hex};
            font-size: 14px;
            background-color: {self.bgcolor_hex};
            border-radius: 6px;
        }}
        '''
        self.positionLabel.setStyleSheet(style)
        self.positionLabel.setText(str(x)+","+str(y))

        # 调整坐标显示位置
        deltY = -28 if y > 50 else 5
        deltX = 10  if x < w-110 else -70 
        self.move(pos + QPoint(deltX, deltY))

        if self.isVisible() == False:
            self.show()

class ScreenColorPicker(QWidget):
    def __init__(self):
        super().__init__()

        self.picking = False
        self.monitors = get_monitors()

        self.layout = QVBoxLayout()
        self.initUI()

        self.position = Position()

    def initUI(self):
        self.setWindowTitle('屏幕取色器')
        self.setWindowIcon(QIcon('icon.png'))
        self.setGeometry(100, 100, 250, 50)

        # 绘制初始界面
        self.pick_color_button = QPushButton('选取颜色', self)
        self.pick_color_button.clicked.connect(self.pickColor)
        self.layout.addWidget(self.pick_color_button)

        self.setLayout(self.layout)

    def pickColor(self):
        # 设置窗口完全透明
        self.setWindowOpacity(0.01)  
        
        # 获取当前的屏幕
        self.screen = self.windowHandle().screen()
        # 截取当前的屏幕，获得鼠标位置后在当前截图中获得像素颜色
        self.pixmap = self.screen.grabWindow(0)

        # 删除界面上的内容避免影响鼠标位置追踪
        self.pick_color_button.deleteLater()
        try:
            self.color_widget.deleteLater()
            self.color_info_hex_btn.deleteLater()
            self.color_info_rgb_btn.deleteLater()
            self.color_info_widget.deleteLater()
        except:
            pass

        # 界面设置为全屏
        self.showFullScreen()
        
        # 鼠标形状设置为 +
        self.setCursor(Qt.CrossCursor)

        # 启用鼠标追踪
        self.setMouseTracking(True)  
        
        self.picking = True

    def mouseMoveEvent(self, event):
        # 获取鼠标全局坐标(支持多显示器)
        mouseX, mouseY = win32api.GetCursorPos()
        #计算相对坐标
        for m in self.monitors:
            if m.x <= mouseX < m.x + m.width and m.y <= mouseY < m.y + m.height:
                # 计算鼠标在当前显示器上的本地位置
                mouseX = mouseX - m.x
                mouseY = mouseY - m.y

                width = m.width
                height = m.height
                break
        # 获取颜色
        color = QColor(self.pixmap.toImage().pixel(mouseX,mouseY)).name()
        self.position.update_position(event.globalPosition().toPoint(), mouseX, mouseY, width, height, color)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pass

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.picking == True:
            # 取色过程结束
            self.picking = False
            self.position.close()

            # 获取鼠标全局坐标(支持多显示器)
            mouseX, mouseY = win32api.GetCursorPos()
            #计算相对坐标
            for m in self.monitors:
                if m.x <= mouseX < m.x + m.width and m.y <= mouseY < m.y + m.height:
                    # 计算鼠标在当前显示器上的本地位置
                    mouseX = mouseX - m.x
                    mouseY = mouseY - m.y
                    break
            # 获取颜色
            color_hex = QColor(self.pixmap.toImage().pixel(mouseX,mouseY)).name()
            color_rgb = '(' + ','.join(map(str, tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))) + ')'

            # 默认拷贝16进制颜色到剪切板
            copy(color_hex)
            
            # 禁用鼠标追踪
            self.setMouseTracking(False)

            # 设置鼠标箭头形状 - 箭头
            self.setCursor(Qt.ArrowCursor)
            # 窗口设置为正常大小
            self.showNormal()
            # 设置窗口完全不透明
            self.setWindowOpacity(1.0)  
            
            # 重新绘制界面
            self.pick_color_button = QPushButton('选取颜色', self)
            self.pick_color_button.setMaximumHeight(30)
            self.pick_color_button.setMinimumHeight(30)
            self.pick_color_button.clicked.connect(self.pickColor)

            self.color_widget = QWidget()
            self.color_widget.setMaximumHeight(30)
            self.color_widget.setMinimumHeight(30)
            self.color_widget.setStyleSheet("QWidget { background-color: " + color_hex + "; }")
            
            self.color_info_hex_btn = QPushButton(color_hex, self)
            self.color_info_hex_btn.setMaximumHeight(30)
            self.color_info_hex_btn.setMinimumHeight(30)
            self.color_info_hex_btn.clicked.connect(lambda: copy(color_hex))

            self.color_info_rgb_btn = QPushButton(color_rgb, self)
            self.color_info_rgb_btn.setMaximumHeight(30)
            self.color_info_rgb_btn.setMinimumHeight(30)
            self.color_info_rgb_btn.clicked.connect(lambda: copy(color_rgb))
            
            self.color_info_widget = QWidget()
            self.color_info_widget.setMaximumHeight(30)
            self.color_info_widget.setMinimumHeight(30)
            self.color_info_layout = QHBoxLayout(self.color_info_widget)
            self.color_info_layout.setContentsMargins(0, 0, 0, 0)
            self.color_info_layout.addWidget(self.color_info_hex_btn)
            self.color_info_layout.addWidget(self.color_info_rgb_btn)
            
            self.layout.addWidget(self.pick_color_button)
            self.layout.addWidget(self.color_widget)
            self.layout.addWidget(self.color_info_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    picker = ScreenColorPicker()
    picker.show()
    sys.exit(app.exec())
