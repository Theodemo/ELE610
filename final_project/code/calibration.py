import cv2
import numpy as np

# Résolution de l'image (à adapter selon ta caméra)
image_width = 1280
image_height = 960
image_size = (image_width, image_height)

# Dictionnaire de correspondance Puck #X → coordonnées 3D
puck_3D_positions = {
    1: [0, 0, 30],
    2: [0, 100, 30],
    3: [100, 0, 30],
    4: [100, 100, 30],
    5: [0, -100, 30],
    6: [-100, 0, 30],
    7: [-100, -100, 30],
    8: [-100, 100, 30],
    9: [100, -100, 30]
}

# === Données à formater pour chaque image ===
# Exemple de données (position de la caméra est juste informative ici)
images_data = [
    {
        "camera_pos": [-100, -100, 500],
        "detections": {
            2: (172, 588),
            3: (656, 579),
            7: (404, 100),
            4: (415, 585),
            1: (407, 342),
        }
    },
    {
        "camera_pos": [-100, 0, 500],
        "detections": {
            2: (414, 582),
            3: (902, 576),
            8: (410, 347),
            7: (648, 93),
            6: (404, 100),
            4: (657, 580),
            1: (648, 337),
            5: (896, 329),
        }
    },
    {
        "camera_pos": [-100, 100, 500],
        "detections": {
            2: (656, 577),
            8: (652, 342),
            6: (648, 94),
            4: (902, 577),
            1: (894, 330),
        }
    },
    {
        "camera_pos": [0, -100, 500],
        "detections": {
            2: (177, 830),
            4: (418, 829),
            3: (661, 825),
            5: (655, 578),
            1: (411, 583),
            7: (409, 344),
        }
    },
    {
        "camera_pos": [0, 0, 500],
        "detections": {
            2: (418, 827),
            3: (908, 822),
            4: (662, 826),
            1: (653, 579),
            6: (410, 345),
            7: (652, 339),
        }
    },
    {
        "camera_pos": [0, 100, 500],
        "detections": {
            6: (652, 340),
            2: (661, 823),
            3: (1155, 819),
            8: (657, 584),
            5: (1150, 571),
            4: (908, 823),
            1: (899, 576),
            7: (897, 333),
        }
    },
    {
        "camera_pos": [100, -100, 500],
        "detections": {
            8: (177, 836),
            6: (172, 592),
            1: (415, 828),
            5: (661, 823),
            7: (414, 586),
        }
    },
    {
        "camera_pos": [100, 0, 500],
        "detections": {
            6: (652, 340),
            2: (661, 823),
            3: (1155, 819),
            8: (657, 584),
            4: (908, 823),
            5: (1150, 571),
            1: (899, 575),
            7: (897, 333),
        }
    },
    {
        "camera_pos": [100, 100, 500],
        "detections": {
            8: (662, 829),
            6: (656, 581),
            5: (1155, 817),
            1: (904, 822),
            7: (902, 577),
        }
    },
]


# === Création des listes pour OpenCV ===
object_points_list = []
image_points_list = []

for img_data in images_data:
    object_points = []
    image_points = []

    for puck_id, pixel_coords in img_data["detections"].items():
        if puck_id in puck_3D_positions:
            object_points.append(puck_3D_positions[puck_id])
            image_points.append(pixel_coords)
        else:
            print(f"⚠️ Puck #{puck_id} non trouvé dans la map 3D")

    if len(object_points) >= 6:
        object_points_list.append(np.array(object_points, dtype=np.float32))
        image_points_list.append(np.array(image_points, dtype=np.float32))


K_init = np.array([[1000, 0, image_width / 2],
                   [0, 1000, image_height / 2],
                   [0, 0, 1]], dtype=np.float32)

# === Calibration ===
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    object_points_list,
    image_points_list,
    image_size,
    cameraMatrix=K_init,
    distCoeffs=None,
    flags=cv2.CALIB_USE_INTRINSIC_GUESS
)


# === Résultats ===
print("✅ Calibration terminée")
print("Matrice intrinsèque (K):\n", K)
print("Coefficients de distorsion:\n", dist)
print(f"Erreur RMS de reprojection: {ret:.4f}")

#if __name__ == "__main__":
#    
#    flip_image("final_project/image/puck_image_-100_-100.png", "final_project/image/puck_image_-100_-100_f.png")
#    flip_image("final_project/image/puck_image_-100_0.png", "final_project/image/puck_image_-100_0_f.png")
#    flip_image("final_project/image/puck_image_-100_100.png", "final_project/image/puck_image_-100_100_f.png")
#    flip_image("final_project/image/puck_image_0_-100.png", "final_project/image/puck_image_0_-100_f.png")
#    flip_image("final_project/image/puck_image_0_0.png", "final_project/image/puck_image_0_0_f.png")
#    flip_image("final_project/image/puck_image_0_100.png", "final_project/image/puck_image_0_100_f.png")
#    flip_image("final_project/image/puck_image_100_-100.png", "final_project/image/puck_image_100_-100_f.png")
#    flip_image("final_project/image/puck_image_100_0.png", "final_project/image/puck_image_100_0_f.png")
#    flip_image("final_project/image/puck_image_100_100.png", "final_project/image/puck_image_100_100_f.png")
#
#
#    # Prendre une photo
#    #take_picture()
#    
#    # Réduire le bruit de l'image capturée
#
#    reduce_image_noise("final_project/image/puck_image_-100_-100_f.png")
#    increase_contrast("final_project/image/denoised_image.png")
#    decode_QR_code("final_project/image/contrast_image.png")
#    
#    reduce_image_noise("final_project/image/puck_image_-100_0_f.png")
#    increase_contrast("final_project/image/denoised_image.png")
#    decode_QR_code("final_project/image/contrast_image.png")
#    
#    reduce_image_noise("final_project/image/puck_image_-100_100_f.png")
#    increase_contrast("final_project/image/denoised_image.png")
#    decode_QR_code("final_project/image/contrast_image.png")
#    
#    reduce_image_noise("final_project/image/puck_image_0_-100_f.png")
#    increase_contrast("final_project/image/denoised_image.png")
#    decode_QR_code("final_project/image/contrast_image.png")
#    
#    reduce_image_noise("final_project/image/puck_image_0_0_f.png")
#    increase_contrast("final_project/image/denoised_image.png")
#    decode_QR_code("final_project/image/contrast_image.png")
#    
#    reduce_image_noise("final_project/image/puck_image_0_100_f.png")
#    increase_contrast("final_project/image/denoised_image.png")
#    decode_QR_code("final_project/image/contrast_image.png")
#    
#    reduce_image_noise("final_project/image/puck_image_100_-100_f.png")
#    increase_contrast("final_project/image/denoised_image.png")
#    decode_QR_code("final_project/image/contrast_image.png")
#    
#    reduce_image_noise("final_project/image/puck_image_100_0_f.png")
#    increase_contrast("final_project/image/denoised_image.png")
#    decode_QR_code("final_project/image/contrast_image.png")
#    
#    reduce_image_noise("final_project/image/puck_image_100_100_f.png")
#    increase_contrast("final_project/image/denoised_image.png")
#    decode_QR_code("final_project/image/contrast_image.png")
#    
#
    # Décoder le QR code de l'image capturée
    #decode_QR_code("final_project/image/QR_code_test.png")
    #decode_QR_code("final_project/image/contrast_image.png")