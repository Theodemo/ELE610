
import cv2

# Ouvrir la caméra (0 pour la première caméra connectée)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra")
    exit()

while True:
    # Lire une image de la caméra
    ret, frame = cap.read()
    
    if not ret:
        print("Erreur : Impossible de lire l'image")
        break
    
    # Afficher l'image
    cv2.imshow('Flux vidéo', frame)
    
    # Quitter la boucle si l'utilisateur appuie sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()