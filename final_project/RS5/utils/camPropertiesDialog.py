from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class CamPropertiesDialog(QDialog):
    def __init__(self, parent=None, current_exposure=50.0, current_fps=30.0):
        super().__init__(parent)  # Ensure the parent is properly passed
        self.setWindowTitle("Camera Properties")
        self.setGeometry(200, 200, 300, 150)

        # Layout
        layout = QVBoxLayout()

        # Exposure Time
        self.exposure_label = QLabel("Exposure Time (ms):")
        self.exposure_input = QLineEdit(str(current_exposure))

        # Frame Rate
        self.fps_label = QLabel("Frame Rate (FPS):")
        self.fps_input = QLineEdit(str(current_fps))

        # Apply Button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.accept)

        # Add widgets to layout
        layout.addWidget(self.exposure_label)
        layout.addWidget(self.exposure_input)
        layout.addWidget(self.fps_label)
        layout.addWidget(self.fps_input)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def get_values(self):
        """Returns user-input exposure time and frame rate as floats."""
        return float(self.exposure_input.text()), float(self.fps_input.text())
