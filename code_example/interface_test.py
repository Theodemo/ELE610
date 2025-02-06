import numpy as np
import cv2
from matplotlib import pyplot as plt
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QFileDialog, QLabel
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initial window size and position
        self.setGeometry(150, 50, 800, 600)
    
        # Initialize the pixmap
        self.pixmap = QPixmap()
        
        # Initialize the menu
        self.initMenu()

    def initMenu(self):
        """Method to initialize the menu bar"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')

        # File menu actions
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.openFile)

        save_action = QAction('Save', self)
        save_action.triggered.connect(self.saveFile)

        info_action = QAction('Print Info', self)
        info_action.triggered.connect(self.printInfo)

        quit_action = QAction('Quit', self)
        quit_action.triggered.connect(self.close)

        # Edit menu actions

        grayscale_action = QAction('Convert to Grayscale', self)
        grayscale_action.triggered.connect(self.convertToGrayscale)

        histogram_action = QAction('Display Histogram', self)
        histogram_action.triggered.connect(self.displayHistogram)

        sobel_action = QAction('Sobel Edges', self)
        sobel_action.triggered.connect(self.sobelEdges)

        binary_action = QAction('Binary Image', self)
        binary_action.triggered.connect(self.binaryImage)

        hough_action = QAction('Hough Transform', self)
        hough_action.triggered.connect(self.houghTransform)

        prob_hough_action = QAction('Probabilistic Hough Transform', self)
        prob_hough_action.triggered.connect(self.probabilisticHoughTransform)

        # Add actions to the menus
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(info_action)
        file_menu.addAction(quit_action)


        edit_menu.addAction(grayscale_action)
        edit_menu.addAction(histogram_action)
        edit_menu.addAction(sobel_action)
        edit_menu.addAction(binary_action)
        edit_menu.addAction(hough_action)
        edit_menu.addAction(prob_hough_action)

    def openFile(self):
        self.image_label = QLabel(self)
        self.image_label.setGeometry(10, 10, 780, 530)
        self.image_label.setPixmap(self.pixmap)
        """Open an image file"""
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Images (*.png *.xpm *.jpg)')
        if file_name:
            self.image_path = file_name
            self.pixmap.load(file_name)
            
            self.update()

    def saveFile(self):
        """Save the image file"""
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Images (*.png *.xpm *.jpg)')
        if file_name:
            self.pixmap.save(file_name)
            self.status.setText(f'Saved: {file_name}')

    def printInfo(self):
        """Show image information"""
        if not self.pixmap.isNull():
            print("Image Information:")
            print(f"Width: {self.pixmap.width()}")
            print(f"Height: {self.pixmap.height()}")
            print(f"Size: {self.pixmap.size()}")
            print(f"Depth: {self.pixmap.depth()}")
            print(f"Has Alpha: {self.pixmap.hasAlpha()}")
            print(f"Is Bitmap: {self.pixmap.isQBitmap()}")

            image_format = self.pixmap.toImage().format()
            print(f"Image Format: {image_format}")

            if self.pixmap.hasAlpha():
                print("The image has an alpha channel.")

            if image_format == 3:  # QImage.Format_Indexed8
                print("Image format: Indexed8")
            elif image_format == 4:  # QImage.Format_RGB32
                print("Image format: RGB32")
            elif image_format == 5:  # QImage.Format_ARGB32
                print("Image format: ARGB32")
            else:
                print(f"Other format: {image_format}")

            print(f"Image has {self.pixmap.width() * self.pixmap.height()} pixels.")
            print(f"Aspect ratio: {self.pixmap.width() / self.pixmap.height():.2f}")
            print(f"Image size: {self.pixmap.size()}")    
        else:
            self.status.setText('No image loaded')


    def convertToGrayscale(self):
        if hasattr(self, 'image_path'):
            img = cv2.imread(self.image_path)
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imshow('Gray Image', gray_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def displayHistogram(self):
        if hasattr(self, 'image_path'):
            img = cv2.imread(self.image_path, 0)
            plt.hist(img.ravel(), 256, [0, 256])
            plt.show()

    def sobelEdges(self):
        if hasattr(self, 'image_path'):
            img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
            sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
            sobel_combined = cv2.magnitude(sobelx, sobely)
            sobel_combined = np.uint8(sobel_combined)
            cv2.imshow('Sobel Edge Emphasized Image', sobel_combined)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def binaryImage(self):
        if hasattr(self, 'image_path'):
            img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
            _, binary_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
            cv2.imshow('Binary Image', binary_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def houghTransform(self):
        if hasattr(self, 'image_path'):
            img = cv2.imread(self.image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
            if lines is not None:
                for line in lines:
                    rho, theta = line[0]
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    x1 = int(x0 + 1000 * (-b))
                    y1 = int(y0 + 1000 * (a))
                    x2 = int(x0 - 1000 * (-b))
                    y2 = int(y0 - 1000 * (a))
                    cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.imshow('Hough Transform', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def probabilisticHoughTransform(self):
        if hasattr(self, 'image_path'):
            img = cv2.imread(self.image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imshow('Probabilistic Hough Transform', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()



    def find_circle(image_path, inverse_ratio=1, min_distance=10, canny_threshold=30, accumulator_threshold=30, min_radius=0, max_radius=0):
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, inverse_ratio, min_distance, param1=canny_threshold, param2=accumulator_threshold, minRadius=2, maxRadius=30)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            num_circles = circles.shape[1]
            print(f"Number of circles detected: {num_circles}")
            for i in circles[0, :]:
                center = (i[0], i[1])
                # circle center
                cv2.circle(img, center, 1, (0, 100, 100), 3)
                # circle outline
                radius = i[2]
                cv2.circle(img, center, radius, (255, 0, 255), 3)
        cv2.imshow('detected circles', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    def paintEvent(self, event):


        """Method to paint the image in the window"""
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