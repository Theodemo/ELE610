import cv2
from pyzbar.pyzbar import decode
import numpy as np
import math
import os

def take_picture():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 960)

    for i in range(15):
        ret, frame = cap.read()
        if not ret:
            print("Erreur : impossible de capturer l'image")
            break

    if ret:
        cv2.imshow("Captured Image", frame)
        cv2.imwrite("final_project/image/puck_image_100_-100.png", frame)
        print("Image saved.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    cap.release()

def flip_image(image_path, output_path):
    img = cv2.imread(image_path)
    flipped_img = cv2.flip(img, 0)
    cv2.imwrite(output_path, flipped_img)
    print(f"L'image a été retournée : {output_path}")

def apply_denoise(image, method="bilateral"):
    if method == "median":
        return cv2.medianBlur(image, 5)
    elif method == "gaussian":
        return cv2.GaussianBlur(image, (5, 5), 0)
    elif method == "bilateral":
        return cv2.bilateralFilter(image, 9, 75, 75)
    return image

def apply_contrast(image, factor=1.5):
    yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    yuv_image[:, :, 0] = np.clip(yuv_image[:, :, 0] * factor, 0, 255).astype(np.uint8)
    return cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR)

def apply_CLAHE(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

def binarize_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

def decode2_QR_code(image_path, camera_pos):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)
    detections = {}
    if decoded_objects:
        for obj in decoded_objects:
            text = obj.data.decode('utf-8')
            if "Puck #" in text:
                puck_id = int(text.split("#")[1])
                points = obj.polygon
                if len(points) == 4:
                    cx = sum(p.x for p in points) // 4
                    cy = sum(p.y for p in points) // 4
                    detections[puck_id] = (cx, cy)
    return {"camera_pos": camera_pos, "detections": detections}

def process_best_combination(input_path, camera_pos, temp_dir):
    base_img = cv2.imread(input_path)
    blur_methods = ["median", "gaussian", "bilateral"]
    contrast_factors = [1.2, 1.5, 2.0]
    use_clahe = [False, True]
    use_binarization = [False, True]

    best_data = None
    max_detections = -1

    idx = 0
    for blur in blur_methods:
        for factor in contrast_factors:
            for clahe in use_clahe:
                for binarize in use_binarization:
                    img = apply_denoise(base_img, blur)
                    img = apply_contrast(img, factor)
                    if clahe:
                        img = apply_CLAHE(img)
                    if binarize:
                        img = binarize_image(img)

                    temp_path = os.path.join(temp_dir, f"temp_{camera_pos[0]}_{camera_pos[1]}_{idx}.png")
                    cv2.imwrite(temp_path, img)

                    data = decode2_QR_code(temp_path, [camera_pos[0], camera_pos[1], 500])
                    if len(data["detections"]) > max_detections:
                        best_data = data
                        max_detections = len(data["detections"])
                    idx += 1
    return best_data if best_data else {"camera_pos": [camera_pos[0], camera_pos[1], 500], "detections": {}}

if __name__ == "__main__":
    camera_positions = [
        [-100, -100], [-100, 0], [-100, 100],
        [0, -100], [0, 0], [0, 100],
        [100, -100], [100, 0], [100, 100]
    ]

    temp_dir = "final_project/image/temp"
    os.makedirs(temp_dir, exist_ok=True)

    images_data = []

    for x, y in camera_positions:
        input_path = f"final_project/image/puck_image_{x}_{y}.png"
        flipped_path = f"final_project/image/puck_image_{x}_{y}_f.png"

        flip_image(input_path, flipped_path)

        data = process_best_combination(flipped_path, [x, y], temp_dir)
        images_data.append(data)

    print("\nimages_data = [")
    for item in images_data:
        print("    {")
        print(f"        \"camera_pos\": {item['camera_pos']},")
        print("        \"detections\": {")
        for k, v in item["detections"].items():
            print(f"            {k}: {v},")
        print("        }")
        print("    },")
    print("]")
