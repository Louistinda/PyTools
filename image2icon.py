import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QComboBox,
                               QFileDialog, QMessageBox, QVBoxLayout, QWidget)
from PySide6.QtGui import QIcon
from PIL import Image

class ImageConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ICON转换器')
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(270, 100)

        # 主窗口布局
        layout = QVBoxLayout()

        # 下拉框
        self.comboBox = QComboBox(self)
        self.comboBox.addItems(["32x32", "64x64", "128x128"])
        layout.addWidget(self.comboBox)

        # 按钮
        self.button = QPushButton('开始转换', self)
        self.button.clicked.connect(self.convert_image)
        layout.addWidget(self.button)

        # 设置布局
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def convert_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, '选择图片', 
                                                   filter='Image files (*.jpg *.png)')
        if file_name:
            size_str = self.comboBox.currentText()
            size = tuple(map(int, size_str.split('x')))
            icon_file_name = QFileDialog.getExistingDirectory(self, '保存图标文件')

            if icon_file_name:
                base_name = file_name.rsplit('/', 1)[-1].rsplit('.', 1)[0]
                final_icon_name = f"{icon_file_name}/{base_name}_{size_str}.ico"

                #图片转换过程
                image = Image.open(file_name)
                white2Transp = True
                if white2Transp == True:
                    image = image.convert("RGBA")
                    datas = image.getdata()
                    newDatas = []
                    for item in datas:
                        # 如果是#FFFFFF，则设置为透明
                        if item[0] >= 240 and item[1] >= 240 and item[2] >= 240:
                            newDatas.append((255, 255, 255, 0))
                        else:
                            newDatas.append(item)
                    
                    # 更新图片数据
                    image.putdata(newDatas)
                image.save(final_icon_name, format='ICO', sizes=[size])
                QMessageBox.information(self, '成功', '图片转换成功！')
            else:
                QMessageBox.warning(self, '警告', '未选择图标文件保存位置。')
        else:
            QMessageBox.warning(self, '警告', '未选择图片。')

def main():
    app = QApplication(sys.argv)
    ex = ImageConverter()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
