import cv2
import numpy as np

# Points 3D connus (en mm dans le repère table)
object_points = np.array([
    [0, -100, 0],
    [100, -100, 0],
    [100, 0, 0],
    [-100, 100, 0]
], dtype=np.float32)

# Points image correspondants (en pixels)
image_points = np.array([
    [902, 368],
    [897, 612],
    [652, 606],
    [414, 359]
], dtype=np.float32)

# Hypothèse : on utilise une matrice de calibration fictive (à ajuster selon ton cas réel)
focal_length = 1000  # à adapter selon ta caméra
cx, cy = 1280 / 2, 960 / 2  # centre de l'image

K = np.array([
    [focal_length, 0, cx],
    [0, focal_length, cy],
    [0, 0, 1]
], dtype=np.float64)

# Pas de distorsion pour simplifier
dist_coeffs = np.zeros((4, 1))

# Estimation des paramètres via solvePnP
success, rvec, tvec = cv2.solvePnP(object_points, image_points, K, dist_coeffs)

# Affichage des résultats
print("Matrice de calibration (K) :")
print(K)



# Matrice de rotation et vecteur de translation (exemple)
R = np.eye(3)  # Caméra orientée comme le monde
t = np.array([[0], [0], [500]])  # Caméra à l'origine

# Coordonnée image (pixel)
image_point = np.array([[740, 480]], dtype='float32')  # centre de l'image

# Si on suppose que Z = 0 (objet sur le sol)
object_points = np.array([
    [0, 0, 0],  # point 3D supposé (plan du sol)
], dtype='float32')

# On utilise solvePnP pour retrouver la pose si on a plusieurs points
success, rvec, tvec = cv2.solvePnP(
    objectPoints=object_points,
    imagePoints=image_point,
    cameraMatrix=K,
    distCoeffs=None,
    flags=cv2.SOLVEPNP_ITERATIVE
)

# Reprojection (pour vérifier)
projected_point, _ = cv2.projectPoints(object_points, rvec, tvec, K, None)
print("Point reprojeté :", projected_point)