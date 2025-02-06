try:
    import cv2
except ImportError:
    print("Error importing cv2, functions from myImageTools have cv2 options disabled.")


img = cv2.imread('C:/Users/jesus/ELE610/py/IA 1.4/table.jpg')
print(f"{img.dtype=}, {img.size=}, {img.ndim=}, {img.shape=}")


print(img.size)


height, width = img.shape[:2]


startX = (height) // 3
stratY = (width) // 3


endX = height - startX
endY = width - stratY


cropped_img = img[startX:endX, stratY:endY]
print(f"{cropped_img.dtype=}, {cropped_img.size=}, {cropped_img.ndim=}, {cropped_img.shape=}")


cv2.imshow("Cropped Image", cropped_img)
cv2.waitKey(0)
cv2.destroyAllWindows()