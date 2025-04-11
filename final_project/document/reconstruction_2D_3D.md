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

### Estimation de la matrice intrinsèque $\mathbf{K}$

Pour estimer $\mathbf{K}$, on procède à une **calibration de caméra** :

1. On imprime un motif connu (ex : **échiquier**).
2. On prend plusieurs photos du motif sous différents angles.
3. On détecte automatiquement les coins du motif (fonction `cv2.findChessboardCorners`).
4. On utilise `cv2.calibrateCamera()` pour estimer :
   - Les paramètres intrinsèques $\mathbf{K}$,
   - Les distorsions optiques,
   - Et éventuellement la position de la caméra pour chaque image.

```python
# Exemple de calibration
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    objectPoints=real_world_points,  # Ex : grille 3D des coins
    imagePoints=detected_corners,    # Coins détectés dans les images
    imageSize=(width, height),       # Taille des images
    cameraMatrix=None,
    distCoeffs=None
)
```

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
