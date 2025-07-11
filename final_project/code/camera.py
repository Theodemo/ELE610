import cv2
from pyzbar.pyzbar import decode
import numpy as np
import math

def take_picture():
    # Ouvrir la caméra (0 = webcam par défaut ou ton IDS camera si elle est détectée ici)
    cap = cv2.VideoCapture(0)

    # Définir la résolution à 1280x960
    cap.set(3, 1280)
    cap.set(4, 960)

    # Capturer une image
    for i in range(15):
        ret, frame = cap.read()
        if not ret:
            print("Erreur : impossible de capturer l'image")
            break

    if ret:
        # Afficher l'image dans une fenêtre
        cv2.imshow("Captured Image", frame)

        # Enregistrer l'image dans un fichier
        cv2.imwrite("final_project/image/puck_image_100_-100.png", frame)
        print("Image saved as puck_image.png")

        # Attendre une touche pour fermer la fenêtre
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Erreur : impossible de capturer une image")

    # Libérer la caméra
    cap.release()

  
def reduce_image_noise(image_path):
    """
    Réduit le bruit de l'image en utilisant un filtre gaussien.
    :param image_path: Chemin de l'image à traiter.
    :return: Image traitée.
    """
    # Lire l'image
    image = cv2.imread(image_path)

    # Appliquer un filtre gaussien pour réduire le bruit
    #denoised_image = cv2.medianBlur(image, 30)
    #denoised_image = cv2.GaussianBlur(image, (5, 5), 0)
    denoised_image = cv2.bilateralFilter(image,9,75,75)


    # Enregistrer l'image traitée
    cv2.imwrite("final_project/image/denoised_image.png", denoised_image)
    print("Image denoised_image.png saved.")

    return denoised_image


def binarize_image(image_path):
    """
    Binarise l'image en utilisant un seuillage adaptatif.
    :param image_path: Chemin de l'image à traiter.
    :return: Image traitée.
    """
    # Lire l'image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Appliquer un seuillage adaptatif   
    ret,binary_image = cv2.threshold(image,127,255,cv2.THRESH_BINARY)

    # Enregistrer l'image traitée
    cv2.imwrite("final_project/image/binary_image.png", binary_image)
    print("Image binary_image.png saved.")

    return binary_image

def increase_contrast(image_path):
    """
    Augmente le contraste de l'image.
    :param image_path: Chemin de l'image à traiter.
    :return: Image traitée.
    """
    # Lire l'image
    image = cv2.imread(image_path)

    # Convertir l'image en espace colorimétrique YUV
    yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)

    # Augmenter le contraste en multipliant la composante Y par 1.5
    yuv_image[:, :, 0] = cv2.multiply(yuv_image[:, :, 0], 1.5)

    # Convertir l'image de retour en espace colorimétrique BGR
    contrast_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR)

    # Enregistrer l'image traitée
    cv2.imwrite("final_project/image/contrast_image.png", contrast_image)
    print("Image contrast_image.png saved.")

    return contrast_image

def decode_QR_code(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Decode QR code(s)
    decoded_objects = decode(image)

    if decoded_objects:
        for obj in decoded_objects:
            # Get the polygon points of the QR code
            points = obj.polygon
            if len(points) == 4:
                # Draw the polygon on the image
                pts = np.array([(point.x, point.y) for point in points], dtype=np.int32)
                cv2.polylines(image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

                # Print decoded text
                print("Decoded text:", obj.data.decode('utf-8'))

                # Print corner points
                #print("The four corners of the QR code are:")
                #for i, point in enumerate(points):
                #    print(f"Point {i+1}: ({point.x}, {point.y})")
                    
                # === Calcul du centre ===
                cx = sum(point.x for point in points) / 4
                cy = sum(point.y for point in points) / 4
                center = (int(cx), int(cy))
                print(f"Centre du QR code : ({center[0]}, {center[1]})")
                
                
                # Dessiner le centre sur l'image
                cv2.circle(image, center, 5, (255, 0, 255), -1)  # Rose/violet

                # Orientation angle: vector from point 1 to point 4
                p1 = points[0]
                p4 = points[3]
                dx = p4.x - p1.x
                dy = p4.y - p1.y

                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)

                #print(f"Orientation angle: {angle_deg:.2f}°")

                # Draw the angle line and arrow on image (optional)
                cv2.arrowedLine(image, (p1.x, p1.y), (p4.x, p4.y), (0, 0, 255), 2, tipLength=0.2)
                cv2.putText(image, f"{angle_deg:.1f} deg", (p1.x + 10, p1.y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        # Show image
        cv2.imwrite("final_project/image/decoded_image_100_100.png",image)
        cv2.imshow("QR Code with Orientation", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No QR code found.")
        

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
                    cx = sum(point.x for point in points) // 4
                    cy = sum(point.y for point in points) // 4
                    detections[puck_id] = (cx, cy)

    return {
        "camera_pos": camera_pos,
        "detections": detections
    }



def flip_image(image_path, output_path):
    # Charge l'image
    img = cv2.imread(image_path)
    
    # Flip horizontalement (pour flip vertical, utiliser 0 pour l'axe vertical)
    flipped_img = cv2.flip(img, 0)  # 1 = Flip horizontal, 0 = Flip vertical, -1 = Flip les deux axes
    
    # Sauvegarde l'image retournée
    cv2.imwrite(output_path, flipped_img)
    print(f"L'image a été retournée et enregistrée sous {output_path}")
    

if __name__ == "__main__":
    camera_positions = [
        [-100, -100], [-100, 0], [-100, 100],
        [0, -100], [0, 0], [0, 100],
        [100, -100], [100, 0], [100, 100]
    ]

    images_data = []

    for x, y in camera_positions:
        input_path = f"final_project/image/puck_image_{x}_{y}.png"
        flipped_path = f"final_project/image/puck_image_{x}_{y}_f.png"

        # Flip
        flip_image(input_path, flipped_path)

        # Traitement
        reduce_image_noise(flipped_path)
        #increase_contrast("final_project/image/denoised_image.png")

        # Decode et récupère les données dans le format voulu
        data = decode2_QR_code("final_project/image/denoised_image.png", [x, y, 500])
        images_data.append(data)

    # Afficher la structure finale
    print("images_data = [")
    for item in images_data:
        print("    {")
        print(f"        \"camera_pos\": {item['camera_pos']},")
        print("        \"detections\": {")
        for k, v in item["detections"].items():
            print(f"            {k}: {v},")
        print("        }")
        print("    },")
    print("]")


#if __name__ == "__main__":
#    
#    #flip_image("final_project/image/puck_image_-100_-100.png", "final_project/image/puck_image_-100_-100_f.png")
#    #flip_image("final_project/image/puck_image_-100_0.png", "final_project/image/puck_image_-100_0_f.png")
#    #flip_image("final_project/image/puck_image_-100_100.png", "final_project/image/puck_image_-100_100_f.png")
#    #flip_image("final_project/image/puck_image_0_-100.png", "final_project/image/puck_image_0_-100_f.png")
#    #flip_image("final_project/image/puck_image_0_0.png", "final_project/image/puck_image_0_0_f.png")
#    #flip_image("final_project/image/puck_image_0_100.png", "final_project/image/puck_image_0_100_f.png")
#    #flip_image("final_project/image/puck_image_100_-100.png", "final_project/image/puck_image_100_-100_f.png")
#    #flip_image("final_project/image/puck_image_100_0.png", "final_project/image/puck_image_100_0_f.png")
#    #flip_image("final_project/image/puck_image_100_100.png", "final_project/image/puck_image_100_100_f.png")
#
#
#    # Prendre une photo
#    #take_picture()
#    
#
#    reduce_image_noise("final_project/image/puck_image_-100_-100_f.png")
#    #increase_contrast("final_project/image/")
#    decode_QR_code("final_project/image/denoised_image.png")
#    
#    #reduce_image_noise("final_project/image/puck_image_-100_0_f.png")
#    #increase_contrast("final_project/image/denoised_image.png")
#    #decode_QR_code("final_project/image/contrast_image.png")
#    #
#    #reduce_image_noise("final_project/image/puck_image_-100_100_f.png")
#    #increase_contrast("final_project/image/denoised_image.png")
#    #decode_QR_code("final_project/image/contrast_image.png")
#    #
#    #reduce_image_noise("final_project/image/puck_image_0_-100_f.png")
#    #increase_contrast("final_project/image/denoised_image.png")
#    #decode_QR_code("final_project/image/contrast_image.png")
#    #
#    #reduce_image_noise("final_project/image/puck_image_0_0_f.png")
#    #increase_contrast("final_project/image/denoised_image.png")
#    #decode_QR_code("final_project/image/contrast_image.png")
#    #
#    #reduce_image_noise("final_project/image/puck_image_0_100_f.png")
#    #increase_contrast("final_project/image/denoised_image.png")
#    #decode_QR_code("final_project/image/contrast_image.png")
#    #
#    #reduce_image_noise("final_project/image/puck_image_100_-100_f.png")
#    #increase_contrast("final_project/image/denoised_image.png")
#    #decode_QR_code("final_project/image/contrast_image.png")
#    #
#    #reduce_image_noise("final_project/image/puck_image_100_0_f.png")
#    #increase_contrast("final_project/image/denoised_image.png")
#    #decode_QR_code("final_project/image/contrast_image.png")
#    #
#    #reduce_image_noise("final_project/image/puck_image_100_100_f.png")
#    #increase_contrast("final_project/image/denoised_image.png")
#    #decode_QR_code("final_project/image/contrast_image.png")
#    