# Contrôle de bras robot

## 🚀 Overview
![Main Preview](assets/img/main.jpg)

Ce projet implémente un système de contrôle pour un bras robotisé ABB utilisant le langage RAPID et des outils Python pour la communication et la gestion des tâches. Il inclut des fonctionnalités pour détecter des objets (pucks), les manipuler, et interagir avec un outil TATEM via Bluetooth.

## 🎯 Purpose
L'objectif principal de ce projet est de fournir une interface robuste pour :
- Contrôler un bras robot ABB via des commandes RAPID.
- Détecter et manipuler des objets sur une table à l'aide de vision par ordinateur.
- Communiquer avec un outil TATEM (Arduino) pour des mesures précises.
- Tester et démontrer des cycles automatisés pour des applications industrielles.

## 📂 Project Structure
Voici un aperçu des principaux fichiers et dossiers du projet :

### `final_project/RS5/`
- **`AppImageViewer5T.py`** : Interface principale pour la gestion des tâches du robot, incluant la détection et la manipulation des pucks.
- **`utils/clsRWS.py`** : Classe pour la communication avec le contrôleur ABB via Robot Web Services (RWS).
- **`utils/pyueye_example_main.py`** : Exemple d'utilisation de la caméra pour capturer des images et détecter des objets.

### `code_example/`
- **`tatemCom.py`** : Interface en ligne de commande pour interagir avec le robot et l'outil TATEM.
- **`TatemRapidIf.py`** : Classe pour gérer la communication avec le robot ABB via RWS.
- **`TatemArduinoIf.py`** : Gestion de la communication Bluetooth avec l'outil TATEM (Arduino).

### `image_acquisition_assignment_2/`
- **`clsRWS.py`** : Exemple de classe pour la communication avec le robot ABB.

## 🛠️ Features
- **Détection d'objets** : Utilisation de la vision par ordinateur pour localiser des pucks sur une table.
- **Manipulation robotique** : Commandes pour déplacer les pucks détectés vers des positions de référence.
- **Communication avec TATEM** : Lecture et écriture des valeurs de temps via Bluetooth.
- **Interface utilisateur** : Menu interactif pour lancer des tâches spécifiques comme `Task01`, `Task03`, ou `collect_pucks`.

## ⚙️ Technologies utilisées
- **Python** : Pour la logique de contrôle et la communication avec le robot.
- **RAPID** : Langage de programmation pour le bras robot ABB.
- **PyQt5** : Interface graphique pour l'interaction utilisateur.
- **BLE (Bluetooth Low Energy)** : Communication avec l'outil TATEM.
- **OpenCV** : Vision par ordinateur pour la détection des pucks.

## 🚀 Getting Started
### Prérequis
- Python 3.6 ou supérieur.
- Bibliothèques Python : `cmd2`, `bleak`, `requests`, `PyQt5`, `opencv-python`.
- Accès à un robot ABB avec RobotWare et une connexion RWS activée.
- Outil TATEM (Arduino) avec Bluetooth activé.

### Installation
1. Clonez ce dépôt :
   ```bash
   git clone <repository-url>
   cd <repository-folder>
## 🌟 License
This project is open-source. Feel free to use, modify, and contribute! 🚀