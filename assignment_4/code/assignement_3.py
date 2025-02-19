import cv2
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from dialogDiskDetection import DiskDetectionDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(150, 50, 1920,1080)
        self.image_path = None
        self.disk_settings = {
            'canny_threshold': 240,
            'accumulator_threshold': 116,
            'radius_check': 350,
            'binary_threshold': 230
        }
        
        self.initUI()
        self.initMenu()

    def initUI(self):
        # Widget principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Création de la grille
        self.grid_layout = QGridLayout()
        self.central_widget.setLayout(self.grid_layout)
        
        # Labels pour afficher les images
        self.labels = [[QLabel(self) for _ in range(2)] for _ in range(2)]
        for i in range(2):
            for j in range(2):
                self.grid_layout.addWidget(self.labels[i][j], i, j)
                self.labels[i][j].setScaledContents(True)

    def initMenu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        disk_menu = menubar.addMenu('Disk')

        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)
        
        
        detect_disk_action = QAction('Detect Disk', self)
        detect_disk_action.triggered.connect(self.showDiskDetectionDialog)
        disk_menu.addAction(detect_disk_action)
        
    def showDiskDetectionDialog(self):
        # Ouvrir le dialogue pour configurer la détection du disque
        dialog = DiskDetectionDialog(self, self.disk_settings)
        dialog.exec_()  # Attendre que l'utilisateur applique les paramètres

    def updateDiskSettings(self, new_settings):
        # Mettre à jour les paramètres de détection des disques
        self.disk_settings = new_settings

        
    def openFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Images (*.png *.xpm *.jpg)')
        if file_name:
            self.image_path = file_name
            img = cv2.imread(file_name)
            self.displayImage(img, 0, 0)  # Affichage de l'image originale
            
    def detect_disk(self):
        inverse_ratio = 1
        min_distance = 15
        canny_threshold = self.disk_settings['canny_threshold']
        accumulator_threshold = self.disk_settings['accumulator_threshold']
        radius_check = self.disk_settings['radius_check']
        binary_threshold = self.disk_settings['binary_threshold']
        
        img = cv2.imread(self.image_path, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        
        canny_edges = cv2.Canny(gray, canny_threshold / 2, canny_threshold)
        self.displayImage(canny_edges, 0, 1)  # Affichage du filtre de Canny

        # Appliquer un seuillage binaire
        _,binary_img = cv2.threshold(gray, binary_threshold, 255, cv2.THRESH_BINARY)
        
        self.displayImage(binary_img, 1, 0)

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

                    # Calculer l'angle médian entre les deux transitions
                    mid_angle = (angle1+angle2) / 2
                    rad_mid = np.deg2rad(mid_angle)

                    # Calculer la position du point médian sur le cercle
                    mid_x = int(center[0] + radius_check * np.cos(rad_mid))
                    mid_y = int(center[1] + radius_check * np.sin(rad_mid))

                    # Ajouter un point au milieu des deux transitions
                    cv2.circle(img, (mid_x, mid_y), 5, (255, 0, 0), -1)  # Marquer le point médian en bleu

        self.displayImage(img, 1, 1)  # Affichage du disque détecté

    def displayImage(self, img, row, col):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width, channel = img.shape
        bytes_per_line = 3 * width
        q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        self.labels[row][col].setPixmap(pixmap)
        self.labels[row][col].setFixedSize(900, 500)  # Taille fixe pour bien séparer les images


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

