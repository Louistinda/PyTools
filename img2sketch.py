from PySide6.QtWidgets import QApplication, QMainWindow, QSlider, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PIL import Image
import numpy as np
import sys

class ImageSketcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_name = None
        self.initUI()

    def initUI(self):
        # Create sliders for depth, elevation, and azimuth with Chinese labels
        self.depth_slider = QSlider(Qt.Horizontal, self)
        self.depth_slider.setMinimum(1)
        self.depth_slider.setMaximum(100)
        self.depth_slider.setValue(10)
        self.depth_slider.setTickPosition(QSlider.TicksBelow)
        self.depth_slider.setTickInterval(10)
        self.depth_slider.valueChanged.connect(self.apply_sketch_effect)
        self.depth_label = QLabel('深度 (Depth)', self)

        self.elevation_slider = QSlider(Qt.Horizontal, self)
        self.elevation_slider.setMinimum(0)
        self.elevation_slider.setMaximum(180)
        self.elevation_slider.setValue(90)
        self.elevation_slider.setTickPosition(QSlider.TicksBelow)
        self.elevation_slider.setTickInterval(10)
        self.elevation_slider.valueChanged.connect(self.apply_sketch_effect)
        self.elevation_label = QLabel('仰角 (Elevation)', self)

        self.azimuth_slider = QSlider(Qt.Horizontal, self)
        self.azimuth_slider.setMinimum(0)
        self.azimuth_slider.setMaximum(360)
        self.azimuth_slider.setValue(45)
        self.azimuth_slider.setTickPosition(QSlider.TicksBelow)
        self.azimuth_slider.setTickInterval(10)
        self.azimuth_slider.valueChanged.connect(self.apply_sketch_effect)
        self.azimuth_label = QLabel('方位角 (Azimuth)', self)

        # Create button to apply sketch effect
        self.button = QPushButton('选择要处理的图片', self)
        self.button.clicked.connect(self.select_file)

        # Create button to apply sketch effect
        self.button1 = QPushButton('保存图片', self)
        self.button1.clicked.connect(self.save_file)

        # Create label to display image
        self.image_label = QLabel(self)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.depth_label)
        layout.addWidget(self.depth_slider)
        layout.addWidget(self.elevation_label)
        layout.addWidget(self.elevation_slider)
        layout.addWidget(self.azimuth_label)
        layout.addWidget(self.azimuth_slider)
        layout.addWidget(self.button)
        layout.addWidget(self.button1)
        layout.addWidget(self.image_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.setWindowTitle('图片转线条风格 (Image to Sketch Converter)')
        self.show()

    def select_file(self):
        self.file_name, _ = QFileDialog.getOpenFileName(self, '打开图片 (Open Image)', '', 'Image Files (*.png *.jpg *.bmp)')
        self.apply_sketch_effect()
    def save_file(self):
        a, _ = QFileDialog.getSaveFileName(self, '保存图片', 'Sketch_Image', 'Image Files (*.png *.jpg *.bmp)')
        self.sketch_pixmap.save(a)

    def apply_sketch_effect(self):
        if self.file_name:
            # Convert sliders' values to appropriate format
            depth = self.depth_slider.value()
            elevation = np.radians(self.elevation_slider.value())
            azimuth = np.radians(self.azimuth_slider.value())

            # Apply sketch effect
            self.sketch_image = self.img_to_sketch(self.file_name, depth, elevation, azimuth)
            

            # Convert the sketch image to QPixmap and display it in the label
            self.sketch_pixmap = QPixmap.fromImage(self.sketch_image)
            
            self.image_label.setPixmap(self.sketch_pixmap.scaled(800, 800, Qt.KeepAspectRatio))

    def img_to_sketch(self, image_path, depth, elevation, azimuth):
        # Open image and convert to grayscale
        img = Image.open(image_path).convert('L')
        img_array = np.array(img).astype('float')

        # Calculate gradient
        grad_x, grad_y = np.gradient(img_array)
        grad_x = grad_x * depth / 100.
        grad_y = grad_y * depth / 100.

        # Calculate unit coordinates
        A = np.sqrt(grad_x**2 + grad_y**2 + 1.)
        uni_x = grad_x / A
        uni_y = grad_y / A
        uni_z = 1. / A

        # Light source direction
        dx = np.cos(elevation) * np.cos(azimuth)
        dy = np.cos(elevation) * np.sin(azimuth)
        dz = np.sin(elevation)

        # Calculate new pixel values
        b = 255 * (dx * uni_x + dy * uni_y + dz * uni_z)
        b = b.clip(0, 255)

        # Create and return the sketch image as a QImage
        return Image.fromarray(b.astype('uint8')).toqimage()

# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageSketcher()
    sys.exit(app.exec())
