import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PySide6.QtGui import QScreen, QPixmap, QPainter, QColor, QCursor, QIcon, QPen, QRegion, QBitmap, QClipboard
from PySide6.QtCore import Qt, QPoint, QTimer, QRect

from pyperclip import *
from screeninfo import get_monitors
import win32api
import win32con
import threading
import time

import os
# ADJUST QT FONT DPI FOR HIGHT SCALE AN 4K MONITOR
# ///////////////////////////////////////////////////////////////
os.environ["QT_FONT_DPI"] = "96"

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

        self.alayout = QHBoxLayout()
        self.alayout.setContentsMargins(0,0,0,0)
        self.alayout.addWidget(self.positionLabel)

        self.setLayout(self.alayout)


    def update_position(self, pos, x, y, w, h, pixmap:QPixmap):
        # 将cropped_pixmap放大4倍
        scaled_pixmap = pixmap.scaled(pixmap.width() * 5, pixmap.height() * 5, Qt.KeepAspectRatio, Qt.FastTransformation)#Qt.SmoothTransformation
        
        # 创建一个画笔对象，设置颜色为黑色
        painter = QPainter(scaled_pixmap)
        pen = QPen(QColor('red'))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # 在放大后的图像中间位置画一条水平的线
        line_y = scaled_pixmap.height()/2
        line_x = scaled_pixmap.width()/2

        painter.drawLine(0, line_y, scaled_pixmap.width(), line_y)
        painter.drawLine(0, line_y+5, scaled_pixmap.width(), line_y+5)
        painter.drawLine(line_x, 0, line_x, scaled_pixmap.height())
        painter.drawLine(line_x+5, 0, line_x+5, scaled_pixmap.height())
        painter.end()
        

        # 创建一个遮罩，用于截取圆形区域
        mask = QBitmap(scaled_pixmap.size())
        mask.fill(Qt.color0)  # 填充黑色
        # 使用 QPainter 在遮罩上绘制白色圆形
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.color1)  # 使用白色画刷
        painter.drawEllipse(0, 0, 100, 100)  # 绘制圆形
        painter.end()
        
        # 将遮罩应用到 pixmap
        scaled_pixmap.setMask(mask)
        
        self.positionLabel.setPixmap(scaled_pixmap)
        
        

        # 调整坐标显示位置
        deltY = -28 if y > 50 else 5
        deltX = 10  if x < w-110 else -70 
        self.move(pos + QPoint(deltX, deltY))

        if self.isVisible() == False:
            self.show()
            
    def keyPressEvent(self, event):
        # 获取当前鼠标位置
        cursor_pos = QCursor.pos()
        # 设置每次移动的步长
        step = 1

        # 根据按下的键移动鼠标位置
        if event.key() == Qt.Key_Up:
            QCursor.setPos(cursor_pos.x(), cursor_pos.y() - step)
        elif event.key() == Qt.Key_Down:
            QCursor.setPos(cursor_pos.x(), cursor_pos.y() + step)
        elif event.key() == Qt.Key_Left:
            QCursor.setPos(cursor_pos.x() - step, cursor_pos.y())
        elif event.key() == Qt.Key_Right:
            QCursor.setPos(cursor_pos.x() + step, cursor_pos.y())

class ScreenColorPicker(QWidget):
    def __init__(self):
        super().__init__()

        self.picking = False
        self.monitors = get_monitors()

        self.layout = QVBoxLayout()
        
        self.initUI()

        self.startX = 0
        self.startY = 0
        self.stopX = 0
        self.stopY = 0
        self.start_point = None
        self.move_point = None

        self.pixmap = QPixmap()

        self.position = Position()
    def initUI(self):
        self.setWindowTitle('PicPicker')
        self.setWindowIcon(QIcon('icon.png'))
        #self.setGeometry(100, 100, 250, 50)
        self.resize(300, 70)

        # 绘制初始界面
        self.discrib_btn = QPushButton("截屏")
        self.discrib_btn.clicked.connect(self.pickColor)
        self.layout.addWidget(self.discrib_btn)
        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)

    def pickColor(self):
        # 设置窗口完全透明
        self.setWindowOpacity(0.2)  
        
        # 获取当前的屏幕
        self.screen = self.windowHandle().screen()
        # 截取当前的屏幕，获得鼠标位置后在当前截图中获得像素颜色
        self.pixmap = self.screen.grabWindow(0)
        #print("屏幕截图尺寸：", self.pixmap.width(),'X',self.pixmap.height())

        # 删除界面上的内容避免影响鼠标位置追踪
        self.discrib_btn.deleteLater()

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

        # 获取屏幕截图
        preViewPixmap = self.pixmap.copy(mouseX - 10, mouseY - 10, 20, 20)
        self.position.update_position(event.globalPosition().toPoint(), mouseX, mouseY, width, height, preViewPixmap)
        self.move_point = QPoint(mouseX, mouseY)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.picking == True:
            # 获取鼠标全局坐标(支持多显示器)
            mouseX, mouseY = win32api.GetCursorPos()
            #计算相对坐标
            for m in self.monitors:
                if m.x <= mouseX < m.x + m.width and m.y <= mouseY < m.y + m.height:
                    # 计算鼠标在当前显示器上的本地位置
                    mouseX = mouseX - m.x
                    mouseY = mouseY - m.y
                    break

            self.start_point = QPoint(mouseX, mouseY)
            #print('self.start_point',self.start_point)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.picking == True:
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

            self.stop_point = QPoint(mouseX, mouseY)
            
            #print('self.stop_point',self.stop_point)

            x = self.start_point.x()
            y = self.start_point.y()
            w = self.stop_point.x() - self.start_point.x() + 1
            h = self.stop_point.y() - self.start_point.y() + 1

            pixmapCopy = self.pixmap.copy(x, y, w, h)

            # 将 QPixmap 复制到剪切板
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(pixmapCopy)
            pixmapCopy.save(os.path.join(os.path.expanduser('~'), 'Desktop')+'/pixmapCopy.png')
            #print(x, y, w, h)

            # 禁用鼠标追踪
            self.setMouseTracking(False)

            # 设置鼠标箭头形状 - 箭头
            self.setCursor(Qt.ArrowCursor)
            # 窗口设置为正常大小
            self.showNormal()
            # 设置窗口完全不透明
            self.setWindowOpacity(1.0)  
            
            # 重新绘制界面
            self.discrib_btn = QPushButton("截屏")
            self.discrib_btn.clicked.connect(self.pickColor)
            self.layout.addWidget(self.discrib_btn)

            
            self.start_point = None
            self.move_point = None

    def paintEvent(self, event):
        if self.start_point != None and self.move_point != None:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            dashed_pen = QPen(Qt.black, 2, Qt.DashLine)
            dashed_pen.setWidth(1)
            painter.setPen(dashed_pen)
            rect = QRect(self.start_point, self.move_point)
            painter.drawRect(rect)

    def keyPressEvent(self, event):
        # 获取当前鼠标位置
        cursor_pos = QCursor.pos()
        # 设置每次移动的步长
        step = 1

        # 根据按下的键移动鼠标位置
        if event.key() == Qt.Key_Up:
            QCursor.setPos(cursor_pos.x(), cursor_pos.y() - step)
        elif event.key() == Qt.Key_Down:
            QCursor.setPos(cursor_pos.x(), cursor_pos.y() + step)
        elif event.key() == Qt.Key_Left:
            QCursor.setPos(cursor_pos.x() - step, cursor_pos.y())
        elif event.key() == Qt.Key_Right:
            QCursor.setPos(cursor_pos.x() + step, cursor_pos.y())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    picker = ScreenColorPicker()
    picker.show()
    sys.exit(app.exec())
