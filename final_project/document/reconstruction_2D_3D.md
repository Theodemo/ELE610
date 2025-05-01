# Reconstruction 3D à partir d’une image 2D

## Énoncé du problème

On souhaite déterminer les **coordonnées réelles (X, Y, Z)** d’un objet dans l’espace 3D à partir de sa position **(x, y)** dans une **image 2D** prise par une caméra.

---

## On cherche à

Reconstituer la **position réelle** d’un point observé dans une image, en utilisant le **modèle de projection de la caméra**.

---

## On sait que

- Une caméra projette un point du monde réel $(X, Y, Z)$ en un point image $(x, y)$ selon le modèle de **caméra à trou d’aiguille** (pinhole).
- Cette projection suit la relation :

  $$
  s
  \begin{bmatrix}
  x \\
  y \\
  1
  \end{bmatrix}
  =
  \mathbf{K} \cdot [\mathbf{R} \ | \ \mathbf{t}] \cdot
  \begin{bmatrix}
  X \\
  Y \\
  Z \\
  1
  \end{bmatrix}
  $$

- Où :
  - $s$ est un facteur d’échelle (lié à la profondeur),
  - $\mathbf{K}$ est la matrice **intrinsèque** (focale, centre optique...),
  - $[\mathbf{R} | \mathbf{t}]$ est la matrice **extrinsèque** (position de la caméra),
  - $(x, y)$ est la **coordonnée pixel**,
  - $(X, Y, Z)$ est la **coordonnée réelle**.

- Ce problème **ne peut pas être résolu sans ambiguïté** sans information sur la **profondeur** (Z), ou sans hypothèse sur le **plan** dans lequel se trouve l’objet (ex: Z = 0 pour le sol).

---

## Par conséquent

Partons de l’hypothèse suivante :

- L’objet est situé sur le **plan du sol**, donc sa **profondeur est Z = 0**.
- On connaît la position et l’orientation de la caméra :
  - La caméra est située à **1,5 mètre de hauteur**, orientée vers l’avant, sans inclinaison.
  - En coordonnées du monde, cela signifie :
    - Rotation $\mathbf{R} = \mathbf{I}_{3×3}$ (pas de rotation),
    - Translation $\mathbf{t} = \begin{bmatrix} 0 \\ 0 \\ 1.5 \end{bmatrix}$ (hauteur = 1.5 m).

Dans ce cas, on peut reconstruire la position réelle du point ainsi :

1. **On inverse la projection perspective** :
   - À partir de l’image $(x, y)$, on génère un **rayon dans l’espace 3D** à travers le centre optique.
2. **On intersecte ce rayon avec le plan Z = 0** pour trouver les coordonnées (X, Y, Z).

---

### Calibration de caméra sans échiquier

Il est possible de calibrer une caméra **sans utiliser de motif d’échiquier**, à condition de disposer de plusieurs images avec :

- Des **points 3D connus** dans un repère fixe (monde/table/etc.)
- Les **projections 2D** correspondantes dans l’image (pixels)

---

#### Conditions nécessaires

1. **Plusieurs images** (au moins 10, idéalement)
2. Au moins **6–8 points** bien répartis dans chaque image
3. Les points doivent être vus **sous différents angles** (pas toujours la même position de la caméra)
4. Les points doivent être **non-coplanaires** si possible (ou bien répartis dans l'image si en 2D)

---

#### Étapes du pipeline

1. Pour chaque image :
   - Identifier les points 3D réels (en mm, cm…)
   - Repérer les points 2D correspondants dans l’image (en pixels)

2. Remplir deux listes :
   - `object_points_list` : liste des points 3D par image
   - `image_points_list` : liste des points 2D par image

3. Appliquer la fonction OpenCV :

```python
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    object_points_list,
    image_points_list,
    image_size=(width, height),
    cameraMatrix=None,
    distCoeffs=None
)
```

4. Récupérer :

    `K` : matrice de calibration (intrinsèques)

    `dist` : coefficients de distorsion

    `rvecs, tvecs` : poses de la caméra pour chaque image

## Conclusion

Ce problème nécessite **la calibration de la caméra** et une **hypothèse sur la profondeur ou le plan de l’objet**. Une fois ces éléments réunis, on peut reconstituer les coordonnées réelles de l’objet avec des outils comme **OpenCV**.

---

## Exemple d’implémentation avec OpenCV

```python
import cv2
import numpy as np

# Matrice intrinsèque (exemple)
K = np.array([
    [800, 0, 320],
    [0, 800, 240],
    [0,   0,   1]
])

# Matrice de rotation et vecteur de translation (exemple)
R = np.eye(3)  # Caméra orientée comme le monde
t = np.array([[0], [0], [1.5]])  # Caméra à l'origine

# Coordonnée image (pixel)
image_point = np.array([[320, 240]], dtype='float32')  # centre de l'image

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

```

```python
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
        "camera_pos": [0, 0, 500],
        "detections": {
            3: (908, 137),
            2: (418, 132),
            6: (410, 613),
            7: (652, 619),
            1: (653, 379),
            5: (901, 384),
            4: (662, 133)
        }
    },
    {
        "camera_pos": [-100, -100, 500],
        "detections": {
            2: (172, 371),
            3: (656, 380),
            6: (163, 852),
            7: (404, 859),
            5: (651, 622),
            4: (415, 374),
            1: (407, 617)
        }
    },
    {
        "camera_pos": [-100, 0, 500],
        "detections": {
            2: (414, 377),
            6: (404, 858),
            8: (410, 612),
            3: (902, 383),
            7: (647, 865),
            1: (648, 622),
            5: (896, 629),
            4: (656, 379)
        }
    },
    {
        "camera_pos": [-100, 100, 500],
        "detections": {
            6: (648, 865),
            8: (652, 617),
            2: (656, 381),
            5: (1146, 635),
            4: (902, 382),
            7: (894, 873)
        }
    },
    {
        "camera_pos": [0, -100, 500],
        "detections": {
            6: (167, 610),
            2: (177, 129),
            3: (662, 134),
            4: (419, 130),
            7: (410, 615),
            1: (411, 375),
            5: (655, 381)
        }
    },
    {
        "camera_pos": [0, 100, 500],
        "detections": {
            8: (657, 374),
            6: (652, 619),
            3: (1155, 140),
            2: (661, 135),
            7: (897, 626),
            1: (899, 383),
            5: (1151, 387),
            4: (908, 135)
        }
    },
    {
        "camera_pos": [100, -100, 500],
        "detections": {
            6: (172, 367),
            8: (177, 122),
            7: (414, 373),
            5: (661, 135),
            1: (415, 130)
        }
    },
    {
        "camera_pos": [100, 0, 500],
        "detections": {
            8: (657, 375),
            3: (1155, 140),
            6: (652, 619),
            2: (661, 135),
            5: (1150, 387),
            1: (898, 383),
            4: (908, 135),
            7: (897, 626)
        }
    },
    {
        "camera_pos": [100, 100, 500],
        "detections": {
            6: (656, 377),
            8: (662, 129),
            5: (1154, 142),
            7: (902, 381)
        }
    }
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

    object_points_list.append(np.array(object_points, dtype=np.float32))
    image_points_list.append(np.array(image_points, dtype=np.float32))

# === Calibration ===
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    object_points_list,
    image_points_list,
    image_size,
    None,
    None
)

# === Résultats ===
print("✅ Calibration terminée")
print("Matrice intrinsèque (K):\n", K)
print("Coefficients de distorsion:\n", dist)
print(f"Erreur RMS de reprojection: {ret:.4f}")

```