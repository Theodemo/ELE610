import numpy as np
import cv2
from collections import defaultdict

# Paramètres intrinsèques de la caméra (à adapter si calibration réelle dispo)
K = np.array([
    [800, 0, 640],  # fx, cx
    [0, 800, 480],  # fy, cy
    [0,   0,   1]
], dtype=np.float64)

# Pucks réels (X, Y, Z) en mm
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

images_data = [
    {
        "camera_pos": [-100, -100, 500],#x,y,z, la caméra est à 500mm au-dessus du plan de la table et regarde en bas
        # la caméra est à (-100, -100) mm par rapport au centre de la table
        "detections": {
            2: (172.5, 588.25), #sur les image on a (-y,-x) en pixel
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

# Projection P = K * [R | t]
def get_projection_matrix(camera_pos):
    R = np.eye(3)  # caméra regarde vers le bas, donc pas besoin de rotation si axes alignés
    C = np.array(camera_pos).reshape((3, 1))  # position de la caméra
    t = -R @ C  # vecteur de translation
    Rt = np.hstack((R, t))
    return K @ Rt

# Recentrer les pixels dans un repère global basé sur la position de la caméra
def re_center_pixels(camera_pos, pixel):
    # La position de la caméra détermine le décalage de l'origine du repère
    # Nous allons supposer que le repère local 2D est décalé en fonction de la position de la caméra
    # Convertir en repère global
    # Ceci peut être une transformation plus complexe selon la géométrie de la scène
    return np.array([pixel[0] - camera_pos[1], pixel[1] - camera_pos[0]], dtype=np.float32)

# Regrouper les observations pour chaque puck
puck_observations = defaultdict(list)

for img in images_data:
    P = get_projection_matrix(img["camera_pos"])
    for puck_id, pixel in img["detections"].items():
        centered_pixel = re_center_pixels(img["camera_pos"], pixel)
        puck_observations[puck_id].append((P, centered_pixel))

# Triangulation multi-vues
def triangulate(observations):
    if len(observations) < 2:
        return None
    A = []
    for P, pt in observations:
        x, y = pt
        A.append(x * P[2] - P[0])
        A.append(y * P[2] - P[1])
    A = np.stack(A)
    _, _, Vt = np.linalg.svd(A)
    X = Vt[-1]
    X = X / X[3]
    return X[:3]

# Résultats
reconstructed = {}
print("\n--- Résultats de Triangulation ---")
for puck_id, obs in puck_observations.items():
    X = triangulate(obs)
    if X is None:
        print(f"Puck {puck_id}: pas assez d'observations.")
        continue
    reconstructed[puck_id] = X
    X_true = np.array(puck_3D_positions[puck_id])
    err = np.linalg.norm(X - X_true)
    print(f"Puck {puck_id}: Reconstruit = {np.round(X, 2)}, Réel = {X_true}, Erreur = {err:.2f} mm")