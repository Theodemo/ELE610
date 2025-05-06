import numpy as np
import cv2
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QFileDialog, QLabel, QSlider, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(150, 50, 800, 600)
        self.pixmap = QPixmap()
        self.image_path = None
        self.initMenu()

    def initMenu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        dice_menu = menubar.addMenu('Dice')
        camera_menu = menubar.addMenu('Camera')
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)

        detect_pips_action = QAction('Detect Pips', self)
        detect_pips_action.triggered.connect(self.detectPips)
        dice_menu.addAction(detect_pips_action)
        
        detect_color_action = QAction('Detect Dice Color', self)
        detect_color_action.triggered.connect(self.detectDiceColor)
        dice_menu.addAction(detect_color_action)
        
        adjust_camera_action = QAction('Adjust Camera', self)
        adjust_camera_action.triggered.connect(self.adjustCameraSettings)
        camera_menu.addAction(adjust_camera_action)
        
    def openFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Images (*.png *.xpm *.jpg)')
        if file_name:
            self.image_path = file_name
            self.pixmap.load(file_name)
            self.update()

    def detectPips(self):
        if not self.image_path:
            return

        img = cv2.imread(self.image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)

        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=5, maxRadius=30)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
                cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)

        self.displayImage(img)

    def detectDiceColor(self):
        if not self.image_path:
            return

        img = cv2.imread(self.image_path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        color_ranges = {
            'yellow': ((20, 100, 100), (30, 255, 255)),
            'blue': ((100, 100, 100), (140, 255, 255))
        }

        detected_colors = []
        for color, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            if np.any(mask):
                detected_colors.append(color)
        
        print(f"Detected Dice Colors: {', '.join(detected_colors) if detected_colors else 'None'}")

    def displayImage(self, img):
        height, width, channel = img.shape
        bytes_per_line = 3 * width
        q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.pixmap = QPixmap.fromImage(q_img)
        self.update()

    def adjustCameraSettings(self):
        self.camera_settings_window = QWidget()
        self.camera_settings_window.setWindowTitle('Adjust Camera Settings')
        layout = QVBoxLayout()
        
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setMinimum(1)
        self.exposure_slider.setMaximum(100)
        layout.addWidget(QLabel('Exposure'))
        layout.addWidget(self.exposure_slider)
        
        self.camera_settings_window.setLayout(layout)
        self.camera_settings_window.show()

    def paintEvent(self, event):
        if not self.pixmap.isNull():
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.pixmap)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

def find_circle_for_disque(image_path, inverse_ratio=1, min_distance=15, 
                           canny_threshold=240, accumulator_threshold=116, radius_check=350):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # Appliquer le filtre de Canny
    edges = cv2.Canny(gray, 100, canny_threshold)

    # Appliquer un seuillage binaire
    _, binary_img = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)

    # Détection des cercles
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, inverse_ratio, min_distance,
                               param1=canny_threshold, param2=accumulator_threshold,
                               minRadius=400, maxRadius=500)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        print(f"Number of circles detected: {len(circles[0])}")
        
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

            # Dessiner le centre et le contour du cercle
            cv2.circle(img, center, 1, (0, 255, 0), 3)
            cv2.circle(img, center, radius, (255, 0, 255), 3)

            # Dessiner un cercle de rayon spécifique pour analyse
            cv2.circle(img, center, radius_check, (0, 255, 255), 2)

            # Détection des transitions noir/blanc
            transition_points = []
            real_points = []
            for angle in range(0, 360, 2):  # Parcours en degrés
                rad = np.deg2rad(angle)
                x = int(center[0] + radius_check * np.cos(rad))
                y = int(center[1] + radius_check * np.sin(rad))

                # Vérification des limites
                if 0 <= x < binary_img.shape[1] and 0 <= y < binary_img.shape[0]:
                    pixel_value = binary_img[y, x]  # Accès en [y, x] car OpenCV est en (row, col)

                    if len(transition_points) > 0 and pixel_value != transition_points[-1][2]:
                        # Marquer les points de transition (changement de couleur)
                        cv2.circle(img, (x, y), 3, (0, 0, 255), -1)  # Rouge pour transition
                        real_points.append((x, y, pixel_value, angle))                        
                    
                    transition_points.append((x, y, pixel_value, angle))  # Ajouter l'angle aussi
                    
            # Si des transitions ont été trouvées, calculez le point médian
            if len(real_points) >= 2:
                # Récupérer les 2 premières transitions
                (x1, y1, val1, angle1) = real_points[0]
                (x2, y2, val2, angle2) = real_points[1]
                print(angle1)
                print(angle2)
                print(real_points)

                # Calculer l'angle médian entre les deux transitions
                mid_angle = (angle1+angle2) / 2
                rad_mid = np.deg2rad(mid_angle)

                # Calculer la position du point médian sur le cercle
                mid_x = int(center[0] + radius_check * np.cos(rad_mid))
                mid_y = int(center[1] + radius_check * np.sin(rad_mid))

                # Ajouter un point au milieu des deux transitions
                cv2.circle(img, (mid_x, mid_y), 5, (255, 0, 0), -1)  # Marquer le point médian en bleu

    cv2.imshow('Detected Circles with Transitions', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Exemple d'utilisation
find_circle_for_disque('assignment_1/image/circle.jpg')