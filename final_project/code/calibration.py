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
    }

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