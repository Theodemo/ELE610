import numpy as np
import cv2
from matplotlib import pyplot as plt

############################################################################################

"""
Open an image file and print its properties.
Parameters:
image_path (str): The path to the image file.
Returns:
None
"""
def open_image_and_print_properties(image_path):

    # Open the image file
    img = cv2.imread(image_path)
      
    # Print the properties of the numpy array
    print( f"{img.dtype = }, {img.size = }, {img.ndim = }, {img.shape = }" )
# Example usage
#open_image_and_print_properties('cropped_chessboard.jpg')

############################################################################################

"""
Open and display an image file.
Parameters:
image_path (str): The path to the image file.
Returns:
None
"""
def display_image(image_path):
    # Open the image file
    img = cv2.imread(image_path)
    
    # Display the image
    cv2.imshow('Image', img)
    
    # Wait for a key press and close the image window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
#display_image('cropped_chessboard.jpg')

############################################################################################

"""
Open an image file, convert it to grayscale, and display it.
Parameters:
image_path (str): The path to the image file.
Returns:
None
"""
def convert_to_grayscale(image_path):
    # Open the image file
    img = cv2.imread(image_path)
    
    # Convert the image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cv2.imshow('Gray Image', gray_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
# Example usage
#convert_to_grayscale('cropped_chessboard.jpg')

############################################################################################

"""
Open an image file, check its color space, and correct it if necessary.
Parameters:
image_path (str): The path to the image file.
Returns:
None
"""

def check_and_correct_color_space(image_path):
    # Open the image file
    img = cv2.imread(image_path)
    
    # Check if the image is in BGR color space (OpenCV default)
    if img is None:
        print("Error: Unable to open image.")
        return
    
    # Display the original image
    cv2.imshow('Original Image', img)
    cv2.waitKey(0)
    
    # Swap the Red and Blue color components to convert BGR to RGB
    corrected_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Display the corrected image
    cv2.imshow('Corrected Image', corrected_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
#check_and_correct_color_space('cropped_chessboard.jpg')

############################################################################################

"""
Open an image file and display its histogram.
Parameters:
image_path (str): The path to the image file.
Returns:
None
"""
def display_histogram(image_path):
    img = cv2.imread(image_path,0)
    plt.hist(img.ravel(),256,[0,256]); 
    plt.show()

# Example usage
#display_histogram('cropped_chessboard.jpg')

############################################################################################


"""
"""
def sobel_edges(image_path, ksize=3, scale=1, delta=0):
    # Open the image file
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Check if the image is loaded properly
    if img is None:
        print("Error: Unable to open image.")
        return
    
    # Apply Sobel filter to emphasize edges
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=ksize, scale=scale, delta=delta)
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=ksize, scale=scale, delta=delta)
    sobel_combined = cv2.magnitude(sobelx, sobely)
    
    # Convert back to uint8
    sobel_combined = np.uint8(sobel_combined)
    
    # Display the original and edge-emphasized images
    cv2.imshow('Original Image', img)
    cv2.imshow('Sobel Edge Emphasized Image', sobel_combined)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
#sobel_edges('cropped_chessboard.jpg')

############################################################################################

"""
Open an image file, apply thresholding to convert it to binary, and display the result.
Parameters:
image_path (str): The path to the image file.
threshold_value (int): The threshold value to convert the image to binary. Default is 128.
    - Increasing the value will make more pixels black.
    - Decreasing the value will make more pixels white.
Returns:
None
"""
def binary_image(image_path, threshold_value=128):
    # Open the image file
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Check if the image is loaded properly
    if img is None:
        print("Error: Unable to open image.")
        return
    
    # Apply thresholding to convert the image to binary
    _, binary_img = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)
    
    # Display the original and binary images
    cv2.imshow('Original Image', img)
    cv2.imshow('Binary Image', binary_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
#binary_image('cropped_chessboard.jpg', threshold_value=128)

############################################################################################

"""
Open an image file, apply probabilistic Hough Line Transform, and display the result.
Parameters:
image_path (str): The path to the image file.
rho (float): Distance resolution of the accumulator in pixels. Default is 1.
    - Increasing the value will detect fewer lines.
    - Decreasing the value will detect more lines.
theta (float): Angle resolution of the accumulator in radians. Default is np.pi/180.
    - Increasing the value will detect fewer lines.
    - Decreasing the value will detect more lines.
threshold (int): Accumulator threshold parameter. Only those lines are returned that get enough votes. Default is 100.
    - Increasing the value will detect fewer lines.
    - Decreasing the value will detect more lines.
min_line_length (int): Minimum line length. Line segments shorter than this are rejected. Default is 500.
    - Increasing the value will detect fewer lines.
    - Decreasing the value will detect more lines.
max_line_gap (int): Maximum allowed gap between line segments to treat them as a single line. Default is 10.
    - Increasing the value will merge more line segments.
    - Decreasing the value will merge fewer line segments.
Returns:
None
"""
def probabilistic_hough_tranform(image_path, rho=1, theta=np.pi/180, threshold=100, min_line_length=100, max_line_gap=10):
    img = cv2.imread(cv2.samples.findFile(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, minLineLength=min_line_length, maxLineGap=max_line_gap)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imshow('houghlines.jpg', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
#probabilistic_hough_tranform('cropped_chessboard.jpg')

############################################################################################

"""
Open an image file, apply Hough Line Transform, and display the result.
Parameters:
image_path (str): The path to the image file.
rho (float): Distance resolution of the accumulator in pixels. Default is 1.
    - Increasing the value will detect fewer lines.
    - Decreasing the value will detect more lines.
theta (float): Angle resolution of the accumulator in radians. Default is np.pi/180.
    - Increasing the value will detect fewer lines.
    - Decreasing the value will detect more lines.
threshold (int): Accumulator threshold parameter. Only those lines are returned that get enough votes. Default is 200.
    - Increasing the value will detect fewer lines.
    - Decreasing the value will detect more lines.
Returns:
None
"""
def hough_tranform(image_path, rho=1, theta=np.pi/180, threshold=200):
    img = cv2.imread(cv2.samples.findFile(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, rho, theta, threshold)
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
    cv2.imshow('houghlines3.jpg', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
#hough_tranform('C:/Users/theod/Documents/UIS/IA/py/Assignement_1/image/cropped_chessboard.jpg')

############################################################################################

"""
Open an image file, apply Hough Circle Transform, and display the result.
Parameters:
image_path (str): The path to the image file.
inverse_ratio (float): Inverse ratio of the accumulator resolution to the image resolution. Default is 1.
    - Increasing the value will detect fewer circles.
    - Decreasing the value will detect more circles.
min_distance (float): Minimum distance between the centers of the detected circles. Default is 10.
    - Increasing the value will detect fewer circles.
    - Decreasing the value will detect more circles.
canny_threshold (float): Higher threshold for the Canny edge detector. Default is 30.
    - Increasing the value will detect fewer circles.
    - Decreasing the value will detect more circles.
accumulator_threshold (float): Accumulator threshold for the circle centers at the detection stage. Default is 30.
    - Increasing the value will detect fewer circles.
    - Decreasing the value will detect more circles.
min_radius (int): Minimum circle radius. Default is 0.
    - Increasing the value will detect fewer circles.
    - Decreasing the value will detect more circles.
max_radius (int): Maximum circle radius. Default is 0.
    - Increasing the value will detect fewer circles.
    - Decreasing the value will detect more circles.
Returns:
None
"""

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

# Example usage
#find_circle('C:/Users/theod/Documents/UIS/IA/py/Assignement_1/image/circle.png')

############################################################################################
"""
Open an image file, convert it to grayscale, apply thresholding, and count the number of black dots (assumed to be dice pips).
Parameters:
image_path (str): The path to the image file.
threshold_value (int): The threshold value to convert the image to binary. Default is 128.
Returns:
int: The number of black dots found in the image.
"""
def count_black_dots(image_path, threshold_value=40):
    # Open the image file
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Check if the image is loaded properly
    if img is None:
        print("Error: Unable to open image.")
        return 0
    
    # Apply thresholding to convert the image to binary
    _, binary_img = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Count the number of contours (black dots)
    num_black_dots = len(contours)
    
    # Display the original and binary images with contours
    cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
    cv2.imshow('Original Image with Contours', img)
    cv2.imshow('Binary Image', binary_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return num_black_dots

# Example usage
num_dots = count_black_dots('C:/Users/theod/Documents/UIS/IA/py/Assignement_1/image/circle.png')
print(f"Number of black dots: {num_dots}")