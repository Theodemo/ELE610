from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QPushButton
from PyQt5.QtCore import Qt

class LuminosityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adjust Luminosity")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        self.label = QLabel("Luminosity Level: 50")
        layout.addWidget(self.label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.update_label)
        layout.addWidget(self.slider)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def update_label(self, value):
        self.label.setText(f"Luminosity Level: {value}")

    def get_luminosity(self):
        return self.slider.value()