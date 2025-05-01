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
        "camera_pos": [-100, -100, 500],#
        "detections": {
            2: (172.5, 588.25),
            3: (657.0, 579.5),
            8: (168.25, 351.75),
            4: (415.0, 585.0),
            1: (406.75, 342.25),
            5: (651.5, 336.25),
            6: (162.75, 107.0),
            7: (404.5, 100.0),
        }
    },
    {
        "camera_pos": [-100, 0, 500],#
        "detections": {
            8: (411.0, 612.5),
            3: (902.25, 383.0),
            7: (648.25, 865.5),
            6: (404.5, 858.75),
            2: (414.5, 376.75),
            1: (648.5, 622.0),
            5: (897.0, 629.25),
            4: (657.0, 379.0),
        }
    },
    {
        "camera_pos": [-100, 100, 500],#
        "detections": {
            2: (656.25, 577.75),
            8: (652.75, 341.75),
            3: (1151.0, 572.5),
            6: (648.25, 94.25),
            1: (894.5, 330.75),
            5: (1146.5, 324.25),
            7: (895.0, 86.0),
            4: (902.5, 577.25),
        }
    },
    {
        "camera_pos": [0, -100, 500],#
        "detections": {
            2: (177.25, 830.25),
            3: (661.5, 824.75),
            8: (173.0, 593.75),
            6: (167.25, 349.75),
            5: (656.0, 577.75),
            7: (410.25, 343.5),
            4: (419.0, 829.0),
            1: (411.5, 584.0),
        }
    },
    {
        "camera_pos": [0, 0, 500],#
        "detections": {
            8: (415.75, 588.75),
            2: (418.75, 827.0),
            3: (908.0, 822.75),
            6: (410.5, 345.25),
            4: (662.75, 826.0),
            1: (653.5, 579.5),
            5: (901.75, 575.25),
            7: (652.0, 339.5),
        }
    },
    {
        "camera_pos": [0, 100, 500],#
        "detections": {
            6: (652.25, 340.25),
            2: (661.75, 823.5),
            3: (1156.5, 819.5),
            8: (657.25, 584.25),
            4: (908.5, 823.75),
            5: (1150.75, 571.25),
            1: (899.25, 576.25),
            7: (897.75, 333.0),
        }
    },
    {
        "camera_pos": [100, -100, 500],#
        "detections": {
            8: (177.25, 836.75),
            1: (415.25, 828.25),
            5: (661.25, 823.25),
            6: (172.0, 592.5),
            7: (414.0, 586.25),
        }
    },
    {
        "camera_pos": [100, 0, 500],#
        "detections": {
            6: (652.25, 619.0),
            8: (657.25, 374.75),
            3: (1155.5, 139.75),
            2: (661.75, 135.75),
            7: (897.5, 626.0),
            5: (1150.5, 387.75),
            1: (899.0, 383.0),
            4: (908.5, 135.75),
        }
    },
    {
        "camera_pos": [100, 100, 500],
        "detections": {
            8: (662.25, 829.75),
            6: (656.25, 582.0),
            1: (904.75, 822.0),
            5: (1154.5, 817.25),
            7: (902.0, 577.75),
        }
    },
]


# Création des points pour calibration
object_points_list = []
image_points_list = []

for img_data in images_data:
    object_points = []
    image_points = []

    for puck_id, pixel_coords in img_data["detections"].items():
        if puck_id in puck_3D_positions:
            object_points.append(puck_3D_positions[puck_id])
            image_points.append(pixel_coords)
    if len(object_points) >= 6:
        object_points_list.append(np.array(object_points, dtype=np.float32))
        image_points_list.append(np.array(image_points, dtype=np.float32))

print(f"Images utilisées pour calibration: {len(object_points_list)}")

# Initialisation réaliste de la matrice K
K_init = np.array([
    [7300, 0, image_width / 2],
    [0, 5600, image_height / 2],
    [0, 0, 1]
], dtype=np.float32)

# Distorsion initiale à zéro
dist_init = np.zeros(5)

# Calibration avec contraintes
flags = (
    cv2.CALIB_USE_INTRINSIC_GUESS |
    cv2.CALIB_FIX_K3 |
    cv2.CALIB_ZERO_TANGENT_DIST
)

ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    object_points_list,
    image_points_list,
    image_size,
    cameraMatrix=K_init,
    distCoeffs=dist_init,
    flags=flags
)

print("✅ Calibration terminée")
print("Matrice intrinsèque (K):\n", K)
print("Coefficients de distorsion:\n", dist.ravel())
print(f"Erreur RMS de reprojection: {ret:.4f}")

# Affiche l'erreur moyenne par image
for i, (obj_pts, img_pts) in enumerate(zip(object_points_list, image_points_list)):
    projected_pts, _ = cv2.projectPoints(obj_pts, rvecs[i], tvecs[i], K, dist)
    projected_pts = projected_pts.reshape(-1, 2)
    error = np.linalg.norm(img_pts - projected_pts, axis=1).mean()
    print(f"Image {i} - Erreur moyenne de reprojection: {error:.2f} pixels")

# Fonction de conversion image → monde
def image_to_world_point(u, v, K, dist, rvec, tvec, z_world=30):
    uv_point = np.array([[u, v]], dtype=np.float32)
    uv_undistorted = cv2.undistortPoints(uv_point, K, dist, P=K)
    uv_homog = np.array([uv_undistorted[0][0][0], uv_undistorted[0][0][1], 1.0])
    R, _ = cv2.Rodrigues(rvec)
    R_inv = np.linalg.inv(R)
    cam_dir = np.linalg.inv(K).dot(uv_homog).reshape(3, 1)
    cam_dir /= np.linalg.norm(cam_dir)
    s = (z_world - (R_inv @ tvec)[2]) / (R_inv @ cam_dir)[2]
    world_point = R_inv @ (s * cam_dir - tvec)
    return world_point.flatten()

# Exemple de conversion d’un point image en coordonnées monde
i = 0  # image à tester
if i < len(rvecs):
    rvec = rvecs[i]
    tvec = tvecs[i]
    u, v = images_data[i]["detections"][4]  # par exemple le puck 3
    X, Y, Z = image_to_world_point(u, v, K, dist, rvec, tvec, z_world=30)
    print(f"Coordonnées 3D estimées: X={X:.2f}, Y={Y:.2f}, Z={Z:.2f}")
    print(f"Coordonnées 3D réelles: {puck_3D_positions[4]}")
else:
    print(f"⚠️ L'image {i} n'a pas été incluse dans la calibration.")