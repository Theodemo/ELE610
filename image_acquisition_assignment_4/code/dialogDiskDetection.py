from PyQt5.QtWidgets import  QDialog, QFormLayout, QSpinBox, QPushButton, QBoxLayout

class DiskDetectionDialog(QDialog):
    def __init__(self, parent, current_values):
        super().__init__(parent)
        self.setWindowTitle('Paramètres de détection de disque')
        self.setGeometry(200, 200, 400, 200)

        # Paramètres de détection
        self.canny_threshold = QSpinBox()
        self.canny_threshold.setRange(0, 1000)
        self.canny_threshold.setValue(current_values['canny_threshold'])

        self.accumulator_threshold = QSpinBox()
        self.accumulator_threshold.setRange(0, 1000)
        self.accumulator_threshold.setValue(current_values['accumulator_threshold'])

        self.radius_check = QSpinBox()
        self.radius_check.setRange(50, 500)
        self.radius_check.setValue(current_values['radius_check'])
        
        self.binary_threshold = QSpinBox()
        self.binary_threshold.setRange(0, 255)
        self.binary_threshold.setValue(current_values['binary_threshold'])

        # Bouton pour appliquer les paramètres
        apply_button = QPushButton('Appliquer')
        apply_button.clicked.connect(self.applySettings)

        # Layout
        layout = QFormLayout()
        layout.addRow('Seuil de Canny:', self.canny_threshold)
        layout.addRow('Seuil de l\'accumulateur:', self.accumulator_threshold)
        layout.addRow('Rayon de vérification:', self.radius_check)
        layout.addRow('Seuil binaire', self.binary_threshold)

        btnLine = QBoxLayout(1)
        btnLine.addWidget(apply_button)
        btnLine.addStretch()
        layout.addRow(btnLine)

        self.setLayout(layout)

    def applySettings(self):
        # Récupérer les valeurs et appliquer la détection des disques en direct
        settings = {
            'canny_threshold': self.canny_threshold.value(),
            'accumulator_threshold': self.accumulator_threshold.value(),
            'radius_check': self.radius_check.value(),
            'binary_threshold': self.binary_threshold.value()
        }
        self.parent().updateDiskSettings(settings)
        self.parent().detect_disk()  # Appliquer immédiatement la détection du disque
        self.accept()  # Fermer le dialogue après application
